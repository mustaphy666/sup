from pathlib import Path
import sqlite3
from datetime import datetime
from app.database import DB_PATH


class ConversationMemory:

    def __init__(self, database_path=None):
        if database_path is None:
            database_path = DB_PATH

        self.database_path = str(database_path)

        Path(self.database_path).parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self._create_tables()

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    def _connect(self):
        conn = sqlite3.connect(self.database_path)
        conn.row_factory = sqlite3.Row
        return conn

    # =========================================================
    # CREATE TABLE
    # =========================================================

    def _create_tables(self):
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    customer_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
            connection.commit()
        finally:
            connection.close()

    # =========================================================
    # OWNERSHIP CHECK
    # =========================================================

    def conversation_belongs_to_customer(
        self,
        conversation_id: str,
        customer_id: str,
    ) -> bool:
        connection = self._connect()
        try:
            rows = connection.execute(
                """
                SELECT DISTINCT customer_id
                FROM conversations
                WHERE conversation_id = ?
                """,
                (conversation_id,),
            ).fetchall()

            if not rows:
                return True  # New conversation ID.

            return all(
                row["customer_id"] == customer_id
                for row in rows
            )
        finally:
            connection.close()

    # =========================================================
    # SAVE MESSAGE
    # =========================================================

    def save_message(
        self,
        conversation_id: str,
        customer_id: str,
        role: str,
        content: str,
    ):
        if not self.conversation_belongs_to_customer(
            conversation_id,
            customer_id,
        ):
            raise PermissionError(
                "You are not authorized to access this conversation."
            )

        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO conversations (
                    conversation_id,
                    customer_id,
                    role,
                    content,
                    created_at
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    conversation_id,
                    customer_id,
                    role,
                    content,
                    datetime.utcnow().isoformat(),
                ),
            )
            connection.commit()
        finally:
            connection.close()

    # =========================================================
    # GET CONVERSATION HISTORY
    # =========================================================

    def get_history(
        self,
        conversation_id: str,
        customer_id: str,
        limit: int = 20,
    ):
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT role, content
                FROM conversations
                WHERE conversation_id = ?
                AND customer_id = ?
                ORDER BY id ASC
                LIMIT ?
                """,
                (
                    conversation_id,
                    customer_id,
                    limit,
                ),
            )
            rows = cursor.fetchall()
            return [
                {
                    "role": row["role"],
                    "content": row["content"],
                }
                for row in rows
            ]
        finally:
            connection.close()

    # =========================================================
    # CLEAR CONVERSATION
    # =========================================================

    def clear_conversation(
        self,
        conversation_id: str,
        customer_id: str,
    ):
        connection = self._connect()
        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                DELETE FROM conversations
                WHERE conversation_id = ?
                AND customer_id = ?
                """,
                (
                    conversation_id,
                    customer_id,
                ),
            )
            connection.commit()
        finally:
            connection.close()


conversation_memory = ConversationMemory()


# Module-level helpers for direct function imports
def conversation_belongs_to_customer(conversation_id: str, customer_id: str) -> bool:
    return conversation_memory.conversation_belongs_to_customer(
        conversation_id, customer_id
    )


def save_message(
    conversation_id: str,
    customer_id: str,
    role: str,
    content: str,
):
    return conversation_memory.save_message(
        conversation_id, customer_id, role, content
    )


def get_history(
    conversation_id: str,
    customer_id: str,
    limit: int = 20,
):
    return conversation_memory.get_history(
        conversation_id, customer_id, limit=limit
    )


def clear_conversation(
    conversation_id: str,
    customer_id: str,
):
    return conversation_memory.clear_conversation(
        conversation_id, customer_id
    )