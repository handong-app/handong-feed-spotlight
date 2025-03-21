import json
from typing import List

import ollama
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.tb_ka_message_repository import TbKaMessageRepository
from app.schemas.feed_message_dto import FeedMessageDto
from app.schemas.spolight_dto import SpotlightDto


class SpotlightService:

    def __init__(self, db: Session):
        self.db = db
        self.tb_ka_message_repository = TbKaMessageRepository(db)

    def get_spotlight(self, spotlight_req_dto: SpotlightDto.GetSpotlightReqDto) -> SpotlightDto.GetSpotlightRespDto:
        """target_date 의 spotlight 와 summary 를 반환 하는 메서드"""

        # target_date 에 업로드 된 신규 메세지를 가져온다.
        fetch_feed_messages_by_date_serv_dto = self.fetch_feed_messages_by_date(spotlight_req_dto.target_date)
        # 가져온 메세지로 spotlight rank 생성
        # generate_spotlight_contents_serv_dto = self.generate_spotlight_rank(fetch_feed_messages_by_date_serv_dto.messages)
        scores = self.generate_individual_scores(fetch_feed_messages_by_date_serv_dto.messages)
        # 생성된 spotlight로 summary 생성

        dto = SpotlightDto.GetSpotlightRespDto(
            target_date = spotlight_req_dto.target_date,
            # summary = generate_spotlight_contents_serv_dto.summary,
            # spotlights = generate_spotlight_contents_serv_dto.spotlights,
            scores = scores
        )

        return dto


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

    def generate_spotlight_rank(self, contents) -> SpotlightDto.GenerateSpotlightRankServDto:
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

    def generate_spotlight_scores(self, messages: List[FeedMessageDto]) :
        """
        각 FeedMessageDto 객체에 대해 개별적으로 100점 만점의 점수를 LLM에게 받아
        숫자 배열로 반환하는 메서드.
        """


        system_prompt = (
            "너는 대학교 게시판에 올라온 메시지를 평가하는 전문가야.\n"
            "아래 메시지에 대해 학생들이 관심을 가질 만한 정도와 유용성을 고려해서 100점 만점 중 몇 점인지 평가해줘.\n"
            "출력은 오직 숫자만, 추가 설명이나 텍스트 없이 오직 숫자만 출력해야 해.\n"
        )

        for msg in messages:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": msg.message}
            ]

            llm_resp = ollama.chat(model="mistral", messages=messages)
            llm_content = llm_resp["message"]["content"].strip()
            print(f"LLM 응답 (메시지 ID {msg.id}): {llm_content}")

            try:
                score = int(llm_content)
            except Exception as e:
                score = 0
            scores.append(score)
        return scores