from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph, add_messages
from langgraph.prebuilt import ToolNode

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatGroq(model="llama-3.1-8b-instant")


@tool
def get_system_time() -> str:
    """현재 시스템 시간을 반환하는 도구 함수"""
    from datetime import datetime

    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


tools = [get_system_time]
llm_with_bind_tools = llm.bind_tools(tools)
tool_node = ToolNode(tools)


def should_continue(state: State):
    """툴 호출이 필요한지 확인"""
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        return "tools"
    return "end"


def model(state: State):
    """여기서는 LLM을 사용하여 링크드인 게시물을 생성합니다."""

    print("===" * 50)
    print("Messages:", len(state["messages"]))
    for i, msg in enumerate(state["messages"]):
        print(
            f"{i}: {type(msg).__name__}: {msg.content[:100] if hasattr(msg, 'content') else str(msg)[:100]}"
        )
    print("===" * 50)

    response = llm_with_bind_tools.invoke(state["messages"])
    return {"messages": [response]}


workflow = StateGraph(State)
workflow.set_entry_point("model")
workflow.add_node("model", model)
workflow.add_node("tools", tool_node)

workflow.add_conditional_edges("model", should_continue, {"tools": "tools", "end": END})
workflow.add_edge("tools", "model")

app = workflow.compile()

response = app.invoke({"messages": [HumanMessage(content="현재시간은?")]})
print("\n최종 응답:")
print(response["messages"][-1].content)
