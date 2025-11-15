# ==============================================
# Prompt Chains 정의
# ==============================================
# 트윗 생성과 반성을 위한 프롬프트 체인을 구성합니다.
# 각 체인은 특정 역할을 수행하는 AI 어시스턴트로 설정됩니다.

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv

# 환경변수 로드 (.env 파일에서 API 키 등을 가져옴)
load_dotenv()

# ==============================================
# 프롬프트 템플릿 정의
# ==============================================

# 트윗 생성용 프롬프트
generation_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a twitter techno influencer. Write a viral tweet about the topic below. Make sure to use hashtags and emojis. "
            "It should be engaging, informative, and have the potential to go viral."
            "\n\n특별 지시사항:"
            "- 280자 이내로 작성"
            "- 관련 해시태그 2-3개 포함"
            "- 이모지 적절히 활용"
            "- 화제성과 공유 가능성 고려"
            "- 기술 트렌드와 연관성 강조",
        ),
        MessagesPlaceholder(variable_name="messages"),  # 이전 대화 컨텍스트 삽입 위치
    ]
)

# 반성/평가용 프롬프트
reflection_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a viral twitter influencer grading a tweet. Generate critique and recommendations for the user's tweet."
            "Always provide detailed recommendations, including requests for length, virality, style, etc."
            "\n\n평가 기준:"
            "1. 바이럴성 (공유 가능성, 화제성)"
            "2. 참여도 (좋아요, 리트윗 유도)"
            "3. 길이와 가독성"
            "4. 해시태그와 이모지 사용"
            "5. 브랜딩과 톤앤매너"
            "\n구체적이고 실행 가능한 개선안을 제시하세요.",
        ),
        MessagesPlaceholder(
            variable_name="messages"
        ),  # 평가할 트윗이 포함된 대화 히스토리
    ]
)


# ==============================================
# LLM 모델 설정
# ==============================================
# Google Generative AI (Gemini) 모델 초기화
# API 키를 환경변수에서 직접 로드하여 인증 문제 방지

# llm = ChatOpenAI(
#     model="gpt-4.1-nano",  # 빠르고 효율적인 Gemini 모델
#     temperature=0.7,  # 창의성과 일관성의 균형
# )

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# ==============================================
# 체인 구성
# ==============================================
# 프롬프트와 LLM을 연결하여 실행 가능한 체인으로 구성
# | 연산자는 LangChain의 파이프라인 연결 방식

generation_prompt_chain = generation_prompt | llm  # 트윗 생성 체인
reflection_prompt_chain = reflection_prompt | llm  # 트윗 평가 체인
