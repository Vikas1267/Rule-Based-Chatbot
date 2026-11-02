"""
Rule Definitions and Knowledge Base for Rule-Based Chatbot.
Contains 4 conversation topics, intent patterns (Regex + Keyword weights),
responses with dynamic slot interpolation, quick reply suggestions, and fallback strategies.
"""
from typing import Dict, List, Any


TOPICS = {
    "orders": {
        "name": "Orders & Shipping",
        "icon": "[Orders]",
        "description": "Order tracking, delivery times, cancellations, and returns.",
        "sample_prompts": [
            "Where is my package ORD-49201?",
            "How do I return a damaged item?",
            "What are your delivery options?",
            "Can I cancel my recent order?"
        ]
    },
    "tech_support": {
        "name": "Technical Support",
        "icon": "[Tech]",
        "description": "Troubleshooting, device issues, error codes, and connectivity.",
        "sample_prompts": [
            "My device won't turn on",
            "I'm seeing error ERR-404",
            "How do I reset my Wi-Fi connection?",
            "The app keeps crashing"
        ]
    },
    "billing": {
        "name": "Account & Billing",
        "icon": "[Billing]",
        "description": "Subscriptions, pricing plans, invoices, and payment methods.",
        "sample_prompts": [
            "What are your subscription pricing plans?",
            "How do I update my payment method?",
            "Where can I download my invoice?",
            "How do I enable two-factor authentication?"
        ]
    },
    "general": {
        "name": "General & FAQ",
        "icon": "[General]",
        "description": "Store hours, live human support, bot capabilities, and small talk.",
        "sample_prompts": [
            "What are your business operating hours?",
            "I want to speak with a human agent",
            "Tell me a funny tech joke",
            "What can you help me with?"
        ]
    }
}



