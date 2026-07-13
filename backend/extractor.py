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


EMPTY_LEAD = {
    "name": None,
    "country": None,
    "budget": None,
    "funding": None,
    "timeline": None,
    "purpose": None
}


def extract_lead(conversation):

    prompt = f"""
You are an information extraction engine.

Extract information ONLY for the CURRENT USER.

IMPORTANT RULES:

1. Return ONLY ONE JSON object.

2. Never return:
- explanations
- markdown
- arrays
- multiple objects

3. Ignore other users.

4. If information is unavailable,
unknown or user refuses to answer,
return null.

Examples:

"I don't know budget"
→ budget = null

"No timeline yet"
→ timeline = null

"Just exploring"
→ purpose = null

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

budget:
AED integer only.

1.5M → 1500000
2 million → 2000000

funding:
Only:
Cash
Mortgage

timeline:
Months integer.

purpose:
Only:
Investment
Personal Use

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

        match = re.search(
            r'\{[\s\S]*\}',
            content
        )

        if not match:

            return EMPTY_LEAD.copy()

        lead = json.loads(
            match.group()
        )

        if lead.get("budget"):

            try:
                lead["budget"] = int(
                    float(
                        lead["budget"]
                    )
                )
            except:
                lead["budget"] = None

        if lead.get("timeline"):

            try:
                lead["timeline"] = int(
                    float(
                        lead["timeline"]
                    )
                )
            except:
                lead["timeline"] = None

        return {

            "name":
                lead.get("name"),

            "country":
                lead.get("country"),

            "budget":
                lead.get("budget"),

            "funding":
                lead.get("funding"),

            "timeline":
                lead.get("timeline"),

            "purpose":
                lead.get("purpose")
        }

    except Exception as e:

        print(
            "\nEXTRACTION ERROR\n"
        )

        print(e)

        return EMPTY_LEAD.copy()
