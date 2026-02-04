"""Utility functions for agents"""
import re
import json
from typing import Union


def extract_json(text: str) -> Union[dict, list]:
    """
    Extract JSON from any LLM response format.
    Handles: ```json ... ```, ``` ... ```, or raw JSON
    """
    if not text:
        return {}
    
    # Remove markdown code blocks
    # Pattern 1: ```json ... ```
    text = re.sub(r'```json\s*', '', text)
    # Pattern 2: ``` ... ```
    text = re.sub(r'```\s*', '', text)
    # Clean up
    text = text.strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON array or object in the text
        patterns = [
            r'\[[\s\S]*\]',  # Array
            r'\{[\s\S]*\}',  # Object
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    continue
        
        # Return empty if nothing works
        return {"error": "Could not parse JSON", "raw": text}
