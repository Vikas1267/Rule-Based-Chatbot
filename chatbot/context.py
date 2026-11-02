"""
Conversation Context and State Management for Rule-Based Chatbot.
Maintains session state, dialogue history, extracted entity slots, and pending prompts.
"""
from datetime import datetime
from typing import Dict, Any, List, Optional


class ConversationContext:
    """Stores the ongoing state of a dialogue session."""

    def __init__(self, session_id: str = "default"):
        self.session_id: str = session_id
        self.history: List[Dict[str, Any]] = []
        self.slots: Dict[str, Any] = {}
        self.last_topic: Optional[str] = None
        self.last_intent: Optional[str] = None
        self.pending_question: Optional[str] = None  # e.g., 'ask_order_id', 'confirm_cancellation'
        self.turn_count: int = 0
        self.fallback_count: int = 0
        self.created_at: datetime = datetime.now()

    def update_slot(self, key: str, value: Any) -> None:
        """Stores or updates an extracted entity slot."""
        if value:
            self.slots[key] = value

    def get_slot(self, key: str, default: Any = None) -> Any:
        """Retrieves a slot value if available."""
        return self.slots.get(key, default)

    def record_turn(
        self,
        user_input: str,
        bot_response: str,
        topic: str,
        intent: str,
        confidence: float,
        matched_rule: str,
        extracted_entities: Dict[str, Any]
    ) -> None:
        """Appends a dialogue turn to the session history."""
        self.turn_count += 1
        self.last_topic = topic
        self.last_intent = intent

        if intent == "fallback":
            self.fallback_count += 1
        else:
            self.fallback_count = 0  # reset consecutive fallbacks

        for k, v in extracted_entities.items():
            if v:
                self.slots[k] = v

        turn_data = {
            "turn": self.turn_count,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "user_input": user_input,
            "bot_response": bot_response,
            "topic": topic,
            "intent": intent,
            "confidence": round(confidence, 2),
            "matched_rule": matched_rule,
            "entities": extracted_entities,
            "current_slots": dict(self.slots)
        }
        self.history.append(turn_data)

    def reset(self) -> None:
        """Resets the context for a brand new conversation."""
        self.history.clear()
        self.slots.clear()
        self.last_topic = None
        self.last_intent = None
        self.pending_question = None
        self.turn_count = 0
        self.fallback_count = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serializes current context to dictionary."""
        return {
            "session_id": self.session_id,
            "turn_count": self.turn_count,
            "slots": self.slots,
            "last_topic": self.last_topic,
            "last_intent": self.last_intent,
            "pending_question": self.pending_question,
            "fallback_count": self.fallback_count,
            "history_length": len(self.history)
        }
