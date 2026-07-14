import os
import tiktoken
from dotenv import load_dotenv
import google.generativeai as genai
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
MODEL = "models/gemini-2.5-flash"  # or "models/gemini-2.0-pro" for the Pro version

# Input prompt
prompt = "**what is capital of india**?"

model = genai.GenerativeModel(MODEL)

response = model.generate_content(prompt)

# Get response text
output_text = response.text
print("Response:", output_text)

# Tokenize response text using tiktoken (GPT-3.5/GPT-4 encoding as proxy)
encoding = tiktoken.get_encoding("cl100k_base")
input_tokens = encoding.encode(prompt)
num_input_tokens = len(input_tokens)
print(f"Input text: '{prompt}'")
print(f"Number of input tokens: {num_input_tokens}")
num_output_tokens = len(encoding.encode(output_text))

print("Output tokens (response text only):", num_output_tokens)
total_tokens = num_input_tokens + num_output_tokens
print(f"\nTotal tokens (input + output): {total_tokens}")