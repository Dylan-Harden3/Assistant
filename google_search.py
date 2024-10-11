from googlesearch import search
from bs4 import BeautifulSoup
import requests
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import EXTRACT_INFO_PROMPT
from langchain_openai import ChatOpenAI


def google_search(query, num_results=3):
    search_results = search(query, num_results)
    return list(search_results)


def fetch_text(url: str):
    try:
        res = requests.get(url, timeout=3)
        res.raise_for_status()
        text = BeautifulSoup(res.text, "html.parser").get_text(
            separator=" ", strip=True
        )
        return text
    except requests.exceptions.RequestException:
        return f"Could not find anything for url {url}"


def get_results_string(results):
    res = []
    for url, result in results:
        res.append(url)
        res.append(result + "\n")
    return "\n".join(res)


async def summarize_search(search):
    prompt = ChatPromptTemplate.from_messages(
        [("system", EXTRACT_INFO_PROMPT), ("human", search)]
    )
    model = ChatOpenAI(model="gpt-4o-mini")
    runnable = prompt | model | StrOutputParser()
    res = await runnable.ainvoke({})
    return res
