from typing import TypedDict, Annotated, Literal
from langchain_core.messages import BaseMessage, AIMessage
from langgraph.graph import StateGraph, add_messages
from chains import first_chain, revisor_chain
from execute_tools import execute_tools
from graph_utils import show_graph


class GraphState(TypedDict):
    """그래프 상태 정의"""

    messages: Annotated[list[BaseMessage], add_messages]


def draft_node(state: GraphState) -> GraphState:
    """초안 작성"""
    result = first_chain.invoke({"messages": state["messages"]})
    return {"messages": [AIMessage(content=result.answer)]}


def execute_tools_node(state: GraphState) -> GraphState:
    """도구 실행"""
    tool_results = execute_tools(state["messages"])
    return {"messages": tool_results}


def revise_node(state: GraphState) -> GraphState:
    """답변 수정"""
    result = revisor_chain.invoke({"messages": state["messages"]})
    return {"messages": [AIMessage(content=result.answer)]}


def should_continue(state: GraphState) -> Literal["execute_tools", "__end__"]:
    """계속할지 결정"""
    messages = state["messages"]
    # 메시지가 5개 이상이면 종료 (초안 + 검색 + 수정 완료)
    if len(messages) >= 5:
        return "__end__"
    return "execute_tools"


# 그래프 구성
graph = StateGraph(GraphState)
graph.add_node("draft", draft_node)
graph.add_node("execute_tools", execute_tools_node)
graph.add_node("revise", revise_node)

graph.add_edge("draft", "execute_tools")
graph.add_edge("execute_tools", "revise")
graph.add_conditional_edges("revise", should_continue)
graph.set_entry_point("draft")

app = graph.compile()
if __name__ == "__main__":
    # 그래프 시각화 (PNG 이미지로 바로 보기)
    print("Reflexion Agent 그래프 시각화")
    show_graph(app, "reflexion_agent")
