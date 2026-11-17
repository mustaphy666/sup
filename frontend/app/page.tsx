"use client";

import { useEffect, useState } from "react";

type Message = {
  role: "user" | "assistant";
  content: string;
};

type Customer = {
  customer_id: string;
  name: string;
  email: string;
  plan: string;
  status: string;
};

type Transaction = {
  transaction_id: string;
  amount: number;
  currency: string;
  description: string;
  date: string;
  status: string;
};

type Refund = {
  refund_id: string;
  transaction_id: string;
  amount: number;
  currency: string;
  reason: string;
  status: string;
  created_at: string;
};

type Ticket = {
  ticket_id: string;
  issue: string;
  status: string;
  created_at: string;
};

const API_URL = "http://127.0.0.1:8000";
const CUSTOMER_ID = "CUST001";

export default function Home() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");

  const [loading, setLoading] = useState(false);

  const [conversationId, setConversationId] = useState("");

  const [customer, setCustomer] =
    useState<Customer | null>(null);

  const [transactions, setTransactions] =
    useState<Transaction[]>([]);

  const [refunds, setRefunds] =
    useState<Refund[]>([]);

  const [tickets, setTickets] =
    useState<Ticket[]>([]);

  const [lastActions, setLastActions] =
    useState<string[]>([]);

  useEffect(() => {
    initialize();
  }, []);

  async function initialize() {
    let id =
      localStorage.getItem(
        "supportflow_conversation_id"
      );

    if (!id) {
      id = crypto.randomUUID();

      localStorage.setItem(
        "supportflow_conversation_id",
        id
      );
    }

    setConversationId(id);

    await Promise.all([
      loadConversation(id),
      loadCustomer(),
      loadRefunds(),
      loadTickets(),
    ]);
  }

  async function loadConversation(id: string) {
    try {
      const response = await fetch(
        `${API_URL}/conversations/${id}?customer_id=${CUSTOMER_ID}`
      );

      if (!response.ok) return;

      const data = await response.json();

      setMessages(data.messages || []);
    } catch (error) {
      console.error(error);
    }
  }

  async function loadCustomer() {
    try {
      const response = await fetch(
        `${API_URL}/customers/${CUSTOMER_ID}`
      );

      if (!response.ok) return;

      const data = await response.json();

      setCustomer(data.customer);

      setTransactions(
        data.transactions?.transactions || []
      );
    } catch (error) {
      console.error(error);
    }
  }

  async function loadRefunds() {
    try {
      const response = await fetch(
        `${API_URL}/customers/${CUSTOMER_ID}/refunds`
      );

      if (!response.ok) return;

      const data = await response.json();

      setRefunds(data.refunds || []);
    } catch (error) {
      console.error(error);
    }
  }

  async function loadTickets() {
    try {
      const response = await fetch(
        `${API_URL}/customers/${CUSTOMER_ID}/tickets`
      );

      if (!response.ok) return;

      const data = await response.json();

      setTickets(data.tickets || []);
    } catch (error) {
      console.error(error);
    }
  }

  async function refreshCustomerData() {
    await Promise.all([
      loadCustomer(),
      loadRefunds(),
      loadTickets(),
    ]);
  }

  async function sendMessage() {
    const message = input.trim();

    if (!message || loading) return;

    setMessages((previous) => [
      ...previous,
      {
        role: "user",
        content: message,
      },
    ]);

    setInput("");
    setLoading(true);
    setLastActions([]);

    try {
      const response = await fetch(
        `${API_URL}/chat`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            customer_id: CUSTOMER_ID,
            conversation_id: conversationId,
            message,
          }),
        }
      );

      if (!response.ok) {
        throw new Error("Chat request failed");
      }

      const data = await response.json();

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            data.response ||
            "I couldn't generate a response.",
        },
      ]);

      setLastActions(data.actions || []);

      await refreshCustomerData();
    } catch (error) {
      console.error(error);

      setMessages((previous) => [
        ...previous,
        {
          role: "assistant",
          content:
            "Sorry, I couldn't connect to the SupportFlow backend.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  }

  async function clearChat() {
    try {
      await fetch(
        `${API_URL}/conversations/${conversationId}?customer_id=${CUSTOMER_ID}`,
        {
          method: "DELETE",
        }
      );

      setMessages([]);
      setLastActions([]);
    } catch (error) {
      console.error(error);
    }
  }

  function formatAction(action: string) {
    return action
      .replace("Used tool: ", "")
      .replaceAll("_", " ")
      .replace(/\b\w/g, (letter) =>
        letter.toUpperCase()
      );
  }

  function formatDate(date: string) {
    return new Date(date).toLocaleDateString(
      "en-US",
      {
        month: "short",
        day: "numeric",
        year: "numeric",
      }
    );
  }

  return (
    <main className="min-h-screen bg-[#09090b] text-white flex">

      {/* =====================================================
          LEFT SIDEBAR
      ====================================================== */}

      <aside className="w-64 shrink-0 border-r border-zinc-800 bg-[#0d0d0f] p-5 flex flex-col">

        <div>

          {/* Logo */}

          <div className="flex items-center gap-3 mb-10">

            <div className="w-10 h-10 rounded-xl bg-white text-black flex items-center justify-center font-bold">
              S
            </div>

            <div>
              <h1 className="font-semibold">
                SupportFlow
              </h1>

              <p className="text-xs text-zinc-500">
                AI Support Agent
              </p>
            </div>

          </div>

          {/* Navigation */}

          <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-3">
            Workspace
          </p>

          <div className="bg-zinc-800/60 border border-zinc-700/50 rounded-xl px-3 py-3 text-sm">
            <div className="flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500" />
              Live Conversation
            </div>
          </div>

        </div>


        {/* Agent capabilities */}

        <div className="mt-8">

          <p className="text-[10px] text-zinc-600 uppercase tracking-widest mb-3">
            Agent capabilities
          </p>

          <div className="space-y-2 text-xs text-zinc-500">

            <div className="flex gap-2">
              <span>✦</span>
              Tool Calling
            </div>

            <div className="flex gap-2">
              <span>✦</span>
              Knowledge Retrieval
            </div>

            <div className="flex gap-2">
              <span>✦</span>
              Customer Memory
            </div>

            <div className="flex gap-2">
              <span>✦</span>
              Support Actions
            </div>

          </div>

        </div>


        <div className="mt-auto border-t border-zinc-800 pt-4">

          <p className="text-xs text-zinc-500">
            Customer
          </p>

          <p className="text-sm mt-1">
            {customer?.name || "Loading..."}
          </p>

          <p className="text-xs text-zinc-600">
            {CUSTOMER_ID}
          </p>

        </div>

      </aside>


      {/* =====================================================
          CENTER CHAT
      ====================================================== */}

      <section className="flex-1 min-w-0 flex flex-col">

        {/* Header */}

        <header className="h-16 shrink-0 border-b border-zinc-800 px-7 flex items-center justify-between">

          <div>

            <h2 className="font-semibold">
              Customer Support
            </h2>

            <p className="text-xs text-zinc-500">
              Autonomous AI support workflow
            </p>

          </div>

          <button
            onClick={clearChat}
            className="text-xs text-zinc-400 hover:text-white border border-zinc-700 rounded-lg px-3 py-2"
          >
            Clear conversation
          </button>

        </header>


        {/* Chat */}

        <div className="flex-1 overflow-y-auto px-8 py-8">

          {messages.length === 0 ? (

            <div className="max-w-2xl mx-auto mt-16">

              <div className="text-center">

                <div className="mx-auto w-14 h-14 rounded-2xl bg-zinc-900 border border-zinc-800 flex items-center justify-center text-2xl mb-5">
                  ✦
                </div>

                <h2 className="text-2xl font-semibold mb-3">
                  SupportFlow
                </h2>

                <p className="text-sm text-zinc-500 leading-6">
                  An AI support agent that can understand
                  requests, retrieve company knowledge,
                  inspect customer data and execute
                  support actions.
                </p>

              </div>


              {/* Suggested prompts */}

              <div className="grid grid-cols-2 gap-3 mt-8">

                {[
                  "Why was I charged twice?",
                  "Can I get a refund?",
                  "What is my current plan?",
                  "I need help with my account",
                ].map((question) => (

                  <button
                    key={question}
                    onClick={() =>
                      setInput(question)
                    }
                    className="text-left border border-zinc-800 bg-zinc-900/40 hover:bg-zinc-800 rounded-xl p-4 text-sm text-zinc-300 transition"
                  >
                    {question}
                  </button>

                ))}

              </div>

            </div>

          ) : (

            <div className="max-w-3xl mx-auto space-y-6">

              {messages.map(
                (message, index) => (

                  <div
                    key={index}
                    className={`flex ${
                      message.role === "user"
                        ? "justify-end"
                        : "justify-start"
                    }`}
                  >

                    <div
                      className={`max-w-[78%] rounded-2xl px-5 py-3 text-sm leading-6 ${
                        message.role === "user"
                          ? "bg-white text-black"
                          : "bg-zinc-900 border border-zinc-800 text-zinc-200"
                      }`}
                    >
                      {message.content}
                    </div>

                  </div>

                )
              )}


              {/* Loading */}

              {loading && (

                <div className="max-w-[78%] border border-zinc-800 bg-zinc-900 rounded-2xl p-5">

                  <div className="flex items-center gap-3 mb-4">

                    <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />

                    <span className="text-xs text-zinc-400">
                      SupportFlow is working...
                    </span>

                  </div>

                  <div className="space-y-3">

                    <div className="text-xs text-zinc-600">
                      Understanding request
                    </div>

                    <div className="text-xs text-zinc-600">
                      Selecting appropriate tools
                    </div>

                    <div className="text-xs text-zinc-600">
                      Executing support workflow
                    </div>

                  </div>

                </div>

              )}


              {/* Agent Activity */}

              {lastActions.length > 0 &&
                !loading && (

                  <div className="border border-zinc-800 bg-[#0d0d0f] rounded-2xl p-5">

                    <div className="flex items-center gap-3 mb-5">

                      <div className="w-8 h-8 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-center">
                        ✓
                      </div>

                      <div>

                        <p className="text-sm font-medium">
                          Agent workflow completed
                        </p>

                        <p className="text-xs text-zinc-600">
                          {lastActions.length} actions executed
                        </p>

                      </div>

                    </div>


                    <div className="space-y-4">

                      {lastActions.map(
                        (action, index) => (

                          <div
                            key={index}
                            className="flex items-center gap-3"
                          >

                            <div className="relative">

                              <div className="w-6 h-6 rounded-full bg-green-500/10 border border-green-500/20 flex items-center justify-center text-[10px] text-green-400">
                                ✓
                              </div>

                            </div>

                            <span className="text-xs text-zinc-400">
                              {formatAction(action)}
                            </span>

                          </div>

                        )
                      )}

                    </div>

                  </div>

                )}

            </div>

          )}

        </div>


        {/* Input */}

        <div className="border-t border-zinc-800 p-5">

          <div className="max-w-3xl mx-auto">

            <div className="flex items-end gap-3 bg-zinc-900 border border-zinc-700 rounded-2xl p-2 focus-within:border-zinc-500">

              <textarea
                value={input}
                onChange={(event) =>
                  setInput(event.target.value)
                }
                onKeyDown={(event) => {

                  if (
                    event.key === "Enter" &&
                    !event.shiftKey
                  ) {
                    event.preventDefault();
                    sendMessage();
                  }

                }}
                placeholder="Ask SupportFlow..."
                rows={1}
                className="flex-1 bg-transparent outline-none resize-none px-3 py-3 text-sm placeholder:text-zinc-600"
              />

              <button
                onClick={sendMessage}
                disabled={
                  loading || !input.trim()
                }
                className="bg-white text-black rounded-xl px-5 py-3 text-sm font-medium hover:bg-zinc-200 disabled:opacity-30 transition"
              >
                Send
              </button>

            </div>

            <p className="text-center text-[10px] text-zinc-700 mt-2">
              AI-generated responses may require verification.
            </p>

          </div>

        </div>

      </section>


      {/* =====================================================
          RIGHT CUSTOMER PANEL
      ====================================================== */}

      <aside className="w-80 shrink-0 border-l border-zinc-800 bg-[#0d0d0f] p-5 overflow-y-auto">

        {/* Customer header */}

        <div className="flex items-center justify-between mb-6">

          <div>

            <p className="text-[10px] text-zinc-600 uppercase tracking-widest">
              Customer
            </p>

            <h3 className="font-semibold mt-1">
              Account overview
            </h3>

          </div>

          <span className="text-[10px] text-green-400 bg-green-400/10 border border-green-500/20 px-2 py-1 rounded-full">
            {customer?.status || "Loading"}
          </span>

        </div>


        {/* Customer card */}

        <div className="border border-zinc-800 rounded-2xl p-4 mb-5">

          <div className="flex items-center gap-3">

            <div className="w-11 h-11 rounded-full bg-zinc-800 flex items-center justify-center font-medium">
              {customer?.name?.charAt(0) || "?"}
            </div>

            <div>

              <p className="text-sm font-medium">
                {customer?.name || "Loading..."}
              </p>

              <p className="text-xs text-zinc-600">
                {customer?.email || "..."}
              </p>

            </div>

          </div>


          <div className="border-t border-zinc-800 mt-4 pt-4 flex justify-between">

            <span className="text-xs text-zinc-600">
              Subscription
            </span>

            <span className="text-xs font-medium">
              {customer?.plan || "..."}
            </span>

          </div>

        </div>


        {/* Transactions */}

        <div className="mb-6">

          <div className="flex justify-between items-center mb-3">

            <h3 className="text-xs font-medium">
              Transactions
            </h3>

            <span className="text-[10px] text-zinc-600">
              {transactions.length}
            </span>

          </div>


          <div className="space-y-2">

            {transactions.map(
              (transaction) => (

                <div
                  key={transaction.transaction_id}
                  className="border border-zinc-800 rounded-xl p-3"
                >

                  <div className="flex justify-between mb-1">

                    <span className="text-[10px] text-zinc-600">
                      {transaction.transaction_id}
                    </span>

                    <span className="text-xs font-medium">
                      {transaction.currency}
                      {transaction.amount.toFixed(2)}
                    </span>

                  </div>

                  <p className="text-xs text-zinc-400">
                    {transaction.description}
                  </p>

                  <div className="flex justify-between mt-2">

                    <span className="text-[10px] text-zinc-700">
                      {transaction.date}
                    </span>

                    <span className="text-[10px] text-green-500">
                      {transaction.status}
                    </span>

                  </div>

                </div>

              )
            )}

          </div>

        </div>


        {/* Refunds */}

        <div className="mb-6">

          <div className="flex items-center justify-between mb-3">

            <h3 className="text-xs font-medium">
              Refund Requests
            </h3>

            <span className="text-[10px] text-zinc-600">
              {refunds.length}
            </span>

          </div>


          {refunds.length === 0 ? (

            <div className="border border-dashed border-zinc-800 rounded-xl p-4 text-center">

              <p className="text-[10px] text-zinc-700">
                No refund requests
              </p>

            </div>

          ) : (

            <div className="space-y-2">

              {refunds.map((refund) => (

                <div
                  key={refund.refund_id}
                  className="border border-zinc-800 rounded-xl p-3"
                >

                  <div className="flex justify-between">

                    <span className="text-[10px] text-zinc-500">
                      {refund.refund_id}
                    </span>

                    <span className="text-[10px] text-yellow-400">
                      {refund.status}
                    </span>

                  </div>

                  <p className="text-xs mt-2">
                    {refund.currency}
                    {refund.amount.toFixed(2)}
                  </p>

                  <p className="text-[10px] text-zinc-600 mt-1">
                    {refund.transaction_id}
                  </p>

                </div>

              ))}

            </div>

          )}

        </div>


        {/* Tickets */}

        <div>

          <div className="flex items-center justify-between mb-3">

            <h3 className="text-xs font-medium">
              Support Tickets
            </h3>

            <span className="text-[10px] text-zinc-600">
              {tickets.length}
            </span>

          </div>


          {tickets.length === 0 ? (

            <div className="border border-dashed border-zinc-800 rounded-xl p-4 text-center">

              <p className="text-[10px] text-zinc-700">
                No support tickets
              </p>

            </div>

          ) : (

            <div className="space-y-2">

              {tickets.map((ticket) => (

                <div
                  key={ticket.ticket_id}
                  className="border border-zinc-800 rounded-xl p-3"
                >

                  <div className="flex justify-between">

                    <span className="text-[10px] text-zinc-500">
                      {ticket.ticket_id}
                    </span>

                    <span className="text-[10px] text-blue-400">
                      {ticket.status}
                    </span>

                  </div>

                  <p className="text-xs text-zinc-400 mt-2">
                    {ticket.issue}
                  </p>

                  <p className="text-[10px] text-zinc-700 mt-2">
                    {formatDate(ticket.created_at)}
                  </p>

                </div>

              ))}

            </div>

          )}

        </div>

      </aside>

    </main>
  );
}