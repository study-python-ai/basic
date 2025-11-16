from typing import TypedDict
from langgraph.graph import StateGraph
from graph_utils.visualizer import quick_visualize


class SimpleState(TypedDict):
    """간단한 상태 정의"""

    count: int


def increment_node(state: SimpleState) -> SimpleState:
    """카운트 증가 노드"""
    return {"count": state["count"] + 1}


def should_continue(state: SimpleState) -> str:
    """계속할지 결정"""
    if state["count"] < 5:
        return 'continue'
    return 'stop'


workflow = StateGraph(SimpleState)

workflow.add_node("increment", increment_node)
workflow.add_conditional_edges(
    "increment", should_continue, {'continue': 'increment', 'stop': '__end__'}
)
workflow.set_entry_point("increment")

app = workflow.compile()

state: SimpleState = {"count": 0}

result = app.invoke(state)
print("최종 상태:", result)

quick_visualize(app)
