


import httpx
import json

SYSTEM_PROMPT = """You are a policy compliance analyst who is analysing the compliance of a Terms of Service or Privacy Policy document against actual laws given within the prompt. 

----
INPUT FORMAT: multiple sets of (id, TOS_Text, matched_law)

id: int
TOS_text: ...
Matched_law: ...

id: int
TOS_text: ...
Matched_law: ...
----
It uses this and assigns {"id": int, "violated": bool, "irrelevant": bool, "reason": "1 line str"}, for each item in the same order as it appears. len(law pairs) == len(output dicts)
CASES:
1. violated = true & irrelevant = false if law is violated by TOS.
2. violated = false & irrelevant = false if law is compliant to TOS. 
3. irrelevant = true & violated = false if matched_law and TOS_text are unrelated.
*** CRITICAL: "violated" and "irrelevant" CANNOT both be true. ***
----
OUTPUT: (needs to be valid JSON and no conversational text)

{
	"analysis": [
			{"id": int, "violated": bool, "irrelevant": bool, "reason": "1 line str"},
			{"id": int, "violated": bool, "irrelevant": bool, "reason": "1 line str"},
			...
	],
	"summary": "A very concise executive summary of the violations found."
}
----
"""

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL = "mistral:latest"

def generate_prompt(law_pairs: list[dict]) -> str:
    pairs_str = "INPUT:\n"
    for i, pair in enumerate(law_pairs):
        pairs_str += f"id: {i+1}\nTOS_text: {pair['TOS_text']}\nMatched_law: {pair['raw_law']}\n\n"
    return SYSTEM_PROMPT + pairs_str + "\nRemember: Output ONLY valid JSON."


def run_inference(law_pairs: list[dict], timeout: float = 150.0, max_retries: int = 1) -> dict:
    prompt = generate_prompt(law_pairs)
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 2048,
        }
    }
    
    last_error = None
    for attempt in range(max_retries + 1):
        try:
            with httpx.Client(timeout=timeout) as client:
                resp = client.post(OLLAMA_URL, json=payload)
                resp.raise_for_status()
                data = resp.json()
            
            raw_response = data.get("response", "")
            
            try:
                result = json.loads(raw_response)
                return result
            except json.JSONDecodeError:
                last_error = f"Failed to parse JSON from model response: {raw_response[:200]}"
                if attempt < max_retries:
                    continue
                return {"raw": raw_response, "error": last_error}
        
        except httpx.ConnectError:
            last_error = "Ollama server not reachable (connection refused)"
        except httpx.TimeoutException:
            last_error = f"Ollama request timed out after {timeout}s"
        except httpx.HTTPStatusError as e:
            last_error = f"Ollama HTTP error: {e.response.status_code}"
        except Exception as e:
            last_error = f"Unexpected error: {str(e)}"
        
        if attempt < max_retries:
            continue
    
    return {"error": last_error}


if __name__ == "__main__":
    pass