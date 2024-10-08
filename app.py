from typing import Dict, Optional
import chainlit as cl
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from prompts import SYSTEM_PROMPT
from typing import cast
from langchain.schema.runnable import Runnable
from utils import parse_llm_response

load_dotenv()

model = ChatOpenAI(model="gpt-4o-mini")


@cl.oauth_callback
def oauth_callback(
    provider_id: str,
    token: str,
    raw_user_data: Dict[str, str],
    default_user: cl.User,
) -> Optional[cl.User]:
    # cl.user_session.set("token", token)
    return default_user


@cl.on_chat_start
async def on_chat_start():
    prompt = ChatPromptTemplate.from_messages(
        [("system", SYSTEM_PROMPT), ("user", "{question}")]
    )
    runnable = prompt | model | StrOutputParser()
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(Runnable, cl.user_session.get("runnable"))

    action = None
    while not action or (action and action["type"] == "tool"):
        llm_response = await runnable.ainvoke({"question": message.content})

        action = parse_llm_response(llm_response)
        if action["type"] == "tool":
            if (
                action["action"] == "ask_user"
            ):  # asking user is special, chainlit requires this functionality to be in the @cl.on_message decorated
                if "question" not in action["action_input"]:
                    action = None
                    break
                user_response = await cl.AskUserMessage(
                    content=action["action_input"]["question"], timeout=1000
                ).send()
                # TODO make it so we store the conversation and can add user_response to the history
            else:
                # TODO make an agnostic way to run tools
                pass
        elif action["type"] == "response":
            await cl.Message(content=action["response"]).send()
            break
            # TODO add this to history as well

    if not action:
        await cl.Message(
            content="I had an internal error, im sorry please try again."
        ).send()
