import sqlite3
from pathlib import Path
from datetime import datetime


DB_PATH = Path(__file__).resolve().parent.parent / "supportflow.db"


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS refunds (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            refund_id TEXT UNIQUE NOT NULL,
            customer_id TEXT NOT NULL,
            transaction_id TEXT NOT NULL,
            amount REAL NOT NULL,
            currency TEXT NOT NULL,
            reason TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS support_tickets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE NOT NULL,
            customer_id TEXT NOT NULL,
            issue TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def create_refund(
    refund_id,
    customer_id,
    transaction_id,
    amount,
    currency,
    reason,
):
    conn = get_connection()

    created_at = datetime.utcnow().isoformat()

    conn.execute(
        """
        INSERT INTO refunds (
            refund_id,
            customer_id,
            transaction_id,
            amount,
            currency,
            reason,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            refund_id,
            customer_id,
            transaction_id,
            amount,
            currency,
            reason,
            "pending",
            created_at,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "refund_id": refund_id,
        "customer_id": customer_id,
        "transaction_id": transaction_id,
        "amount": amount,
        "currency": currency,
        "reason": reason,
        "status": "pending",
        "created_at": created_at,
    }


def get_refunds(customer_id):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            refund_id,
            customer_id,
            transaction_id,
            amount,
            currency,
            reason,
            status,
            created_at
        FROM refunds
        WHERE customer_id = ?
        ORDER BY id DESC
        """,
        (customer_id,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]


def refund_exists(transaction_id):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT refund_id
        FROM refunds
        WHERE transaction_id = ?
        LIMIT 1
        """,
        (transaction_id,),
    ).fetchone()

    conn.close()

    return row is not None


def create_ticket(
    ticket_id,
    customer_id,
    issue,
):
    conn = get_connection()

    created_at = datetime.utcnow().isoformat()

    conn.execute(
        """
        INSERT INTO support_tickets (
            ticket_id,
            customer_id,
            issue,
            status,
            created_at
        )
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            ticket_id,
            customer_id,
            issue,
            "open",
            created_at,
        ),
    )

    conn.commit()
    conn.close()

    return {
        "ticket_id": ticket_id,
        "customer_id": customer_id,
        "issue": issue,
        "status": "open",
        "created_at": created_at,
    }


def get_tickets(customer_id):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT
            ticket_id,
            customer_id,
            issue,
            status,
            created_at
        FROM support_tickets
        WHERE customer_id = ?
        ORDER BY id DESC
        """,
        (customer_id,),
    ).fetchall()

    conn.close()

    return [dict(row) for row in rows]