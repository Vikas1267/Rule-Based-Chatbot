"""
Comprehensive Unit Test Suite for Rule-Based Chatbot.
Tests intent matching, keyword scoring, regex entity extraction,
fallback levels, and multi-turn context retention.
"""
import unittest
from chatbot.engine import RuleBasedChatbot
from chatbot.context import ConversationContext
from chatbot.normalizer import TextNormalizer


class TestTextNormalizer(unittest.TestCase):
    def test_contraction_expansion(self):
        text = "I'm looking for my order and won't wait"
        cleaned = TextNormalizer.clean(text)
        self.assertIn("i am", cleaned)
        self.assertIn("will not", cleaned)

    def test_spacy_nlp_pipeline(self):
        doc = TextNormalizer.parse_spacy("I have three broken packages")
        lemmas = [token.lemma_.lower() for token in doc if not token.is_stop and not token.is_punct]
        self.assertIn("break", lemmas)  # spaCy lemmatization: 'broken' -> 'break'
        self.assertIn("package", lemmas)  # spaCy lemmatization: 'packages' -> 'package'

    def test_re_regex_elongations_and_cleaning(self):
        # re regular expressions reduce elongated repetitions
        cleaned = TextNormalizer.clean("hiiiiii pleaaase help meee")
        self.assertIn("hello", cleaned)
        self.assertIn("please", cleaned)
        self.assertIn("help", cleaned)


class TestRuleBasedChatbot(unittest.TestCase):
    def setUp(self):
        self.bot = RuleBasedChatbot()

    def test_topic_orders_tracking(self):
        res = self.bot.process_message("Where is my package ORD-88192?")
        self.assertEqual(res["topic"], "orders")
        self.assertEqual(res["intent"], "track_order")
        self.assertGreaterEqual(res["confidence"], 0.70)
        self.assertEqual(res["entities"].get("order_id"), "ORD-88192")
        self.assertIn("ORD-88192", res["response"])

    def test_topic_tech_support_power_issue(self):
        res = self.bot.process_message("My device won't turn on and screen is black")
        self.assertEqual(res["topic"], "tech_support")
        self.assertEqual(res["intent"], "device_power_issue")
        # Check that response contains helpful troubleshooting terminology
        self.assertTrue(any(word in res["response"].lower() for word in ["power", "charging", "battery", "reset"]))

    def test_topic_tech_support_error_code_entity(self):
        res = self.bot.process_message("The app crashed with error ERR-404")
        self.assertEqual(res["topic"], "tech_support")
        self.assertEqual(res["intent"], "app_crash_error")
        self.assertEqual(res["entities"].get("error_code"), "ERR-404")

    def test_topic_billing_subscriptions(self):
        res = self.bot.process_message("What are the subscription pricing tiers?")
        self.assertEqual(res["topic"], "billing")
        self.assertEqual(res["intent"], "subscription_plans")
        self.assertTrue(any(word in res["response"].lower() for word in ["pro", "subscription", "pricing", "plan", "billing"]))


    def test_topic_general_faq_and_joke(self):
        res = self.bot.process_message("Tell me a funny joke")
        self.assertEqual(res["topic"], "general")
        self.assertEqual(res["intent"], "small_talk_joke")

    def test_human_agent_escalation(self):
        res = self.bot.process_message("I need to speak to a real human person")
        self.assertEqual(res["topic"], "general")
        self.assertEqual(res["intent"], "human_agent")
        self.assertTrue(any(phrase in res["response"] for phrase in ["Hotline", "support queue", "priority@example.com"]))


    def test_greeting_variations(self):
        # Variations like 'hii', 'heyy' should correctly map to greeting
        for greeting_text in ["hii", "heyy", "hiii", "hello"]:
            res = self.bot.process_message(greeting_text)
            self.assertEqual(res["topic"], "general")
            self.assertEqual(res["intent"], "greeting")
            self.assertGreaterEqual(res["confidence"], 0.70)

    def test_single_keyword_mapping(self):
        # Single keywords should directly trigger the correct intent without saying 'I don't know'
        test_cases = [
            ("refund", "return_refund", "orders"),
            ("wifi", "wifi_connectivity", "tech_support"),
            ("pricing", "subscription_plans", "billing"),
            ("invoice", "view_invoices", "billing"),
            ("joke", "small_talk_joke", "general")
        ]
        for kw, expected_intent, expected_topic in test_cases:
            res = self.bot.process_message(kw)
            self.assertEqual(res["topic"], expected_topic)
            self.assertEqual(res["intent"], expected_intent)

    def test_fallback_mechanism_unknown_input(self):
        # Gibberish input triggers proactive fallback without saying 'I don't know'
        res = self.bot.process_message("xyzzy flubber blorp wampus")
        self.assertEqual(res["topic"], "fallback")
        self.assertEqual(res["intent"], "fallback")
        self.assertEqual(res["confidence"], 0.0)
        # Verify it provides a helpful, short answer rather than a dead-end
        self.assertNotIn("i don't know", res["response"].lower())
        self.assertTrue(len(res["response"]) > 0)

    def test_multi_turn_context_and_memory(self):
        # Turn 1: User tracks order
        r1 = self.bot.process_message("Track my order ORD-55412")
        self.assertEqual(self.bot.context.get_slot("order_id"), "ORD-55412")

        # Turn 2: User wants to cancel that order without repeating the ID
        r2 = self.bot.process_message("Can I cancel it?")
        self.assertEqual(r2["intent"], "cancel_order")
        # Turn 3: User confirms cancellation
        r3 = self.bot.process_message("Yes, please confirm")
        self.assertEqual(r3["intent"], "cancel_order_confirmed")
        self.assertIn("ORD-55412", r3["response"])

    def test_compound_greeting_and_question(self):
        # A sentence with a greeting prefix plus a question should answer the question
        res = self.bot.process_message("hii what are u doing")
        self.assertEqual(res["intent"], "what_are_you_doing")
        self.assertTrue(any(word in res["response"].lower() for word in ["assist", "assisting", "help"]))

    def test_numeric_topic_selection(self):
        # Numeric inputs 1, 2, 3, 4 should explain the corresponding topic
        res4 = self.bot.process_message("4")
        self.assertEqual(res4["topic"], "general")
        self.assertEqual(res4["intent"], "topic_selection_4")
        self.assertIn("General FAQs", res4["response"])

        res1 = self.bot.process_message("1")
        self.assertEqual(res1["topic"], "orders")
        self.assertEqual(res1["intent"], "topic_selection_1")
        self.assertIn("Orders & Shipping", res1["response"])


if __name__ == "__main__":
    unittest.main()

