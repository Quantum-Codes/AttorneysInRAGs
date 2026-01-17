# THIS IS NOT SVO. BUT THIS REMOVES STOPWORDS AND REPEATS FOR THE COSINE SIMILARITY CALCULATION
# THIS IS ACCEPTABLE

import spacy, time

nlp = spacy.load("en_core_web_sm")

# Words that change legal meaning - NEVER remove these
LEGAL_OPERATORS = {"not", "no", "never", "only", "unless", "except", "if", "then"}

def legal_distill_v2(text):
    doc = nlp(text)
    clean_tokens = []
    
    for token in doc:
        # Keep Numbers (for retention logic), Nouns, and Verbs
        if token.pos_ in ["NOUN", "PROPN", "VERB", "NUM"] or token.text.lower() in LEGAL_OPERATORS:
            if token.lemma_.lower() not in ["be", "have", "occur", "apply"]:
                clean_tokens.append(token.lemma_.lower())
    
    # Deduplicate while preserving order
    seen = set()
    final_tokens = []
    for t in clean_tokens:
        if t in LEGAL_OPERATORS or t not in seen:
            final_tokens.append(t)
            seen.add(t)
            
    return " ".join(final_tokens)

# --- TEST ---
tos_1 = "If a transfer of any Customer Data from Salesforce to Supplier occurs in connection with the Licensed Software then, notwithstanding anything to the contrary, Section 3(v) of these Software Terms shall apply."
tos_2 = "Supplier will deliver the most current version of the Licensed Software to Salesforce via electronic delivery or load-and-leave services, and will not deliver tangible materials to Salesforce without Salesforce’s advance written consent"

t1 = time.time()
print(f"Distilled 1: {legal_distill_v2(tos_1)}")
print(f"Distilled 2: {legal_distill_v2(tos_2)}")
print(f"Time taken: {time.time() - t1} seconds")

"""
OUT:
Distilled 1: if transfer customer data salesforce supplier connection licensed software then contrary section 3(v term
Distilled 2: supplier deliver version licensed software salesforce delivery load leave service not material advance write consent
Time taken: 0.012683868408203125 seconds
"""

{
    "summary": "heheheha",
    "safety_score": 0.98,
    "violations": [
        {
            "violating_rule": "FROM TOS",
            "actual_rule": "FROM ACTUAL POLICY DOCS",
            "source": "WHAT PART OF THE DOC IT CAME FROM + WHICH DOC: '[cite: xxx] IT act'",
        }
    ]
}