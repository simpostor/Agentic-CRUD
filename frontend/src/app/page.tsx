"use client";
import { useState } from 'react';

export default function VaultPage() {
  const [status, setStatus] = useState("Status: Ready 🟢");

  const saveToVault = async (service: string) => {
    const keyInput = document.getElementById('api-key') as HTMLInputElement;
    const apiKey = keyInput.value;

    if (!apiKey) {
      setStatus("Error: Key is empty ⚠️");
      return;
    }

    try {
      const res = await fetch("http://192.168.0.105:8080/vault/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ service_name: service, api_key: apiKey }),
      });
      
      if (res.ok) {
        setStatus("Configured ✅");
        keyInput.value = "";
      } else {
        setStatus("Server Error ❌");
      }
    } catch (err) {
      setStatus("Connection Failed ❌");
    }
  };

  return (
    <main className="flex flex-col items-center justify-center min-h-screen bg-black text-white p-6 font-sans">
      <div className="w-full max-w-sm space-y-6">
        <h1 className="text-3xl font-bold text-center tracking-tight">Agentic Vault</h1>
        <p className="text-center text-gray-400 text-sm font-medium">{status}</p>
        
        <input 
          id="api-key"
          type="password" 
          placeholder="Enter Gemini API Key" 
          className="w-full p-4 bg-zinc-900 border border-zinc-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 transition-all"
        />
        
        <button 
          onClick={() => saveToVault("GEMINI")}
          className="w-full p-4 bg-blue-600 hover:bg-blue-500 rounded-xl font-bold transition-colors active:scale-95"
        >
          Save to Oracle 23ai
        </button>
      </div>
    </main>
  );
}