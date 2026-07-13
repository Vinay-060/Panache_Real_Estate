import os

from dotenv import load_dotenv
import cohere

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
saved_users = set()


#################################################
# Save Condition
#################################################

def should_save_lead(lead):

    fields = [

        lead.get("name"),
        lead.get("country"),
        lead.get("budget"),
        lead.get("funding"),
        lead.get("timeline"),
        lead.get("purpose")
    ]

    filled = sum(
        x is not None
        for x in fields
    )

    return filled >= 4


#################################################
# LLM Response
#################################################

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


#################################################
# Start
#################################################

async def start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    conversation_memory[user_id] = ""

    saved_users.discard(
        user_id
    )

    await update.message.reply_text(

        "Hello 👋\n\n"
        "Welcome to Panache Homes.\n\n"
        "How may I assist you today regarding Dubai real estate opportunities?"
    )


#################################################
# Main Chat
#################################################

async def chat(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    text = (
        update.message.text
        .strip()
    )

    #################################################
    # Create User Memory
    #################################################

    if user_id not in conversation_memory:

        conversation_memory[user_id] = ""

    #################################################
    # Greetings
    #################################################

    if (

        text.lower()

        in [

            "hi",
            "hello",
            "hey",
            "hii"
        ]

        and

        conversation_memory[user_id] == ""
    ):

        await update.message.reply_text(

            "Hello 👋\n\n"
            "Welcome to Panache Homes.\n\n"
            "How may I assist you today regarding Dubai real estate opportunities?"
        )

        return

    #################################################
    # Store Message
    #################################################

    conversation_memory[user_id] += (

        f"\nUser: {text}"
    )

    conversation = (
        conversation_memory[user_id]
    )

    print("\nCONVERSATION\n")
    print(conversation)

    #################################################
    # Recent Messages Only
    #################################################

    recent_conversation = "\n".join(

        conversation
        .split("\n")[-10:]
    )

    #################################################
    # Extract Lead
    #################################################

    try:

        lead = extract_lead(
            recent_conversation
        )

    except Exception as e:

        print(
            "Extraction Error"
        )

        print(e)

        lead = {

            "name": None,
            "country": None,
            "budget": None,
            "funding": None,
            "timeline": None,
            "purpose": None
        }

    print("\nLEAD\n")
    print(lead)

    #################################################
    # Ask LLM
    #################################################

    reply = ask_llm(
        recent_conversation
    )

    conversation_memory[user_id] += (

        f"\nAssistant: {reply}"
    )

    await update.message.reply_text(
        reply
    )

    #################################################
    # Save Lead
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

        print(
            "\nFINAL LEAD\n"
        )

        print(lead)

        try:

            send_to_n8n(
                lead
            )

            saved_users.add(
                user_id
            )

            #################################################
            # Clear Conversation
            #################################################

            conversation_memory.pop(

                user_id,
                None
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
    # End Conversation
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

        saved_users.discard(
            user_id
        )


#################################################
# Main
#################################################

if __name__ == "__main__":

    app = (

        ApplicationBuilder()

        .token(
            os.getenv(
                "TELEGRAM_BOT_TOKEN"
            )
        )

        .build()
    )

    app.add_handler(

        CommandHandler(
            "start",
            start
        )
    )

    app.add_handler(

        MessageHandler(
            filters.TEXT,
            chat
        )
    )

    print(
        "Bot Running..."
    )

    app.run_polling()
