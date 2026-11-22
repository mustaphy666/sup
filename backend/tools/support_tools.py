import uuid
import sqlite3
from app.database import (
    create_refund,
    refund_exists,
    create_ticket,
    get_refunds,
    get_tickets,
)


CUSTOMERS = {
    "CUST001": {
        "customer_id": "CUST001",
        "name": "John Doe",
        "email": "john@example.com",
        "plan": "Premium",
        "status": "active",
    },
    "CUST002": {
        "customer_id": "CUST002",
        "name": "Sarah Smith",
        "email": "sarah@example.com",
        "plan": "Basic",
        "status": "active",
    },
}


TRANSACTIONS = {
    "CUST001": [
        {
            "transaction_id": "TXN1001",
            "amount": 49.99,
            "currency": "$",
            "description": "Premium Subscription",
            "date": "2026-09-01",
            "status": "completed",
        },
        {
            "transaction_id": "TXN1002",
            "amount": 49.99,
            "currency": "$",
            "description": "Premium Subscription",
            "date": "2026-09-01",
            "status": "completed",
        },
        {
            "transaction_id": "TXN1003",
            "amount": 12.50,
            "currency": "$",
            "description": "Additional Storage",
            "date": "2026-09-03",
            "status": "completed",
        },
    ],
    "CUST002": [
        {
            "transaction_id": "TXN2001",
            "amount": 9.99,
            "currency": "$",
            "description": "Basic Subscription",
            "date": "2026-09-01",
            "status": "completed",
        }
    ],
}


def check_customer(customer_id: str):

    customer = CUSTOMERS.get(customer_id)

    if not customer:
        return {
            "success": False,
            "error": "Customer not found",
        }

    return {
        "success": True,
        "customer": customer,
    }


def get_transactions(customer_id: str):

    transactions = TRANSACTIONS.get(customer_id)

    if transactions is None:
        return {
            "success": False,
            "error": "Customer not found",
        }

    return {
        "success": True,
        "transactions": transactions,
    }


def check_refund_eligibility(
    customer_id: str,
    transaction_id: str,
):

    transactions = TRANSACTIONS.get(customer_id, [])

    transaction = next(
        (
            txn
            for txn in transactions
            if txn["transaction_id"] == transaction_id
        ),
        None,
    )

    if not transaction:
        return {
            "success": False,
            "eligible": False,
            "reason": "Transaction not found.",
        }

    if transaction["status"] != "completed":
        return {
            "success": True,
            "eligible": False,
            "reason": "Only completed transactions can be refunded.",
        }

    if refund_exists(transaction_id):
        return {
            "success": True,
            "eligible": False,
            "reason": "A refund request already exists for this transaction.",
        }

    return {
        "success": True,
        "eligible": True,
        "reason": "Transaction is eligible for refund review.",
        "transaction": transaction,
    }


def request_refund(
    customer_id: str,
    transaction_id: str,
    reason: str,
):
    transactions = TRANSACTIONS.get(customer_id, [])

    transaction = next(
        (
            txn
            for txn in transactions
            if txn["transaction_id"] == transaction_id
        ),
        None,
    )

    if not transaction:
        return {
            "success": False,
            "error": "Transaction not found.",
        }

    if transaction["status"] != "completed":
        return {
            "success": False,
            "error": "Only completed transactions can be refunded.",
        }

    # Check whether this customer already requested a refund.
    if refund_exists(customer_id, transaction_id):
        return {
            "success": False,
            "error": "A refund request already exists for this transaction.",
        }

    # Generate a unique refund ID.
    refund_id = f"REFUND-{uuid.uuid4().hex[:12].upper()}"

    try:
        refund = create_refund(
            refund_id=refund_id,
            customer_id=customer_id,
            transaction_id=transaction_id,
            amount=transaction["amount"],
            currency=transaction["currency"],
            reason=reason,
        )

        return {
            "success": True,
            "message": "Refund request created successfully.",
            "refund": refund,
        }

    except sqlite3.IntegrityError:
        # Another request may have inserted the refund first.
        if refund_exists(customer_id, transaction_id):
            return {
                "success": False,
                "error": "A refund request already exists for this transaction.",
            }

        raise 


def create_support_ticket(
    customer_id: str,
    issue: str,
):

    existing_tickets = get_tickets(customer_id)

    ticket_number = len(existing_tickets) + 1

    ticket_id = f"TICKET-{ticket_number:04d}"

    ticket = create_ticket(
        ticket_id=ticket_id,
        customer_id=customer_id,
        issue=issue,
    )

    return {
        "success": True,
        "message": "Support ticket created successfully.",
        "ticket": ticket,
    }


def get_customer_refunds(customer_id: str):

    return {
        "success": True,
        "refunds": get_refunds(customer_id),
    }


def get_customer_tickets(customer_id: str):

    return {
        "success": True,
        "tickets": get_tickets(customer_id),
    }