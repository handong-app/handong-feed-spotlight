from huggingface_hub import login
from huggingface_hub import HfFolder

from app.core.config import EnvVariables

HfFolder.save_token(EnvVariables.HUGGING_FACE_TOKEN)

import re
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline


# 한국어 NER 모델 불러오기 (본 파일 import 시 바로 실행 됨)
model_name = "Leo97/KoELECTRA-small-v3-modu-ner"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForTokenClassification.from_pretrained(model_name)

# NER 파이프라인 만들기
ner_pipeline = pipeline("ner", model=model, tokenizer=tokenizer, aggregation_strategy="simple")

def mask_korean_names_ner(text: str) -> str:
    """
    택스트 내의 한국어 이름을 찾아서 "[이름]" 으로 마스킹하는 함수

    :param text:
    :return text:
    """
    entities = ner_pipeline(text)
    # print(text, entities)
    for entity in entities:
        if entity['entity_group'] == 'PS':
            text = text.replace(entity['word'], '[이름]')
    return text


def mask_link(text: str) -> str:
    """
    텍스트 내의 Link 를 찾아서 "[링크]"로 마스킹하는 함수

    :param text:
    :return text:
    """
    return re.sub(r'https?://[^\s]+', '[링크]', text)


def mask_email(text: str) -> str:
    """
    텍스트 내의 이메일 주소를 찾아서 "[이메일]"로 마스킹하는 함수.
    이메일 주소 패턴: 영문자, 숫자, 일부 특수문자(@ 앞부분), 그리고 도메인 형식을 포함합니다.

    :param text:
    :return text:
    """
    email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    masked_text = re.sub(email_pattern, '[이메일]', text)
    return masked_text


def mask_phone_number(text: str) -> str:
    """
    주어진 텍스트에서 전화번호 형식을 찾아 "[전화번호]"로 대체하는 함수.
    일반적인 휴대폰 번호 형식 (예: 010-1234-5678, 01112345678, 010 1234 5678 등)을 대상으로 합니다.

    :param text:
    :return text:
    """
    phone_pattern = re.compile(r'\b(01[0-9])[-.\s]?(\d{3,4})[-.\s]?(\d{4})\b')
    masked_text = phone_pattern.sub('[전화번호]', text)
    return masked_text

def mask_all_ppi(text: str) -> str:
    """
    이름, 링크, 이메일, 전화번호를 순차적으로 마스킹하여 반환하는 함수.
    모든 관련 마스킹 함수를 하나의 파이프라인으로 적용합니다.

    :param text:
    :return text:
    """
    from functools import reduce

    masking_functions = (mask_korean_names_ner, mask_link, mask_email, mask_phone_number)

    return reduce(lambda acc, func: func(acc), masking_functions, text)

