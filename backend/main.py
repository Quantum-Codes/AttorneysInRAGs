from module_2 import RelevanceFilter
from module_3_4 import find_violations
from module_5 import generate_prompt
import json, time

legal_filter = RelevanceFilter()

if __name__ == "__main__":
    with open("backend/text.txt", "r") as f:
        raw_pdf_text = f.read()

    start = time.time()
    clean_chunks = legal_filter.process_document(raw_pdf_text)
    
    print(f"Done in {time.time() - start:.2f}s")
    print(f"Extracted {len(clean_chunks)} valid legal clauses.")
    
    # # --- 4. OUTPUT ---
    # # clean_chunks is now ready for your Vector DB
    # for chunk in clean_chunks[:3]:
    #     print(f"\n[DOMAINS: {chunk['metadata']['domains']}]")
    #     print(chunk['text'])

    t1 = time.time()
    
    # Run the full pipeline
    accepted_matches = find_violations(clean_chunks)
    
    t2 = time.time()
    
    print(f"Total Pipeline Time: {t2 - t1:.4f} seconds")
    print(f"Accepted Matches: {len(accepted_matches)}")
    
    print(json.dumps(accepted_matches, indent=2))
    print(accepted_matches, "\n\n\n\n")
    # Generate prompt for LLM
    prompt = generate_prompt(accepted_matches)
    print("\nGenerated Prompt for LLM:")
    print(prompt)