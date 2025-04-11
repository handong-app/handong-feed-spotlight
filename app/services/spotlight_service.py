import json
import re
from typing import List

import ollama
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.tb_ka_message_repository import TbKaMessageRepository
from app.repositories.tb_spotlight_score_repository import SpotlightScoreRepository
from app.repositories.tb_spotlight_summary_repository import SpotlightSummaryRepository
from app.schemas.feed_message_dto import FeedMessageDto
from app.schemas.spotlight_dto import SpotlightDto


class SpotlightService:

    def __init__(self, db: Session):
        self.db = db
        self.tb_ka_message_repository = TbKaMessageRepository(db)

    def get_spotlight(self, spotlight_req_dto: SpotlightDto.GetSpotlightReqDto) -> SpotlightDto.GetSpotlightRespDto:
        """target_date 의 spotlight 와 summary 를 반환 하는 메서드"""

        # target_date 에 업로드 된 신규 메세지를 가져온다.
        fetch_feed_messages_by_date_serv_dto = self.fetch_feed_messages_by_date(spotlight_req_dto.target_date)

        # 가져온 메세지들의 spotlight 점수 생성
        generate_spotlight_score_serv_dtos = self.generate_spotlight_scores(fetch_feed_messages_by_date_serv_dto.messages)

        # 스코어 DB에 저장
        score_repo = SpotlightScoreRepository(self.db)
        score_repo.save_scores(generate_spotlight_score_serv_dtos, spotlight_req_dto.target_date)

        # 가져온 메세지들의 spotlight summary 생성
        generated_summary = self.generate_spotlight_summary(fetch_feed_messages_by_date_serv_dto.messages)

        # summary DB에 저장
        summary_repo = SpotlightSummaryRepository(self.db)
        summary_repo.save_summary(generated_summary, spotlight_req_dto.target_date)


        # 생성된 spotlight score 와 summary 로 최종 response dto 생성
        get_spotlight_resp_dto = SpotlightDto.GetSpotlightRespDto(
            for_date = spotlight_req_dto.target_date,
            summary = generated_summary,
            scores = generate_spotlight_score_serv_dtos
        )

        return get_spotlight_resp_dto


    def fetch_feed_messages_by_date(self, target_date: str) -> SpotlightDto.FetchFeedMessagesByDateServDto:
        """target_date 에 업로드된 신규 메세지들을 가져오는 메서드"""
        messages = self.tb_ka_message_repository.get_messages_by_date(target_date)

        converted_messages = []
        for msg in messages:
            msg_dict = dict(msg)
            if isinstance(msg_dict.get("last_sent_at_datetime"), datetime):
                msg_dict["last_sent_at_datetime"] = msg_dict["last_sent_at_datetime"].isoformat()
            converted_messages.append(msg_dict)

        dto = SpotlightDto.FetchFeedMessagesByDateServDto(
            target_date=target_date,
            messages=converted_messages
        )
        return dto

    # DEPRECATED
    @staticmethod
    def generate_spotlight_rank(self, contents):
        """
        LLM에게 contents 중에서 중요도 기준으로 순위를 매기는 요청을 보내고,
        응답(예: [{ "id": "...", "rank": 1 }, ...])을 받아 DTO로 반환하는 메서드
        """

        # system_prompt = """
        #         Persona:
        #              - 너는 대학교 게시판에 올라온 컨텐츠를 선별하는 분석가야.
        #              - 너는 배열으로 주어진 메세지 중에 학생들이 관심이 있을 것 같은 메세지를 기준으로 순위를 매겨야 해.
        #              - 최대 10개까지만 선정해야 해.
        #         Instruction:
        #              - 반드시 'Response Format' 에 따라야해.
        #              - "rank" : "순위, 1부터10까지의 정수 중 하나"
        #              - "id" : "메세지의 id, UUID"
        #
        #         Response Format:
        #             [
        #                 {
        #                     "rank" : "1"
        #                     "id" : "c479515986ed41e9a0399726103dc039"
        #                 },
        #                 {
        #                     "rank" : "2"
        #                     "id" : "c479515986ed41e9a0399726103dc040"
        #                 }, ...
        #                 {
        #                     "rank" : "10"
        #                     "id" : "c479515986ed41e9a0399726103dc049"
        #                 }
        #             ]
        #         """
        system_prompt = """
            너는 대학교 게시판에 올라온 메시지들을 평가하는 전문가야.
            아래에 주어진 입력은 메시지 리스트로, 각 메시지는 다음 두 필드를 가진 JSON 객체야:
            - id: 메시지의 고유 식별자 (문자열)
            - message: 메시지 내용 (문자열)

            각 메시지에 대해 학생들이 관심을 가질 만한 정도와 유용성을 고려해서 100점 만점으로 점수를 매겨.
            출력은 반드시 순수한 JSON 배열이어야 해.
            즉, 각 메시지에 해당하는 점수를 순서대로 배열에 담아서 출력해.
            추가 설명, 번호, 주석 등은 전혀 포함하면 안 되고 오직 숫자 배열만 반환해.
            예시 입력:
            ```
            [
              { "id": "123e4567-e89b-12d3-a456-426614174000", "message": "이번 주 행사에 참여해보세요!" },
              { "id": "123e4567-e89b-12d3-a456-426614174001", "message": "도서관 공지: 정기 청소 안내" }
            ]
            ```

            출력 예시 (응답 포맷):
            ```
            [85, 60]
            ```
        """


        converted_content = json.dumps([msg.dict() for msg in contents], ensure_ascii=False)

        # print("Converted content:", converted_content)

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": converted_content}
        ]
        llm_resp = ollama.chat(model="mistral", messages=messages)
        llm_content = llm_resp["message"]["content"]
        print("LLM response content:", llm_content)

        # try:
        #
        #     llm_data = json.loads(llm_content)
        # except Exception as e:
        #     raise Exception("LLM 응답 파싱 실패: " + str(e))

        # spotlights = llm_data.get("spotlights", [])
        spotlights = llm_content

        dto = SpotlightDto.GenerateSpotlightRankServDto(
            spotlights=spotlights
        )
        return dto

    @staticmethod
    def generate_spotlight_scores(messages: List[FeedMessageDto]) -> List[SpotlightDto.GenerateSpotlightScoreServDto]:
        """
        각 FeedMessageDto 객체에 대해 개별적으로 100점 만점의 점수를 LLM에게 받아
        숫자 배열로 반환하는 메서드.

        IMPORTANT: 만약 LLM 응답을 Int 형으로 캐스팅 할 때 ValueError (실패) 발생시 -1 로 저장.
        """

        generate_spotlight_score_serv_dtos: List[SpotlightDto.GenerateSpotlightScoreServDto] = []

        system_prompt = (
            """
            너는 대학교 게시판에 올라온 메시지를 평가하는 전문가야.
            아래 메시지에 대해 학생들이 관심을 가질 만한 정도와 유용성을 고려해서 100점 만점 중 몇 점인지 평가해줘.
            출력은 오직 숫자만, 추가 설명이나 텍스트 없이 오직 숫자만 출력해야 해.
            
            점수 기준:
                - 분실물이나 판매글은 점수를 낮게 줘야해.
            """
        )

        for msg in messages:
            prompts = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg.message}
            ]

            llm_resp = ollama.chat(model="mistral", messages=prompts)
            llm_content = llm_resp["message"]["content"].strip()
            print(f"LLM 응답 (메시지 ID {msg.id}): {llm_content}")

            try:
                score = int(llm_content)
            except ValueError as e:
                # IMPORTANT: int 형으로 변경 실패시 -1 처리
                score = -1

            generate_spotlight_score_serv_dtos.append(SpotlightDto.GenerateSpotlightScoreServDto(
                tb_ka_message_id=msg.id,
                score=score
            ))

        return generate_spotlight_score_serv_dtos

    def generate_spotlight_summary(self, messages: List[FeedMessageDto]) -> str:

        preprocessed_messages = self.preprocess_messages(messages)

        print(preprocessed_messages)

        system_prompt = (
            """
            Persona:
                - 너는 대학교 게시판에 올라온 글을 종합하여, 전체적인 분위기와 핵심 정보를 오직 딱 한 문장으로 요약하는 한국인 전문가야.
            
            Instruction:
                - 출력은 반드시 단 하나의 완성된 문장으로만 작성해야해.
                - 답변은 반드시 한국어로 생성해.
                - 출력 형식은 반드시 다음과 같아:
                    "오늘은 [핵심 정보] 한 정보들이 주로 나왔네요! 전반적으로 [분위기/트렌드] 한 분위기 인 듯해요!"
            """
        )

        prompts = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": preprocessed_messages}
        ]

        llm_resp = ollama.chat(model="mistral", messages=prompts)
        llm_content = llm_resp["message"]["content"].strip()

        print(f"LLM 응답: {llm_content}")
        summary:str = llm_content

        return summary


    @staticmethod
    def preprocess_messages(messages) -> str:
        # result = {}
        # for i, msg in enumerate(messages, start=1):
        #     text = msg.message
        #     # URL 제거
        #     text = re.sub(r'https?://\S+', '', text)
        #     # 모든 특수문자 제거 (문자, 숫자, 공백만 남김; Unicode 문자를 포함)
        #     text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
        #     # 앞뒤 공백 제거
        #     text = text.strip()
        #     # 각 메시지를 "message1", "message2", ... 키로 저장
        #     result[f"message{i}"] = text
        # # JSON 문자열 형식으로 리턴 (들여쓰기로 가독성 높임)
        # return json.dumps(result, ensure_ascii=False, indent=2)
        result = ""
        for i, msg in enumerate(messages, start=1):
            text = msg.message
            # URL 제거
            text = re.sub(r'https?://\S+', '', text)
            # 모든 특수문자 제거 (문자, 숫자, 공백만 남김; Unicode 문자를 포함)
            text = re.sub(r'[^\w\s]', '', text, flags=re.UNICODE)
            # 앞뒤 공백 제거
            text = text.strip()
            # 각 메시지를 "message1", "message2", ... 키로 저장
            result += text
            result += "\n"
        return result
