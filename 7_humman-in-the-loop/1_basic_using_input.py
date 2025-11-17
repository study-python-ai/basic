from typing import Annotated, Final, TypedDict

from dotenv import load_dotenv
from langchain_core.messages import HumanMessage
from langchain_groq import ChatGroq
from langgraph.graph import END, StateGraph, add_messages

load_dotenv()


class State(TypedDict):
    messages: Annotated[list, add_messages]


llm = ChatGroq(model="llama-3.1-8b-instant")

POST: Final[str] = "post"

GENERATE_POST: Final[str] = "generate_post"
GET_REVIEW_DECISION: Final[str] = "get_review_decision"
COLLECT_FEEDBACK: Final[str] = "collect_feedback"


def generate_post(state: State):
    return {"messages": [llm.invoke(state["messages"])]}


def get_review_decision(state: State):
    last_message = state["messages"][-1]

    print("Generated Post:\n", last_message.content)

    descision = input("Post to LinkedIn? (yes/no): ")
    if descision.lower() == "yes":
        return POST
    else:
        return COLLECT_FEEDBACK


def post(state: State):
    final_post = state["messages"][-1].content
    print("Final LinkedIn Post:\n")
    print(final_post)
    print("Post has been approved and is now live on LinkedIn!")


def collect_feedback(state: State):
    feedback = input("How can I improve this post?")
    return {"messages": [HumanMessage(content=feedback)]}


graph = StateGraph(State)

graph.add_node(GENERATE_POST, generate_post)
graph.add_node(GET_REVIEW_DECISION, get_review_decision)
graph.add_node(COLLECT_FEEDBACK, collect_feedback)
graph.add_node(POST, post)

graph.set_entry_point(GENERATE_POST)

graph.add_conditional_edges(GENERATE_POST, get_review_decision)
graph.add_edge(POST, END)
graph.add_edge(COLLECT_FEEDBACK, GENERATE_POST)

app = graph.compile()

response = app.invoke(
    {
        "messages": [
            HumanMessage(
                content="Write me a LinkedIn post on AI Agents taking over content creation Answer in Korean."
            )
        ]
    }
)

print(response)
