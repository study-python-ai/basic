# ==============================================
# Structured Outputs 체인 구성
# ==============================================
# OpenAI의 구조화된 출력 기능을 사용하여 일관된 형식의 응답을 생성하는 체인을 정의합니다.

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from datetime import datetime
from langchain_openai import ChatOpenAI
from regex import R
from schema import AnswerQuestion, ReviseAnswer
from langchain_core.messages import HumanMessage
from dotenv import load_dotenv

# 환경변수 로드 (OpenAI API 키 등)
load_dotenv()

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

# OpenAI GPT-4o-mini 모델 설정
llm = ChatOpenAI(
    model="gpt-4o-mini", temperature=0  # 일관된 출력을 위한 낮은 temperature
)

# 구조화된 출력 체인 구성 (새로운 방식)
# 프롬프트 → 구조화된 출력이 바인딩된 LLM
first_chain = first_responder_prompt_template | llm.bind_tools(
    tools=[AnswerQuestion], tool_choice="AnswerQuestion"
)

# 답변 수정자 섹션
revise_instructions = """새로운 정보를 활용하여 이전 답변을 수정하세요.
    - 이전 reflection을 바탕으로 답변에 중요한 정보를 추가해야 합니다.
    - 검증 가능하도록 수정된 답변에 반드시 참고자료섹션의 숫자를 인용해서 포함해야 합니다.
    - 답변마다 "참고자료" 섹션의 번호를 추가하세요 (단어 제한에 포함되지 않음). 형식:
        - [1] https://example.com
        - [2] https://example.com
    - 이전 reflection 활용하여 답변에서 불필요한 정보를 제거하고 250단어를 초과하지 않도록 하세요.
"""

# 수정된 revisor 프롬프트 템플릿
revisor_prompt_template = actor_prompt_template.partial(
    first_instruction=revise_instructions
)

# 답변 수정 체인 구성 (새로운 방식)
# 수정 프롬프트 → 구조화된 출력이 바인딩된 LLM
revisor_chain = revisor_prompt_template | llm.bind_tools(
    tools=[ReviseAnswer], tool_choice="ReviseAnswer"
)


# ==============================================
# 테스트 실행
# ==============================================

if __name__ == "__main__":
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
    print(f"답변: {response.answer}")
    print(f"\n검색 쿼리: {response.search_queries}")
    print(f"\n반성 - 누락된 부분: {response.reflection.missing}")
    print(f"\n반성 - 불필요한 부분: {response.reflection.superfluous}")
