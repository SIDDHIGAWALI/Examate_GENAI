def get_user_name(user):
    return user["name"]


def get_user_email(user):
    return user["email"]


def get_user_age(user):
    return user["age"]


def is_adult(user):
    if user["age"] >= 18:
        return True

    return False


def update_user_name(user, new_name):

    user["name"] = new_name

    return user


def validate_user(user):

    if not user.get("name"):
        raise ValueError("Name is required")

    if not user.get("email"):
        raise ValueError("Email is required")

    if user.get("age", 0) < 0:
        raise ValueError("Invalid age")

    return True