INTENT_RULES: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # TOPIC 1: ORDERS & SHIPPING
    # =========================================================================
    "track_order": {
        "topic": "orders",
        "title": "Track Order / Delivery Status",
        "patterns": [
            r"\b(?:track|locate|where(?:\s+is)?|status(?:\s+of)?|check)\b.*?\b(?:order|package|parcel|shipment|delivery)\b",
            r"\border\s+(?:status|tracking|location)\b",
            r"\bwhere\s+(?:is\s+)?my\s+(?:stuff|item|package|order)\b",
            r"\btrack\b\s+(?:ord[-\w]+|#\d+|\d+)"
        ],
        "keywords": {
            "track": 3.0,
            "order": 2.5,
            "package": 2.5,
            "parcel": 2.5,
            "shipment": 2.5,
            "delivery": 2.0,
            "status": 2.0,
            "where": 1.5,
            "arrive": 1.5,
            "dispatch": 1.5,
            "transit": 2.0
        },
        "responses": [
            "I can assist with tracking your shipment! {slot_status}Please provide your order number (e.g. ORD-12345) to see the live status.",
            "Checking shipment logs for you... {slot_status}Standard deliveries typically arrive within 2-4 business days."
        ],
        "quick_replies": ["Track ORD-88492", "Shipping delivery times", "Cancel my order"]
    },

    "cancel_order": {
        "topic": "orders",
        "title": "Cancel Order",
        "patterns": [
            r"\b(?:cancel|stop|abort|terminate|halt)\b.*?\b(?:order|purchase|shipment|delivery|it|this)?\b",
            r"\bhow\s+(?:do|can)\s+i\s+cancel\b",
            r"\bi\s+want\s+to\s+cancel\b",
            r"\b(?:can\s+i\s+)?cancel(?:\s+it|\s+this|\s+my\s+order)?\b",
            r"^(?:cancel|stop)\b"
        ],

        "keywords": {
            "cancel": 3.5,
            "order": 2.0,
            "stop": 2.0,
            "abort": 2.5,
            "mistake": 1.5,
            "refund": 1.0
        },
        "responses": [
            "Orders can be cancelled free of charge within 60 minutes of placement before dispatch. {slot_cancel_status}Would you like me to flag order {order_id} for cancellation?",
            "To cancel an active order, navigate to your Account > Orders > Cancel Order. If already shipped, you can refuse the parcel upon delivery for a full refund."
        ],
        "quick_replies": ["Yes, cancel my order", "Return & Refund policy", "Speak to human agent"]
    },

    "return_refund": {
        "topic": "orders",
        "title": "Returns & Refunds Policy",
        "patterns": [
            r"\b(?:return|refund|exchange|money\s+back|send\s+back)\b.*?\b(?:policy|item|product|order|package)?\b",
            r"\bhow\s+(?:do|can)\s+i\s+(?:get\s+a\s+refund|return)\b",
            r"\bwarranty\s+(?:policy|claim)\b"
        ],
        "keywords": {
            "return": 3.0,
            "refund": 3.0,
            "exchange": 2.5,
            "policy": 2.0,
            "warranty": 2.5,
            "broken": 1.5,
            "damaged": 1.5,
            "reimburse": 2.5
        },
        "responses": [
            "We offer a hassle-free 30-day money-back guarantee! Items must be in original condition with tags. Refunds are processed back to your original payment method in 3-5 business days.",
            "To initiate a return or warranty claim: Repack the item in its original box with your order slip and hand it over to any authorized courier."
        ],
        "quick_replies": ["How long do refunds take?", "Track my return package", "Speak to support"]
    },


    "shipping_info": {
        "topic": "orders",
        "title": "Shipping Options & Delivery Times",
        "patterns": [
            r"\b(?:shipping|delivery)\b.*?\b(?:time|cost|fee|speed|options|international|express|fast)\b",
            r"\bhow\s+long\s+(?:does|will)\s+(?:shipping|delivery)\s+take\b",
            r"\bdo\s+you\s+ship\s+internationally\b"
        ],
        "keywords": {
            "shipping": 3.0,
            "delivery": 3.0,
            "international": 2.5,
            "express": 2.0,
            "overnight": 2.0,
            "duration": 2.0,
            "cost": 1.5,
            "courier": 2.0,
            "fedex": 1.5,
            "dhl": 1.5
        },
        "responses": [
            "We provide Standard (3-5 business days, Free over $50) and Express Next-Day Shipping ($9.99). We also ship to over 140 countries globally!",
            "Domestic orders ship via FedEx or DHL with full end-to-end tracking. International shipping typically arrives in 7-10 business days."
        ],
        "quick_replies": ["Track my package", "International shipping rates", "Business hours"]
    },

    "modify_address": {
        "topic": "orders",
        "title": "Change Shipping Address",
        "patterns": [
            r"\b(?:change|update|modify|edit|wrong)\b.*?\b(?:address|destination|shipping\s+address|location)\b",
            r"\bsent\s+to\s+wrong\s+address\b"
        ],
        "keywords": {
            "change": 2.0,
            "update": 2.0,
            "modify": 2.0,
            "address": 3.5,
            "destination": 2.5,
            "shipping": 1.5,
            "wrong": 1.5
        },
        "responses": [
            "Address modifications can be made within 1 hour of placing the order. Please provide your Order ID and new street address so we can intercept the label.",
            "If your order has not been dispatched, you can update your shipping address in Account > Orders > Edit Destination."
        ],
        "quick_replies": ["Track my order", "Cancel order", "Speak to agent"]
    },

    # =========================================================================
    # TOPIC 2: TECHNICAL SUPPORT & TROUBLESHOOTING
    # =========================================================================
    "device_power_issue": {
        "topic": "tech_support",
        "title": "Device Power & Hardware Issue",
        "patterns": [
            r"\b(?:device|phone|laptop|unit|tablet|screen)\b.*?\b(?:won't|will\s+not|not|doesn't)\s+(?:turn\s+on|power\s+on|start|boot|charge)\b",
            r"\b(?:black\s+screen|dead\s+battery|not\s+charging|unresponsive)\b",
            r"\bwon't\s+turn\s+on\b"
        ],
        "keywords": {
            "power": 3.0,
            "boot": 2.5,
            "charge": 2.5,
            "battery": 2.5,
            "screen": 2.0,
            "dead": 2.0,
            "turn": 1.5,
            "black": 1.5,
            "unresponsive": 2.5,
            "device": 1.5
        },
        "responses": [
            "Let's troubleshoot the power issue step-by-step:\n1. Connect the original charging cable directly to a wall outlet for at least 15 minutes.\n2. Perform a hard reset by holding the Power button down for 15-20 seconds.\n3. Check if the LED indicator pulses or blinks.",
            "If your device remains unresponsive after 30 minutes of charging, the battery or internal power regulator may require hardware warranty inspection."
        ],
        "quick_replies": ["Hard reset guide", "Warranty claim", "Speak to human technician"]
    },

    "password_reset": {
        "topic": "tech_support",
        "title": "Password Reset & Login Assistance",
        "patterns": [
            r"\b(?:forgot|reset|change|recover|lost)\b.*?\b(?:password|passcode|login|credentials|pin)\b",
            r"\bcan't\s+(?:log\s*in|sign\s*in)\b",
            r"\blockout|locked\s+out\b"
        ],
        "keywords": {
            "password": 3.5,
            "reset": 3.0,
            "login": 2.5,
            "forgot": 2.5,
            "recover": 2.5,
            "credentials": 2.0,
            "locked": 2.0,
            "access": 1.5
        },
        "responses": [
            "To reset your password:\n1. Click 'Forgot Password' on the sign-in screen.\n2. Enter your registered email address.\n3. Check your inbox (and spam folder) for a secure reset link valid for 30 minutes.",
            "If your account is temporarily locked due to multiple incorrect attempts, the lock automatically clears in 15 minutes, or you can request an instant unlock token via SMS."
        ],
        "quick_replies": ["Two-factor authentication", "Update email address", "Speak to human agent"]
    },

    "wifi_connectivity": {
        "topic": "tech_support",
        "title": "Wi-Fi & Network Connectivity",
        "patterns": [
            r"\b(?:wifi|wi-fi|internet|network|connection|offline|bluetooth)\b.*?\b(?:dropped|disconnected|slow|not\s+working|cannot\s+connect|fail)\b",
            r"\bcan't\s+connect\s+to\s+(?:wifi|internet|network)\b",
            r"\bno\s+internet\s+connection\b"
        ],
        "keywords": {
            "wifi": 3.5,
            "network": 3.0,
            "internet": 3.0,
            "connection": 2.5,
            "offline": 2.5,
            "disconnect": 2.0,
            "router": 2.0,
            "signal": 1.5,
            "bluetooth": 2.0
        },
        "responses": [
            "Quick network troubleshooting:\n1. Toggle Airplane Mode ON for 10 seconds, then OFF.\n2. Restart your Wi-Fi router (power down for 30 seconds).\n3. Forget the Wi-Fi network in Settings and re-enter the wireless security key.",
            "Ensure your device is within line-of-sight of a 2.4GHz or 5GHz band, and verify all Ethernet and power cables are connected."
        ],

        "quick_replies": ["Check system status", "Factory reset device", "Contact tech support"]
    },

    "app_crash_error": {
        "topic": "tech_support",
        "title": "App Crash & Error Codes",
        "patterns": [
            r"\b(?:app|software|program|system)\b.*?\b(?:crash|freeze|hang|stuck|closes|quit|error)\b",
            r"\berror\s+(?:code\s+)?(?:err-\d+|0x[0-9a-f]+|\d+)\b",
            r"\bthe\s+app\s+keeps\s+crashing\b"
        ],
        "keywords": {
            "crash": 3.5,
            "error": 3.0,
            "freeze": 2.5,
            "glitch": 2.0,
            "bug": 2.0,
            "stuck": 2.0,
            "code": 1.5,
            "hang": 2.0,
            "force": 1.5,
            "close": 1.5
        },
        "responses": [
            "App stability fix:\n1. Force stop the application and restart your device.\n2. Clear application cache from Settings > Apps > Storage > Clear Cache.\n3. Verify you have installed the latest release from the App Store / Play Store.",
            "If you encountered an error code{slot_error_code}, our automated error diagnostics report this as a temporary handshake issue. Updating to the latest patch will resolve it."
        ],
        "quick_replies": ["Check for updates", "Report bug to team", "Factory reset"]
    },

    "factory_reset": {
        "topic": "tech_support",
        "title": "Factory Reset & Data Wipe",
        "patterns": [
            r"\b(?:factory|hard)\s+reset\b",
            r"\bhow\s+(?:do|can)\s+i\s+(?:factory\s+reset|wipe|format)\b",
            r"\brestore\s+to\s+default\b"
        ],
        "keywords": {
            "factory": 3.5,
            "reset": 3.0,
            "wipe": 3.0,
            "format": 2.5,
            "restore": 2.5,
            "default": 2.0,
            "clean": 1.5
        },
        "responses": [
            "[!] Note: A factory reset wipes all local files and restores original manufacturer settings. Backup your data first!\nSteps: Settings > System > Advanced > Reset Options > Erase All Data.",
            "To perform a hardware recovery reset: Power off device, hold Volume Down + Power button simultaneously until the recovery fastboot menu appears."
        ],

        "quick_replies": ["Backup my data", "Password reset", "Speak to tech specialist"]
    },

    # =========================================================================
    # TOPIC 3: ACCOUNT & BILLING
    # =========================================================================
    "subscription_plans": {
        "topic": "billing",
        "title": "Pricing & Subscription Tiers",
        "patterns": [
            r"\b(?:pricing|subscription|plans?|tiers?|cost|how\s+much\s+(?:is|does))\b",
            r"\b(?:free|pro|enterprise|monthly|annual)\s+(?:plan|cost|price)\b",
            r"\bupgrade\s+(?:my\s+)?account\b"
        ],
        "keywords": {
            "subscription": 3.5,
            "pricing": 3.5,
            "plan": 3.0,
            "tier": 2.5,
            "cost": 2.5,
            "price": 2.5,
            "free": 2.0,
            "pro": 2.0,
            "enterprise": 2.0,
            "upgrade": 2.0
        },
        "responses": [
            "We offer 3 straightforward subscription tiers:\n- Free Starter ($0/mo): Core features with community support.\n- Pro ($14/mo or $120/yr): Unlimited access, priority speed, 24/7 support.\n- Enterprise ($49/mo): Dedicated account manager, custom SLAs, audit logs.",
            "You can upgrade or downgrade anytime with pro-rated billing applied immediately to your balance!"
        ],
        "quick_replies": ["Upgrade to Pro", "Download invoice", "Payment methods"]
    },

    "payment_methods": {
        "topic": "billing",
        "title": "Update Payment Methods",
        "patterns": [
            r"\b(?:update|change|add|remove|switch)\b.*?\b(?:card|credit\s*card|debit|payment|paypal|bank)\b",
            r"\bpayment\s+methods?\b",
            r"\bdeclined\s+(?:card|payment)\b"
        ],
        "keywords": {
            "payment": 3.5,
            "card": 3.0,
            "credit": 2.5,
            "debit": 2.5,
            "paypal": 2.5,
            "billing": 2.0,
            "update": 2.0,
            "declined": 2.0,
            "cvv": 1.5
        },
        "responses": [
            "We accept Visa, Mastercard, American Express, PayPal, and Apple/Google Pay. You can securely update your billing card at Account > Billing > Payment Methods.",
            "All payment transactions are encrypted using PCI-DSS compliant 256-bit SSL protocols. We never store raw credit card numbers on our servers."
        ],
        "quick_replies": ["Subscription plans", "View invoices", "Speak to billing"]
    },

    "view_invoices": {
        "topic": "billing",
        "title": "View & Download Invoices",
        "patterns": [
            r"\b(?:download|view|get|see|find)\b.*?\b(?:invoice|receipt|statement|bill|tax\s+document)\b",
            r"\bwhere\s+is\s+my\s+(?:receipt|invoice|bill)\b"
        ],
        "keywords": {
            "invoice": 3.5,
            "receipt": 3.5,
            "statement": 3.0,
            "bill": 2.5,
            "download": 2.5,
            "tax": 2.0,
            "pdf": 2.0
        },
        "responses": [
            "All monthly invoices and PDF tax receipts are accessible under Account > Billing History. You can bulk download statements anytime.",
            "Need a custom tax exemption or company VAT number on your invoices? You can configure your company tax information in Billing Preferences."
        ],
        "quick_replies": ["Update billing details", "Subscription tiers", "Speak to agent"]
    },

    "two_factor_auth": {
        "topic": "billing",
        "title": "Two-Factor Authentication (2FA)",
        "patterns": [
            r"\b(?:2fa|two-factor|mfa|authenticator|security\s+code|otp)\b",
            r"\benable\s+(?:2fa|mfa|two\s+factor)\b",
            r"\baccount\s+security\b"
        ],
        "keywords": {
            "2fa": 3.5,
            "mfa": 3.5,
            "two-factor": 3.5,
            "authenticator": 3.0,
            "security": 2.5,
            "otp": 2.5,
            "protect": 2.0
        },
        "responses": [
            "Protect your account with Two-Factor Authentication! Go to Account > Security > Enable 2FA. We support Google Authenticator, Authy, and hardware FIDO keys.",
            "Make sure to save your 10 backup emergency codes in a secure location after configuring your authenticator app."
        ],
        "quick_replies": ["Password reset", "Payment methods", "Close account"]
    },

    "delete_account": {
        "topic": "billing",
        "title": "Account Cancellation & Data Deletion",
        "patterns": [
            r"\b(?:delete|close|remove|cancel)\b.*?\b(?:my\s+)?(?:account|profile|membership|data)\b",
            r"\bgdpr\s+(?:request|deletion)\b"
        ],
        "keywords": {
            "delete": 3.5,
            "close": 3.0,
            "account": 3.0,
            "cancel": 2.5,
            "gdpr": 2.5,
            "data": 2.0,
            "terminate": 2.5
        },
        "responses": [
            "To close your account and initiate permanent GDPR data erasure: Head to Account > Privacy > Request Account Deletion. A 7-day grace period is provided if you change your mind.",
            "Please note that deleting your account will terminate all active subscriptions and license keys linked with your email."
        ],
        "quick_replies": ["Cancel subscription instead", "Download my data", "Speak to support"]
    },

    # =========================================================================
    # TOPIC 4: GENERAL INQUIRIES & FAQ & SMALL TALK
    # =========================================================================
    "greeting": {
        "topic": "general",
        "title": "Greeting",
        "patterns": [
            r"\b(?:hello+|hi+|hey+|howdy|greetings?|good\s+(?:morning|afternoon|evening)|yo|sup|hola)\b",
            r"^h[iey]+"
        ],
        "keywords": {
            "hello": 3.5,
            "hi": 3.5,
            "hii": 3.5,
            "hey": 3.5,
            "howdy": 2.5,
            "greetings": 2.5,
            "morning": 2.0,
            "afternoon": 2.0,
            "evening": 2.0
        },
        "responses": [
            "Hello! [Assistant] I'm your Rule-Based Assistant. How can I help you today? I can assist with Orders, Technical Support, Account & Billing, or General FAQs.",
            "Greetings! Welcome to our support desk. Feel free to ask about your package status, troubleshoot a device, or inquire about pricing."
        ],
        "quick_replies": ["Track an Order", "Technical Troubleshooting", "Pricing & Plans", "Store Hours"]
    },

    "bot_identity": {
        "topic": "general",
        "title": "Bot Identity & Capabilities",
        "patterns": [
            r"\bwho\s+are\s+you\b",
            r"\bwhat\s+(?:can|do)\s+you\s+do\b",
            r"\bwhat\s+is\s+your\s+name\b",
            r"\bhelp\s+me|help\b"
        ],
        "keywords": {
            "who": 2.5,
            "what": 2.0,
            "capabilities": 3.0,
            "features": 2.5,
            "bot": 2.5,
            "ai": 2.0,
            "help": 2.5
        },
        "responses": [
            "I am an intelligent Rule-Based Conversational Chatbot powered by regex pattern matching, keyword scoring, and entity extraction! I cover 4 domains:\n1. [Orders] Orders & Shipping\n2. [Tech] Tech Support & Troubleshooting\n3. [Billing] Account & Billing\n4. [General] General FAQs & Store Information.",
            "Think of me as your 24/7 concierge! Ask me questions like 'Track ORD-40192', 'My device won't turn on', 'What are your pricing plans?', or 'Can I talk to a human?'"
        ],
        "quick_replies": ["Orders & Shipping", "Tech Support", "Account & Billing", "Talk to Human"]
    },

    "store_hours_location": {
        "topic": "general",
        "title": "Store Hours & Contact Information",
        "patterns": [
            r"\b(?:hours|open|closed|schedule|timing|location|address|office|store)\b",
            r"\bwhat\s+time\s+(?:do|are)\s+you\s+(?:open|close)\b",
            r"\bwhere\s+are\s+you\s+located\b"
        ],
        "keywords": {
            "hours": 3.5,
            "timing": 3.0,
            "location": 3.0,
            "open": 2.5,
            "close": 2.5,
            "address": 2.5,
            "office": 2.5,
            "weekend": 2.0,
            "sunday": 1.5
        },
        "responses": [
            "[Hours] Monday - Friday: 8:00 AM - 8:00 PM EST. Saturday & Sunday: 9:00 AM - 5:00 PM EST.\n[Location] Flagship Center: 500 Tech Plaza, Suite 400, New York, NY 10001.\n[Online] Digital Support: Available 24/7 via this chatbot!",
            "Our physical customer service hubs are open weekdays 9:00 AM to 6:00 PM. Our automated systems are always operational 24/7/365."
        ],
        "quick_replies": ["Speak to human agent", "Contact email", "Pricing plans"]
    },

    "human_agent": {
        "topic": "general",
        "title": "Human Representative Escalation",
        "patterns": [
            r"\b(?:human|person|agent|representative|specialist|manager|operator|talk\s+to\s+someone)\b",
            r"\bi\s+want\s+to\s+speak\s+with\s+a\s+human\b",
            r"\btransfer\s+me\b"
        ],
        "keywords": {
            "human": 3.5,
            "agent": 3.5,
            "representative": 3.5,
            "person": 3.0,
            "operator": 3.0,
            "specialist": 2.5,
            "speak": 2.0,
            "transfer": 3.0,
            "escalate": 3.0
        },
        "responses": [
            "I'd be glad to connect you with a specialist! Customer Service Hotline: +1 (800) 555-0199 (Mon-Fri 8am-8pm EST). Or I can generate an express support ticket right now for you.",
            "Routing you to our customer support queue... Estimated current wait time: ~3 minutes."
        ],
        "quick_replies": ["Call Support Hotline", "Generate Support Ticket", "Keep chatting with bot"]
    },

    "how_are_you": {
        "topic": "general",
        "title": "How Are You",
        "patterns": [
            r"\bhow\s+(?:are\s+you|are\s+u|r\s+u|is\s+it\s+going|do\s+you\s+do)\b",
            r"\bhow('s|\s+is)\s+it\s+going\b",
            r"\bhow\s+are\s+things\b",
            r"\bhow\s+do\s+you\s+feel\b"
        ],
        "keywords": {
            "how": 3.0,
            "doing": 3.0,
            "going": 2.5,
            "feeling": 2.5,
            "today": 1.5
        },
        "responses": [
            "I'm doing great, thank you for asking! How can I help you today?",
            "Doing wonderful and ready to assist you! What can I help you with?"
        ],
        "quick_replies": ["Track an order", "Tech troubleshooting", "Pricing plans"]
    },

    "what_are_you_doing": {
        "topic": "general",
        "title": "What Are You Doing",
        "patterns": [
            r"\bwhat\s+(?:are\s+you|are\s+u|r\s+u)\s+doing\b",
            r"\bwhat\s+are\s+you\s+up\s+to\b",
            r"\bwhat\s+you\s+doing\b",
            r"\bwhat\s+do\s+you\s+do\b"
        ],
        "keywords": {
            "doing": 3.5,
            "what": 2.0
        },
        "responses": [
            "I'm right here assisting you with customer support! I can help you with order tracking, tech troubleshooting, billing, or general questions. What's on your mind?",
            "I'm ready to help you with any questions about packages, technical issues, or pricing plans. How can I assist you today?"
        ],
        "quick_replies": ["Track an order", "Tech troubleshooting", "Pricing plans"]
    },



    "small_talk_joke": {
        "topic": "general",
        "title": "Tell a Joke",
        "patterns": [
            r"\b(?:tell\s+me\s+a\s+joke|make\s+me\s+laugh|joke|funny)\b"
        ],
        "keywords": {
            "joke": 4.0,
            "funny": 3.0,
            "laugh": 3.0,
            "humor": 2.5
        },
        "responses": [
            "Why do programmers prefer dark mode? Because light attracts bugs! :-)",
            "There are 10 types of people in the world: those who understand binary, and those who don't!",
            "Why did the database administrator walk out of the restaurant? Because there were too many tables!"
        ],
        "quick_replies": ["Tell another joke", "What can you do?", "Track my order"]
    },

    "compliment_gratitude": {
        "topic": "general",
        "title": "Gratitude / Compliments",
        "patterns": [
            r"\b(?:thank\s+you|thanks|thx|awesome|great\s+job|good\s+bot|appreciate\s+it|you\s+rock)\b"
        ],
        "keywords": {
            "thanks": 3.5,
            "thank": 3.5,
            "awesome": 3.0,
            "great": 2.5,
            "helpful": 2.5,
            "good": 2.0,
            "perfect": 2.5
        },
        "responses": [
            "You're very welcome! Glad I could assist. Let me know if you need anything else today!",
            "Always happy to help! Don't hesitate to reach back out if you have more questions."
        ],
        "quick_replies": ["Track an order", "Tech troubleshooting", "I'm all good!"]
    },

    "farewell": {
        "topic": "general",
        "title": "Farewell",
        "patterns": [
            r"^(?:goodbye|bye|cya|see\s+you|have\s+a\s+good\s+(?:day|night)|farewell|quit|exit)\b"
        ],
        "keywords": {
            "goodbye": 3.5,
            "bye": 3.5,
            "cya": 3.0,
            "farewell": 3.0,
            "exit": 2.5,
            "quit": 2.5
        },
        "responses": [
            "Goodbye! Have a wonderful day ahead. Feel free to return anytime you need support!",
            "Thanks for chatting with us today. Take care!"
        ],
        "quick_replies": ["Start new chat", "Store hours", "Pricing plans"]
    }
}



FALLBACK_LEVELS = [
    {
        "level": 1,
        "message": "I can help with Orders, Tech Support, Billing & Plans, or FAQs. For example, you can ask 'track package ORD-12345', 'device won't turn on', or 'pricing tiers'. What would you like assistance with?",
        "include_suggestions": True
    },
    {
        "level": 2,
        "message": "Here are the 4 main areas I cover:\n1. [Orders] Track or cancel shipments, returns & refunds\n2. [Tech] Power issues, Wi-Fi drops, crash errors\n3. [Billing] Subscriptions, invoices, payment cards\n4. [General] Support hours & live representative transfer\nType any of these keywords to get started!",
        "include_topics": True
    },
    {
        "level": 3,
        "message": "To get you specialized help right away, support ticket #{ticket_id} has been created for your request. You can also reach our customer support desk at 1-800-555-0199.",
        "include_escalation": True
    }
]

