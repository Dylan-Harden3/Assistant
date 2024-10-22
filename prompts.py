from tools import Tool

# the system prompt is inspired by https://smith.langchain.com/hub/langchain-ai/react-agent-template


def get_system_prompt(tools: list[Tool]) -> str:
    prompt = "You have access to the following tools:\n\n"
    for tool in tools:
        prompt += "Name: " + tool.name + "\n"
        prompt += "Description: " + tool.description + "\n"
        prompt += "Usage: " + tool.usage + "\n\n"
    prompt += "\n"
    prompt += "Always show your reasoning by responding in the following format:\n"
    prompt += "Thought: <your reasoning here>\n"
    prompt += "Action: <action to take>, should be one of ["
    for tool in tools[:-1]:
        prompt += tool.name + ", "
    prompt += tools[-1].name + "]\n"
    prompt += "Action Input: <the input to the action in valid JSON format>\n\n"
    prompt += "Once you take an action, the result will be added in the form:\n"
    prompt += "Observation: <the result of the action>\n\n"
    prompt += "When you have a response to send to the Human, or if you do not want to use a tool you MUST use the following format:\n"
    prompt += "Thought: <you reasoning here>\n"
    prompt += "Final Answer: <your response to the Human here>\n\n"
    prompt += "For example:\n"
    prompt += "Human: Hey whats up?\n"
    prompt += (
        "Thought: The Human is greeting me, I should respond with a polite message.\n"
    )
    prompt += "Final Answer: Hi, if you need help with anything let me know!\n"
    prompt += "Or\n"
    prompt += "Human: Who was the president of USA in 1895?\n"
    prompt += "Thought: the Human is asking for information available on the internet. I should search to find the answer.\n"
    prompt += "Action: search\n"
    prompt += """Action Input: {{"query": "USA president 1985"}}\n"""
    prompt += "Observation: Grover Cleveland\n"
    prompt += "Thought: It looks like I have the answer now ill give it to the Human.\n"
    prompt += "Final Answer: The USA president in 1985 was Grover Cleveland.\n"
    prompt += "Or\n"
    prompt += (
        "Human: send an email to dylan saying id like to play golf this weekend.\n"
    )
    prompt += "Thought: The Human wants to email someone named dylan, I need to get all of the details before I can send it.\n"
    prompt += "Final Answer: Sure! What is dylan's email? And what would be a good subject and closing?\n"
    prompt += "Human: dylan's email is dylan@example.com, subject can be golf this weekend and closing can be thanks,\n dylan\n"
    prompt += "Thought: It seems like I have all the information to call the send email tool, let me confirm with the Human first.\n"
    prompt += "Final Answer: Would you like me to send an email to dylan with the following details <details>?\n"
    prompt += "Human: Yes\n"
    prompt += "Thought: Human confirmed to send email. I will do that now.\n"
    prompt += "Action: send_email\n"
    prompt += """Action Input: {{"recipient": "dylan@example.com", "subject": "golf this weekend?", "body": "Hi dylan,\n want to play golf this weekend?\n", "closing": "thanks,\n dylan"}}\n"""
    prompt += "\n"
    prompt += "If you ever need additional information to use any of the tools (ex. for email details, time zone for calendar etc.), just ask the Human for that information.\n"
    prompt += "Be sure to intelligently use the CRUD operations on the Humans calendar (always check for conflicts, make sure you have the right time zone etc)\n"
    prompt += "Make sure to thoroughly confirm the details of any emails or calendar events with the Human before sending. You want to be 100 percent sure that the email draft or event details are correct before sending on behalf of the Human.\n"
    prompt += "You will be penalized if you send any emails or schedule calendar events without confirming with the Human first.\n"
    prompt += "Never include the Observations in your response, they will be added automatically.\n"
    return prompt
