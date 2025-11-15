from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from dotenv import load_dotenv

# 환경설정
env = load_dotenv()

# LLM
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")

# 결과
result = llm.invoke("신은 죽었는가?")
print(result)
