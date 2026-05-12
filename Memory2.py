from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAI
from dotenv import load_dotenv
from langchain_classic.memory import ConversationBufferWindowMemory
from langchain_classic.chains import ConversationChain

load_dotenv()
llm=ChatGoogleGenerativeAI(
model="gemini-2.5-flash-lite",
temperature=0.7,
)
# chat_history = []
memory = ConversationBufferWindowMemory(k=2) # k is the number of previous interactions to keep in memory. 
#ConverationChain is a chain that maintains a conversation history and can generate responses based on that history. 
# It uses a language model (LLM) to generate responses and a memory component to store the conversation history. 
# The verbose=True argument allows you to see the intermediate steps of the conversation, 
# which can be helpful for debugging and understanding how the model is generating responses.
conversation=ConversationChain(llm=llm, memory=memory, verbose=True)
# Example interaction
print(conversation.predict(input="Hi there!"))#predict method is used to generate a response based on the input provided.
print(conversation.predict(input="I want to know more about Agenti Ai."))
print(conversation.predict(input="Tell me how fast they are developing?"))
print(conversation.predict(input="Tell me about their future?"))
print(conversation.predict(input="What are some platforms they are using?"))