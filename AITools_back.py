# This coode is with old Run method, not the new agent executor. We will update it in next video.
from langchain_classic.agents import AgentType, initialize_agent

from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
import requests, math
import os
from dotenv import load_dotenv
#from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
load_dotenv()
#llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm=ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")
 
# 1. Calculator
def calculator(expr:str):
    try:
        return str(eval(expr))
    except Exception as e:
        return f"Error: {e}"
 
# 2. Joke generator
def joke(topic:str):
    return f"Here’s a {topic}-themed joke: Why did the {topic} cross the road? To learn Agentic AI!"
 
# 3. Weather (fake API call using Open-Meteo as demo)
def weather(city: str):
    """Get demo weather info for a city using Open-Meteo geocoding API."""
    try:
        url = f"https://geocoding-api.open-meteo.com/v1/search?name={city}"
        r = requests.get(url, timeout=10).json()
        if "results" not in r or not r["results"]:
            return f"No weather info for {city}"
        coords = r["results"][0]
        return f"{city} located at lat {coords['latitude']}, lon {coords['longitude']}"
    except Exception as e:
        return f"Error fetching weather: {e}"
 
tools = [
    Tool(name="Calculator", func=calculator, description="Evaluate math expressions."),
    Tool(name="Joke", func=joke, description="Tell a quick joke about a topic."),
    Tool(name="Weather", func=weather, description="Useful for looking up a city's location coordinates, latitude, longitude, or demo weather info"),
]
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True
)
print(agent.run("What is 12 * (7+3)?"))
print(agent.run("Tell me a joke about robots."))
print(agent.run("where is Dhayari located?"))