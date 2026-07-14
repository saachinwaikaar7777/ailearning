from langchain_classic.agents import AgentType, initialize_agent
from langchain_core.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI
import requests
import os
from dotenv import load_dotenv

load_dotenv()

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash-lite")


# 1. Unit Converter
def unit_converter(query: str):
    """
    Convert between common units.
    Expected format: '<value> <from_unit> to <to_unit>'
    Example: '100 km to miles', '5 kg to lbs', '32 celsius to fahrenheit'
    """
    try:
        query = query.lower().strip()
        parts = query.split()

        # Parse: <value> <from_unit> to <to_unit>
        value = float(parts[0])
        from_unit = parts[1]
        to_unit = parts[3]

        conversions = {
            ("km", "miles"):      lambda x: x * 0.621371,
            ("miles", "km"):      lambda x: x * 1.60934,
            ("kg", "lbs"):        lambda x: x * 2.20462,
            ("lbs", "kg"):        lambda x: x * 0.453592,
            ("celsius", "fahrenheit"): lambda x: (x * 9/5) + 32,
            ("fahrenheit", "celsius"): lambda x: (x - 32) * 5/9,
            ("meters", "feet"):   lambda x: x * 3.28084,
            ("feet", "meters"):   lambda x: x * 0.3048,
            ("liters", "gallons"): lambda x: x * 0.264172,
            ("gallons", "liters"): lambda x: x * 3.78541,
        }

        key = (from_unit, to_unit)
        if key in conversions:
            result = conversions[key](value)
            return f"{value} {from_unit} = {round(result, 4)} {to_unit}"
        else:
            return f"Conversion from '{from_unit}' to '{to_unit}' is not supported."
    except Exception as e:
        return f"Error in conversion: {e}. Use format: '100 km to miles'"


# 2. Fun Fact Generator
def fun_fact(topic: str):
    """Return a fun fact about a given topic."""
    facts = {
        "space":      "A day on Venus is longer than a year on Venus — it rotates so slowly!",
        "ocean":      "More than 80% of the world's oceans remain unexplored by humans.",
        "animals":    "A group of flamingos is called a 'flamboyance'.",
        "technology": "The first computer bug was an actual bug — a moth found inside a Harvard computer in 1947.",
        "food":       "Honey never spoils. Archaeologists have found 3000-year-old honey in Egyptian tombs still edible.",
        "human body": "The human nose can detect over 1 trillion different scents.",
        "history":    "Cleopatra lived closer in time to the Moon landing than to the construction of the Great Pyramid.",
        "math":       "A 'googol' is 1 followed by 100 zeros, and it inspired the name of the search engine Google.",
    }
    topic_lower = topic.lower()
    for key, fact in facts.items():
        if key in topic_lower or topic_lower in key:
            return f"Fun fact about {topic}: {fact}"
    return (
        f"Fun fact about {topic}: Did you know that '{topic}' is one of the most searched "
        f"topics online? Curiosity drives us to learn more every day!"
    )


# 3. Country Info Lookup (using REST Countries API)
def country_info(country: str):
    """Fetch basic information about a country using the REST Countries API."""
    try:
        url = f"https://restcountries.com/v3.1/name/{country}"
        response = requests.get(url, timeout=10)
        data = response.json()

        if isinstance(data, dict) and data.get("status") == 404:
            return f"Country '{country}' not found."

        c = data[0]
        name       = c["name"]["common"]
        capital    = c.get("capital", ["N/A"])[0]
        population = c.get("population", "N/A")
        region     = c.get("region", "N/A")
        subregion  = c.get("subregion", "N/A")
        area       = c.get("area", "N/A")
        languages  = ", ".join(c.get("languages", {}).values()) or "N/A"
        currencies = ", ".join(
            v["name"] for v in c.get("currencies", {}).values()
        ) or "N/A"

        return (
            f"Country: {name}\n"
            f"Capital: {capital}\n"
            f"Region: {region} ({subregion})\n"
            f"Population: {population:,}\n"
            f"Area: {area} km²\n"
            f"Languages: {languages}\n"
            f"Currency: {currencies}"
        )
    except Exception as e:
        return f"Error fetching country info: {e}"


# Define tools
tools = [
    Tool(
        name="UnitConverter",
        func=unit_converter,
        description=(
            "Convert between units of measurement. "
            "Input format: '<value> <from_unit> to <to_unit>'. "
            "Supported: km/miles, kg/lbs, celsius/fahrenheit, meters/feet, liters/gallons."
        ),
    ),
    Tool(
        name="FunFact",
        func=fun_fact,
        description=(
            "Get an interesting fun fact about a topic. "
            "Topics include: space, ocean, animals, technology, food, human body, history, math."
        ),
    ),
    Tool(
        name="CountryInfo",
        func=country_info,
        description=(
            "Look up information about a country — capital, population, region, "
            "area, languages, and currency."
        ),
    ),
]

# Initialize agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

# --- Test the agent ---
if __name__ == "__main__":
    
    print("\n" + "="*50)
    print(agent.invoke("Convert 100 km to miles"))

    print("\n" + "="*50)
    print(agent.invoke("Tell me a fun fact about space."))

    print("\n" + "="*50)
    print(agent.invoke("What can you tell me about Japan?"))
