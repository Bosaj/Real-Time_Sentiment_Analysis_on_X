import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "scripts")))
from social_sentiment_crawler import SocialSentimentCrawler


class TestSocialSentimentCrawler(unittest.TestCase):
    def test_clean_social_text(self):
        raw = "Loving the new AI agent workflow! @Bosaj https://github.com/Bosaj"
        cleaned = SocialSentimentCrawler.clean_social_text(raw)
        self.assertEqual(cleaned, "Loving the new AI agent workflow!")

    def test_create_sentiment_record(self):
        rec = SocialSentimentCrawler.create_sentiment_record("Great news today! @user", platform="X")
        self.assertEqual(rec["platform"], "X")
        self.assertTrue(rec["id"].startswith("post_"))
        self.assertEqual(rec["cleaned_text"], "Great news today!")


if __name__ == "__main__":
    unittest.main()
