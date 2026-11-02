"""
Core Rule-Based Chatbot Engine.
Coordinates text normalization, entity/slot extraction, regex pattern matching,
weighted keyword scoring, context memory, and tiered fallback resolution.
"""
import random
import re
from typing import Dict, Any, List, Optional, Tuple

from .context import ConversationContext
from .normalizer import TextNormalizer
from .rules import INTENT_RULES, TOPICS, FALLBACK_LEVELS


class RuleBasedChatbot:
    """The central conversational agent implementing regex and keyword-based rule matching."""

    CONFIDENCE_THRESHOLD = 0.20

    # Regex patterns for Entity/Slot extraction
    ENTITY_PATTERNS = {
        "order_id": [
            r"\bORD-([A-Za-z0-9]+)\b",
            r"\border\s+(?:id\s+|number\s+|#)?([A-Za-z0-9\-]{4,10})\b",
            r"#(\d{4,8})\b"
        ],
        "email": [
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
        ],
        "error_code": [
            r"\b(ERR-\d{3,4})\b",
            r"\b(0x[0-9a-fA-F]{4,8})\b",
            r"\berror\s+(?:code\s+)?(\d{3,4})\b"
        ],
        "phone": [
            r"\b(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b"
        ]
    }

    def __init__(self, context: Optional[ConversationContext] = None):
        self.context = context or ConversationContext()
        self.rules = INTENT_RULES
        self.topics = TOPICS

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """Extracts slots/entities like order_id, email, error_code using regex."""
        extracted: Dict[str, Any] = {}
        for entity_type, patterns in self.ENTITY_PATTERNS.items():
            for pat in patterns:
                match = re.search(pat, text, re.IGNORECASE)
                if match:
                    # Capture group 1 if present, else full match
                    val = match.group(1) if match.groups() else match.group(0)
                    if entity_type == "order_id" and not val.upper().startswith("ORD-") and not val.startswith("#"):
                        val = f"ORD-{val.upper()}"
                    extracted[entity_type] = val.strip()
                    break
        return extracted

    def match_regex_patterns(self, text: str) -> Optional[Tuple[str, float, str]]:
        """Scans for regex pattern matches across all intents, prioritizing specific questions over greetings."""
        normalized_text = TextNormalizer.clean(text)
        greeting_match = None

        for intent_id, intent_data in self.rules.items():
            for pattern in intent_data.get("patterns", []):
                if re.search(pattern, normalized_text, re.IGNORECASE):
                    if intent_id == "greeting":
                        greeting_match = (intent_id, 0.95, f"regex: {pattern}")
                        break
                    # Specific non-greeting pattern matched
                    return (intent_id, 0.95, f"regex: {pattern}")

        if greeting_match:
            return greeting_match
        return None

    def calculate_keyword_score(self, user_keywords: set, intent_id: str) -> Tuple[float, List[str]]:
        """Calculates normalized weighted keyword match score for an intent."""
        intent_data = self.rules[intent_id]
        intent_keywords = intent_data.get("keywords", {})
        if not intent_keywords or not user_keywords:
            return 0.0, []

        total_weight = sum(intent_keywords.values())
        matched_weight = 0.0
        max_single_weight = 0.0
        matched_words = []

        for kw, weight in intent_keywords.items():
            # Check direct keyword or partial stem match
            if kw in user_keywords:
                matched_weight += weight
                max_single_weight = max(max_single_weight, weight)
                matched_words.append(kw)
            else:
                # Substring check for compound or inflected terms (require min length of 4 to prevent false positives)
                for ukw in user_keywords:
                    if len(ukw) >= 4 and len(kw) >= 4 and (ukw in kw or kw in ukw):
                        matched_weight += weight * 0.75
                        max_single_weight = max(max_single_weight, weight * 0.75)
                        matched_words.append(kw)
                        break

        # Additional topic bonus if user query explicitly mentions the topic name
        topic_key = intent_data.get("topic")
        if topic_key and topic_key in user_keywords:
            matched_weight += 1.5

        # Normalize score: combine density score with single strong keyword sensitivity
        density_score = min(1.0, matched_weight / (total_weight * 0.6))
        single_boost = min(1.0, max_single_weight / 3.2) if max_single_weight >= 2.0 else 0.0
        score = max(density_score, single_boost)
        return score, matched_words

    def score_all_intents(self, user_keywords: set) -> List[Dict[str, Any]]:
        """Ranks all intents according to keyword match scores."""
        scores = []
        for intent_id, intent_data in self.rules.items():
            score, matched_words = self.calculate_keyword_score(user_keywords, intent_id)
            if score > 0:
                scores.append({
                    "intent": intent_id,
                    "topic": intent_data["topic"],
                    "title": intent_data["title"],
                    "score": round(score, 3),
                    "matched_words": matched_words
                })
        scores.sort(key=lambda x: x["score"], reverse=True)
        return scores

    def handle_context_continuation(self, text: str, user_keywords: set) -> Optional[Dict[str, Any]]:
        """Handles conversational context (e.g. affirmations, order confirmation, numeric menu selection)."""
        lower = text.strip().lower()

        # Numeric menu selection: '1', '2', '3', '4', 'option 1', etc.
        topic_menu_map = {
            "1": ("orders", "Orders & Shipping covers tracking packages, cancelling orders, return policies, and delivery options.\nFor example, try asking: 'Where is package ORD-12345?' or 'How do I return an item?'"),
            "2": ("tech_support", "Technical Support covers device power issues, Wi-Fi connectivity, app crash codes, and password resets.\nFor example, try asking: 'My device won't turn on' or 'How do I reset my password?'"),
            "3": ("billing", "Account & Billing covers subscription plans, payment methods, downloading invoices, and 2FA security.\nFor example, try asking: 'What are your pricing plans?' or 'How do I update my card?'"),
            "4": ("general", "General FAQs cover our business operating hours, store locations, and live representative contact.\nFor example, try asking: 'What are your hours?' or 'I want to speak with a human agent.'")
        }
        num_match = re.search(r"^(?:option\s+|topic\s+|#)?([1-4])$", lower)
        if num_match:
            num = num_match.group(1)
            topic_name, desc = topic_menu_map[num]
            return {
                "topic": topic_name,
                "intent": f"topic_selection_{num}",
                "confidence": 1.0,
                "matched_rule": f"menu_selection: option_{num}",
                "response": desc,
                "quick_replies": []
            }

        # Affirmations
        is_yes = bool(re.search(r"^(?:yes|yep|yeah|sure|confirm|ok|okay|please|y)\b", lower))
        is_no = bool(re.search(r"^(?:no|nope|cancel|stop|nevermind|n)\b", lower))

        if self.context.last_intent == "cancel_order" and (is_yes or "confirm" in lower):
            order_id = self.context.get_slot("order_id", "ORD-Recent")
            return {
                "topic": "orders",
                "intent": "cancel_order_confirmed",
                "confidence": 1.0,
                "matched_rule": "contextual: confirmation",
                "response": f"[v] Cancellation confirmed for order {order_id}. A confirmation receipt and refund notice have been dispatched to your email.",
                "quick_replies": ["Track refund status", "Shop new items", "Store hours"]
            }

        if self.context.last_intent == "human_agent" and (is_yes or "call" in lower):
            ticket_id = f"TCK-{random.randint(10000, 99999)}"
            return {
                "topic": "general",
                "intent": "escalation_ticket_created",
                "confidence": 1.0,
                "matched_rule": "contextual: human_escalation",
                "response": f"[Ticket] Ticket #{ticket_id} created! Priority customer care will contact you shortly. You may also dial toll-free 1-800-555-0199 quoting #{ticket_id}.",
                "quick_replies": ["Return to main menu", "Check operating hours"]
            }

        return None


    def format_response(self, intent_id: str, entities: Dict[str, Any]) -> str:
        """Selects and interpolates response templates with extracted or remembered slots."""
        intent_data = self.rules[intent_id]
        raw_response = random.choice(intent_data["responses"])

        # Determine slot values from current turn or context memory
        order_id = entities.get("order_id") or self.context.get_slot("order_id", "ORD-Sample")
        error_code = entities.get("error_code") or self.context.get_slot("error_code", "ERR-General")

        slot_status = ""
        slot_cancel_status = ""
        slot_error_code = ""

        if entities.get("order_id") or self.context.get_slot("order_id"):
            slot_status = f"Status for [{order_id}]: Currently In Transit via FedEx Express (Estimated Delivery: Tomorrow by 4:00 PM). "
            slot_cancel_status = f"Active order [{order_id}] is verified and within cancellation limits. "

        if entities.get("error_code") or self.context.get_slot("error_code"):
            slot_error_code = f" [{error_code}]"

        interpolated = raw_response.format(
            order_id=order_id,
            error_code=error_code,
            slot_status=slot_status,
            slot_cancel_status=slot_cancel_status,
            slot_error_code=slot_error_code
        )
        return interpolated

    def build_fallback_response(self, ranked_scores: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Builds a smart tiered fallback response when confidence is below threshold."""
        fallback_level_idx = min(self.context.fallback_count, len(FALLBACK_LEVELS) - 1)
        fallback_config = FALLBACK_LEVELS[fallback_level_idx]

        ticket_id = f"TCK-{random.randint(10000, 99999)}"
        msg = fallback_config["message"].format(ticket_id=ticket_id)

        quick_replies = []
        suggestions = []

        # If there are partial matches, provide "Did you mean?" suggestions
        if ranked_scores and ranked_scores[0]["score"] >= 0.15:
            top_candidates = ranked_scores[:2]
            suggestions = [c["title"] for c in top_candidates]
            quick_replies = [c["title"] for c in top_candidates]
            msg += "\n\nDid you mean one of these topics?"
            for cand in top_candidates:
                msg += f"\n- {cand['title']}"
        elif fallback_config.get("include_topics"):
            quick_replies = [t["name"] for t in self.topics.values()]
        elif fallback_config.get("include_escalation"):
            quick_replies = ["Talk to human agent", "Call 1-800-555-0199", "Restart chat"]
        else:
            quick_replies = ["Track an order", "Device troubleshooting", "Pricing plans", "Store hours"]

        return {
            "topic": "fallback",
            "intent": "fallback",
            "confidence": 0.0,
            "matched_rule": f"fallback: level_{fallback_level_idx + 1}",
            "response": msg,
            "quick_replies": quick_replies,
            "suggestions": suggestions,
            "ticket_id": ticket_id if fallback_config.get("include_escalation") else None
        }

    def process_message(self, user_input: str) -> Dict[str, Any]:
        """Main pipeline: processes user input, resolves intent, updates context, returns response."""
        clean_input = user_input.strip()
        if not clean_input:
            return {
                "topic": "general",
                "intent": "empty_input",
                "confidence": 1.0,
                "matched_rule": "default: empty",
                "response": "Please type a question or choose an option from /topics to get started!",
                "quick_replies": ["Track an order", "Tech troubleshooting", "Pricing plans", "Store hours"],
                "entities": {},
                "context": self.context.to_dict()
            }


        # 1. Extract entities/slots
        entities = self.extract_entities(clean_input)
        for k, v in entities.items():
            self.context.update_slot(k, v)

        # 2. Extract keywords
        user_keywords = TextNormalizer.extract_keywords(clean_input)

        # 3. Check for multi-turn contextual continuations
        context_result = self.handle_context_continuation(clean_input, user_keywords)
        if context_result:
            self.context.record_turn(
                user_input=clean_input,
                bot_response=context_result["response"],
                topic=context_result["topic"],
                intent=context_result["intent"],
                confidence=context_result["confidence"],
                matched_rule=context_result["matched_rule"],
                extracted_entities=entities
            )
            context_result["entities"] = entities
            context_result["context"] = self.context.to_dict()
            context_result["user_keywords"] = sorted(list(user_keywords))
            return context_result

        # 4. Attempt exact regex match
        regex_match = self.match_regex_patterns(clean_input)
        if regex_match:
            intent_id, confidence, matched_rule = regex_match
            response_text = self.format_response(intent_id, entities)
            quick_replies = self.rules[intent_id].get("quick_replies", [])
            topic = self.rules[intent_id]["topic"]

            self.context.record_turn(
                user_input=clean_input,
                bot_response=response_text,
                topic=topic,
                intent=intent_id,
                confidence=confidence,
                matched_rule=matched_rule,
                extracted_entities=entities
            )
            return {
                "topic": topic,
                "intent": intent_id,
                "confidence": confidence,
                "matched_rule": matched_rule,
                "response": response_text,
                "quick_replies": quick_replies,
                "entities": entities,
                "context": self.context.to_dict(),
                "user_keywords": sorted(list(user_keywords))
            }

        # 5. Fall back to weighted keyword scoring
        ranked_scores = self.score_all_intents(user_keywords)

        if ranked_scores and ranked_scores[0]["score"] >= self.CONFIDENCE_THRESHOLD:
            top_intent = ranked_scores[0]
            intent_id = top_intent["intent"]
            confidence = min(0.92, top_intent["score"])
            matched_words = ", ".join(top_intent["matched_words"])
            matched_rule = f"keywords: [{matched_words}] (score: {top_intent['score']:.2f})"
            response_text = self.format_response(intent_id, entities)
            quick_replies = self.rules[intent_id].get("quick_replies", [])
            topic = self.rules[intent_id]["topic"]

            self.context.record_turn(
                user_input=clean_input,
                bot_response=response_text,
                topic=topic,
                intent=intent_id,
                confidence=confidence,
                matched_rule=matched_rule,
                extracted_entities=entities
            )
            return {
                "topic": topic,
                "intent": intent_id,
                "confidence": confidence,
                "matched_rule": matched_rule,
                "response": response_text,
                "quick_replies": quick_replies,
                "entities": entities,
                "context": self.context.to_dict(),
                "user_keywords": sorted(list(user_keywords))
            }


        # 6. Fallback response
        fallback_result = self.build_fallback_response(ranked_scores)
        self.context.record_turn(
            user_input=clean_input,
            bot_response=fallback_result["response"],
            topic=fallback_result["topic"],
            intent=fallback_result["intent"],
            confidence=fallback_result["confidence"],
            matched_rule=fallback_result["matched_rule"],
            extracted_entities=entities
        )
        fallback_result["entities"] = entities
        fallback_result["context"] = self.context.to_dict()
        fallback_result["user_keywords"] = sorted(list(user_keywords))
        return fallback_result

    def reset_session(self) -> None:
        """Resets the conversation state."""
        self.context.reset()

