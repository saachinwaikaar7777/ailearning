from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableParallel
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(
    model="tinyllama",
    temperature=0
)
country = input("Enter the country to know its currency: \n")

capital_prompt = ChatPromptTemplate.from_template(
    "What is the capital of {country}?"
)

capital_chain = (
    capital_prompt
    | llm
    | StrOutputParser()
)

# -----------------------------
# Prompt 2 → Famous Food
# -----------------------------
food_prompt = ChatPromptTemplate.from_template(
    "What is the most famous food in {country}?"
)

food_chain = (
    food_prompt
    | llm
    | StrOutputParser()
)

# -----------------------------
# Prompt 3 → Tourist Places
# -----------------------------
places_prompt = ChatPromptTemplate.from_template(
    "List 3 famous tourist places in {country}"
)

places_chain = (
    places_prompt
    | llm
    | StrOutputParser()
)

# -----------------------------
# Parallel Chain
# -----------------------------
parallel_chain = RunnableParallel(
    capital=capital_chain,
    food=food_chain,
    places=places_chain
)

# Execute
response = parallel_chain.invoke({
    "country": country
})

print("Graphical Chain (ASCII) Below: ")
parallel_chain.get_graph().print_ascii()
print("\nParallel Chain Output:\n")

print("Capital:")
print(response["capital"])

print("\nFood:")
print(response["food"])

print("\nTourist Places:")
print(response["places"])