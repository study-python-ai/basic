import operator
from langgraph.graph import StateGraph
from typing import TypedDict, List, Annotated

from graph_utils.visualizer import quick_visualize


class SimpleState(TypedDict):
    count: int
    sum: Annotated[int, operator.add]
    history: Annotated[List[int], operator.concat]


def increment(state: SimpleState) -> SimpleState:

    new_count = state["count"] + 1

    return {"count": new_count, "sum": new_count, "history": [new_count]}


def print_state(state: SimpleState) -> SimpleState:
    print(f"현재 상태: {state}")
    return state


def should_continue(state):
    if state["count"] < 5:
        return "continue"
    else:
        return "stop"


workflow = StateGraph(SimpleState)

workflow.add_node("increment", increment)
workflow.add_node("print", print_state)

workflow.set_entry_point("increment")

workflow.add_conditional_edges(
    "increment", should_continue, {"continue": "print", "stop": "__end__"}
)
workflow.add_edge("print", "increment")

app = workflow.compile()

state: SimpleState = {"count": 0, "sum": 0, "history": []}


quick_visualize(app)
result = app.invoke(state)

print("최종 상태:", result)
