from pydantic import BaseModel


class FeedMessageDto(BaseModel):
    """ FetchFeedMessagesByDateServDto 의 messages (배열) 필드에 들어갈 요소의 타입을 지정해주는 역할"""
    id: str
    message: str
