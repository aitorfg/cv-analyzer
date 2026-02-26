import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
from typing import List


class CVAnalysisResult(BaseModel):
    match_score: int = Field(description="Compatibility score from 0 to 100")
    strengths: List[str] = Field(description="Key strengths matching the job offer")
    gaps: List[str] = Field(description="Skills or experience gaps identified")
    recommendations: str = Field(description="Concrete recommendations to improve candidacy")
    summary: str = Field(description="Overall summary of the candidate's fit for the role")
    seniority_match: str = Field(description="Assessment of seniority level match: 'below', 'match', 'above'")


ANALYSIS_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are an expert technical recruiter and career advisor specializing in software engineering and data roles.
Your task is to analyze a candidate's CV against a job offer and provide a detailed, honest, and constructive assessment.

Be specific, actionable, and focus on technical skills, experience, and cultural fit.
Always respond in the same language as the CV provided.

Return ONLY a valid JSON object with this exact structure:
{{
    "match_score": <integer 0-100>,
    "strengths": [<list of specific strengths as strings>],
    "gaps": [<list of specific gaps as strings>],
    "recommendations": "<concrete actionable recommendations as a string>",
    "summary": "<overall summary as a string>",
    "seniority_match": "<'below', 'match', or 'above'>"
}}

Do not include any text outside the JSON object."""),
    ("human", """Please analyze this CV against the job offer provided.

--- CV ---
{cv_text}

--- JOB OFFER ---
{job_offer}

Provide your analysis as a JSON object.""")
])


def analyze_cv(cv_text: str, job_offer: str) -> CVAnalysisResult:
    """Analyze a CV against a job offer using Gemini via LangChain."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key="AIzaSyAS4RwSUU4GLkndCml8WltNkZy8Q6yvZQA",
        temperature=0.3,
    )

    parser = JsonOutputParser(pydantic_object=CVAnalysisResult)
    chain = ANALYSIS_PROMPT | llm | parser

    result = chain.invoke({
        "cv_text": cv_text,
        "job_offer": job_offer
    })

    return CVAnalysisResult(**result)
