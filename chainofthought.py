import ollama

# Define a Chain of Thought prompt
# Example: Breaking down a word problem into logical steps
cot_prompt = """
Solve the problem using these steps:
1. Define variables
2. Form equations
3. Solve step-by-step

Return:
Steps:
Final Answer:

Problem:
A father is 4 times as old as his son. 
In 10 years, he will be twice as old as his son.
What are their current ages?
"""
# Call Llama3 model
response = ollama.chat(#chat method is used to generate a response from the model based on the provided prompt.
    # It takes in the model name and a list of messages, where each message has a role (e.g., "user") 
    # and content (the actual prompt). The response will contain the model's output based on the given prompt.
    model='llama3:8b',
    messages=[
        {"role": "user", "content": cot_prompt}
    ]
)

# Print output
print(response['message']['content'])