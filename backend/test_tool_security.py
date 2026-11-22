from memory.conversation_memory import (
    save_message,
    get_history,
    clear_conversation,
)

conversation_id = "SECURITY-TEST-001"

# Customer 1 creates a conversation.
save_message(
    conversation_id,
    "CUST001",
    "user",
    "Hello, I need help with my subscription."
)

# Customer 1 should see their message.
history1 = get_history(conversation_id, "CUST001")
print("TEST 1:", history1)

# Customer 2 should not see Customer 1's messages.
history2 = get_history(conversation_id, "CUST002")
print("TEST 2:", history2)

# Customer 2 attempts to insert a message into Customer 1's conversation.
try:
    save_message(
        conversation_id,
        "CUST002",
        "user",
        "Trying to access another customer's conversation."
    )
    print("TEST 3: FAILED — unauthorized message was accepted.")

except PermissionError:
    print("TEST 3: PASSED — unauthorized access blocked.")

# Customer 1 should still be able to clear their conversation.
clear_conversation(conversation_id, "CUST001")
print("TEST 4: Conversation cleared.")