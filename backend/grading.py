def calculate_grade(data):

    budget = data.get("budget")
    timeline = data.get("timeline")

    try:
        budget = int(budget)
    except:
        budget = None

    try:
        timeline = int(timeline)
    except:
        timeline = None

    if budget is None and timeline is None:
        return "D"

    if budget is None:
        return "C"

    if budget < 1_000_000:
        return "C"

    if timeline and timeline <= 3:
        return "A"

    return "B"