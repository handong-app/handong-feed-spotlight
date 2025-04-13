import json
import ollama
import logging

from google import genai
from google.genai import types

from app.core.config import EnvVariables
from app.schemas.tag_labeling_dto import MessageTagAssignment

logger = logging.getLogger(__name__)

class LLMService:
    def assign_tag_to_message(self, subject_id, message, tags) -> MessageTagAssignment | None:
        """
        단일 메시지에 적합한 태그 코드를 할당합니다.
        최대 3번까지 재시도하며, Gemini API를 호출하여 태그 코드 배열(JSON 문자열)을 반환받습니다.
        """
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                response_text = self.request_tag_assignment(message, tags)
                logger.info(f"Gemini API response for subject_id {subject_id}, attempt {attempt}: {response_text}")
                tag_codes = self.extract_tag_codes_array_from_json_str(response_text)
                if isinstance(tag_codes, list) and all(isinstance(tc, str) for tc in tag_codes) and tag_codes:
                    return MessageTagAssignment(subject_id=subject_id, tag_codes=tag_codes)
                else:
                    raise Exception("추출된 결과가 유효한 문자열 배열이 아닙니다.")
            except Exception as e:
                logger.error(f"Gemini API 응답 파싱 실패 for subject_id {subject_id} on attempt {attempt}: {e}")
                if attempt == max_attempts:
                    raise Exception(
                        f"assign_tag_to_message 실패: {subject_id}에 대해 {max_attempts}번 시도했으나 실패했습니다. ({e})") from e


    def request_tag_assignment(self, message, tags) -> str:
        """
        EnvVariables.LLM_PROVIDER 값을 참조하여, Ollama 또는 Gemini API 호출 함수를 선택합니다.
        """
        provider = EnvVariables.LLM_PROVIDER.lower()
        if provider == "gemini":
            return self.request_tag_assignment_gemini(message, tags)
        elif provider == "ollama":
            return self.request_tag_assignment_ollama(message, tags)
        else:
            raise Exception(f"지원하지 않는 LLM provider: {provider}")


    def request_tag_assignment_ollama(self, message, tags) -> str:
        """
        Ollama 를 호출하여 프롬프트에 따른 LLM 응답(태그 코드 배열의 JSON 문자열)을 반환합니다.
        """
        prompt_dict =  self.get_prompt(message, tags)
        messages = [
            {"role": "system", "content": prompt_dict["system_prompt"]},
            {"role": "user", "content": prompt_dict["content"]},
        ]

        llm_resp = ollama.chat(model="llama3:8b", messages=messages)
        try:
            response_text = llm_resp["message"]["content"]
            return response_text
        except Exception as e:
            logger.error(f"Ollama call failed: {e}")
            raise Exception("Ollama 호출 실패: " + str(e)) from e


    def request_tag_assignment_gemini(self, message, tags) -> str:
        """
        Gemini API를 호출하여 프롬프트에 따른 LLM 응답(태그 코드 배열의 JSON 문자열)을 반환합니다.
        """
        try:
            client = genai.Client(api_key=EnvVariables.GEMINI_API_KEY)
            prompt_dict = self.get_prompt(message, tags)

            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                config=types.GenerateContentConfig(
                    system_instruction=prompt_dict["system_prompt"]),
                contents=prompt_dict["content"],
            )

            return response.text
        except Exception as e:
            logger.error(f"Gemini API call failed: {e}")
            raise Exception("Gemini API 호출 실패: " + str(e)) from e


    @staticmethod
    def get_prompt(message, tags) -> dict:
        system_prompt = f"""
             persona: 너는 콘텐츠 라벨링 전문가야.
             instruction:
                  - 아래 단일 메시지를 참고하여, 해당 메시지에 적합한 태그 코드 배열 (string[])만을 출력해줘.
                  - 태그의 "llm_desc"가 각 태그의 선별 기준이야.
                  - 적합성이 95% 이상일 경우에만 출력에 포함시키며, 태그는 최대 3개까지만 선택해.
                  - 출력은 반드시 오직 순수한 JSON 배열만 출력해야 해. 다른 텍스트나 번호 매김 없이 오직 JSON 형식이어야 해.
             태그 목록:
             {json.dumps(tags, ensure_ascii=False, indent=2)}
             출력 형식 예시:
             ["<tag_code1>", "<tag_code2>", ...]
             """
        content = json.dumps({"message": message}, ensure_ascii=False, indent=2)
        return {"system_prompt": system_prompt, "content": content}

    @staticmethod
    def extract_tag_codes_array_from_json_str(text) -> list:
        """
        JSON str 에서 array 부분만 추출 (대괄호 사이 값)
        - 만약 추출 결과가 dict 배열이면, 각 dict의 "code" 필드만 추출하여 문자열 배열로 변환/

        :param text: JSON 문자열
        :return: 태그 코드 문자열 배열
        """
        try:
            start = text.find('[')
            end = text.rfind(']')
            if start == -1 or end == -1:
                raise Exception("Can't find JSON array in text")
            json_array_str = text[start:end + 1]
            tag_codes = json.loads(json_array_str)
            if not isinstance(tag_codes, list):
                raise Exception("Result is not a list")

            # 만약 추출 결과가 dict 배열인 경우, 'code' 필드만 빼내어 문자열 배열로 변환
            if tag_codes and isinstance(tag_codes[0], dict):
                tag_codes = [d.get("code", "") for d in tag_codes if "code" in d]

            return tag_codes
        except Exception as e:
            raise Exception(str(e)) from e