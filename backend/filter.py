import re
import spacy
from transformers import pipeline

class RelevanceFilter:

    def __init__(self):
        
        # --- 1. Load spaCy (Chunking Engine) ---
        # Optimization: We disable 'ner' and 'tagger' to make splitting 100x faster.
        try:
            self.nlp = spacy.load(
                "en_core_web_sm",
                disable=["ner", "tagger", "lemmatizer", "attribute_ruler"]
            )
            # Ensure the sentencizer (sentence splitter) is active
            if "sentencizer" not in self.nlp.pipe_names:
                self.nlp.add_pipe("sentencizer")
        except Exception as e:
            self.nlp = None

        # --- 2. Load DistilBERT (AI Filter - Gate 2) ---
        # Optimization: CPU-friendly model loaded into RAM once.
        try:
            self.classifier = pipeline(
                "zero-shot-classification",
                model="valhalla/distilbart-mnli-12-1", 
                device= 0 # -1 for CPU, 0 for GPU
            )
        except Exception as e:
            self.classifier = None

        # --- 3. Define Ontology (The Source of Truth) ---
        self.ontology = {
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
        
        # --- 4. Build Reverse Index (Domain Lookup) ---
        self.keyword_to_domain = {}
        all_keywords = set()
        
        for domain, keywords in self.ontology.items():
            for kw in keywords:
                lower_kw = kw.lower()
                all_keywords.add(lower_kw)
                self.keyword_to_domain[lower_kw] = domain

        # --- 5. Build Optimized Regex (Gate 1) ---
        # Sort by length descending to match longer phrases first
        sorted_kws = sorted(list(all_keywords), key=len, reverse=True)
        # \b ensures we match "age" but not "page"
        pattern_str = r'\b(?:' + '|'.join(map(re.escape, sorted_kws)) + r')\b'
        self.ontology_regex = re.compile(pattern_str, re.IGNORECASE)

    def process_document(self, raw_text):
        if not self.nlp or not raw_text:
            return []

        # 1. Chunking (spaCy)
        doc = self.nlp(raw_text)
        
        valid_chunks = []
        
        # 2. Iterate over sentences
        for sent in doc.sents:
            text_chunk = sent.text.strip()
            
            if len(text_chunk) < 15:
                continue

            if "means" in text_chunk.lower(): # skip definitions
                continue

            keep, reason, domains = self._is_relevant(text_chunk)
            
            if keep:
                valid_chunks.append({
                    "text": text_chunk,
                    "metadata": {
                        "domains": domains,       # e.g., ['LIABILITY', 'DATA_SHARING']
                        "filter_reason": reason   # e.g., "Matched 'indemnify'"
                    }
                })
        
        return valid_chunks

    def _is_relevant(self, text):
        
        matches = self.ontology_regex.findall(text)
        if not matches:
            return False, "Dropped: No Ontology terms found", []

        # Map Keywords to Domains
        detected_domains = set()
        for m in matches:
            dom = self.keyword_to_domain.get(m.lower())
            if dom:
                detected_domains.add(dom)
        
        domain_list = list(detected_domains)

        # --- Gate 2: AI Classifier ---
        if self.classifier:
            try:
                # Truncate to 512 for speed & safety
                res = self.classifier(text[:512], candidate_labels=["legal clause", "irrelevant noise"])
                
                if res['labels'][0] == "irrelevant noise" and res['scores'][0] > 0.7:
                    return False, f"AI detected noise ({res['scores'][0]:.2f})", []
            except Exception:
                pass # Fail open (Keep text if AI fails)

        return True, f"Valid (Matched: {len(matches)} terms)", domain_list
