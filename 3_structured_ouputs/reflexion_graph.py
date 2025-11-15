from typing import List


from langchain_core.messages import BaseMessage, ToolMessage
from langgraph.graph import END, MessageGraph

from chains import first_chain, revisor_chain
from execute_tools import execute_tools


graph = MessageGraph()


graph.add_node("draft", first_chain)
graph.add_node("execute_tools", execute_tools)
graph.add_node("revise", revisor_chain)


graph.add_edge("draft", "execute_tools")
graph.add_edge("execute_tools", "revise")


# 최대 반복 횟수 설정
MAX_ITERATIONS = 1


def event_loop(state: List[BaseMessage]) -> str:
    count_tool_visits = sum(isinstance(item, ToolMessage) for item in state)
    print(f">>>>>>{count_tool_visits}")
    num_iterations = count_tool_visits
    if num_iterations > MAX_ITERATIONS:
        return END

    return "execute_tools"


graph.add_conditional_edges("revise", event_loop)
graph.set_entry_point("draft")


app = graph.compile()
print(app.get_graph().draw_mermaid())

response = app.invoke(
    "소상공인이 AI를 활용하여 사업을 성장시킬 수 있는 방법에 대한 블로그 포스트를 작성해주세요"
)

print(response[-1].tool_calls[0]["args"]["answer"])
