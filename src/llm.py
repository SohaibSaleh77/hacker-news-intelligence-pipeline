from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from typing import List
from src.config import LLM_CFG
from src.prompts import PROMPT
from src.utils import get_log

log = get_log("LLM")

class Category(BaseModel):
    name: str = Field(description="Category name")
    score: float = Field(description="Confidence score 0.0-1.0")

class Metadata(BaseModel):
    top_cats: List[Category] = Field(description="Top 3 categories")
    summary: str = Field(description="2-sentence TL;DR")
    orgs: List[str] = Field(description="Companies mentioned")
    tech: List[str] = Field(description="Technologies mentioned")
    people: List[str] = Field(description="Key people mentioned")

def init_ai():
    llm = ChatOpenAI(
        model=LLM_CFG["model"],
        temperature=LLM_CFG["temp"],
        api_key=LLM_CFG["key"],
        base_url=LLM_CFG["url"],
        max_tokens=LLM_CFG["tokens"],
    )
    # model supports function calling; use it for structured output
    return llm.with_structured_output(Metadata, method="function_calling")

def parse(ai, text, cats):
    # Truncate text using the configurable limit from LLM_CFG
    txt = text[:LLM_CFG["max_text_chars"]]
    p = PROMPT.format(
        cats="\n".join(f"- {c}" for c in cats),
        text=txt
    )
    try:
        return ai.invoke(p)
    except Exception as e:
        log.error(f"AI failed: {e}")
        return None
