import os

from dotenv import load_dotenv

import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

MODEL = "models/gemini-2.5-flash"  # or "models/gemini-2.0-pro" for the Pro version
 
 
# Input prompt

prompt = "what is capital of india"
 
 
model = genai.GenerativeModel(MODEL)
 
 
# Generate response

response = model.generate_content(prompt)
 
 
# Extract token usage from usage_metadata

print("Prompt:", prompt)

print("Generated text:", response.text)
 
 
print("Prompt tokens:", response.usage_metadata.prompt_token_count)

#print("Generated tokens:", response.usage_metadata.generated_token_count)

print("Output tokens:", response.usage_metadata.candidates_token_count)

print("Total tokens:", response.usage_metadata.prompt_token_count + response.usage_metadata.candidates_token_count)