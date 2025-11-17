from datetime import datetime

from dotenv import load_dotenv

# from langgraph.prebuilt import create_react_agent
from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

# 환경 설정 로드
load_dotenv()

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)


@tool
def get_system_time(format: str = "%Y-%m-%d %H:%M:%S") -> str:
    """오늘 날짜와 시간을 지정된 형식으로 반환합니다."""
    return datetime.now().strftime(format)


# tools
search_tool = TavilySearch(search_depth="basic")

# 툴 정의
tools = [search_tool, get_system_time]

# Agent 생성
react_agent_runnable = create_agent(model=llm, tools=tools)
