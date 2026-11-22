from app.services.llm_service import llm_service


def test_customer_tool_security():

    result = llm_service.execute_tool(
        "get_transactions",
        {"customer_id": "CUST002"},
        "CUST001",
    )

    assert result["success"] is False


def test_customer_tool_uses_authenticated_id():

    result = llm_service.execute_tool(
        "get_transactions",
        {},
        "CUST001",
    )

    assert result["success"] is True


def test_unknown_tool():

    result = llm_service.execute_tool(
        "unknown_tool",
        {},
        "CUST001",
    )

    assert result["success"] is False