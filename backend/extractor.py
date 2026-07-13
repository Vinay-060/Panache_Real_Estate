import os
import json
import cohere

from dotenv import load_dotenv

load_dotenv()

co = cohere.ClientV2(
    api_key=os.getenv(
        "COHERE_API_KEY"
    )
)


def extract_lead(conversation):

    prompt = f"""

You are a JSON extraction engine.



Extract lead information from the conversation.



Return ONLY a valid JSON object.



Do NOT add:

- explanations

- markdown

- ```json

- extra text



Schema:



{{

    "name": null,

    "country": null,

    "budget": null,

    "funding": null,

    "timeline": null,

    "purpose": null

}}



Rules:



1. Budget must be AED integer.



Examples:

1.5M → 1500000

2 million → 2000000



2. Funding:

Only:

- Cash

- Mortgage



3. Timeline:

Return number of months only.



Examples:

2 months → 2

within 6 months → 6



4. Purpose:

Only:

- Investment

- Personal Use



Unknown values must remain null.



Conversation:



{conversation}

"""

    response = co.chat(

        model="command-a-03-2025",

        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    content = (
        response
        .message
        .content[0]
        .text
    )

    print("\nRAW RESPONSE\n")
    print(content)

    content = (
        content
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )

    try:

        lead = json.loads(content)


        if isinstance(lead, list):

            lead = lead[-1]

        if lead.get("budget"):

            lead["budget"] = int(
                lead["budget"]
            )

        if lead.get("timeline"):

            lead["timeline"] = int(
                lead["timeline"]
            )

        return lead

    except Exception as e:

        print(
            "JSON ERROR"
        )

        print(e)

        return {

            "name": None,
            "country": None,
            "budget": None,
            "funding": None,
            "timeline": None,
            "purpose": None
        }
        
        
