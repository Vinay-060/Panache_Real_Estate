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
You are an information extraction engine.

Extract lead information from the CURRENT USER conversation.

IMPORTANT:

1. Return ONLY JSON.

2. Never explain.

3. Never return markdown.

4. Never return arrays.

5. Never return multiple objects.

6. Use information mentioned earlier
in the same conversation.

7. Do NOT reset existing fields to null.

Schema:

{{
"name":null,
"country":null,
"budget":null,
"funding":null,
"timeline":null,
"purpose":null
}}

Rules:

budget:

Convert to integer AED.

Examples:

1M → 1000000
2.5 million → 2500000

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

            return {

                "name": None,
                "country": None,
                "budget": None,
                "funding": None,
                "timeline": None,
                "purpose": None
            }

        lead = json.loads(
            match.group()
        )

        if lead.get("budget"):

            lead["budget"] = int(
                float(
                    lead["budget"]
                )
            )

        if lead.get("timeline"):

            lead["timeline"] = int(
                float(
                    lead["timeline"]
                )
            )

        return lead

    except Exception as e:

        print(e)

        return {

            "name": None,
            "country": None,
            "budget": None,
            "funding": None,
            "timeline": None,
            "purpose": None
        }
