from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_community.tools import TavilySearchResults
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool

# 환경설정
load_dotenv()

# tools
search_tool = TavilySearchResults(search_depth="basic")


@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """오늘 날짜와 시간을 지정된 형식으로 반환합니다."""
    from datetime import datetime

    return datetime.now().strftime(format)


# LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# agent 생성
agent = create_react_agent(llm, [search_tool, get_system_time])

# 방법 1: LangGraph의 간단한 디버그 모드
print("=== 방법 1: 간단한 실행 (verbose 스타일) ===")
query = "대한민국 대통령이 선출된지 몇 일이 지났나요"
messages = [HumanMessage(content=query)]

# 간단하게 실행하고 결과만 보기
result = agent.invoke({"messages": messages})
print("Final result:", result["messages"][-1].content)

print("\n" + "=" * 50)
print("=== 방법 2: 스트리밍으로 상세 과정 보기 ===")

# 상세한 과정을 보고 싶다면 스트리밍 사용
for step in agent.stream({"messages": messages}):
    for node, data in step.items():
        if "messages" in data:
            for msg in data["messages"]:
                if hasattr(msg, "tool_calls") and msg.tool_calls:
                    for tool_m in msg.tool_calls:
                        print(f"🔧 도구 사용: {tool_m['name']}")
                        print(f"   입력: {tool_m['args']}")
                elif hasattr(msg, "name") and msg.name:
                    print(f"✅ 도구 결과: {msg.content[:200]}...")
                elif msg.content and not hasattr(msg, "tool_calls"):
                    print(f"💭 최종 답변: {msg.content}")

print("\n=== 완료 ===")
