from tools.support_tools import CUSTOMERS


def find_customer_by_email(email: str):
    email = email.lower().strip()

    for customer in CUSTOMERS.values():
        if customer["email"].lower() == email:
            return customer

    return None