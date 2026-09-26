import math
import requests
from dotenv import load_dotenv
from langchain_core.tools import tool
from langchain_tavily import TavilySearch
from database import save_memory, search_memory
from rag import retrieve_from_rag


load_dotenv()


CURRENT_THREAD_ID = "default"


def set_current_thread_id(thread_id: str):
    global CURRENT_THREAD_ID
    CURRENT_THREAD_ID = thread_id


web_search = TavilySearch(
    max_results=5,
    topic="general",
    search_depth="advanced"
)


@tool
def calculator(expression: str) -> str:
    """
    Useful for simple math calculations.
    Input should be a valid math expression.
    Example: 2 + 2, math.sqrt(16), 10 * 5
    """

    try:
        allowed = {
            "math": math,
            "abs": abs,
            "round": round,
            "min": min,
            "max": max,
            "sum": sum
        }

        result = eval(expression, {"__builtins__": {}}, allowed)
        return str(result)

    except Exception as e:
        return f"Calculation error: {str(e)}"


@tool
def search_uploaded_documents(query: str) -> str:
    """
    Search uploaded documents for relevant information.
    Use this when the user asks about uploaded PDFs, DOCX, TXT, notes, files, or documents.
    """

    return retrieve_from_rag(
        query=query,
        thread_id=CURRENT_THREAD_ID
    )


@tool
def remember_this(memory: str) -> str:
    """
    Save an important user preference or fact into long-term memory.
    Use this when the user asks you to remember something.
    """

    return save_memory(
        thread_id=CURRENT_THREAD_ID,
        memory=memory
    )


@tool
def recall_memory(query: str) -> str:
    """
    Recall saved long-term memories about the user or this conversation.
    """

    return search_memory(
        thread_id=CURRENT_THREAD_ID,
        query=query
    )


@tool
def community_health_lookup(county: str, state: str) -> str:
    """
    Look up county-level public health information from CDC PLACES.

    Use this tool when the user asks about community or county health
    statistics such as diabetes prevalence.

    The county should be provided without the word "County".
    Example:
    county="Cherokee"
    state="GA"
    """

    try:
        url = "https://data.cdc.gov/resource/i46a-9kgh.json"

        params = {
            "stateabbr": state.upper(),
            "countyname": county.replace(" County", ""),
            "$select": (
                "stateabbr,"
                "statedesc,"
                "countyname,"
                "diabetes_crudeprev,"
                "diabetes_crude95ci,"
                "diabetes_adjprev,"
                "diabetes_adj95ci"
            ),
            "$limit": 1
        }

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        if not data:
            return (
                f"No CDC PLACES data was found for "
                f"{county} County, {state.upper()}."
            )

        result = data[0]

        state_name = result.get("statedesc", state.upper())
        county_name = result.get("countyname", f"{county} County")

        crude_prevalence = result.get(
            "diabetes_crudeprev",
            "Not available"
        )

        crude_ci = result.get(
            "diabetes_crude95ci",
            "Not available"
        )

        age_adjusted_prevalence = result.get(
            "diabetes_adjprev",
            "Not available"
        )

        age_adjusted_ci = result.get(
            "diabetes_adj95ci",
            "Not available"
        )

        return f"""
CDC PLACES county health data:

Location: {county_name}, {state_name}

Diagnosed diabetes among adults:
- Crude prevalence: {crude_prevalence}%
- Crude 95% confidence interval: {crude_ci}
- Age-adjusted prevalence: {age_adjusted_prevalence}%
- Age-adjusted 95% confidence interval: {age_adjusted_ci}

Source: CDC PLACES, County Data, 2025 release.
These are model-based population estimates and should not be interpreted as individual medical advice.
"""

    except requests.exceptions.RequestException as e:
        return f"CDC PLACES API request failed: {str(e)}"

    except Exception as e:
        return f"CDC PLACES lookup error: {str(e)}"


tools = [
    calculator,
    search_uploaded_documents,
    remember_this,
    recall_memory,
    web_search,
    community_health_lookup
]