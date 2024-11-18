import chainlit as cl
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.chat_history import (
    BaseChatMessageHistory,
    InMemoryChatMessageHistory,
)
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from utils import parse_llm_response, read_pdf
from tools import (
    Email,
    Search,
    CreateEvent,
    ReadCalendar,
    DeleteEvent,
    GetDate,
)
from prompts import get_system_prompt
from langchain_openai import ChatOpenAI
from rag import rag_pipeline

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
    messages[-1].content += f"\nObservation: {tool_text}"
    await store[session_id].aadd_messages(messages)


load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")

tools = [
    Email(),
    Search(),
    CreateEvent(),
    ReadCalendar(),
    DeleteEvent(),
    GetDate(),
]

name_to_tool = {tool.name: tool for tool in tools}
SYSTEM_PROMPT = get_system_prompt(tools)


@cl.set_chat_profiles
async def chat_profile():
    return [cl.ChatProfile(name="Assistant", markdown_description="")]


@cl.on_chat_start
async def on_chat_start():
    prompt = ChatPromptTemplate.from_messages(
        [
            SystemMessage(content=SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="messages"),
        ]
    )
    runnable = prompt | model | StrOutputParser()
    with_message_history = RunnableWithMessageHistory(runnable, get_session_history)
    cl.user_session.set("runnable", with_message_history)


@cl.on_message
async def on_message(message: cl.Message):
    try:
        pdf_text = []
        if message.elements:
            for el in message.elements:
                pdf_text.append(read_pdf(el.path))

            pdf_text = "".join(pdf_text)
            pdf_text = await rag_pipeline(pdf_text, message.content)

        runnable = cl.user_session.get("runnable")
        action = None
        attempts = 0
        prompt = message.content

        if pdf_text:
            prompt = pdf_text + "\n\n" + message.content

        while (
            not action or (action and action["type"] == "tool")
        ) and attempts < MAX_ATTEMPTS:
            if attempts == 0:
                llm_response = await runnable.ainvoke(
                    input={"messages": [HumanMessage(content=prompt)]},
                    config={"configurable": {"session_id": cl.user_session.get("id")}},
                )
                attempts += 1
            else:
                llm_response = await runnable.ainvoke(
                    [],
                    config={"configurable": {"session_id": cl.user_session.get("id")}},
                )
            action = parse_llm_response(llm_response)
            if not action:
                attempts += 1
                await remove_last_message(
                    cl.user_session.get("id")
                )  # if LLM didn't provide valid input remove that message from the history
                continue
            attempts = 1
            if action["type"] == "tool":
                res = name_to_tool[action["action"]].run(**action["action_input"])
                await add_tool_result(cl.user_session.get("id"), res)
            elif action["type"] == "response":
                await cl.Message(content=action["response"]).send()
            else:
                await cl.Message(
                    content="I had an internal error, im sorry please try again."
                ).send()
    except Exception:
        await cl.Message(
            content="I had an internal error, im sorry please try again."
        ).send()
