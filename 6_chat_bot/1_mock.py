from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langchain_core.language_models.fake_chat_models import FakeListChatModel
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph, add_messages

load_dotenv()

responses: List[str] = [
    "안녕하세요! 무엇을 도와드릴까요?",
    "오늘 날짜는 2024년 6월 1일입니다.",
]


class BasicChatState(TypedDict):
    messages: Annotated[list[AIMessage | HumanMessage], add_messages]


# 가짜 모델 생성
mock_llm = FakeListChatModel(responses=responses)
# llm =  ChatGroq(model="llama-3.1-8b-instant")

# 그래프 선언
workflow = StateGraph(BasicChatState)


def chatbot(state: BasicChatState) -> dict:
    """챗봇 에이전트 노드: LLM을 호출하여 응답 생성"""
    return {"messages": [mock_llm.invoke(state["messages"])]}


workflow.add_node("chatbot", chatbot)
workflow.set_entry_point("chatbot")

workflow.add_edge(START, "chatbot")
workflow.add_edge("chatbot", END)

# 애플리케이션 컴파일 및 실행
app = workflow.compile()

# 그래프 시각화 (머메이드 형식)
print(app.get_graph().draw_mermaid())

input_message = HumanMessage(content="안녕?")

response = app.invoke(input={"messages": [input_message]})

print(response)
