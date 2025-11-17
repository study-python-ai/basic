"""
Human-in-the-Loop Multi-turn Conversation System

개발 가이드 - Command 패턴 vs 조건부 엣지:

1. Command 패턴 (현재 코드 방식):
    - 적용: 노드에서 바로 다음 경로를 결정할 수 있을 때
    - 장점: 상태 업데이트와 라우팅을 한 번에 처리, 간결한 코드
    - 사용 상황: 사용자 입력에 따른 즉시 분기, 단순한 조건부 로직

    2. 조건부 엣지 (add_conditional_edges):
    - 적용: 복잡한 라우팅 로직이나 조건을 재사용할 때
    - 장점: 라우팅 로직을 분리, 여러 노드에서 같은 조건 재사용 가능
    - 사용 상황: 복잡한 비즈니스 로직, 다중 조건 분기, 재사용 가능한 라우팅

추천: 간단한 분기는 Command 패턴, 복잡한 로직은 조건부 엣지 사용
"""

import uuid
from datetime import datetime
from typing import Annotated, List, TypedDict

from dotenv import load_dotenv
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.runnables.config import RunnableConfig
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, StateGraph, add_messages
from langgraph.types import Command, interrupt

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant")
search_tool = TavilySearch()


@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """오늘 날짜와 시간을 지정된 형식으로 반환합니다."""

    return datetime.now().strftime(format)


tools = [search_tool, get_system_time]


react_agent_runnable = create_agent(model=llm, tools=tools)


class State(TypedDict):
    linkedin_topic: str
    generated_post: Annotated[List[str], add_messages]
    human_feedback: Annotated[List[str], add_messages]


def model(state: State):
    """Here, we're using the LLM to generate a LinkedIn post with human feedback incorporated"""

    print("[model] Generating content")
    linkedin_topic = state["linkedin_topic"]
    feedback = (
        state["human_feedback"] if "human_feedback" in state else ["아직 피드백 없음"]
    )

    # Here, we define the prompt

    prompt = f"""

        링크드인 주제: {linkedin_topic}
        human_feedback: {feedback[-1] if feedback else "아직 피드백 없음"}

        링크드인 주제를 바탕으로 체계적이고 읽기 쉬운 링크드인 게시물을 작성해주세요.

        이전 "human_feedback"을 고려하여 응답을 개선해주세요.
    """
    messages = [
        SystemMessage(
            content="당신은 링크드인 콘텐츠 작성 전문가입니다. 글 내용은 200자 이하이어야합니다."
        ),
        HumanMessage(content=prompt),
    ]

    response = react_agent_runnable.invoke({"messages": messages})

    geneated_linkedin_post = response["messages"][-1].content

    print(f"[model_node] Generated post:\n{geneated_linkedin_post}\n")

    return {
        "generated_post": [AIMessage(content=geneated_linkedin_post)],
        "human_feedback": feedback,
    }


def human_node(state: State):
    """Human Intervention node - loops back to model unless input is done"""

    print("\n [human_node] awaiting human feedback...")

    generated_post = state["generated_post"]

    # Interrupt to get user feedback

    user_feedback = interrupt(
        {
            "generated_post": generated_post,
            "message": "피드백을 제공하거나 '완료'를 입력하여 마무리하세요",
        }
    )

    print(f"[human_node] Received human feedback: {user_feedback}")

    # If user types "완료", transition to END node
    if user_feedback.lower() in ["done", "완료"]:
        return Command(
            update={"human_feedback": state["human_feedback"] + ["완료됨"]},
            goto="end_node",
        )

    # Otherwise, update feedback and return to model for re-generation
    return Command(
        update={"human_feedback": state["human_feedback"] + [user_feedback]},
        goto="model",
    )


def end_node(state: State):
    """Final node"""
    print("\n[end_node] Process finished")
    print("Final Generated Post:", state["generated_post"][-1])
    print("Final Human Feedback", state["human_feedback"])
    return {
        "generated_post": state["generated_post"],
        "human_feedback": state["human_feedback"],
    }


# Buiding the Graph

graph = StateGraph(State)
graph.add_node("model", model)
graph.add_node("human_node", human_node)
graph.add_node("end_node", end_node)

graph.set_entry_point("model")

# Define the flow

graph.add_edge(START, "model")
graph.add_edge("model", "human_node")

graph.set_finish_point("end_node")

# Enable Interrupt mechanism
checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

thread_config = {"configurable": {"thread_id": uuid.uuid4()}}

linkedin_topic = input("링크드인 주제를 입력하세요: ")

initial_state: State = {
    "linkedin_topic": linkedin_topic,
    "generated_post": [],
    "human_feedback": [],
}

thread_config: RunnableConfig = {"configurable": {"thread_id": str(uuid.uuid4())}}


for chunk in app.stream(initial_state, config=thread_config):
    for node_id, value in chunk.items():

        if node_id == "__interrupt__":
            while True:
                user_feedback = input(
                    "피드백을 제공하거나 완료 시 '완료'를 입력하세요: "
                )

                # Resume the graph execution with the user's feedback
                app.invoke(Command(resume=user_feedback), config=thread_config)

                # Exit loop if user says done or 완료
                if user_feedback.lower() in ["done", "완료"]:
                    break
