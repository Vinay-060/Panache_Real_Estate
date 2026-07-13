import os
import json
import re
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

Extract investor information ONLY for the CURRENT USER.

IMPORTANT RULES:

1. Return EXACTLY ONE JSON object.

2. Never return:
- JSON arrays
- Multiple objects
- Explanations
- Markdown
- ```json

3. Ignore previous users.

4. Extract information only from the
latest user messages.

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

name:
First name only.

country:
Country of residence.

budget:
AED integer only.

Examples:

1.5M → 1500000
2 million → 2000000

funding:
Only:

- Cash
- Mortgage

timeline:
Months integer only.

Examples:

2 months → 2
within six months → 6

purpose:
Only:

- Investment
- Personal Use

Unknown or no values must remain null.

Conversation:

{conversation}
"""

    try:

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

        #################################################
        # Extract only first JSON object
        #################################################

        match = re.search(
            r'\{[\s\S]*\}',
            content
        )

        if not match:

            raise Exception(
                "No JSON found"
            )

        content = match.group()

        lead = json.loads(
            content
        )

        #################################################
        # Budget
        #################################################

        if lead.get("budget"):

            try:

                lead["budget"] = int(
                    float(
                        lead["budget"]
                    )
                )

            except:

                lead["budget"] = None

        #################################################
        # Timeline
        #################################################

        if lead.get("timeline"):

            try:

                lead["timeline"] = int(
                    float(
                        lead["timeline"]
                    )
                )

            except:

                lead["timeline"] = None

        #################################################
        # Normalize values
        #################################################

        if lead.get("funding"):

            value = (
                lead["funding"]
                .strip()
                .title()
            )

            if value not in [

                "Cash",
                "Mortgage"
            ]:

                value = None

            lead["funding"] = value

        if lead.get("purpose"):

            value = (
                lead["purpose"]
                .strip()
                .title()
            )

            if value not in [

                "Investment",
                "Personal Use"
            ]:

                value = None

            lead["purpose"] = value

        print("\nLEAD\n")
        print(lead)

        return lead

    except Exception as e:

        print(
            "\nEXTRACTION ERROR\n"
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
