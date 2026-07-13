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


#################################################
# LLM
#################################################

def ask_llm(conversation):

    knowledge = "\n".join(

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
                    + "\n\nKnowledge:\n"
                    + knowledge
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
# Save condition
#################################################

def should_save_lead(lead):

    fields = [

        lead["name"],
        lead["country"],
        lead["budget"],
        lead["funding"],
        lead["timeline"],
        lead["purpose"]
    ]

    return sum(
        x is not None
        for x in fields
    ) >= 4


#################################################
# Missing Question
#################################################

def get_next_question(lead):

    if not lead["name"]:

        return "May I know your name?"

    if not lead["country"]:

        return (
            f"Thank you, {lead['name']} 😊\n\n"
            "Which country are you currently residing in?"
        )

    if not lead["budget"]:

        return (
            "Do you have an investment "
            "budget range in mind (AED)?"
        )

    if not lead["funding"]:

        return (
            "Will this purchase be through "
            "Cash or Mortgage financing?"
        )

    if not lead["timeline"]:

        return (
            "What is your expected "
            "purchase timeline?"
        )

    if not lead["purpose"]:

        return (
            "Will this property be for "
            "Investment or Personal Use?"
        )

    return None


#################################################
# START
#################################################

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
        "How may I assist you "
        "regarding Dubai real estate?"
    )


#################################################
# CHAT
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
    # Greetings
    #################################################

    greetings = [

        "hi",
        "hello",
        "hey",
        "good morning"
    ]

    if (

        text.lower()

        in greetings

        and

        conversation_memory[user_id]
        == ""

    ):

        await update.message.reply_text(

            "Hello 👋\n\n"
            "Welcome to Panache Homes.\n\n"
            "How may I assist you today?"
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
    # Extract
    #################################################

    extracted = extract_lead(
        conversation
    )

    #################################################
    # Merge
    #################################################

    for k, v in extracted.items():

        if v is not None:

            lead_memory[user_id][k] = v

    lead = (
        lead_memory[user_id]
    )

    print("\nLEAD\n")
    print(lead)

    #################################################
    # Ask Missing Questions
    #################################################

    next_question = (
        get_next_question(
            lead
        )
    )

    if next_question:

        reply = next_question

    else:

        #################################################
        # Knowledge phase
        #################################################

        reply = ask_llm(
            conversation
        )

    #################################################

    conversation_memory[user_id] += (

        f"\nAssistant: {reply}"
    )

    await update.message.reply_text(
        reply
    )

    #################################################
    # Save
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

        print("\nFINAL\n")
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

            print(e)

    #################################################
    # End conversation
    #################################################

    if text.lower() in [

        "thank you",
        "thanks",
        "bye",
        "no thanks"
    ]:

        await update.message.reply_text(

            "Thank you for contacting "
            "Panache Homes 😊\n\n"
            "Should you require any "
            "further assistance regarding "
            "Dubai real estate opportunities, "
            "please feel free to reach out.\n\n"
            "Best regards,\n"
            "Panache Homes"
        )

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


#################################################
# MAIN
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
