"""
Nexus Social — Gemini Service
================================
ALL AI business logic lives here.
Each method maps to one social media AI feature.

Features:
  - Caption generation (style + platform aware)
  - Hashtag strategy (tiered by volume)
  - Content moderation (structured JSON scoring)
  - Sentiment analysis (emotional breakdown)
  - Creator growth strategy
  - Post performance prediction
  - AI-powered smart search
  - Trending topic summaries
"""

import json
import logging
import re
from typing import Optional

import google.generativeai as genai
from google.cloud import secretmanager

from backend.config import Settings

logger = logging.getLogger(__name__)

SOCIAL_PERSONA = """You are an expert AI assistant for a social media platform called Nexus.
You help creators grow their audience, moderate content safely, and generate engaging posts.
Always be practical, data-driven, and specific in your recommendations.
Keep responses concise and actionable."""


class GeminiService:
    """
    Central AI service for all Nexus social media features.

    Architecture note:
      - Each public method = one product feature
      - All prompt engineering is here, not in the router or frontend
      - Temperature varies per feature (creative vs factual)
      - Structured outputs use JSON prompting + safe parsing
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._api_key: Optional[str] = None

    async def initialise(self):
        """Resolve API key and configure Gemini SDK."""
        self._api_key = await self._resolve_api_key()
        genai.configure(api_key=self._api_key)
        logger.info(f"GeminiService initialised | model: {self.settings.gemini_model}")

    async def _resolve_api_key(self) -> str:
        """Resolve key: env var → Secret Manager → error."""
        if self.settings.gemini_api_key:
            logger.info("Gemini API key loaded from environment")
            return self.settings.gemini_api_key

        if self.settings.gcp_project_id:
            try:
                client = secretmanager.SecretManagerServiceClient()
                name = f"projects/{self.settings.gcp_project_id}/secrets/{self.settings.secret_name}/versions/latest"
                response = client.access_secret_version(request={"name": name})
                key = response.payload.data.decode("utf-8").strip()
                logger.info("Gemini API key loaded from Secret Manager")
                return key
            except Exception as e:
                logger.warning(f"Secret Manager error: {e}")

        raise RuntimeError(
            "Gemini API key not found. Set GEMINI_API_KEY or configure GCP_PROJECT_ID."
        )

    def _model(self, temperature: float) -> genai.GenerativeModel:
        """Return configured model instance."""
        return genai.GenerativeModel(
            model_name=self.settings.gemini_model,
            system_instruction=SOCIAL_PERSONA,
            generation_config=genai.GenerationConfig(
                temperature=temperature,
                max_output_tokens=self.settings.max_output_tokens,
                top_p=0.95,
            )
        )

    async def _generate(self, prompt: str, temperature: float) -> str:
        """Core single-turn generation."""
        model = self._model(temperature)
        response = model.generate_content(prompt)
        return response.text.strip()

    def _parse_json(self, raw: str, fallback: dict) -> dict:
        """Safely parse JSON from Gemini output — strips markdown fences."""
        cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError:
            logger.warning(f"JSON parse failed, using fallback. Raw: {raw[:200]}")
            return fallback

    # ─── Feature 1: Caption Generation ────────────────────────────────────────

    async def generate_captions(
        self,
        description: str,
        style: str,
        platform: str
    ) -> list[str]:
        """
        Generate 3 distinct social media captions.

        Args:
            description: Post description or draft text
            style: Tone — Inspirational | Professional | Humorous | Minimal | Storytelling
            platform: Target — LinkedIn | Instagram | Twitter/X

        Returns:
            List of exactly 3 caption strings with hashtags
        """
        platform_rules = {
            "LinkedIn": "Professional tone, can be longer (150-300 words), focus on insights and value, include 3-5 relevant hashtags",
            "Instagram": "Visual and engaging, use emojis tastefully, strong call-to-action, include 8-15 hashtags",
            "Twitter/X": "Punchy and concise, must be under 250 characters including hashtags, 2-3 hashtags max"
        }

        prompt = f"""Generate exactly 3 distinct {style} social media captions for {platform}.

