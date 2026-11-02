"""
Text Preprocessing and NLP Normalizer for Rule-Based Chatbot.
Combines Python's `re` (regular expressions) for contraction expansion, character
normalization, and pattern cleaning with `spacy` for linguistic tokenization,
lemmatization, POS tagging, and stopword filtering.
"""
import re
from typing import List, Set, Dict, Any, Tuple
import spacy

# Load spaCy English pipeline (en_core_web_sm) with graceful fallback to blank English model
try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    nlp = spacy.blank("en")


CONTRACTIONS = {
    r"\bi'm\b": "i am",
    r"\bi've\b": "i have",
    r"\bi'll\b": "i will",
    r"\bi'd\b": "i would",
    r"\byou're\b": "you are",
    r"\byou've\b": "you have",
    r"\byou'll\b": "you will",
    r"\bhe's\b": "he is",
    r"\bshe's\b": "she is",
    r"\bit's\b": "it is",
    r"\bwe're\b": "we are",
    r"\bthey're\b": "they are",
    r"\bcan't\b": "cannot",
    r"\bcouldn't\b": "could not",
    r"\bwon't\b": "will not",
    r"\bwouldn't\b": "would not",
    r"\bdon't\b": "do not",
    r"\bdoesn't\b": "does not",
    r"\bdidn't\b": "did not",
    r"\bisn't\b": "is not",
    r"\baren't\b": "are not",
    r"\bwasn't\b": "was not",
    r"\bweren't\b": "were not",
    r"\bwhat's\b": "what is",
    r"\bwhere's\b": "where is",
    r"\bhow's\b": "how is",
    r"\bwho's\b": "who is",
}

SYNONYMS = {
    # Greetings & Variations
    "hey": "hello",
    "heyy": "hello",
    "heyyy": "hello",
    "hi": "hello",
    "hii": "hello",
    "hiii": "hello",
    "hiiii": "hello",
    "howdy": "hello",
    "greetings": "hello",
    "sup": "hello",
    "yo": "hello",
    "hola": "hello",
    "helloo": "hello",
    "hellooo": "hello",
    # Farewells
    "bye": "goodbye",
    "byee": "goodbye",
    "cya": "goodbye",
    "adios": "goodbye",
    "see ya": "goodbye",
    # Gratitude
    "thx": "thanks",
    "ty": "thanks",
    "tysm": "thanks",
    "appreciate": "thanks",
    # Slang & Contractions
    "pls": "please",
    "plz": "please",
    "u": "you",
    "ur": "your",
    "r": "are",
    # Technical
    "broke": "broken",
    "glitch": "bug",
    "issue": "problem",
    "malfunction": "broken",
    "reboot": "restart",
    # Logistics
    "package": "order",
    "parcel": "order",
    "shipment": "delivery",
    "tracking": "track",
    "whereabouts": "location",
    # Billing
    "cost": "price",
    "charge": "price",
    "fee": "price",
    "bill": "billing",
    "invoice": "billing",
    "sub": "subscription",
}

# Custom stopword additions to complement spaCy's built-in stopword list
EXTRA_STOPWORDS = {"please", "pls", "plz", "just", "now", "too", "very"}


class TextNormalizer:
    """Preprocesses input text using re (regex) and spacy (NLP)."""

    @staticmethod
    def expand_contractions(text: str) -> str:
        """Expands common English contractions using re (regular expressions)."""
        lower = text.lower()
        for pattern, replacement in CONTRACTIONS.items():
            lower = re.sub(pattern, replacement, lower)
        return lower

    @classmethod
    def clean(cls, text: str) -> str:
        """Performs lowercasing, contraction expansion, elongation reduction, and regex normalization."""
        if not text:
            return ""
        text = cls.expand_contractions(text)
        # Normalize greetings with trailing repeated letters using re (e.g. 'hiiii' -> 'hello', 'heyyy' -> 'hello')
        text = re.sub(r"\bh+i+\b", "hello", text)
        text = re.sub(r"\bh+e+y+\b", "hello", text)
        text = re.sub(r"\bh+e+l+o+\b", "hello", text)
        # Reduce any 3+ repeated characters using re (e.g. 'pleaaase' -> 'please', 'nooo' -> 'no')
        text = re.sub(r"([a-zA-Z])\1{2,}", r"\1", text)
        # Remove special characters except alphanumeric, basic hyphens/hashtags for IDs using re
        text = re.sub(r"[^\w\s\-#@]", " ", text)
        # Collapse multiple spaces using re
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @classmethod
    def parse_spacy(cls, text: str):
        """Processes cleaned text through the spaCy NLP pipeline."""
        cleaned = cls.clean(text)
        return nlp(cleaned)

    @classmethod
    def tokenize(cls, text: str, remove_stopwords: bool = False) -> List[str]:
        """Tokenizes text using spaCy and re, with optional stopword filtering."""
        doc = cls.parse_spacy(text)
        tokens = []
        for token in doc:
            token_text = token.text.strip()
            if not token_text or token.is_punct or token.is_space:
                continue
            if remove_stopwords and (token.is_stop or token_text.lower() in EXTRA_STOPWORDS):
                continue
            tokens.append(token_text.lower())

        # If spacy produced no tokens due to punctuation/edge cases, fall back to regex tokenization
        if not tokens and text:
            cleaned = cls.clean(text)
            tokens = re.findall(r"\b[\w\-#]+\b", cleaned)
            if remove_stopwords:
                tokens = [t for t in tokens if t not in EXTRA_STOPWORDS and not nlp.vocab[t].is_stop]
        return tokens

    @classmethod
    def normalize_tokens(cls, tokens: List[str]) -> List[str]:
        """Replaces tokens with canonical synonyms and spaCy lemmas."""
        normalized = []
        for token in tokens:
            # Check explicit synonym mapping first
            syn = SYNONYMS.get(token, token)
            # Use spaCy for linguistic lemmatization if unchanged
            if syn == token:
                doc = nlp(syn)
                if doc and len(doc) > 0 and doc[0].lemma_:
                    syn = doc[0].lemma_.lower()
            # Also apply synonym on the lemma if applicable
            syn = SYNONYMS.get(syn, syn)
            normalized.append(syn)
        return normalized

    @classmethod
    def extract_keywords(cls, text: str) -> Set[str]:
        """
        Extracts a comprehensive normalized set of keywords using spaCy lemmatization
        and canonical synonym mappings.
        """
        raw_tokens = cls.tokenize(text, remove_stopwords=True)
        normalized = cls.normalize_tokens(raw_tokens)
        keyword_set = set(normalized)

        # Include raw tokens as well (so both lemma and token match intent keywords)
        for t in raw_tokens:
            keyword_set.add(t)

        # Also parse directly with spaCy to add lemmatized content words
        doc = cls.parse_spacy(text)
        for token in doc:
            if not token.is_stop and not token.is_punct and not token.is_space:
                lemma = token.lemma_.lower()
                keyword_set.add(lemma)
                if lemma in SYNONYMS:
                    keyword_set.add(SYNONYMS[lemma])

        return keyword_set
