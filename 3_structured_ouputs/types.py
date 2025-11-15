from langchain_text_splitters import Language
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")


class Country(BaseModel):
    name: str = Field(..., description="국가 이름")
    capital: str = Field(..., description="수도 이름")
    language: str = Field(..., description="언어")
    population: int = Field(..., description="인구 수")
    area: float = Field(..., description="면적 (제곱킬로미터)")


country_output_model = llm.with_structured_output(Country)

print(country_output_model)

response = country_output_model.invoke("대한민국 대한 간단한 정보를 알려줘.")

print(response)
