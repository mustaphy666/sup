import sqlite3
from pathlib import Path
from datetime import datetime, timezone
import uuid
import os

DB_PATH = Path(
    os.getenv(
        "DATABASE_PATH",
        str(Path(__file__).resolve().parent.parent / "supportflow.db")
    )
)

DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(str(DB_PATH))
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
    CREATE UNIQUE INDEX IF NOT EXISTS
    idx_refunds_customer_transaction
    ON refunds(customer_id, transaction_id)
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
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id TEXT PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            customer_id TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
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

    created_at = datetime.now().isoformat()

    try:
        conn.execute("BEGIN IMMEDIATE")

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

    except sqlite3.IntegrityError:
        conn.rollback()
        raise

    except Exception:
        conn.rollback()
        raise

    finally:
        conn.close()


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


def refund_exists(customer_id, transaction_id):
    conn = get_connection()

    try:
        row = conn.execute(
            """
            SELECT refund_id
            FROM refunds
            WHERE customer_id = ?
            AND transaction_id = ?
            LIMIT 1
            """,
            (customer_id, transaction_id),
        ).fetchone()

        return row is not None

    finally:
        conn.close()


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
def create_user(email, customer_id, password_hash):
    conn = get_connection()

    user_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    try:
        conn.execute(
            """
            INSERT INTO users (
                user_id,
                email,
                customer_id,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                user_id,
                email,
                customer_id,
                password_hash,
                created_at,
            ),
        )

        conn.commit()

        return {
            "user_id": user_id,
            "email": email,
            "customer_id": customer_id,
            "created_at": created_at,
        }

    finally:
        conn.close()


def get_user_by_email(email):
    conn = get_connection()

    try:
        user = conn.execute(
            "SELECT * FROM users WHERE email = ?",
            (email,),
        ).fetchone()

        return dict(user) if user else None

    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_connection()

    try:
        user = conn.execute(
            "SELECT * FROM users WHERE user_id = ?",
            (user_id,),
        ).fetchone()

        return dict(user) if user else None

    finally:
        conn.close()