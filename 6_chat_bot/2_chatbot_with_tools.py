from typing import Annotated, Final, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.graph import END, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()

search_tool = TavilySearch(search_depth="basic")
tools = [search_tool]

# 모델 생성
llm = ChatGroq(
    model="llama-3.1-8b-instant"
)  # 가격 input 0.05 / 1K 토큰, 0.08 / 1k 토큰


llm_with_tools = llm.bind_tools(tools=tools)


class BasicChatState(TypedDict):
    messages: Annotated[list[AIMessage | HumanMessage], add_messages]


# 그래프 선언
workflow = StateGraph(BasicChatState)


def chatbot(state: BasicChatState) -> dict:
    """챗봇 에이전트 노드: LLM을 호출하여 응답 생성"""
    reseponse = llm_with_tools.invoke(state["messages"])

    return {"messages": [reseponse]}


def tool_router(state: BasicChatState) -> str:
    """도구 노드: 간단한 도구 기능 구현"""
    last_message: AIMessage | HumanMessage = state["messages"][-1]

    if hasattr(last_message, 'tool_calls') and len(last_message.tool_calls) > 0:
        return "tool_node"
    else:
        return END


tool_node = ToolNode(tools=tools)

CHAT_BOT: Final[str] = "chatbot"
TOOL_NODE: Final[str] = "tool_node"
TOOL_ROUTER: Final[str] = "tool_router"

workflow.add_node(CHAT_BOT, chatbot)
workflow.add_node(TOOL_NODE, tool_node)
workflow.add_node(TOOL_ROUTER, tool_router)

workflow.set_entry_point(CHAT_BOT)
workflow.add_conditional_edges(CHAT_BOT, tool_router)
workflow.add_edge(TOOL_NODE, CHAT_BOT)

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
