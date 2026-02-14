import json
import re
import ast

def parse_llm_output(content: str, expected_type: str = "json"):
    """
    Parses LLM output content into a structured format (dict or list).
    
    Args:
        content (str): The raw string output from the LLM.
        expected_type (str): "json" for JSON objects/lists, "list" for Python literal lists.
        
    Returns:
        The parsed object (dict or list).
        
    Raises:
        ValueError: If parsing fails.
    """
    content = content.strip()
    
    try:
        # standard markdown code block cleanup
        if "```" in content:
            # Extract content inside the first code block
            pattern = r"```(?:json|python)?\s*(.*?)```"
            match = re.search(pattern, content, re.DOTALL)
            if match:
                content = match.group(1).strip()
            else:
                # Fallback: just remove the backticks if regex fails for some reason
                content = content.replace("```json", "").replace("```python", "").replace("```", "").strip()

        if expected_type == "json":
            return json.loads(content)
            
        elif expected_type == "list":
            # For Python literal lists like ['a', 'b']
            parsed = ast.literal_eval(content)
            if not isinstance(parsed, list):
                raise ValueError("Parsed content is not a list")
            return parsed
            
        else:
            raise ValueError(f"Unknown expected_type: {expected_type}")
            
    except Exception as e:
        print(f"❌ Error parsing LLM output: {e}")
        print(f"Raw content was: {content[:100]}...") # Print preview
        raise e
