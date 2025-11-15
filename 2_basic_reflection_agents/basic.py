# ==============================================
# Basic Reflection Agent 구현
# ==============================================
# 이 스크립트는 LangGraph 1.0을 사용하여 "생성-반성" 패턴의 에이전트를 구현합니다.
# 트윗을 생성한 후 스스로 평가하고 개선하는 과정을 반복합니다.

from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph import END, StateGraph, add_messages
from typing_extensions import TypedDict, Annotated
from chains import generation_prompt_chain, reflection_prompt_chain

# 환경변수 로드 (Google API Key 등)
load_dotenv()


# ==============================================
# Agent State 정의 (리듀서 사용)
# ==============================================
# LangGraph 1.0 방식: StateGraph with messages key + Reducer
# add_messages 리듀서가 자동으로 메시지 리스트를 병합/누적 관리


class AgentState(TypedDict):
    """에이전트의 상태를 정의하는 타입 (리듀서 포함)

    Attributes:
        messages: add_messages 리듀서로 관리되는 메시지 리스트
        자동으로 새 메시지들이 기존 리스트에 추가됨
    """

    messages: Annotated[list[BaseMessage], add_messages]


# StateGraph 초기화 - 메시지 기반 상태 관리
graph = StateGraph(AgentState)


# ==============================================
# 노드 정의
# ==============================================
# 각 노드는 에이전트의 특정 기능을 담당합니다.

REFLECT = "reflect"  # 반성/평가 노드 이름
GENERATE = "generate"  # 생성 노드 이름


def generate_node(state: AgentState) -> AgentState:
    """트윗 생성 노드 (리듀서 사용)

    사용자의 요청이나 이전 반성 결과를 바탕으로 새로운 트윗을 생성합니다.

    Args:
        state: 현재 에이전트 상태 (메시지 히스토리 포함)

    Returns:
        생성된 AI 응답 - add_messages 리듀서가 자동으로 기존 메시지에 추가
    """
    response = generation_prompt_chain.invoke({"messages": state["messages"]})
    # ✨ 리듀서 사용: 단순히 새 메시지만 반환하면 자동으로 기존 메시지에 추가됨
    return {"messages": [response]}


def reflect_node(state: AgentState) -> AgentState:
    """반성/평가 노드 (리듀서 사용)

    생성된 트윗을 분석하고 개선점을 제시합니다.
    바이럴성, 스타일, 길이 등을 평가하여 피드백을 생성합니다.

    Args:
        state: 현재 에이전트 상태 (생성된 트윗 포함)

    Returns:
        반성 결과 - add_messages 리듀서가 자동으로 기존 메시지에 추가
    """
    response = reflection_prompt_chain.invoke({"messages": state["messages"]})
    # ✨ 리듀서 사용: 단순히 새 메시지만 반환하면 자동으로 기존 메시지에 추가됨
    reflection_msg = HumanMessage(content=response.content)
    return {"messages": [reflection_msg]}


# ==============================================
# 그래프 구성
# ==============================================
# 노드들을 연결하여 실행 흐름을 정의합니다.

# 노드 추가
graph.add_node(GENERATE, generate_node)  # 트윗 생성 노드
graph.add_node(REFLECT, reflect_node)  # 반성/평가 노드

# 시작점 설정: 첫 번째로 실행될 노드
graph.set_entry_point(GENERATE)

# 주의: GENERATE에서 고정 엣지를 설정하지 않음!
# 대신 조건부 엣지만 설정하여 조건에 따라 분기되도록 함


def should_continue(state: AgentState):
    """조건부 라우팅 함수

    메시지 개수를 확인하여 작업을 계속할지 종료할지 결정합니다.
    2개 이상의 메시지가 있으면 충분히 반복했다고 판단하여 종료합니다.

    Args:
        state: 현재 에이전트 상태

    Returns:
        REFLECT: 반성 단계로 이동
        END: 작업 종료
    """
    if len(state["messages"]) > 3:  # 3개부터 종료
        return END  # 메시지가 3개 이상이면 종료
    return REFLECT  # 아니면 계속 반성


# 조건부 엣지: GENERATE 노드에서 조건에 따라 분기
# 이것만 설정하고 고정 엣지는 설정하지 않음!
graph.add_conditional_edges(GENERATE, should_continue)

# REFLECT → GENERATE: 반성 후 다시 생성으로 돌아감
graph.add_edge(REFLECT, GENERATE)

# 그래프 컴파일 - 실행 가능한 앱으로 변환
app = graph.compile()

# 그래프 구조 시각화
print("=== 그래프 구조 ===")
print(app.get_graph().draw_mermaid())
print(app.get_graph().draw_ascii())

# 테스트 실행
message = HumanMessage(content="최신 AI 기술에 대한 바이럴 트윗 작성해줘.")
print("\n=== Agent 실행 시작 ===")
response = app.invoke({"messages": [message]}, {"recursion_limit": 10})
print(f"총 메시지 수: {len(response['messages'])}\n")

for i, msg in enumerate(response["messages"], 1):
    msg_type = type(msg).__name__
    role = " 사용자" if msg_type == "HumanMessage" else " AI"
    print(f"[{i}] {role} ({msg_type}):")
    print(f"{msg.content}\n")
    print("-" * 30)

print("\n최종 결과:")
print(response["messages"][-1].content)
