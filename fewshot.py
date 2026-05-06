import ollama
few_shot_prompt = """
Convert the given movie to its genre.
Input: Sholay
Genre: Action, Adventure, Thriller
Input: DDLJ
Genre: Romance, Drama
Input: "The Race"
Output:
"""

# Send the request to Ollama
response = ollama.generate(
    model='tinyllama:latest',
    prompt=few_shot_prompt
)

# Print the model's completion
print(response['response'])