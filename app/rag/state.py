from typing import List, Literal
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langchain_core.documents import Document

class RouteDecision(BaseModel):
    route: Literal["kb", "direct"] = Field(
        description="Choose 'kb' when the query requires information from the company's knowledge base, such as HR policies, IT support, onboarding, products, or internal procedures. Choose 'direct' for greetings, casual conversation, or general questions that do not require company-specific information.")

class EvidenceGrade(BaseModel):
    grade: Literal["good", "weak"] = Field(
        description="Choose 'good' if the retrieved documents contain relevant and sufficient information to answer the user's question accurately. Choose 'weak' if the documents are irrelevant, incomplete, ambiguous, or do not provide enough evidence to answer confidently.")

class AgentState(TypedDict):
    question: str
    current_query: str
    kb_docs: List[Document]
    web_results: str
    kb_grade: str
    web_grade: str
    answer: str
    source_used: str
    retry_count: int
    trace: List[str]
    citations: List[dict]