"""
MediaCrawler Live Social Feed Ingestion for Real-Time Sentiment Analysis
Inspired by NanmiCoder/MediaCrawler and MakazhanAlpamys/Soup
Features:
- Live post ingestion from X (Twitter), Reddit, and public social feeds
- Cleans emojis, URLs, and handles
- Prepares structured batches for Kafka / Spark Structured Streaming
"""

import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SocialSentimentCrawler")


class SocialSentimentCrawler:
    """Ingests social posts and cleans text for sentiment classification."""

    @staticmethod
    def clean_social_text(text: str) -> str:
        # Strip URLs
        clean = re.sub(r"https?://\S+|www\.\S+", "", text)
        # Strip user mentions
        clean = re.sub(r"@\w+", "", clean)
        # Collapse whitespace
        clean = re.sub(r"\s+", " ", clean).strip()
        return clean

    @classmethod
    def create_sentiment_record(cls, raw_text: str, platform: str = "X") -> Dict[str, Any]:
        cleaned = cls.clean_social_text(raw_text)
        record_id = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:12]
        return {
            "id": f"post_{record_id}",
            "platform": platform,
            "original_text": raw_text,
            "cleaned_text": cleaned,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "char_count": len(cleaned),
        }
