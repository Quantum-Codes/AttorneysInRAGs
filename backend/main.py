from module_2 import RelevanceFilter
from module_3_4 import find_violations
from module_5 import run_inference
import json, time

legal_filter = RelevanceFilter()

def pipeline(text: str) -> dict:
    """Run full analysis pipeline. Returns dict with 'success' flag and 'data' or 'error'."""
    try:
        start = time.time()
        clean_chunks = legal_filter.process_document(text)
        
        print(f"Done in {time.time() - start:.2f}s")
        print(f"Extracted {len(clean_chunks)} valid legal clauses.")
        
        if not clean_chunks:
            return {"success": False, "error": "No valid legal clauses found"}

        t1 = time.time()
        accepted_matches = find_violations(clean_chunks)
        t2 = time.time()
        
        print(f"Total Pipeline Time: {t2 - t1:.4f} seconds")
        print(f"Accepted Matches: {len(accepted_matches)}")
        
        if not accepted_matches:
            return {"success": True, "data": None, "message": "No potential violations found"}
        
        print(json.dumps(accepted_matches, indent=2))
        
        result = run_inference(accepted_matches)
        
        if "error" in result:
            print(f"Inference error: {result['error']}")
            return {"success": False, "error": result["error"]}
        
        print(result)
        return {"success": True, "data": result, "matches": accepted_matches}
    
    except Exception as e:
        print(f"Pipeline error: {e}")
        return {"success": False, "error": str(e)}


if __name__ == "__main__":
    from pathlib import Path
    
    text_file = Path(__file__).parent / "text.txt"
    with open(text_file, "r") as f:
        raw_text = f.read()
    
    print("=" * 60)
    print("RUNNING PIPELINE TEST")
    print("=" * 60)
    
    t_start = time.time()
    result = pipeline(raw_text)
    t_end = time.time()
    
    print("\n" + "=" * 60)
    print(f"TOTAL TIME: {t_end - t_start:.2f}s")
    print(f"SUCCESS: {result.get('success')}")
    if result.get("error"):
        print(f"ERROR: {result.get('error')}")
    print("=" * 60)
    print(json.dumps(result, indent=2))