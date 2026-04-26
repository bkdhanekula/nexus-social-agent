"""
Nexus Social — Pydantic Models
================================
Request and response schemas for all API endpoints.
FastAPI auto-generates Swagger docs from these models.
"""

from typing import Optional, Any
from pydantic import BaseModel, Field


# ─── Request Models ────────────────────────────────────────────────────────────

class CaptionRequest(BaseModel):
    description: str = Field(..., min_length=10, example="Attended a GDG AI hackathon, built a Gemini-powered wellness app")
    style: str = Field("Inspirational", example="Professional", description="Inspirational | Professional | Humorous | Minimal | Storytelling")
    platform: str = Field("LinkedIn", example="LinkedIn", description="LinkedIn | Instagram | Twitter/X")

    class Config:
        json_schema_extra = {
            "example": {
                "description": "Built an AI wellness app at the GDG hackathon using Gemini + Firebase",
                "style": "Professional",
                "platform": "LinkedIn"
            }
        }


class HashtagRequest(BaseModel):
    topic: str = Field(..., min_length=3, example="AI hackathon Hyderabad developer community")


class ModerationRequest(BaseModel):
    content: str = Field(..., min_length=5, example="This is the post content to moderate")


class SentimentRequest(BaseModel):
    text: str = Field(..., min_length=5, example="Amazing event today! Really inspired by the AI demos.")


class GrowthRequest(BaseModel):
    niche: str = Field(..., min_length=10, example="I post about AI and data engineering, want to grow developer audience in India")


class PredictRequest(BaseModel):
    post: str = Field(..., min_length=10, example="Just deployed my first AI app on GCP Cloud Run! Thread below...")


class SearchRequest(BaseModel):
    query: str = Field(..., min_length=2, example="Gemini AI developers")


class TrendingRequest(BaseModel):
    hashtag: str = Field(..., min_length=2, example="AgenticAI")


# ─── Response Models ───────────────────────────────────────────────────────────

class CaptionResponse(BaseModel):
    captions: list[str] = Field(..., description="Exactly 3 caption variations")
    style: str
    platform: str


class HashtagResponse(BaseModel):
    hashtags: list[str] = Field(..., description="Up to 20 hashtags starting with #")
    topic: str
    count: int


class ModerationResponse(BaseModel):
    verdict: str = Field(..., description="SAFE | WARNING | VIOLATION")
    score: int = Field(..., ge=0, le=100)
    categories: dict[str, Any]
    summary: str
    recommendation: str


class SentimentResponse(BaseModel):
    analysis: str = Field(..., description="Detailed sentiment breakdown")


class GrowthResponse(BaseModel):
    strategy: str = Field(..., description="Structured growth strategy")


class PredictResponse(BaseModel):
    prediction: str = Field(..., description="Performance prediction with improvement suggestions")


class SearchResponse(BaseModel):
    results: list[dict] = Field(..., description="List of search result objects")
    query: str


class TrendingResponse(BaseModel):
    summary: str = Field(..., description="2-sentence trending topic explanation")
    hashtag: str
