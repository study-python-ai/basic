# ==============================================
# Structured Outputs 스키마 정의
# ==============================================
# Pydantic을 사용하여 AI 모델의 구조화된 출력 형식을 정의합니다.
# 이 스키마들은 LLM이 일관된 형식으로 응답을 생성하도록 강제합니다.

from pydantic import BaseModel, Field
from typing import List


class Reflection(BaseModel):
    """반성/평가 결과 스키마

    AI가 자신의 답변에 대해 자체 평가할 때 사용하는 구조화된 형식입니다.
    누락된 부분과 불필요한 부분을 명확히 구분하여 평가합니다.
    """

    missing: str = Field(
        description="누락된 내용에 대한 비판적 분석 - 답변에서 빠진 중요한 요소들"
    )
    superfluous: str = Field(
        description="불필요한 내용에 대한 비판적 분석 - 답변에서 제거해야 할 부분들"
    )


class AnswerQuestion(BaseModel):
    """질문 답변 스키마

    AI가 질문에 대한 완전한 답변을 생성할 때 사용하는 구조화된 형식입니다.
    답변, 추가 연구 쿼리, 자체 반성을 모두 포함합니다.
    """

    answer: str = Field(
        description="질문에 대한 ~250단어 분량의 답변 - 핵심 내용을 포괄적으로 다룸"
    )
    search_queries: List[str] = Field(
        description="답변 개선을 위한 1-3개의 추가 검색 쿼리 - 더 나은 정보 수집을 위한 키워드"
    )
    reflection: Reflection = Field(
        description="답변 품질에 대한 자체 반성 - 누락 및 불필요한 부분 분석"
    )
