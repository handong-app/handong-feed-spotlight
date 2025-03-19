import json
import ollama
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.tb_ka_message_repository import TbKaMessageRepository
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
        generate_spotlight_contents_serv_dto = self.generate_spotlight_rank(fetch_feed_messages_by_date_serv_dto.messages)
        # 생성된 spotlight로 summary 생성

        dto = SpotlightDto.GetSpotlightRespDto(
            target_date = spotlight_req_dto.target_date,
            # summary = generate_spotlight_contents_serv_dto.summary,
            spotlights = generate_spotlight_contents_serv_dto.spotlights,
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

        system_prompt = """
                Persona: 
                     - 너는 대학교 게시판에 올라온 컨텐츠를 선별하는 분석가야. 
                     - 너는 배열으로 주어진 메세지 중에 학생들이 관심이 있을 것 같은 메세지를 기준으로 순위를 매겨야 해.
                     - 최대 10개까지만 선정해야 해.
                Instruction:
                     - 반드시 'Response Format' 에 따라야해.
                     - "rank" : "순위, 1부터10까지의 정수 중 하나"
                     - "id" : "메세지의 id, UUID"
                     
                Response Format: 
                    [
                        { 
                            "rank" : "1"
                            "id" : "c479515986ed41e9a0399726103dc039"
                        },
                        { 
                            "rank" : "2"
                            "id" : "c479515986ed41e9a0399726103dc040"
                        }, ...
                        { 
                            "rank" : "10"
                            "id" : "c479515986ed41e9a0399726103dc049"
                        }
                    ]
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