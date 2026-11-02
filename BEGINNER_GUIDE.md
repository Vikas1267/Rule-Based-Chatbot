# 📘 Beginner's Guide: Understanding Rule-Based Chatbots

Welcome! If you are new to Natural Language Processing (NLP), Regular Expressions (Regex), or Python chatbots, this guide explains exactly how this chatbot works under the hood in simple, clear terms.

---

## 🧭 Table of Contents
1. [What is a Rule-Based Chatbot?](#1-what-is-a-rule-based-chatbot)
2. [How the NLP Pipeline Works (Step-by-Step)](#2-how-the-nlp-pipeline-works-step-by-step)
3. [Understanding Regex Pattern Matching](#3-understanding-regex-pattern-matching)
4. [Understanding Keyword Mapping & Scoring](#4-understanding-keyword-mapping--scoring)
5. [How Slot Filling / Entity Extraction Works](#5-how-slot-filling--entity-extraction-works)
6. [Why Fallback Responses Are Essential](#6-why-fallback-responses-are-essential)
7. [How to Add Your Own Custom Rule in 3 Minutes](#7-how-to-add-your-own-custom-rule-in-3-minutes)

---

## 1. What is a Rule-Based Chatbot?

Unlike Generative AI (like ChatGPT) which generates text using billions of statistical weights, a **Rule-Based Chatbot** operates on explicit, deterministic logic:
- **Predictable**: It always responds in a controlled, safe way defined by your business rules.
- **Fast & Lightweight**: Requires zero external API keys, zero GPUs, and runs entirely on your local machine in milliseconds.
- **Auditable**: Every single answer can be traced to a specific rule, keyword weight, or regex pattern.

---

## 2. How the NLP Pipeline Works (Step-by-Step)

When a user types a message into the chat:
```
"Hey! Where's my package ORD-49201?"
```

The message moves through 5 systematic phases powered by **`re`** and **`spacy`**:

```
[User Text]
    │
    ▼
1. Contraction Expansion (re)  ──► "where's" becomes "where is" via re.sub
    │
    ▼
2. Regex Cleaning (re)         ──► Elongated slang reduced ("pleaaase" -> "please", "hiii" -> "hello")
    │
    ▼
3. Linguistic NLP (spacy)      ──► spaCy en_core_web_sm tokenizes & lemmatizes:
    │                              "packages" -> "package", "broken" -> "break"
    │                              Filters grammatical stopwords (is, my, the, a)
    ▼
4. Entity Extraction (re)      ──► Regex capture groups extract: order_id = "ORD-49201"
    │
    ▼
5. Pattern & Keyword Match     ──► Matches intent: "track_order" (Confidence: 95%)
```

---

## 3. Understanding Regex Pattern Matching

**Regular Expressions (Regex)** allow us to define flexible search patterns rather than checking exact string equality.

### Example 1: Extracting an Order ID
```python
r"\bORD-([A-Za-z0-9]+)\b"
```
- `\b`: Word boundary (ensures we don't match inside a longer word).
- `ORD-`: Must literally begin with `ORD-`.
- `(...)`: Capture group (saves the matched value into a slot variable).
- `[A-Za-z0-9]+`: One or more letters or numbers.

### Example 2: Matching Intent Patterns
```python
r"\b(?:track|locate|where(?:\s+is)?)\b.*?\b(?:order|package|parcel|shipment)\b"
```
- Matches sentences containing words like *"where is"* or *"track"*, followed later by *"order"* or *"package"*.
- Matches both: *"Can you track my package?"* and *"Where is my order?"*.

---

## 4. Understanding Keyword Mapping & Scoring

What if the user phrases their question in an unusual way that does not match an exact regex pattern?
This is where **Weighted Keyword Scoring** comes in.

In `chatbot/rules.py`, each intent has assigned keywords and importance weights:
```python
"keywords": {
    "track": 3.0,     # High importance
    "order": 2.5,     # High importance
    "delivery": 2.0,  # Medium importance
    "transit": 2.0
}
```

### The Scoring Formula:
$$\text{Score} = \frac{\sum \text{Weights of Matched Keywords}}{\text{Total Possible Weight} \times 0.7}$$

- If the user types: *"Check tracking and delivery status"*, the keywords `track` and `delivery` trigger.
- The score exceeds our confidence threshold ($0.32$), and the bot accurately routes to `track_order`!

---

## 5. How Slot Filling / Entity Extraction Works

Chatbots become much smarter when they remember specific details across turns.

### Multi-Turn Dialogue Example:
1. **Turn 1 (User)**: *"Where is my order ORD-88192?"*
   - Chatbot extracts: `order_id = "ORD-88192"`.
   - Chatbot saves this in `context.slots["order_id"]`.
   - Chatbot replies: *"Status for [ORD-88192]: In Transit with FedEx..."*
2. **Turn 2 (User)**: *"Can I cancel it?"*
   - Notice the user did **not** re-type `ORD-88192`.
   - The chatbot retrieves `order_id` from memory and responds: *"Order [ORD-88192] can be cancelled within 60 minutes. Would you like to confirm?"*
3. **Turn 3 (User)**: *"Yes"*
   - The bot detects the affirmative confirmation and finalizes cancellation for `ORD-88192`.

---

## 6. Why Fallback Responses Are Essential

In the real world, users may enter typos, unsupported requests, or gibberish (e.g., *"blorp flubber"*).
A naive chatbot crashes or says nothing. Our chatbot uses a **3-Level Tiered Fallback**:

1. **Level 1 (Clarification & Suggestions)**:
   - Uses partial keyword overlap to calculate *"Did you mean...?"* suggestion chips.
2. **Level 2 (Topic Directory Menu)**:
   - If the user is still stuck, displays the 4 supported topics (Orders, Tech Support, Billing, General).
3. **Level 3 (Human Escalation)**:
   - Generates a simulated support ticket (`#TCK-#####`) and provides the hotline number.

---

## 7. How to Add Your Own Custom Rule in 3 Minutes

Want to teach the chatbot a brand new skill (e.g., *"Check Gift Card Balance"*)?
Simply open `chatbot/rules.py` and add this entry to `INTENT_RULES`:

```python
"gift_card_balance": {
    "topic": "billing",
    "title": "Gift Card Balance Inquiry",
    "patterns": [
        r"\b(?:gift\s*card|voucher)\b.*?\b(?:balance|how\s+much|remaining)\b"
    ],
    "keywords": {
        "gift": 3.0,
        "card": 2.5,
        "balance": 3.5,
        "voucher": 2.5
    },
    "responses": [
        "You can check your gift card balance at https://store.example.com/giftcard by entering the 16-digit code on the back."
    ],
    "quick_replies": ["Redeem a gift card", "Pricing plans", "Speak to billing"]
}
```

That's it! The chatbot immediately inherits:
- Regex pattern matching
- Keyword scoring fallback
- Live Match Inspector support in the terminal debug banner
- CLI command discovery

