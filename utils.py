import re
import json
from typing import Optional
from datetime import datetime
import tiktoken
import pdfplumber

TOOL_CALL_PATTERN = re.compile(r"Action: (.*?)\nAction Input: ({.*})", re.DOTALL)

FINAL_RESPONSE_PATTERN = re.compile(r"Final Answer: (.*)", re.DOTALL)


def parse_llm_response(response: str) -> Optional[dict]:
    tool_match = TOOL_CALL_PATTERN.search(response)
    if tool_match:
        action = tool_match.group(1).strip()
        if "(" in action:
            action = action[: action.index("(")]
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


def check_iso_format(date_time: str) -> bool:
    try:
        datetime.strptime(date_time, "%Y-%m-%dT%H:%M:%S")
        return True
    except ValueError:
        return False


def count_tokens(text: str) -> int:
    try:
        encoding = tiktoken.encoding_for_model("gpt-4o-mini")
        tokens = encoding.encode(text)
        return len(tokens)
    except Exception:
        return 0


def read_pdf(path: str) -> str:
    pdf_text = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            pdf_text.append(page.extract_text())
            pdf_text.append("\n")
    return "\n".join(pdf_text)
