#from langchain_openai import ChatOpenAI
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.tools import tool
from langchain.agents import create_agent
# create_react_agent is a function that creates an agent based on the ReAct framework,
#  which combines reasoning and acting. AgentExecutor is a class that executes the agent's 
# actions and manages the interaction between the agent and the tools it uses.
#from langchain import hub
#hub is a module that allows you to access pre-built prompts and templates 
# for various tasks, such as the ReAct prompt used in this code.
from dotenv import load_dotenv
import os
load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite", temperature=0)

# -------------------------------
# Step 1: LLM
# -------------------------------
#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

#llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")

# -------------------------------
# Step 2: Tool (Decorator)
# -------------------------------

def research_tool(query: str) -> str:
    """Useful for research on any topic"""
    return f"Exercise has numerous health benefits, including improved cardiovascular health, stronger muscles, and better mental well-being."
#In a real implementation, this function would perform actual research, 
# such as querying a search engine or database, and return relevant information based on the input query.

tools = [research_tool]

# -------------------------------
# Step 3: Research Agent
# -------------------------------
research_agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="You are a research agent. Use tools to gather information."
)

# -------------------------------
# Step 4: Writer Agent
# -------------------------------
writer_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt="You are a writer agent. Summarize and refine the input."
)

# -------------------------------
# Step 5: Orchestration
# -------------------------------
def run_agents(topic):
    print("\n--- Research Agent ---\n")
    research_result = research_agent.invoke(
        {"messages": [{"role": "user", "content": topic}]}
    )

    research_output = research_result["messages"][-1].content
    print(f"Research Output: {research_output}")
     #access the last message in the research agent's response, which contains the output from the research tool, and stores it in the variable research_output.

    print("\n--- Writer Agent ---\n")
    writer_result = writer_agent.invoke(
        {"messages": [{"role": "user", "content": research_output}]}
    )
    return writer_result["messages"][-1].content


# -------------------------------
# Step 6: Run
# -------------------------------
if __name__ == "__main__":#this line checks if the script is being run directly, 
#_name__ is a special variable in Python that is set to "__main__" when the script is executed directly,
 #(as the main program) rather than imported as a module in another script. If this condition is true,
 #  the code block under this statement will be executed.
    result = run_agents("Impact of exercise on wealth")

    print("\n--- Final Output ---\n")
    print(result)