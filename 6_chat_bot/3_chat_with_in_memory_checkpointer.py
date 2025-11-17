from typing import Annotated, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_groq import ChatGroq
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph, add_messages

load_dotenv()

memory = MemorySaver()

llm = ChatGroq(model="llama-3.1-8b-instant")


class BasicChatState(TypedDict):
    messages: Annotated[list, add_messages]


def chatbot(state: BasicChatState):
    return {"messages": [llm.invoke(state["messages"])]}


graph = StateGraph(BasicChatState)

graph.add_node("chatbot", chatbot)

graph.add_edge("chatbot", END)

graph.set_entry_point("chatbot")

app = graph.compile(checkpointer=memory)

config: RunnableConfig = {"configurable": {"thread_id": "1"}}

while True:
    # 사용자 입력 받기
    user_input = input("User: ")

    # 종료 조건
    if user_input in ["exit", "end"]:
        break

    # 챗봇 호출
    result = app.invoke({"messages": [HumanMessage(content=user_input)]}, config=config)

    # AI 응답 출력
    print("AI: " + result["messages"][-1].content)
