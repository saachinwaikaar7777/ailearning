import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
# Load environment variables from .env file
load_dotenv()
# Initialize the Google Generative AI model
model = GoogleGenerativeAI(
    model="gemini-2.5-flash-lite", 
temperature=0.7
)

def zero_shot_prompt():
    topic= input("Enter a topic: ")
    template= "Explain the concept of {topic} in simple terms."
    #finalprompt = f"Explain the concept of {topic} in simple terms."
    finalprompt = PromptTemplate(template=template, input_variables=["topic"]).format(topic=topic)
    #format method is used to fill in the template with the user-provided topic.Because until you call .format(), this is just a template, not a usable prompt.
    response = model.invoke(finalprompt)
    print (response)        
if __name__ == "__main__":   
    zero_shot_prompt()    

