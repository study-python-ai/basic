# ==============================================
# Structured Outputs 체인 구성
# ==============================================
# OpenAI의 구조화된 출력 기능을 사용하여 일관된 형식의 응답을 생성하는 체인을 정의합니다.

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime
from langchain_openai import ChatOpenAI
from schema import AnswerQuestion, Reflection
from langchain_core.output_parsers import PydanticToolsParser
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# 환경변수 로드 (OpenAI API 키 등)
load_dotenv()

# Pydantic 도구 파서 - 구조화된 출력을 파싱
pydantic_parser = PydanticToolsParser(tools=[AnswerQuestion])

# ==============================================
# Actor 에이전트 프롬프트 템플릿
# ==============================================
# AI 연구원 역할로 질문에 답변하고 자체 반성하는 프롬프트

actor_prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
당신은 전문 AI 연구원입니다.
현재 시간: {time}

다음 단계를 따라 답변해주세요:
1. {first_instruction}
2. 당신의 답변을 반성하고 비판적으로 평가하세요. 개선을 위해 엄격하게 분석해주세요.
3. 반성 후, **답변 개선을 위한 1-3개의 검색 쿼리를 별도로 나열**해주세요. 반성 내용에 포함시키지 마세요.

반드시 지정된 형식을 사용하여 답변해주세요.""",
        ),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "위 사용자의 질문에 요구된 형식으로 답변해주세요."),
    ]
).partial(time=lambda: datetime.now().strftime("%Y년 %m월 %d일 %H:%M:%S"))

# 첫 번째 응답자용 프롬프트 - 상세한 답변 요구
first_responder_prompt_template = actor_prompt_template.partial(
    first_instruction="질문에 대한 상세하고 포괄적인 ~250단어 답변을 제공하세요"
)

# ==============================================
# LLM 모델 및 체인 구성
# ==============================================

# OpenAI GPT-4o-mini 모델 설정
llm = ChatOpenAI(
    model="gpt-4o-mini", temperature=0  # 일관된 출력을 위한 낮은 temperature
)

# 구조화된 출력 체인 구성
# 프롬프트 → 도구 바인딩된 LLM → Pydantic 파서
first_chain = (
    first_responder_prompt_template
    | llm.bind_tools(tools=[AnswerQuestion], tool_choice="AnswerQuestion")
    | pydantic_parser
)

# ==============================================
# 테스트 실행
# ==============================================

# 예시 질문으로 체인 테스트
response = first_chain.invoke(
    {
        "messages": [
            HumanMessage(
                content="소상공인이 AI를 활용하여 사업을 성장시킬 수 있는 방법에 대한 블로그 포스트를 작성해주세요"
            )
        ]
    }
)

print("=== 구조화된 출력 결과 ===")
print(f"답변: {response[0].answer}")
print(f"\n검색 쿼리: {response[0].search_queries}")
print(f"\n반성 - 누락된 부분: {response[0].reflection.missing}")
print(f"\n반성 - 불필요한 부분: {response[0].reflection.superfluous}")
