from module_3_4 import find_violations
from module_5 import generate_prompt
import json, time

if __name__ == "__main__":
    tos_1 = "If a transfer of any Customer Data from Salesforce to Supplier occurs in connection with the Licensed Software then, notwithstanding anything to the contrary, Section 3(v) of these Software Terms shall apply."
    tos_2 = "Supplier will deliver the most current version of the Licensed Software to Salesforce via electronic delivery or load-and-leave services, and will not deliver tangible materials to Salesforce without Salesforce’s advance written consent"

    input_sentences = [tos_1, tos_2]

    t1 = time.time()
    
    # Run the full pipeline
    accepted_matches = find_violations(input_sentences)
    
    t2 = time.time()
    
    print(f"Total Pipeline Time: {t2 - t1:.4f} seconds")
    print(f"Accepted Matches: {len(accepted_matches)}")
    
    print(json.dumps(accepted_matches, indent=2))

    # Generate prompt for LLM
    prompt = generate_prompt(accepted_matches)
    print("\nGenerated Prompt for LLM:")
    print(prompt)