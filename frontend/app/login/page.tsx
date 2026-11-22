"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";

export default function LoginPage() {
  const router = useRouter();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [register, setRegister] = useState(false);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();

    setLoading(true);
    setError("");

    try {
      const endpoint = register
        ? "/auth/register"
        : "/auth/login";

      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ email, password }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || data.error || "Authentication failed.");
      }

      localStorage.setItem(
        "supportflow_token",
        data.access_token
      );

      router.push("/");
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong."
      );
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="min-h-screen bg-[#09090b] text-white flex items-center justify-center p-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md bg-zinc-900 border border-zinc-800 rounded-2xl p-8"
      >
        <h1 className="text-2xl font-bold mb-2">
          SupportFlow AI
        </h1>

        <p className="text-zinc-400 text-sm mb-8">
          {register ? "Create your account" : "Welcome back"}
        </p>

        <label className="text-sm">Email</label>

        <input
          type="email"
          required
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full mt-2 mb-5 p-3 rounded-lg bg-black border border-zinc-700"
        />

        <label className="text-sm">Password</label>

        <input
          type="password"
          required
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full mt-2 mb-5 p-3 rounded-lg bg-black border border-zinc-700"
        />

        {error && (
          <p className="text-red-400 text-sm mb-4">
            {error}
          </p>
        )}

        <button
          disabled={loading}
          className="w-full bg-white text-black rounded-lg p-3 font-semibold"
        >
          {loading
            ? "Please wait..."
            : register
            ? "Create account"
            : "Sign in"}
        </button>

        <button
          type="button"
          onClick={() => setRegister(!register)}
          className="w-full mt-5 text-sm text-zinc-400"
        >
          {register
            ? "Already have an account? Sign in"
            : "New customer? Create an account"}
        </button>
      </form>
    </main>
  );
}