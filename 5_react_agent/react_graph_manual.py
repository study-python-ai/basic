from datetime import datetime

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.graph import END, StateGraph
from langgraph.prebuilt import ToolNode
from react_state import AgentState

load_dotenv()


@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """오늘 날짜와 시간을 지정된 형식으로 반환합니다."""
    return datetime.now().strftime(format)


# LLM 및 도구 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
search_tool = TavilySearch(search_depth="basic")
tools = [search_tool, get_system_time]

# LLM에 도구 바인딩
llm_with_tools = llm.bind_tools(tools)


# Agent 노드: LLM을 호출하여 다음 액션 결정
def call_agent(state: AgentState) -> dict:
    """Agent 노드: LLM을 호출하여 응답을 생성합니다."""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}


# Tools 노드 생성
tool_node = ToolNode(tools)


# 조건부 엣지: Agent 응답에 따라 다음 노드 결정
def should_continue(state: AgentState) -> str:
    """Agent의 응답을 확인하고 도구 호출 여부를 결정합니다.

    Args:
        state: 현재 상태

    Returns:
        "tools": 도구를 실행해야 하는 경우
        "__end__": 최종 답변을 생성한 경우
    """
    messages = state["messages"]
    last_message = messages[-1]

    # AIMessage이고 tool_calls가 있으면 도구 실행
    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    # 그렇지 않으면 종료
    return "__end__"


# StateGraph 생성
workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("agent", call_agent)
workflow.add_node("tools", tool_node)

# 시작점 설정
workflow.set_entry_point("agent")

# 조건부 엣지 추가: agent -> tools or END
workflow.add_conditional_edges(
    "agent", should_continue, {"tools": "tools", "__end__": END}
)

# 일반 엣지 추가: tools -> agent
workflow.add_edge("tools", "agent")

# 그래프 컴파일
app = workflow.compile()

print(app.get_graph().draw_mermaid())