Post description: "{description}"

Platform rules: {platform_rules.get(platform, 'Standard social media best practices')}

Requirements:
- Each caption must feel completely different from the others
- Include relevant hashtags at the end of each caption
- Number each caption: 1. 2. 3.
- Separate each with a blank line
- Do NOT include any preamble or explanation — just the 3 numbered captions

Generate the 3 captions now:"""

        logger.info(f"Generating captions: style={style}, platform={platform}")
        raw = await self._generate(prompt, self.settings.caption_temperature)

        # Parse numbered captions
        captions = []
        for block in re.split(r'\n\s*\n', raw):
            block = block.strip()
            if block:
                # Remove leading number like "1." or "1)"
                clean = re.sub(r'^\d+[\.\)]\s*', '', block).strip()
                if len(clean) > 20:
                    captions.append(clean)

        # Ensure exactly 3
        if len(captions) < 3:
            captions = [raw.strip()]  # Fallback: return as single item
        return captions[:3]

    # ─── Feature 2: Hashtag Generation ────────────────────────────────────────

    async def generate_hashtags(self, topic: str) -> list[str]:
        """
        Generate 20 tiered hashtags for a topic.

        Args:
            topic: Content topic or niche

        Returns:
            List of 20 hashtag strings (with #)
        """
        prompt = f"""Generate exactly 20 highly relevant hashtags for: "{topic}"

Structure as 3 tiers:
- 5 HIGH-VOLUME hashtags (millions of posts, very popular)
- 8 MEDIUM-VOLUME hashtags (thousands of posts, niche but active)
- 7 MICRO-NICHE hashtags (hundreds of posts, highly targeted)

Return ONLY the hashtags, one per line, each starting with #.
No explanations, no tier labels, no numbering — just the hashtags."""

        logger.info(f"Generating hashtags for topic: {topic}")
        raw = await self._generate(prompt, self.settings.hashtag_temperature)

        hashtags = [
            line.strip()
            for line in raw.split('\n')
            if line.strip().startswith('#')
        ]
        return hashtags[:20]

    # ─── Feature 3: Content Moderation ────────────────────────────────────────

    async def moderate_content(self, content: str) -> dict:
        """
        Analyse content for policy violations.

        Args:
            content: User-generated text to moderate

        Returns:
            Structured moderation result with verdict, scores, and recommendation
        """
        prompt = f"""Analyse this social media content for safety and policy compliance:

"{content}"

Return a JSON object with this exact structure:
{{
  "verdict": "SAFE" or "WARNING" or "VIOLATION",
  "score": <overall risk score 0-100>,
  "categories": {{
    "toxicity": <0-100>,
    "spam": <0-100>,
    "misinformation": <0-100>,
    "harassment": <0-100>,
    "hateSpeech": <0-100>
  }},
  "summary": "<1-2 sentence explanation>",
  "recommendation": "<specific action to take>"
}}

Return ONLY valid JSON. No markdown, no explanation."""

        logger.info("Moderating content")
        raw = await self._generate(prompt, self.settings.moderation_temperature)

        fallback = {
            "verdict": "WARNING",
            "score": 50,
            "categories": {
                "toxicity": 0, "spam": 0,
                "misinformation": 0, "harassment": 0, "hateSpeech": 0
            },
            "summary": "Could not complete moderation analysis.",
            "recommendation": "Manual review recommended."
        }
        return self._parse_json(raw, fallback)

    # ─── Feature 4: Sentiment Analysis ────────────────────────────────────────

    async def analyse_sentiment(self, text: str) -> str:
        """
        Analyse emotional tone and community sentiment.

        Args:
            text: Post or comment text to analyse

        Returns:
            Structured sentiment breakdown with recommendations
        """
        prompt = f"""Analyse the sentiment of this social media content:

"{text}"

Provide:
1. Overall sentiment (Positive/Negative/Neutral/Mixed) with confidence %
2. Emotional tone breakdown (joy, anger, sadness, surprise, fear, disgust — top 3 only)
3. Key sentiment drivers (2-3 specific phrases or themes)
4. Predicted audience reaction (how followers likely respond)
5. Creator recommendation (one actionable suggestion)

Keep it under 180 words, practical and specific."""

        logger.info("Analysing sentiment")
        return await self._generate(prompt, self.settings.sentiment_temperature)

    # ─── Feature 5: Growth Strategy ───────────────────────────────────────────

    async def get_growth_advice(self, niche: str) -> str:
        """
        Generate personalised creator growth strategy.

        Args:
            niche: Creator's content niche and goals

        Returns:
            Structured growth strategy with specific actions
        """
        prompt = f"""Create a specific social media growth strategy for:
"{niche}"

Format exactly as:
**Content Strategy**
• [point 1]
• [point 2]
• [point 3]

**Posting Schedule**
[specific days and times with reasoning]

**Engagement Tactics**
• [tactic 1]
• [tactic 2]

**Growth Hack**
[one unique, non-obvious insight]

**30-Day Goal**
[specific measurable target]

Keep under 200 words. Be specific — name platforms, times, content formats."""

        logger.info(f"Generating growth strategy for niche: {niche[:50]}")
        return await self._generate(prompt, self.settings.growth_temperature)

    # ─── Feature 6: Performance Prediction ────────────────────────────────────

    async def predict_performance(self, post: str) -> str:
        """
        Predict social media engagement for a draft post.

        Args:
            post: Draft post text

        Returns:
            Engagement prediction with improvement suggestions
        """
        prompt = f"""Predict the social media performance of this post:

"{post}"

Provide:
1. **Engagement Score**: X/100 (with one-line reasoning)
2. **Estimated Reach**: Low/Medium/High (with why)
3. **Reaction Split**: estimated % likes vs comments vs shares
4. **Best Posting Time**: specific day + time with reasoning
5. **Top 3 Improvements**: concrete edits to boost performance

Be specific and data-driven. Under 200 words."""

        logger.info("Predicting post performance")
        return await self._generate(prompt, self.settings.predict_temperature)

    # ─── Feature 7: Smart Search ───────────────────────────────────────────────

    async def smart_search(self, query: str) -> list[dict]:
        """
        Generate AI-powered search suggestions.

        Args:
            query: User search query

        Returns:
            List of 4 search result objects (users, hashtags, posts)
        """
        prompt = f"""For the social media search query "{query}", generate 4 relevant results.

Return a JSON array with exactly 4 items:
[
  {{"type": "user", "name": "Full Name", "handle": "@handle", "bio": "short professional bio"}},
  {{"type": "hashtag", "tag": "#hashtag", "posts": "42.3k"}},
  {{"type": "post", "preview": "first 80 chars of a relevant post...", "author": "Author Name"}},
  {{"type": "user", "name": "Full Name 2", "handle": "@handle2", "bio": "short bio"}}
]

Return ONLY valid JSON array. No markdown."""

        logger.info(f"Smart search for: {query}")
        raw = await self._generate(prompt, self.settings.search_temperature)

        try:
            cleaned = re.sub(r"```(?:json)?|```", "", raw).strip()
            results = json.loads(cleaned)
            if isinstance(results, list):
                return results[:4]
        except Exception:
            logger.warning("Smart search JSON parse failed")
        return []

    # ─── Feature 8: Trending Summary ──────────────────────────────────────────

    async def trending_summary(self, hashtag: str) -> str:
        """
        Generate a brief explanation of why a hashtag is trending.

        Args:
            hashtag: Hashtag name without #

        Returns:
            2-sentence trending topic explanation
        """
        prompt = f"""Write exactly 2 sentences explaining why #{hashtag} is trending 
in the tech and AI developer community. 
Be informative, specific, and engaging. 
Do not start with "#{hashtag} is trending because" — be more creative."""

        logger.info(f"Generating trending summary for #{hashtag}")
        return await self._generate(prompt, self.settings.trending_temperature)
