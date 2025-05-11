# Handong Feed Spotlight

**handong-feed-spotlight**는 LLM 기반 모델을 활용하여 의미 기반 태그를 자동으로 할당하는 백엔드 마이크로서비스입니다.

---
## 📚 목차

1. [소개](#handong-feed-spotlight)
2. [주요 기능](#-주요-기능)
3. [프로젝트 구조](#-프로젝트-구조)
4. [실행 방법](#-실행-방법)
   - [1. 의존성 설치](#1-의존성-설치)
   - [2. 환경 변수 설정](#2-환경-변수-설정)
   - [3. 태그 할당 워크플로우 실행](#3-태그-할당-워크플로우-실행)
   - [4. LLM 기반 태그 할당 로직 설명](#4-llm-기반-태그-할당-로직-설명)
5. [테스트 방법](#-테스트-방법)
   - [로컬 테스트 방법](#로컬-테스트-방법)
   - [GitHub Actions 테스트 (로컬)](#github-actions-테스트-로컬)
___

## 📌 주요 기능

- **LLM 기반 태그 자동 분류**: Ollama 또는 Gemini를 사용하여 메시지에 가장 적합한 태그를 자동으로 할당합니다.
- **태그 실패 로그 관리**: 실패한 태그 작업을 기록하고 이후 재시도할 수 있습니다.
- **자동 실행을 위한 GitHub Actions 통합**: 일정한 주기로 태그 할당 프로세스를 실행하는 워크플로우 제공.
- **태그 할당 상태 관리**: 태그가 성공적으로 할당되면 외부 시스템의 상태도 함께 갱신합니다.

---

## 📂 프로젝트 구조
```text
app/
├── clients/               # 외부 API 클라이언트
├── core/                  # 공통 설정 및 유틸
├── schemas/               # Pydantic 기반 요청/응답 DTO
├── services/              # 핵심 비즈니스 로직
├── scripts/
│   └── tag_assignment_runner.py  # 태그 할당 실행 스크립트
.github/
└── workflows/
└── tag-assignment.yml        # GitHub Actions 워크플로우
```

---

## 🚀 실행 방법

### 1. 의존성 설치

```bash
pip install -r requirements.txt
```

### 2. 환경 변수 설정

`.env` 파일 또는 GitHub Secrets에 다음 환경변수를 설정합니다:

| 환경 변수 | 설명 |
|-----------|------|
| `API_PORT` | 실행될 API 서버 포트 번호 |
| `DB_HOST` | 데이터베이스 호스트 주소 |
| `DB_NAME` | 데이터베이스 이름 |
| `DB_USERNAME` | DB 접속 계정 ID |
| `DB_PASSWORD` | DB 접속 계정 비밀번호 |
| `DB_PORT` | 데이터베이스 포트 번호 |
| `DB_CLASSNAME` | JDBC 연결 시 사용할 클래스 이름 등 (선택적) |
| `BASE_URL` | 외부 API 또는 애플리케이션의 기본 URL |
| `LLM_PROVIDER` | 사용할 LLM 종류 (`ollama` 또는 `gemini`) |
| `OLLAMA_MODEL` | Ollama에 사용할 모델명 (예: `llama3`) |
| `GEMINI_API_KEY` | Gemini API 키 |
| `GEMINI_API_URL` | Gemini API 엔드포인트 |
| `LLM_API_REQUESTS_PER_MINUTE` | LLM 호출 제한 (분당 최대 요청 수) |
| `HUGGING_FACE_TOKEN` | HuggingFace API 인증 토큰 (사용 시) |

- GitHub Actions에서 사용하는 경우, 해당 변수는 **Repository → Settings → Secrets and variables → Actions → New repository secret** 경로에서 추가할 수 있습니다.

### 3. 태그 할당 워크플로우 실행

이 프로젝트는 GitHub Actions를 통해 태그 할당 작업을 자동으로 실행할 수 있도록 설정되어 있습니다.

#### 수동 실행 방법

1. GitHub 저장소의 [Actions 탭](https://github.com/handong-app/handong-feed-spotlight/actions)으로 이동합니다.
2. `Run Tag Assignment Job` 워크플로우를 선택합니다.
3. `Run workflow` 버튼을 눌러 수동 실행합니다.

> ✅ **주의:** 워크플로우를 수동 실행하기 전에 반드시 필요한 환경 변수가 GitHub Secrets에 등록되어 있어야 합니다.

#### 사용 이미지 및 플랫폼

GitHub Actions 외에 로컬에서도 [`act`](https://github.com/nektos/act) 도구를 사용하여 실행 가능합니다:

```bash
act -P ubuntu-latest=catthehacker/ubuntu:act-latest
```
Apple silicon Mac의 경우 아키텍처 문제를 방지하기 위해 다음과 같이 실행하는 것이 좋습니다:
```bash
act -P ubuntu-latest=catthehacker/ubuntu:act-latest --container-architecture linux/amd64
```
> ✅ **주의:** Docker가 설치되어 있고 실행 중이어야 합니다.

### 4. LLM 기반 태그 할당 로직 설명

이 프로젝트는 OpenAI 기반의 Ollama 또는 Google Gemini LLM API를 통해 메시지에 적합한 태그를 자동으로 할당합니다.

#### 태그 할당 흐름 요약

1. 지정된 기간 또는 실패 로그에서 피드 데이터를 불러옵니다.
2. 각 메시지에 대해 다음을 수행합니다:
   - 메시지에서 개인정보(PPI)를 마스킹합니다.
   - 정제된 텍스트를 LLM에게 전달하여 적절한 태그를 요청합니다.
   - LLM이 응답한 태그 코드 리스트를 파싱합니다.
   - 할당된 태그를 DTO에 저장합니다.
3. 태그 할당이 완료되면 주제(subject)의 `is_tag_assigned` 상태를 `true`로 업데이트하며, `handong-feed-app`의 외부 API를 통해 DB에 전송합니다.

#### LLM 호출 제한 (Rate Limit)

- `GEMINI_API`를 사용하는 경우, **분당 요청 횟수 제한(RPM)이 존재합니다.**
- `.env` 또는 GitHub Secrets의 `LLM_API_REQUESTS_PER_MINUTE` 변수로 설정 가능합니다.
- `LLMService` 내부에서 해당 제한을 감지하고 자동으로 대기(sleep) 처리를 합니다.

```python
logger.info(f"[LLMService] {EnvVariables.LLM_API_REQUESTS_PER_MINUTE}회 요청 완료. {wait_seconds}초 대기합니다...")
```
#### 프롬프트 포멧
```json
System:
- 역할: 콘텐츠 라벨링 전문가
- 조건:
  - JSON 배열 형식으로만 응답
  - 최대 3개 태그 선택
  - 적합성이 95% 이상인 경우에만 포함

User:
{
  "message": "메시지 내용"
}
```

## 🎯 테스트 방법

#### 로컬 테스트 방법

1. `.env` 파일 작성 (또는 `.secrets` 파일을 사용하여 `act`용 시크릿 지정)
2. 다음 명령어를 사용하여 직접 스크립트 실행:

   ```bash
   poetry run python app/scripts/run_tag_assignment_runner.py
   ```
   또는 virtualenv 환경이라면:
   ```bash
   python app/scripts/run_tag_assignment_runner.py
   ```

#### GitHub Actions 테스트 (로컬)
Docker가 설치되어 있다면 act 도구로 GitHub Actions를 로컬에서 실행할 수 있습니다.
```bash
act -P ubuntu-latest=catthehacker/ubuntu:act-latest
```
필요 조건 
- Docker가 실행 중이어야 합니다.
- `.env` 파일 작성 (환경 변수 용)
