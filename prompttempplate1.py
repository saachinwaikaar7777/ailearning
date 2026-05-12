import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI, ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate

load_dotenv()


template = "Explain {topic} in simple terms."

prompt = PromptTemplate(
    template=template,
    input_variables=["topic"]
)
llm=ChatGoogleGenerativeAI(
model="gemini-2.5-flash-lite",
temperature=0.7,
)
final_prompt = prompt.format(topic="AI")
print(final_prompt)

response=llm.invoke(final_prompt)
print(response.content)