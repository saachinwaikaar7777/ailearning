# Define the prompt
#import openai
#from langchain_openai import OpenAI, ChatOpenAI
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate, HumanMessagePromptTemplate, SystemMessagePromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser

llm = ChatOllama(
    model="tinyllama:latest",
    temperature=0
)
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
         ("human", "Whats the currency of {country}?")
    ]
)
country = input("Enter the country to know its currency: \n")

# Define a simple chain

simple_chain = prompt | llm | StrOutputParser()

print(type(simple_chain))

# | llm

print("Graphical Chain (ASCII) Below: ")
simple_chain.get_graph().print_ascii()

response = simple_chain.invoke(country)

print("The output from the LLM is :\n", response)

#print(type(response))
"""
Think of the LLM response like:

A delivery package

Inside package:

actual item
labels
metadata
tracking info

StrOutputParser() opens the package and extracts only:

the useful item
One-Line Explanation

StrOutputParser() converts the structured LLM response object into a clean plain-text string
so it can be easily used in chains, prompts, tools, and applications.
"""