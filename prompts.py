from langchain.prompts import PromptTemplate

CLASSIFY_PROMPT = f"""
Your task is to classify the user's prompt so it can be sent to different AI agents.
There are four categories: EMAIL, CALENDAR, SEARCH, and CHAT.

If the prompt has to do with emails output "EMAIL".
If the prompt has to do with scheduling meetings or calendar events output "CALENDAR".
If the prompt has to do with searching the internet or an LLM would need to search the internet to answer the prompt, output "SEARCH".
If the prompt could simply be answered by an LLM or has to do with anything else, output "CHAT".

Respond with only the category and no other text.

{{prompt}}
"""

GET_RECIPIENT_EMAIL_PROMPT = f"""
You are an AI email assistant. Your task is to tell whether the user's prompt contains a valid email address to send to.

If the prompt contains a valid email address to send to, output the email address.
If the prompt does not contain a valid email address to send to, output INVALID.

For example:
user: "Send an email to john@doe.com asking him about his availability next week."
assistant: "john@doe.com"

user: "Send an email to John asking him about his availability next week."
assistant: "INVALID"

Respond with only the email address or INVALID and no other text.

{{prompt}}
"""

GET_RECIPIENT_EMAIL_PROMPT = f"""
Your task is to come up with a prompt for a text field so the user can input the email address they want to send to.

For example:
user: "Send an email to John asking him about his availability next week."
assistant: "Sure, can you please provide John's email address?"

Respond with only the prompt and no other text.

{{prompt}}
"""

EMAIL_DRAFT_PROMPT = f"""
You are an AI email assistant. Your task is to create a draft email based on the user's request.

Respond with a valid JSON object with the following structure:
"recipient": <email address to send to>,
"subject": <email subject>,
"body": <body of the email>

{{prompt}}
"""