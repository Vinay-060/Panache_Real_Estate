user_states = {}


def get_state(user_id):

    if user_id not in user_states:

        user_states[user_id] = {
            "name": None,
            "country": None,
            "budget": None,
            "funding": None,
            "timeline": None,
            "purpose": None,
            "grade": None
        }

    return user_states[user_id]