# ReAct Agent 구현 비교

## 개요
이 프로젝트는 LangGraph를 사용한 ReAct(Reasoning and Acting) 에이전트의 두 가지 구현 방식을 보여줍니다.

## 파일 구조

### 공통 파일
- `react_state.py`: Agent의 상태 정의 (TypedDict 사용)

### 구현 방식 1: create_agent 사용 (LangChain 1.0)
- `agent_reason_runnable.py`: `create_agent` 함수를 사용한 간단한 구현
- `react_graph.py`: create_agent로 생성된 에이전트 실행

### 구현 방식 2: 수동 StateGraph 구성 (과거 버전 스타일)
- `react_graph_manual.py`: StateGraph를 직접 구성한 구현
- `test_manual_graph.py`: 수동 구현 에이전트 실행

## 주요 차이점

### 1. create_agent 사용 (현재 LangChain 1.0)

**장점:**
- 코드가 간결함
- 내부 구현 세부사항 숨김
- 빠른 프로토타이핑 가능

**코드 예시:**
```python
from langchain.agents import create_agent

react_agent_runnable = create_agent(model=llm, tools=tools)
```

### 2. 수동 StateGraph 구성 (과거 버전 스타일)

**장점:**
- 각 단계를 명확하게 제어 가능
- 커스터마이징 용이
- ReAct 패턴의 내부 동작 이해에 도움
- 디버깅이 쉬움

**주요 컴포넌트:**

#### a. Agent 노드
```python
def call_agent(state: AgentState) -> dict:
    """LLM을 호출하여 응답을 생성"""
    messages = state["messages"]
    response = llm_with_tools.invoke(messages)
    return {"messages": [response]}
```

#### b. Tools 노드
```python
tool_node = ToolNode(tools)
```

#### c. 조건부 엣지
```python
def should_continue(state: AgentState) -> str:
    """도구 호출 여부 결정"""
    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"  # 도구 실행

    return "__end__"  # 종료
```

#### d. 그래프 구성
```python
workflow = StateGraph(AgentState)

# 노드 추가
workflow.add_node("agent", call_agent)
workflow.add_node("tools", tool_node)

# 엣지 추가
workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue, {...})
workflow.add_edge("tools", "agent")

app = workflow.compile()
```

## ReAct 패턴 동작 흐름

```
1. 시작노드 
[START]

2. 에이전트 노드
[Agent] ← LLM이 사용자 질문 분석
3. 에이전트 노드 판단 
3-1. 도구 호출 필요? → [Tools] → 도구 실행 → [Agent]로 다시
3-2. 최종 답변 가능? → [END]
```

## 실행 방법

### create_agent 버전 실행
```bash
python react_graph.py
```

### 수동 구현 버전 실행
```bash
python test_manual_graph.py
```

## 언제 어떤 방식을 사용할까?

### create_agent 사용
- 빠른 프로토타이핑이 필요할 때
- 표준적인 ReAct 패턴만 필요할 때
- 코드 간결성이 중요할 때

### 수동 StateGraph 구성
- 에이전트 동작을 세밀하게 제어해야 할 때
- 커스텀 로직이 필요할 때
- 학습 목적으로 내부 동작을 이해하고 싶을 때
- 복잡한 워크플로우를 구성할 때

## 도구

### 1. TavilySearch
웹 검색을 수행하는 도구

### 2. get_system_time
현재 시스템 날짜/시간을 반환하는 커스텀 도구

## 주요 학습 포인트

1. **상태 관리**: `AgentState`를 통한 메시지 기록 관리
2. **도구 바인딩**: `llm.bind_tools()`로 LLM에 도구 연결
3. **조건부 라우팅**: `should_continue`로 다음 노드 결정
4. **순환 구조**: tools → agent로 돌아가는 루프 구조
5. **스트리밍**: `stream()`을 통한 실시간 진행 상황 확인
