from typing import Dict, Optional
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import BaseChatMessageHistory, InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage
from prompts import SYSTEM_PROMPT
from typing import cast
from langchain.schema.runnable import Runnable
from utils import parse_llm_response
from tools import EmailTool

MAX_ATTEMPTS = 3
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

async def remove_last_message(session_id: str):
    if session_id not in store:
        return
    messages = await store[session_id].aget_messages()
    store[session_id].clear()
    if type(messages[-1]) is AIMessage:
        messages = messages[:-1]
    await store[session_id].aadd_messages(messages)

async def add_tool_result(session_id: str, tool_text: str):
    if session_id not in store:
        return

    messages = await store[session_id].aget_messages()
    if type(messages[-1]) is not AIMessage:
        return

    store[session_id].clear()
    messages[-1].content += f"\nTool Result: {tool_text}"
    await store[session_id].aadd_messages(messages)

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")
tools = {
    "send_email": EmailTool()
}

@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    return default_user


@cl.on_chat_start
async def on_chat_start():
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), MessagesPlaceholder(variable_name="messages")]
    )
    runnable = prompt | model | StrOutputParser()
    with_message_history = RunnableWithMessageHistory(runnable, get_session_history)
    cl.user_session.set("runnable", with_message_history)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(Runnable, cl.user_session.get("runnable"))
    action = None
    attempts = 0
    while (not action or (action and action["type"] == "tool")) and attempts < MAX_ATTEMPTS:
        attempts += 1
        llm_response = await runnable.ainvoke([HumanMessage(content=message.content)], config={"configurable": {"session_id": cl.user_session.get("id")}})
        print(llm_response)
        action = parse_llm_response(llm_response)
        if not action:
            await remove_last_message(cl.user_session.get("id")) # if it didnt provide valid input remove that message from the history
            continue
        if action["type"] == "tool":
            res = tools[action["action"]].run(**action["action_input"])
            # TODO add tool result to llm message
        elif action["type"] == "response":
            await cl.Message(content=action["response"]).send()

    if not action:
        await cl.Message(
            content="I had an internal error, im sorry please try again."
        ).send()
