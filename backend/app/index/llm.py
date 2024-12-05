"""
This contains code for handling the user query and inference
"""

import logging

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from app.config import QUERY_DECOMPOSITION_MODEL, ANSWER_MODEL
from app.index.prompts import (
    answer_message,
    query_decomposition_message,
    system_message,
)

logger = logging.getLogger(__name__)

query_decomposition_model = ChatOpenAI(model=QUERY_DECOMPOSITION_MODEL)
answer_model = ChatOpenAI(model=ANSWER_MODEL)


def generate_query_variants(user_query: str, max_variants: int) -> list[str]:
    """
    Analyses and decomposes the user query into multiple search queries
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_message), ("user", query_decomposition_message)]
    )
    prompt = prompt_template.invoke(
        {"user_query": user_query, "max_variants": max_variants}
    )
    logger.info(f"Generated queries: {prompt.to_messages()}")
    chain = query_decomposition_model | StrOutputParser()
    response = chain.invoke(prompt)
    return [r.strip() for r in response.split("\n")]


def answer_question(user_query: str, context: list[dict[str, str]]) -> str:
    """
    Answers a user question using the context provided
    """
    prompt_template = ChatPromptTemplate.from_messages(
        [("system", system_message), ("user", answer_message)]
    )
    prompt = prompt_template.invoke(
        {"question": user_query, "context": context}
    )
    logger.info(f"Answering question: {prompt.to_messages()}")
    chain = answer_model | StrOutputParser()
    response = chain.invoke(prompt)
    return response


def extract_ids_from_llm_response(response: str) -> list[str]:
    """
    Extracts the source ids from the response in the answer. The ids
    are uuid v4 that should be marked with '```' at the beginning and end.
    """
    return response.split("```")[1::2]
