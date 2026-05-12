#from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableSequence, RunnablePassthrough

# 1. Initialize Model
#llm = ChatOpenAI(model="gpt-5-nano")
llm = ChatOllama(
    model="tinyllama:latest",
    temperature=0.7
)

# 2. Define Prompts
capital_prompt = ChatPromptTemplate.from_messages([
    #from_messages creates a prompt template from a list of messages
    ("system", "You are a helpful assistant."),
    ("human", "Whats the capital of {country}?")
])

# Added the {capital} variable here so the prompt knows where to inject the input
places_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "Only List 2 Popular places to visit in the capital city: {capital}")#capital variable is used to inject the capital city name
])

# 3. Define Chains
capital_chain = capital_prompt | llm | StrOutputParser()
#creates a chain that takes country input, generates capital city name, and parses output
places_chain = places_prompt | llm | StrOutputParser()
#creates a chain that takes capital city name, generates popular places to visit, and parses output

# 4. Construct RunnableSequence without lambdas
# We use a dictionary mapping to "wrap" the string output of chain 1
# into a dictionary for chain 2.
sequential_chain = RunnableSequence(#RunnableSequence chains multiple runnables together in sequence,     # passing the output of one as input to the next
    capital_chain,
    {"capital": RunnablePassthrough()}, 

    places_chain 
    #places_chain is the final chain in the sequence, it takes the capital city name and generates popular places to visit
)    #"capital": RunnablePassthrough() creates a mapping where the output of the previous chain (a string) is passed through unchanged and assigned to the key 'capital'.
    # This converts the string to {'capital': '...'}
    #RunnablePassthrough simply passes the input through unchanged, in this case wrapping the string into a dictionary,
    # it allows the output of capital_chain to be used as input for places_chain

# 5. Execution
country_name = input("Enter the country to know its capital: \n")

# Pass the input as a dictionary to satisfy the first PromptTemplate
response = sequential_chain.invoke({"country": country_name})
#invoke runs the sequential chain with the provided input, passing the country name to the first chain and ultimately getting the popular places in the capital city

print("\nOutput of the Sequential Chain Below: ")
print(response)

print("\nGraphical Chain (ASCII) Below: ")
sequential_chain.get_graph().print_ascii()