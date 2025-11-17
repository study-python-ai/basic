from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from schema import AnswerQuestion, ReviseAnswer

load_dotenv()

# LLM 설정
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 초안 작성 프롬프트
draft_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are an expert AI researcher. Provide a detailed ~250-word answer with reflection and search queries.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# 수정 프롬프트
revise_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "Revise your previous answer using the new search information. Keep it under 250 words and add references.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)

# 체인 생성 (LangGraph 1.0 방식)
first_chain = draft_prompt | llm.with_structured_output(AnswerQuestion)
revisor_chain = revise_prompt | llm.with_structured_output(ReviseAnswer)
