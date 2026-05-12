from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="tinyllama:latest",
    temperature=0
)


# ─────────────────────────────────────────
# STEP 1: Define each destination chain (using Runnable)
# ─────────────────────────────────────────

math_prompt = PromptTemplate.from_template(
    "You are a math expert. Answer this math question:\n{input}"
)
math_chain = math_prompt | llm

history_prompt = PromptTemplate.from_template(
    "You are a history professor. Answer this history question:\n{input}"
)
history_chain = history_prompt | llm

science_prompt = PromptTemplate.from_template(
    "You are a science expert. Answer this science question:\n{input}"
)
science_chain = science_prompt | llm


# ─────────────────────────────────────────
# STEP 2: Register them with a NAME + DESCRIPTION
# (This is the "address" — just a label!)
# ─────────────────────────────────────────

destination_chains = {
    "math":    math_chain,      # key = name the router will call
    "history": history_chain,
    "science": science_chain,
}

# ─────────────────────────────────────────
# STEP 3: Describe each destination for the router
# (Router reads these to decide which key to pick)
# ─────────────────────────────────────────

destinations_info = [
    {"name": "math",    "description": "Good for answering math and calculation questions"},
    {"name": "history", "description": "Good for answering history and past events questions"},
    {"name": "science", "description": "Good for answering science and biology questions"},
]

# ─────────────────────────────────────────
# STEP 4: Create router chain and test it
# ─────────────────────────────────────────

router_prompt_template = """Given the input question, which of these topics is most relevant?
Topics:
- math: for math and calculation questions
- history: for history and past events questions
- science: for science and biology questions

Return ONLY the topic name. Do not explain. Answer with only ONE word: math, history, or science.

Question: {input}
Answer:"""

router_prompt = PromptTemplate.from_template(router_prompt_template)
router_chain = router_prompt | llm
# Test the router
def route_question(question: str):
    # Route the question
    route = router_chain.invoke({"input": question})

    # Extract text from the response
    if hasattr(route, "content"):
        response_text = route.content.strip().lower()
    else:
        response_text = str(route).strip().lower()

    # Find the first valid topic keyword
    topic = None
    for valid_topic in ["math", "history", "science"]:
        if valid_topic in response_text:
            topic = valid_topic
            break

    return topic, response_text


if __name__ == "__main__":
    test_question = input("Enter a question to route (e.g. 'What is 2+2?' or 'Who was the first president?'):\n")
    print(f"Question: {test_question}")

    topic, response_text = route_question(test_question)
    print(f"Router Decision: {topic}")

    # Invoke the appropriate chain
    if topic and topic in destination_chains:
        try:
            print(f"\nUsing {topic} chain...")
            result = destination_chains[topic].invoke({"input": test_question})
            if hasattr(result, 'content'):
                print(f"Answer: {result.content}")
            else:
                print(f"Answer: {result}")
        except Exception as e:
            print(f"Error invoking {topic} chain: {e}")
    else:
        print(f"Could not determine topic from: {response_text}")