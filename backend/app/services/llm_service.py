import os

from dotenv import load_dotenv
from google import genai
from google.genai import types

from tools.support_tools import (
    check_customer,
    get_transactions,
    check_refund_eligibility,
    request_refund,
    create_support_ticket,
    get_customer_refunds,
    get_customer_tickets,
)

from app.rag.knowledge_base import knowledge_base


load_dotenv()


class LLMService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")

        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set.")

        self.client = genai.Client(api_key=api_key)

    # ---------------------------------------------------------
    # TOOL DEFINITIONS
    # ---------------------------------------------------------

    def get_tools(self):

        return [
            types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name="check_customer",
                        description="Check customer account information.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "customer_id": types.Schema(
                                    type="STRING",
                                    description="Customer ID such as CUST001.",
                                )
                            },
                            required=["customer_id"],
                        ),
                    ),

                    types.FunctionDeclaration(
                        name="get_transactions",
                        description="Retrieve a customer's recent transactions.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "customer_id": types.Schema(
                                    type="STRING",
                                    description="Customer ID.",
                                )
                            },
                            required=["customer_id"],
                        ),
                    ),

                    types.FunctionDeclaration(
                        name="check_refund_eligibility",
                        description="Check whether a specific transaction is eligible for a refund request.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "customer_id": types.Schema(
                                    type="STRING",
                                    description="Customer ID.",
                                ),
                                "transaction_id": types.Schema(
                                    type="STRING",
                                    description="Transaction ID.",
                                ),
                            },
                            required=[
                                "customer_id",
                                "transaction_id",
                            ],
                        ),
                    ),

                    types.FunctionDeclaration(
                        name="request_refund",
                        description="Create a refund request for an eligible transaction.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "customer_id": types.Schema(
                                    type="STRING",
                                    description="Customer ID.",
                                ),
                                "transaction_id": types.Schema(
                                    type="STRING",
                                    description="Transaction ID.",
                                ),
                                "reason": types.Schema(
                                    type="STRING",
                                    description="Reason for the refund request.",
                                ),
                            },
                            required=[
                                "customer_id",
                                "transaction_id",
                                "reason",
                            ],
                        ),
                    ),

                    types.FunctionDeclaration(
                        name="create_support_ticket",
                        description="Create a support ticket when an issue needs escalation.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "customer_id": types.Schema(
                                    type="STRING",
                                    description="Customer ID.",
                                ),
                                "issue": types.Schema(
                                    type="STRING",
                                    description="Description of the customer's issue.",
                                ),
                            },
                            required=[
                                "customer_id",
                                "issue",
                            ],
                        ),
                    ),

                    types.FunctionDeclaration(
                        name="search_knowledge_base",
                        description="Search the company knowledge base for policies and support information.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "query": types.Schema(
                                    type="STRING",
                                    description="Question or topic to search for.",
                                )
                            },
                            required=["query"],
                        ),
                    ),
                    types.FunctionDeclaration(
                        name="get_customer_refunds",
                        description="Retrieve existing refund requests for the customer.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "customer_id": types.Schema(
                                    type="STRING",
                                    description="Customer ID"
                                )
                            },
                            required=["customer_id"],
                        ),
                    ),

                    types.FunctionDeclaration(
                        name="get_customer_tickets",
                        description="Retrieve support tickets for the customer.",
                        parameters=types.Schema(
                            type="OBJECT",
                            properties={
                                "customer_id": types.Schema(
                                    type="STRING",
                                    description="Customer ID"
                                )
                            },
                            required=["customer_id"],
                        ),
                    ),
                ]
            )
        ]       
                    

    # ---------------------------------------------------------
    # TOOL EXECUTION
    # ---------------------------------------------------------

    def execute_tool(
        self,
        function_name,
        function_args,
        authenticated_customer_id,
    ):

        # -----------------------------------------------------
        # SECURITY: Never allow the model to access another
        # customer's account.
        # -----------------------------------------------------

        if "customer_id" in function_args:

            requested_customer_id = function_args["customer_id"]

            placeholders = {
                None,
                "",
                "string",
                "customer_id",
                "CUST_ID",
                "CUSTOMER_ID",
            }

            if requested_customer_id in placeholders:
                function_args["customer_id"] = authenticated_customer_id

            elif requested_customer_id != authenticated_customer_id:
                return {
                    "success": False,
                    "error": "Unauthorized customer access.",
                }
            elif function_name == "get_customer_refunds":
                return get_customer_refunds(**function_args)

            elif function_name == "get_customer_tickets":
                return get_customer_tickets(**function_args)

        else:
            # Some tool calls may omit customer_id.
            if function_name in [
                "request_refund",
                "check_refund_eligibility",
                "create_support_ticket",
            ]:
                function_args["customer_id"] = authenticated_customer_id

        # -----------------------------------------------------
        # TOOL DISPATCH
        # -----------------------------------------------------

        if function_name == "check_customer":
            return check_customer(
                function_args["customer_id"]
            )

        elif function_name == "get_transactions":
            return get_transactions(
                function_args["customer_id"]
            )

        elif function_name == "check_refund_eligibility":
            return check_refund_eligibility(
                function_args["customer_id"],
                function_args["transaction_id"],
            )

        elif function_name == "request_refund":
            return request_refund(
                function_args["customer_id"],
                function_args["transaction_id"],
                function_args["reason"],
            )

        elif function_name == "create_support_ticket":
            return create_support_ticket(
                function_args["customer_id"],
                function_args["issue"],
            )

        elif function_name == "search_knowledge_base":

            results = knowledge_base.search(
                function_args["query"]
            )

            return {
                "success": True,
                "results": results,
            }

        return {
            "success": False,
            "error": f"Unknown tool: {function_name}",
        }

    # ---------------------------------------------------------
    # SAFE TEXT EXTRACTION
    # ---------------------------------------------------------

    def extract_text(self, response):

        try:
            if response.text:
                return response.text
        except Exception:
            pass

        try:
            for candidate in response.candidates or []:

                content = candidate.content

                if not content:
                    continue

                for part in content.parts or []:

                    if getattr(part, "text", None):
                        return part.text

        except Exception:
            pass

        return ""

    # ---------------------------------------------------------
    # MAIN AGENT
    # ---------------------------------------------------------

    async def generate_response(
        self,
        customer_id: str,
        customer_message: str,
        conversation_history=None,
    ):

        actions = []

        # -----------------------------------------------------
        # SYSTEM INSTRUCTION
        # -----------------------------------------------------

        system_instruction = """
You are SupportFlow AI, an intelligent customer support agent.

Your job is to solve customer support requests using the available
tools and company knowledge base.

IMPORTANT RULES:

1. CUSTOMER SECURITY
- Only access information belonging to the authenticated customer.
- Never reveal another customer's information.
- Never request passwords, OTPs, PINs, or full payment card numbers.

2. TRANSACTIONS
- Use get_transactions when transaction information is required.
- Do not invent transaction information.
- Use the actual transaction data returned by the tool.

3. REFUNDS
- If the customer asks about a refund, investigate the relevant
  transaction.
- Use check_refund_eligibility before creating a refund request.
- Only use request_refund when appropriate.
- Clearly explain that a refund request is not the same as a completed
  refund.
- Never claim money has been returned unless the tool explicitly says so.

4. KNOWLEDGE BASE
- Use search_knowledge_base when company policies or support
  procedures are relevant.
- Do not invent company policies.
- Base policy-related answers on retrieved knowledge.

5. SUPPORT TICKETS
- Create a support ticket when the customer's issue needs escalation.
- Give the customer the ticket ID returned by the tool.

6. REASONING
- You may use multiple tools when necessary.
- Do not stop after the first tool if additional information is needed.
- After completing the necessary actions, provide a concise and useful
  final response.

7. COMMUNICATION
- Be professional and natural.
- Explain what you actually did.
- Never expose internal reasoning or hidden chain-of-thought.
"""

        # -----------------------------------------------------
        # BUILD CONVERSATION
        # -----------------------------------------------------

        contents = []

        if conversation_history:

            for message in conversation_history:

                role = message["role"]
                content = message["content"]

                gemini_role = (
                    "model"
                    if role == "assistant"
                    else "user"
                )

                contents.append(
                    types.Content(
                        role=gemini_role,
                        parts=[
                            types.Part(
                                text=content
                            )
                        ],
                    )
                )

        contents.append(
            types.Content(
                role="user",
                parts=[
                    types.Part(
                        text=customer_message
                    )
                ],
            )
        )

        # -----------------------------------------------------
        # AGENT LOOP
        # -----------------------------------------------------

        for iteration in range(6):

            print("\n" + "=" * 60)
            print(f"AGENT ITERATION: {iteration + 1}")
            print("=" * 60)

            try:

                response = await self.client.aio.models.generate_content(
                    model="gemini-3.6-flash",
                    contents=contents,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=self.get_tools(),
                    ),
                )

            except Exception as e:

                print("GEMINI ERROR:", e)

                return {
                    "response": (
                        "I'm sorry, but I encountered a problem "
                        "while processing your request."
                    ),
                    "actions": actions,
                }

            # -------------------------------------------------
            # CHECK FOR TOOL CALLS
            # -------------------------------------------------

            function_calls = []

            try:

                for candidate in response.candidates or []:

                    if not candidate.content:
                        continue

                    for part in candidate.content.parts or []:

                        if getattr(part, "function_call", None):
                            function_calls.append(
                                part.function_call
                            )

            except Exception as e:

                print("FUNCTION CALL PARSING ERROR:", e)

            # -------------------------------------------------
            # NO TOOL CALL → FINAL ANSWER
            # -------------------------------------------------

            if not function_calls:

                final_text = self.extract_text(response)

                if not final_text:

                    final_text = (
                        "I wasn't able to generate a response."
                    )

                print("FINAL RESPONSE:")
                print(final_text)

                return {
                    "response": final_text,
                    "actions": actions,
                }

            # -------------------------------------------------
            # SAVE MODEL TOOL-CALL MESSAGE
            # -------------------------------------------------

            contents.append(response.candidates[0].content)

            # -------------------------------------------------
            # EXECUTE TOOLS
            # -------------------------------------------------

            for function_call in function_calls:

                function_name = function_call.name

                function_args = dict(
                    function_call.args or {}
                )

                print("\nAI TOOL CALL:")
                print("Function:", function_name)
                print("Arguments:", function_args)

                actions.append(
                    f"Used tool: {function_name}"
                )

                # ---------------------------------------------
                # EXECUTE
                # ---------------------------------------------

                try:

                    tool_result = self.execute_tool(
                        function_name,
                        function_args,
                        customer_id,
                    )

                except Exception as e:

                    tool_result = {
                        "success": False,
                        "error": str(e),
                    }

                print("\nTOOL RESULT:")
                print(tool_result)

                # ---------------------------------------------
                # RETURN TOOL RESULT TO GEMINI
                # ---------------------------------------------

                contents.append(
                    types.Content(
                        role="user",
                        parts=[
                            types.Part.from_function_response(
                                name=function_name,
                                response=tool_result,
                            )
                        ],
                    )
                )

        # -----------------------------------------------------
        # MAX ITERATIONS
        # -----------------------------------------------------

        return {
            "response": (
                "I wasn't able to complete the request within "
                "the allowed number of agent steps."
            ),
            "actions": actions,
        }


# -------------------------------------------------------------
# GLOBAL SERVICE INSTANCE
# -------------------------------------------------------------

llm_service = LLMService()