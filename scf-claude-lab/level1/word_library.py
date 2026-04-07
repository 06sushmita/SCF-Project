# word_library.py

# Words that make a control vague (should be rejected)
VAGUE_WORDS = [
    "should", "may", "appropriate", "adequate",
    "ensure", "proper", "sufficient", "reasonable",
    "as needed", "where possible"
]

# Keywords used to determine risk impact
IMPACT_KEYWORDS = {
    "High": [
        "encrypt", "encryption", "sensitive", "confidential",
        "authentication", "access control", "customer data",
        "payment", "financial"
    ],

    "Medium": [
        "log", "monitor", "audit", "tracking", "review"
    ],

    "Low": []
}

# Control types
CONTROL_TYPE_KEYWORDS = {

    "Preventive": [
        "encrypt", "authentication", "access", "restrict",
        "password", "authorization"
    ],

    "Detective": [
        "monitor", "log", "audit", "detect", "alert"
    ],

    "Corrective": [
        "recover", "restore", "remediate", "backup"
    ]
}

# Frequency detection
FREQUENCY_KEYWORDS = {
    "Real-time": ["real-time", "continuous"],
    "Daily": ["daily"],
    "Weekly": ["weekly"],
    "Monthly": ["monthly"],
    "Quarterly": ["quarterly"],
    "Annually": ["annually", "yearly"]
}