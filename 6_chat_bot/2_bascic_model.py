from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, START, StateGraph, add_messages

load_dotenv()

responses: List[str] = [
    "안녕하세요! 무엇을 도와드릴까요?",
    "오늘 날짜는 2024년 6월 1일입니다.",
]


class BasicChatState(TypedDict):
    messages: Annotated[list[AIMessage | HumanMessage], add_messages]


# 모델 생성
llm = ChatGroq(
    model="llama-3.1-8b-instant"
)  # 가격 input 0.05 / 1K 토큰, 0.08 / 1k 토큰

# 그래프 선언
workflow = StateGraph(BasicChatState)


def chatbot(state: BasicChatState) -> dict:
    """챗봇 에이전트 노드: LLM을 호출하여 응답 생성"""
    reseponse = llm.invoke(state["messages"])

    return {"messages": [reseponse]}


workflow.add_node("chatbot", chatbot)
workflow.set_entry_point("chatbot")

workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# 애플리케이션 컴파일 및 실행
app = workflow.compile()

while True:
    # 사용자 입력 받기
    user_input = input("User: ")

    # 종료 조건
    if user_input in ["exit", "end"]:
        break

    # 챗봇 호출
    result = app.invoke({"messages": [HumanMessage(content=user_input)]})
    print(result)
