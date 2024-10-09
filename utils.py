import re
import json
from typing import Optional

TOOL_CALL_PATTERN = re.compile(r"Action: (.*?)\nAction Input: ({.*})", re.DOTALL)

FINAL_RESPONSE_PATTERN = re.compile(r"Final Answer: (.*)", re.DOTALL)


def parse_llm_response(response: str) -> Optional[dict]:
    tool_match = TOOL_CALL_PATTERN.search(response)
    if tool_match:
        action = tool_match.group(1).strip()
        action_input = tool_match.group(2).strip()
        try:
            action_input_dict = json.loads(action_input)
            return {
                "type": "tool",
                "action": action,
                "action_input": action_input_dict,
            }
        except json.JSONDecodeError:
            print("JSON DECODING ERROR")
            return None

    response_match = FINAL_RESPONSE_PATTERN.search(response)
    if response_match:
        final_answer = response_match.group(1).strip()
        return {"type": "response", "response": final_answer}

    return None