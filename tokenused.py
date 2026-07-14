#import tiktoken
import os #let you interact with the operating system, here used to access environment variables
from dotenv import load_dotenv #load environment variables from .env file,
import google.generativeai as genai

from langchain_google_genai import ChatGoogleGenerativeAI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
#from openai import OpenAI
#from langchain_openai import OpenAI, ChatOpenAI
load_dotenv()#reads the .env file and loads the environment variables into the system, allows you to access them using os.getenv()
#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
input_prompt = "Whats the capital of India?"

#chat_model = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7)
chat_model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite", temperature=0.7)
# Initialize tiktoken encoding
#encoding = tiktoken.get_encoding("cl100k_base") #tiktoken is a library for 
#tokenization, and "cl100k_base" is a specific encoding scheme used by OpenAI models. 
# This line initializes the encoding object that will be used to encode the input and output text into tokens.

# Calculate input tokens
#input_tokens = encoding.encode(input_prompt)

#input_tokens =chat_model.get_num_tokens(input_prompt)
 #get the tokenized prompts for the input text using the chat model's token counting method, which is specific to the model being used. This is an alternative to using tiktoken for token counting.
 #get the tokenized prompts for the input text using the chat model's token counting method, which is specific to the model being used. This is an alternative to using tiktoken for token counting.
 #count the number of tokens in the input prompt using the chat model's token counting method, which is specific to the model being used. This is an alternative to using tiktoken for token counting.
num_input_tokens = chat_model.get_num_tokens(input_prompt)
print(f"Input text: '{input_prompt}'")
print(f"Number of input tokens: {num_input_tokens}")

# Get LLM response
#response_llm = client.chat.completions.create(	model="gpt-3.5-turbo",	messages=[{"role": "user", "content": input_prompt}]
#)
#response_llm = response_llm.choices[0].message #access the first generated answer, 
#extracts the text of the assistant's response from the API response object, 
# and stores it in the variable response_llm.
response_llm=chat_model.invoke(input_prompt) #invoke the chat model with the input prompt, which sends the prompt to the model and gets the generated response. The response is stored in the variable response_llm.
print(response_llm)
output_text = response_llm.content #access the content of the assistant's response, which is the generated text, and stores it in the variable output_text.

# Calculate output tokens
num_output_tokens = chat_model.get_num_tokens(output_text) #count the number of tokens in the output text using the chat model's token counting method, which is specific to the model being used. This is an alternative to using tiktoken for token counting.

print(f"\nOutput text: '{output_text}'")
print(f"Number of output tokens: {num_output_tokens}")

total_tokens = num_input_tokens + num_output_tokens
print(f"\nTotal tokens (input + output): {total_tokens}")