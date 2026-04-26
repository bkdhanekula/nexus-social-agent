"""
Nexus Social — API Router
===========================
8 social media AI endpoints.
This layer handles HTTP only — all logic is in GeminiService.
"""

import logging
from fastapi import APIRouter, Request, HTTPException

from backend.models.schemas import (
    CaptionRequest, CaptionResponse,
    HashtagRequest, HashtagResponse,
    ModerationRequest, ModerationResponse,
    SentimentRequest, SentimentResponse,
    GrowthRequest, GrowthResponse,
    PredictRequest, PredictResponse,
    SearchRequest, SearchResponse,
    TrendingRequest, TrendingResponse,
)

logger = logging.getLogger(__name__)
router = APIRouter()


def get_gemini(request: Request):
    gemini = getattr(request.app.state, "gemini", None)
    if not gemini:
        raise HTTPException(status_code=503, detail="Gemini service not initialised")
    return gemini


# ─── POST /api/social/captions ────────────────────────────────────────────────
@router.post(
    "/captions",
    response_model=CaptionResponse,
    summary="Generate 3 social media captions",
    description="Style and platform-aware caption generation. Returns exactly 3 distinct variations with hashtags."
)
async def captions(payload: CaptionRequest, request: Request):
    try:
        gemini = get_gemini(request)
        result = await gemini.generate_captions(
            description=payload.description,
            style=payload.style,
            platform=payload.platform
        )
        return CaptionResponse(
            captions=result,
            style=payload.style,
            platform=payload.platform
        )
    except Exception as e:
        logger.error(f"Caption generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /api/social/hashtags ────────────────────────────────────────────────
@router.post(
    "/hashtags",
    response_model=HashtagResponse,
    summary="Generate 20 tiered hashtags",
    description="Returns hashtags split across high-volume, medium-volume, and micro-niche tiers."
)
async def hashtags(payload: HashtagRequest, request: Request):
    try:
        gemini = get_gemini(request)
        result = await gemini.generate_hashtags(topic=payload.topic)
        return HashtagResponse(
            hashtags=result,
            topic=payload.topic,
            count=len(result)
        )
    except Exception as e:
        logger.error(f"Hashtag generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /api/social/moderate ────────────────────────────────────────────────
@router.post(
    "/moderate",
    response_model=ModerationResponse,
    summary="Moderate content for policy violations",
    description="Returns verdict (SAFE/WARNING/VIOLATION), risk scores per category, and action recommendation."
)
async def moderate(payload: ModerationRequest, request: Request):
    try:
        gemini = get_gemini(request)
        result = await gemini.moderate_content(content=payload.content)
        return ModerationResponse(**result)
    except Exception as e:
        logger.error(f"Moderation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /api/social/sentiment ───────────────────────────────────────────────
@router.post(
    "/sentiment",
    response_model=SentimentResponse,
    summary="Analyse content sentiment",
    description="Returns emotional tone breakdown, key drivers, audience reaction prediction, and creator recommendation."
)
async def sentiment(payload: SentimentRequest, request: Request):
    try:
        gemini = get_gemini(request)
        result = await gemini.analyse_sentiment(text=payload.text)
        return SentimentResponse(analysis=result)
    except Exception as e:
        logger.error(f"Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /api/social/growth ──────────────────────────────────────────────────
@router.post(
    "/growth",
    response_model=GrowthResponse,
    summary="Generate creator growth strategy",
    description="Personalised content strategy, posting schedule, engagement tactics, and 30-day goal."
)
async def growth(payload: GrowthRequest, request: Request):
    try:
        gemini = get_gemini(request)
        result = await gemini.get_growth_advice(niche=payload.niche)
        return GrowthResponse(strategy=result)
    except Exception as e:
        logger.error(f"Growth advice failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /api/social/predict ─────────────────────────────────────────────────
@router.post(
    "/predict",
    response_model=PredictResponse,
    summary="Predict post engagement performance",
    description="Returns engagement score, estimated reach, reaction split, best posting time, and improvement suggestions."
)
async def predict(payload: PredictRequest, request: Request):
    try:
        gemini = get_gemini(request)
        result = await gemini.predict_performance(post=payload.post)
        return PredictResponse(prediction=result)
    except Exception as e:
        logger.error(f"Performance prediction failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /api/social/search ──────────────────────────────────────────────────
@router.post(
    "/search",
    response_model=SearchResponse,
    summary="AI-powered smart search",
    description="Returns 4 contextually relevant search results (users, hashtags, posts) for a query."
)
async def search(payload: SearchRequest, request: Request):
    try:
        gemini = get_gemini(request)
        result = await gemini.smart_search(query=payload.query)
        return SearchResponse(results=result, query=payload.query)
    except Exception as e:
        logger.error(f"Smart search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── POST /api/social/trending-summary ───────────────────────────────────────
@router.post(
    "/trending-summary",
    response_model=TrendingResponse,
    summary="Generate trending topic summary",
    description="Returns a 2-sentence explanation of why a hashtag is trending in the tech/AI community."
)
async def trending_summary(payload: TrendingRequest, request: Request):
    try:
        gemini = get_gemini(request)
        result = await gemini.trending_summary(hashtag=payload.hashtag)
        return TrendingResponse(summary=result, hashtag=payload.hashtag)
    except Exception as e:
        logger.error(f"Trending summary failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
