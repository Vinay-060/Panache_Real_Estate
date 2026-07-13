import os
import cohere

from dotenv import load_dotenv

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

from extractor import extract_lead
from grading import calculate_grade
from automation import send_to_n8n
from prompts import SYSTEM_PROMPT
from knowledge import KNOWLEDGE

load_dotenv()

co = cohere.ClientV2(
    api_key=os.getenv(
        "COHERE_API_KEY"
    )
)

conversation_memory = {}

lead_memory = {}

saved_users = set()


def should_save_lead(lead):

    fields = [

        lead["name"],
        lead["country"],
        lead["budget"],
        lead["funding"],
        lead["timeline"],
        lead["purpose"]
    ]

    filled = sum(
        x is not None
        for x in fields
    )

    return filled >= 4


def ask_llm(conversation):

    knowledge_text = "\n".join(

        f"{k}: {v}"

        for k, v in KNOWLEDGE.items()
    )

    response = co.chat(

        model="command-a-03-2025",

        messages=[

            {
                "role": "system",
                "content":

                    SYSTEM_PROMPT
                    + "\n\nKnowledge Base:\n"
                    + knowledge_text
            },

            {
                "role": "user",
                "content": conversation
            }
        ]
    )

    return (
        response
        .message
        .content[0]
        .text
    )


async def start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    conversation_memory[user_id] = ""

    lead_memory[user_id] = {

        "name": None,
        "country": None,
        "budget": None,
        "funding": None,
        "timeline": None,
        "purpose": None
    }

    saved_users.discard(
        user_id
    )

    await update.message.reply_text(

        "Hello 👋\n\n"
        "Welcome to Panache Homes.\n\n"
        "How may I assist you today regarding Dubai real estate opportunities?"
    )


async def chat(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    text = (
        update.message.text
        .strip()
    )

    if user_id not in conversation_memory:

        conversation_memory[user_id] = ""

    if user_id not in lead_memory:

        lead_memory[user_id] = {

            "name": None,
            "country": None,
            "budget": None,
            "funding": None,
            "timeline": None,
            "purpose": None
        }

    #################################################
    # Store current user's conversation
    #################################################

    conversation_memory[user_id] += (

        f"\nUser: {text}"
    )

    conversation = (
        conversation_memory[user_id]
    )

    #################################################
    # Extract latest data
    #################################################

    extracted = extract_lead(
        conversation
    )

    #################################################
    # Merge data
    #################################################

    for k, v in extracted.items():

        if v is not None:

            lead_memory[user_id][k] = v

    lead = (
        lead_memory[user_id]
    )

    print("\nCURRENT LEAD\n")
    print(lead)

    #################################################
    # Ask assistant
    #################################################

    reply = ask_llm(
        conversation
    )

    conversation_memory[user_id] += (

        f"\nAssistant: {reply}"
    )

    await update.message.reply_text(
        reply
    )

    #################################################
    # Save once
    #################################################

    if (

        user_id not in saved_users

        and

        should_save_lead(
            lead
        )
    ):

        lead["grade"] = (
            calculate_grade(
                lead
            )
        )

        print("\nFINAL LEAD\n")
        print(lead)

        try:

            send_to_n8n(
                lead
            )

            saved_users.add(
                user_id
            )

            print(
                "Lead Saved"
            )

        except Exception as e:

            print(
                "n8n Error"
            )

            print(e)

    #################################################
    # End conversation
    #################################################

    if text.lower() in [

        "bye",
        "thank you",
        "thanks",
        "no thanks"
    ]:

        conversation_memory.pop(
            user_id,
            None
        )

        lead_memory.pop(
            user_id,
            None
        )

        saved_users.discard(
            user_id
        )
