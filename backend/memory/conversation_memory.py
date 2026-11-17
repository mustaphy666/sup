import sqlite3
from datetime import datetime


class ConversationMemory:

    def __init__(self, database_path="supportflow.db"):

        self.database_path = database_path

        self._create_tables()

    # =========================================================
    # DATABASE CONNECTION
    # =========================================================

    def _connect(self):

        return sqlite3.connect(
            self.database_path
        )

    # =========================================================
    # CREATE TABLE
    # =========================================================

    def _create_tables(self):

        connection = self._connect()

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

        connection = self._connect()

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

        connection.close()

        return [
            {
                "role": row[0],
                "content": row[1],
            }

            for row in rows
        ]

    # =========================================================
    # CLEAR CONVERSATION
    # =========================================================

    def clear_conversation(
        self,
        conversation_id: str,
        customer_id: str,
    ):

        connection = self._connect()

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

        connection.close()


conversation_memory = ConversationMemory()