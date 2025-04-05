import json
import ollama
from app.schemas.tag_labeling_dto import MessageTagAssignment, MessageTagLabelingRespDto
from app.util.text_cleaner import TextCleaner


class TagLabelingService:
    def __init__(self):
        self.cleaner = TextCleaner()

    def assign_tags_to_messages_iterative(self, messages, tags) -> MessageTagLabelingRespDto:
        """
        """
        assignments = []

        for msg in messages:
            subject_id = msg.get("subject_id")
            raw_text = msg.get("message", "")
            cleaned_message = self.cleaner.clean(raw_text)
            assignment = self.assign_tag_to_message(subject_id, cleaned_message, tags)
            assignments.append(assignment)

        dto = MessageTagLabelingRespDto(assignments=assignments)
        return dto

    def assign_tag_to_message(self, subject_id, message, tags) -> MessageTagAssignment:
        system_prompt = f"""
                   persona: 너는 콘텐츠 라벨링 전문가야.
                   instruction:
                        - 아래 단일 메시지를 참고하여, 해당 메시지에 적합한 태그 코드 배열만을 출력해줘.
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
            print(f"LLM response for subject_id {subject_id}:", response_text)

            tag_codes = self.extract_tag_codes_array_from_json_str(response_text)

        except Exception as e:
            raise Exception(f"LLM response parsing failed for subject_id {subject_id}: " + str(e))

        return MessageTagAssignment(subject_id=subject_id, tag_codes=tag_codes)

    @staticmethod
    def extract_tag_codes_array_from_json_str(text) -> list:
        """
        JSON str 에서 array 부분만 추출 (대괄호 사이 값)
        :param text:
        :return:
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

            return tag_codes

        except Exception as e:
            raise Exception(str(e))