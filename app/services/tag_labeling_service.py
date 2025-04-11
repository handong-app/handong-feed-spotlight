import logging
import json
import ollama
from app.schemas.tag_labeling_dto import MessageTagAssignment, MessageTagLabelingRespDto
from app.util.pii_cleaner import mask_all_ppi
from app.util.text_cleaner import TextCleaner

logger = logging.getLogger(__name__)

class TagLabelingService:
    def __init__(self):
        self.cleaner = TextCleaner()

    def assign_tags_to_messages_iterative(self, messages, tags) -> MessageTagLabelingRespDto:
        """
        """

        if not messages:
            logger.warning("Empty messages list provided")
            return MessageTagLabelingRespDto(assignments=[])

        if not tags:
            logger.warning("Empty tags list provided")
            return MessageTagLabelingRespDto(assignments=[])

        assignments = []

        for msg in messages:
            subject_id = msg.get("subject_id")

            if not subject_id:
                logger.warning("Message without subject_id found, skipping")
                continue

            raw_text = msg.get("message", "")

            masked_text = mask_all_ppi(raw_text)

            cleaned_message = self.cleaner.clean(masked_text)

            assignment = self.assign_tag_to_message(subject_id, cleaned_message, tags)
            assignments.append(assignment)
        return MessageTagLabelingRespDto(assignments=assignments)

    def assign_tag_to_message(self, subject_id, message, tags) -> MessageTagAssignment:
        """
        단일 메시지에 적합한 태그를 할당합니다.

        Args:
            subject_id: 메시지의 고유 식별자
            message: 태그를 할당할 전처리된 메시지 내용
            tags: 할당 가능한 태그 목록

        Returns:
            MessageTagAssignment: 메시지에 할당된 태그 정보
        """
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            system_prompt = f"""
                           persona: 너는 콘텐츠 라벨링 전문가야.
                           instruction:
                                - 아래 단일 메시지를 참고하여, 해당 메시지에 적합한 태그 코드 배열 :string[]만을 출력해줘.
                                - 태그의 "llm_desc" 가 각 태그의 선별 기준이야.
                                - 적합성이 95% 이상일 경우에만 출력에 포함시켜.
                                - 태그는 최대 3개까지만 선택해.
                                - 출력은 반드시 오직 순수한 JSON 배열만 출력해야 해. 다른 텍스트나 번호 매김 없이 오직 JSON 형식이어야 해.
                           태그 목록:
                           {json.dumps(tags, ensure_ascii=False, indent=2)}
                           메시지:
                           {json.dumps({"message": message}, ensure_ascii=False, indent=2)}
                           출력 형식 예시:
                           ["<tag_code1>", "<tag_code2>", ...]
                           """
            messages_for_llm = [
                {"role": "system", "content": system_prompt}
            ]
            llm_resp = ollama.chat(model="llama3:8b", messages=messages_for_llm)
            try:
                response_text = llm_resp["message"]["content"]
                logger.info(f"LLM response for subject_id {subject_id}, attempt {attempt}: {response_text}")

                tag_codes = self.extract_tag_codes_array_from_json_str(response_text)

                # 최종 tag_codes가 모두 문자열인지, 빈 배열이 아닌지 확인
                if isinstance(tag_codes, list) and all(isinstance(tc, str) for tc in tag_codes) and tag_codes:
                    return MessageTagAssignment(subject_id=subject_id, tag_codes=tag_codes)
                else:
                    raise Exception("추출된 결과가 유효한 문자열 배열이 아닙니다.")
            except Exception as e:
                logger.error(f"LLM 응답 파싱 실패 for subject_id {subject_id} on attempt {attempt}: {e}")
                if attempt == max_attempts:
                    raise Exception(f"assign_tag_to_message 실패: {subject_id}에 대해 {max_attempts}번 시도했으나 실패했습니다. ({e})")

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