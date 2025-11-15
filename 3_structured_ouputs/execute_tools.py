import json
from typing import List
from unittest.mock import Base
from langchain_core.messages import AIMessage, BaseMessage, ToolMessage, HumanMessage
from langchain_community.tools import TavilySearchResults

tavily_tool = TavilySearchResults(search_depth="basic")


def execute_tools(state: List[BaseMessage]) -> List[BaseMessage]:
    """도구 실행기"""
    last_ai_message: AIMessage = state[-1]  # 마지막 AI 메시지 가져오기

    if not hasattr(last_ai_message, "tool_calls") or not last_ai_message.tool_calls:
        return []  # 도구 호출이 없으면 종료

    tool_messages: List[ToolMessage] = []

    for tool_call in last_ai_message.tool_calls:

        tool_name = tool_call["name"]  # 도구 이름
        tool_args = tool_call["args"]  # 도구 인자

        # 특정 도구에 대해 처리
        if tool_name in ["AnswerQuestion", "ReviseAnswer"]:

            call_id = tool_call["id"]
            search_queries = tool_args.get("search_queries", [])
            queury_results = {}

            # 각 검색 쿼리에 대해 도구 실행
            for query in search_queries:
                # Tavily 도구로 검색 실행
                search_result = tavily_tool.run(tool_input=query)
                queury_results[query] = search_result

            # 도구 메시지 생성 및 추가
            tool_messages.append(
                ToolMessage(content=json.dumps(queury_results), tool_call_id=call_id)
            )

    return tool_messages
