ONTOLOGY = {
    "DATA_COLLECTION": [
        "collect", "obtain", "gather", "process", "harvest", "record", 
        "capture", "track", "monitor", "log", "observe", "acquire", 
        "receive", "store", "cookies", "pixels", "beacons", "fingerprint",
        "telemetry", "analytics", "input", "submission", "automated", "profiling"
    ],
    "DATA_RETENTION": [
        "retain", "retention", "store", "storage", "keep", "archive", 
        "preserve", "maintain", "hold", "duration", "period", "timeline",
        "deletion", "purge", "erase", "disposal", "record keeping",
        "life cycle", "expiry", "rolling period"
    ],
    "DATA_SHARING": [
        "share", "transfer", "disclose", "disclosure", "distribute", 
        "transmit", "exchange", "third party", "partner", "vendor", 
        "affiliate", "subsidiary", "processor", "service provider", 
        "outsource", "cross-border", "international transfer", "recipient",
        "sell", "rent", "monetize", "broker", "joint venture"
    ],
    "CONSENT": [
        "consent", "agree", "agreement", "permission", "permit", 
        "allow", "authorization", "opt-in", "opt-out", "subscribe", 
        "acknowledge", "accept", "assent", "voluntary", "withdraw", 
        "revoke", "choice", "preference", "affirmative action", "unconditional"
    ],
    "SECURITY_PRACTICES": [
        "security", "secure", "safeguard", "protect", "protection", 
        "encryption", "encrypted", "cryptography", "firewall", "hashing", 
        "salt", "access control", "authentication", "authorization", 
        "integrity", "confidentiality", "ISO", "ISO 27001", "SOC2", 
        "audit", "vulnerability", "patch", "ssl", "tls", "https", 
        "physical security", "technical measures", "organizational measures"
    ],
    "BREACH_RESPONSE": [
        "breach", "incident", "compromise", "hack", "leak", "loss", 
        "unauthorized access", "report", "notify", "notification", 
        "alert", "inform", "mitigate", "remedy", "CERT-In", "CSIRT", 
        "response team", "root cause analysis", "forensic", "Data Protection Board",
        "6 hours"
    ],
    "USER_RIGHTS": [
        "right to", "access", "rectify", "correction", "correct", 
        "update", "modify", "delete", "erasure", "forget", "withdraw", 
        "portability", "download", "copy", "review", "restrict", 
        "object", "nominate", "nominee", "representative", "summary"
    ],
    "GRIEVANCE": [
        "grievance", "complaint", "concern", "dispute", "redressal", 
        "officer", "nodal", "contact", "support", "helpdesk", "ombudsman", 
        "resolution", "ticket", "escalation", "email", "address", 
        "phone", "feedback", "15 days", "24 hours"
    ],
    "POLICY_CHANGES": [
        "change", "update", "modify", "amend", "alter", "revise", 
        "revision", "version", "effective date", "notification", 
        "notice", "inform", "alert", "post", "publish", "discretion"
    ],
    "LIABILITY": [
        "liability", "liable", "responsible", "responsibility", 
        "indemnify", "indemnity", "guarantee", "warranty", "warrant", 
        "damages", "loss", "risk", "disclaimer", "limitation", 
        "exclude", "hold harmless"
    ],
    "INTERMEDIARY_DUTIES": [
        "intermediary", "content", "upload", "publish", "host", 
        "transmit", "remove", "takedown", "disable", "block", 
        "due diligence", "rules", "regulations", "unlawful", 
        "prohibited", "court order", "agency", "law enforcement",
        "Chief Compliance Officer", "Nodal Contact Person"
    ],
    "SENSITIVE_DATA": [
        "sensitive", "spdi", "financial", "bank", "credit card", 
        "payment", "password", "biometric", "physical", "physiological", 
        "mental health", "medical", "records", "history", "sexual", 
        "orientation", "caste", "tribe", "religious", "political",
        "transgender status", "intersex status"
    ],
    "CHILDREN_DATA": [
        "child", "children", "minor", "under 18", "age", "parent", 
        "parental", "guardian", "verifiable", "verification", 
        "detrimental", "well-being", "tracking", "monitoring",
        "targeted advertising", "behavioral monitoring"
    ],
    "LOGGING_AUDIT": [
        "log", "logging", "audit trail", "system event", "timestamp", 
        "NTP", "synchronized", "rolling", "period", "network", 
        "traffic", "IP address", "access log", "ICT logs", "180 days"
    ]
}

def map_ontology(clause_text: str):
    tags = []
    lower = clause_text.lower()

    for tag, keywords in ONTOLOGY.items():
        if any(k in lower for k in keywords):
            tags.append(tag)

    return tags
