from langchain_core.prompts import PromptTemplate
from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="llama3:8b",
    temperature=0
)

# ─────────────────────────────────────────
# STEP 1: Define each destination chain
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
# STEP 2: Register destination chains
# ─────────────────────────────────────────

destination_chains = {
    "math":    math_chain,
    "history": history_chain,
    "science": science_chain,
}


# ─────────────────────────────────────────
# STEP 3: Router prompt
# ─────────────────────────────────────────

router_prompt_template = """Classify the question into exactly one category.
Categories: math, history, science
Rules:
- math: arithmetic, algebra, geometry, calculus, calculations
- history: historical events, dates, people from the past, civilizations
- science: physics, chemistry, biology, newton, laws of nature, scientific concepts

Respond with ONLY the category word. No explanation. No punctuation.

Question: {input}
Topic:"""

router_prompt = PromptTemplate.from_template(router_prompt_template)
router_chain = router_prompt | llm


# ─────────────────────────────────────────
# STEP 4: Keyword fallback map
# ─────────────────────────────────────────

FALLBACK_KEYWORDS = {
    "math": [
        "math", "calculat", "algebra", "geometry", "arithmetic",
        "equation", "number", "addition", "subtract", "multiply",
        "divide", "fraction", "percentage", "trigonometry", "calculus",
        "integral", "derivative", "matrix", "probability", "statistics"
    ],
    "history": [
        "history", "historical", "president", "war", "ancient",
        "civilization", "century", "dynasty", "empire", "king",
        "queen", "revolution", "independence", "treaty", "battle",
        "world war", "colonial", "medieval", "renaissance", "period"
    ],
    "science": [
        "science", "physics", "biology", "chemistry", "newton",
        "law of", "force", "energy", "momentum", "reaction",
        "molecule", "atom", "gravity", "velocity", "acceleration",
        "thermodynamics", "quantum", "relativity", "evolution",
        "cell", "dna", "ecosystem", "element", "compound", "photosynthesis"
    ],
}


# ─────────────────────────────────────────
# STEP 5: Topic extraction helper
# ─────────────────────────────────────────

def extract_topic(text: str) -> str | None:
    """Scan text for topic keywords and return matched topic."""
    text_lower = text.lower()
    for topic, keywords in FALLBACK_KEYWORDS.items():
        if any(kw in text_lower for kw in keywords):
            return topic
    return None


# ─────────────────────────────────────────
# STEP 6: Route question with two-layer fallback
# ─────────────────────────────────────────

def route_question(question: str):
    """
    Layer 1: Ask LLM to classify → scan its response for topic keyword.
    Layer 2: If LLM response is unhelpful → scan the original question directly.
    """
    route = router_chain.invoke({"input": question})
    response_text = (route.content if hasattr(route, "content") else str(route)).strip().lower()

    print(f"\n[DEBUG] LLM router raw response: '{response_text}'")

    # Layer 1: scan LLM response
    topic = extract_topic(response_text)

    # Layer 2: fallback — scan original question
    if topic is None:
        print("[DEBUG] LLM response unclear, falling back to question keyword scan...")
        topic = extract_topic(question)

    return topic, response_text


# ─────────────────────────────────────────
# STEP 7: Main
# ─────────────────────────────────────────

if __name__ == "__main__":
    test_question = input("Enter a question:\n> ").strip()
    print(f"\nQuestion: {test_question}")

    topic, response_text = route_question(test_question)
    print(f"Router Decision: {topic}")

    if topic and topic in destination_chains:
        print(f"\nUsing '{topic}' chain...")
        try:
            result = destination_chains[topic].invoke({"input": test_question})
            answer = result.content if hasattr(result, "content") else str(result)
            print(f"\nAnswer:\n{answer}")
        except Exception as e:
            print(f"Error invoking '{topic}' chain: {e}")
    else:
        print(f"\nCould not determine topic from question or LLM response.")
        print("Please try rephrasing your question.")