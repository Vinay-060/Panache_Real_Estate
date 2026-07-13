def is_lead_complete(lead):

    filled = 0

    fields = [
        "name",
        "country",
        "budget",
        "funding",
        "timeline",
        "purpose"
    ]

    for field in fields:
        if lead.get(field):
            filled += 1

    # Save only after at least 4 fields
    return filled >= 4