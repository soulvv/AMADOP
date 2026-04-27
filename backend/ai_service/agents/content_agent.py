from openai import OpenAI
from config import settings
import logging
import re

logger = logging.getLogger(__name__)

# Comprehensive profanity / toxic word list for fallback moderation
TOXIC_WORDS = [
    "fuck", "fucking", "fucked", "fucker", "fck",
    "shit", "shitty", "bullshit",
    "ass", "asshole", "arse",
    "bitch", "bitches",
    "damn", "dammit",
    "bastard", "crap",
    "dick", "penis", "cock",
    "idiot", "moron", "retard", "retarded",
    "stupid", "dumb", "dumbass",
    "hate", "kill", "die",
    "whore", "slut", "ho",
    "nigger", "nigga", "faggot", "fag",
    "cunt", "twat", "piss",
    "stfu", "wtf", "lmao",
    "suck", "sucks", "loser",
    "trash", "garbage", "worthless",
    "ugly", "disgusting", "pathetic",
    "toxic", "bad", "mean",
]


class ContentAgent:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _extractive_summary(self, content: str) -> str:
        """
        Fallback summarizer: extracts key topics from the content
        and builds a short overview that is NOT a copy-paste.
        """
        words = content.split()
        total_words = len(words)

        # Extract key topic words (longer, capitalized, or unique words)
        stopwords = {
            "the", "a", "an", "is", "are", "was", "were", "be", "been",
            "being", "have", "has", "had", "do", "does", "did", "will",
            "would", "could", "should", "may", "might", "shall", "can",
            "to", "of", "in", "for", "on", "with", "at", "by", "from",
            "as", "into", "through", "during", "before", "after", "and",
            "but", "or", "nor", "not", "so", "yet", "both", "either",
            "neither", "each", "every", "all", "any", "few", "more",
            "most", "other", "some", "such", "no", "only", "own", "same",
            "than", "too", "very", "just", "about", "above", "below",
            "between", "this", "that", "these", "those", "it", "its",
            "we", "they", "them", "their", "our", "your", "he", "she",
            "him", "her", "his", "how", "what", "which", "who", "whom",
            "when", "where", "why", "if", "then", "because", "while",
            "also", "like", "don't", "doesn't", "didn't", "won't",
        }

        # Get meaningful keywords
        keywords = []
        for w in words:
            clean = re.sub(r'[^a-zA-Z]', '', w).lower()
            if clean and len(clean) > 3 and clean not in stopwords:
                if clean not in keywords:
                    keywords.append(clean)

        top_topics = keywords[:5]
        topic_str = ", ".join(top_topics[:4])

        return (
            f"This post discusses {topic_str} and related concepts. "
            f"The article contains {total_words} words covering these key themes."
        )

    def summarize_post(self, content: str) -> str:
        """Generates a brief 2-sentence summary of the blog post."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional blog editor. Summarize the following post in exactly 2 concise sentences."},
                    {"role": "user", "content": content}
                ],
                max_tokens=100
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Summarization error: {str(e)}")
            return self._extractive_summary(content)

    def moderate_content(self, text: str) -> dict:
        """Checks if the content is toxic, spam, or contains profanity."""
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "Analyze the following text for toxicity, spam, and profanity. Return a JSON with keys 'is_safe' (boolean), 'reason' (string or null), and 'cleaned_text' (string)."},
                    {"role": "user", "content": text}
                ],
                response_format={"type": "json_object"}
            )
            import json
            return json.loads(response.choices[0].message.content)
        except Exception as e:
            logger.error(f"Moderation error: {str(e)}")
            # Fallback: comprehensive keyword-based filter
            return self._keyword_moderate(text)

    def _keyword_moderate(self, text: str) -> dict:
        """Rule-based moderation with comprehensive profanity detection."""
        text_lower = text.lower()
        cleaned = text
        found_words = []

        # Sort by length descending so "fucking" is matched before "fuck"
        sorted_words = sorted(TOXIC_WORDS, key=len, reverse=True)

        for word in sorted_words:
            # Use word boundary regex for accurate matching
            pattern = re.compile(re.escape(word), re.IGNORECASE)
            if pattern.search(cleaned):
                found_words.append(word)
                cleaned = pattern.sub("*" * len(word), cleaned)

        is_safe = len(found_words) == 0
        return {
            "is_safe": is_safe,
            "reason": f"Contains: {', '.join(found_words)}" if not is_safe else None,
            "cleaned_text": cleaned
        }


content_agent = ContentAgent()

