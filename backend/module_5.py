


import httpx
import json
import re

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


def extract_json(text: str) -> dict | None:
    """Try multiple strategies to extract valid JSON from LLM response."""
    
    # Strategy 1: Direct parse
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    
    # Strategy 2: Remove markdown code blocks
    cleaned = re.sub(r'^```(?:json)?\s*', '', text.strip())
    cleaned = re.sub(r'\s*```$', '', cleaned)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Strategy 3: Find JSON object between first { and last }
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    
    # Strategy 4: Fix common issues (trailing commas, single quotes)
    if match:
        fixed = match.group()
        # Remove trailing commas before } or ]
        fixed = re.sub(r',(\s*[}\]])', r'\1', fixed)
        # Replace single quotes with double quotes (risky but worth trying)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            pass
        
        # Try with single quote replacement
        fixed_quotes = fixed.replace("'", '"')
        try:
            return json.loads(fixed_quotes)
        except json.JSONDecodeError:
            pass
    
    # Strategy 5: Try to find and parse just the analysis array
    array_match = re.search(r'"analysis"\s*:\s*(\[.*?\])', text, re.DOTALL)
    summary_match = re.search(r'"summary"\s*:\s*"([^"]*)"', text)
    if array_match:
        try:
            analysis = json.loads(array_match.group(1))
            summary = summary_match.group(1) if summary_match else "Analysis complete."
            return {"analysis": analysis, "summary": summary}
        except json.JSONDecodeError:
            pass
    
    return None


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
            
            result = extract_json(raw_response)
            if result is not None:
                return result
            
            last_error = f"Failed to parse JSON from model response: {raw_response}"
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