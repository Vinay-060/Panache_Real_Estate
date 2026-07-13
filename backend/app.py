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

# Store complete conversation
conversation_memory = {}

# Avoid duplicate sheet rows
saved_users = set()


#################################################
# Helper Functions
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
# Telegram Commands
#################################################

async def start(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    conversation_memory[user_id] = ""

    if user_id in saved_users:
        saved_users.remove(user_id)

    await update.message.reply_text(
        "Hi 👋\n\n"
        "Welcome to Panache Homes.\n\n"
        "I'd love to understand your Dubai property goals.\n\n"
        "May I know your name?"
    )


#################################################
# Main Chat
#################################################

async def chat(
        update: Update,
        context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    text = update.message.text

    #################################################
    # Create memory
    #################################################

    if user_id not in conversation_memory:

        conversation_memory[user_id] = ""

    #################################################
    # Store message
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
    # Ask LLM
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
    # Extract Lead
    #################################################

    try:

        lead = extract_lead(
            conversation
        )

    except Exception as e:

        print("Extraction Error")

        print(e)

        return

    print("\nLEAD\n")

    print(lead)

    #################################################
    # Save only once
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