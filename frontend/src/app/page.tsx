"use client";
import { useState, useEffect } from 'react';

const BACKEND_URL = "http://103.59.213.189:2112";

export default function AgenticApp() {
  const [user, setUser] = useState("");
  const [pass, setPass] = useState("");
  const [view, setView] = useState("login"); 
  const [messages, setMessages] = useState<{role: string, text: string}[]>([]);
  const [employees, setEmployees] = useState<any[]>([]);
  const [status, setStatus] = useState("Ready 🟢");

  // --- Utility Functions ---

  const fetchEmployees = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/employees`);
      const data = await res.json();
      setEmployees(data);
    } catch (e) {
      console.error("Failed to fetch employees");
    }
  };

  const handleAuth = async () => {
    try {
      const res = await fetch(`${BACKEND_URL}/auth/login`, {
        method: "POST", 
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username: user, password: pass})
      });
      const data = await res.json();

      if (res.ok) {
        const keyCheck = await fetch(`${BACKEND_URL}/user/check-keys/${user}`);
        const keyData = await keyCheck.json();
        setView(keyData.has_keys ? "chat" : "setup");
      } else {
        alert(data.detail || "Login failed.");
      }
    } catch (e) {
      alert("Cannot connect to backend.");
    }
  };

  const saveKey = async (svc: string, inputId: string) => {
    const key = (document.getElementById(inputId) as HTMLInputElement).value;
    if (!key) return;

    const res = await fetch(`${BACKEND_URL}/vault/save`, {
      method: "POST", 
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({username: user, service_name: svc, api_key: key})
    });
    if (res.ok) {
      setStatus(`${svc} Key Saved!`);
      (document.getElementById(inputId) as HTMLInputElement).value = "";
    }
  };

  const sendMessage = async () => {
    const input = document.getElementById('msg') as HTMLInputElement;
    if (!input.value) return;

    const userText = input.value;
    const currentHistory = [...messages, {role: 'user', text: userText}];
    setMessages(currentHistory);
    input.value = "";
    setStatus("Thinking... 🤖");

    try {
      const res = await fetch(`${BACKEND_URL}/chat`, {
        method: "POST", 
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({username: user, message: userText, history: messages})
      });
      const data = await res.json();
      
      if (data.status === "SUCCESS") {
        setMessages([...currentHistory, {role: 'bot', text: data.reply}]);
        setStatus("Ready 🟢");
      } else {
        setStatus("Failsafe failed ❌");
      }
    } catch (e) {
      setStatus("Connection Error ❌");
    }
  };

  const handleAddEmployee = async () => {
    const name = (document.getElementById('emp-name') as HTMLInputElement).value;
    const role = (document.getElementById('emp-role') as HTMLInputElement).value;
    const dept = (document.getElementById('emp-dept') as HTMLInputElement).value;
    const salInput = (document.getElementById('emp-sal') as HTMLInputElement).value;

    if (!name || !salInput) return;

    try {
      const res = await fetch(`${BACKEND_URL}/employees`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({
          name: name,
          role: role,
          department: dept,
          salary: parseFloat(salInput) // Crucial: Fixes 422 by sending a number
        })
      });

      if (res.ok) {
        fetchEmployees();
        // Clear inputs
        ['emp-name', 'emp-role', 'emp-dept', 'emp-sal'].forEach(id => {
          (document.getElementById(id) as HTMLInputElement).value = "";
        });
      }
    } catch (e) {
      console.error("Failed to add employee");
    }
  };

  return (
    <main className="min-h-screen bg-black text-white flex flex-col items-center p-6">
      <div className="w-full max-w-md space-y-6 mt-10">
        
        {/* VIEW: LOGIN */}
        {view === "login" && (
          <div className="bg-zinc-900 p-8 rounded-3xl border border-zinc-800 space-y-4 shadow-2xl">
            <h1 className="text-3xl font-bold text-center">Vault</h1>
            <input placeholder="Username" onChange={e=>setUser(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleAuth()} className="w-full p-4 bg-black rounded-xl border border-zinc-800 outline-none" />
            <input type="password" placeholder="Password" onChange={e=>setPass(e.target.value)} onKeyDown={e => e.key === 'Enter' && handleAuth()} className="w-full p-4 bg-black rounded-xl border border-zinc-800 outline-none" />
            <button onClick={handleAuth} className="w-full p-4 bg-blue-600 rounded-xl font-bold hover:bg-blue-500">Login / Sign Up</button>
          </div>
        )}

        {/* VIEW: SETUP */}
        {view === "setup" && (
          <div className="bg-zinc-900 p-8 rounded-3xl border border-zinc-800 space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-xl font-bold">Configure Vault</h1>
                <button onClick={()=>setView("chat")} className="text-zinc-500 text-sm px-4 py-2 border border-zinc-800 rounded-xl">Skip to Chat</button>
            </div>
            <div className="space-y-3">
              <label className="text-xs text-zinc-500 font-bold uppercase">Groq Cloud</label>
              <div className="flex gap-2">
                <input id="key-groq" type="password" placeholder="gsk_..." className="flex-1 p-3 bg-black rounded-xl border border-zinc-800 text-sm" />
                <button onClick={()=>saveKey("GROQ", "key-groq")} className="px-4 bg-orange-600 rounded-xl font-bold text-xs">Save</button>
              </div>
            </div>
            <div className="space-y-3">
              <label className="text-xs text-zinc-500 font-bold uppercase">OpenRouter</label>
              <div className="flex gap-2">
                <input id="key-or" type="password" placeholder="sk-or-..." className="flex-1 p-3 bg-black rounded-xl border border-zinc-800 text-sm" />
                <button onClick={()=>saveKey("OPENROUTER", "key-or")} className="px-4 bg-purple-600 rounded-xl font-bold text-xs">Save</button>
              </div>
            </div>
            <p className="text-center text-xs text-green-500 font-mono">{status}</p>
          </div>
        )}

        {/* VIEW: CHAT */}
        {view === "chat" && (
          <div className="h-[85vh] flex flex-col space-y-4">
             <div className="flex justify-between items-center px-2">
                <h2 className="font-bold text-zinc-400">Agent: <span className="text-white">Active</span></h2>
                <div className="flex gap-2">
                    <button onClick={() => { fetchEmployees(); setView("crud"); }} className="text-xs bg-blue-600 px-3 py-1 rounded-full">Manual CRUD</button>
                    <button onClick={()=>setView("setup")} className="text-xs bg-zinc-800 px-3 py-1 rounded-full">Vault</button>
                </div>
             </div>
             <div className="flex-1 overflow-y-auto bg-zinc-900/40 rounded-3xl p-4 space-y-4 border border-zinc-800/50 backdrop-blur-md">
                {messages.map((m, i) => (
                    <div key={i} className={`p-4 rounded-2xl max-w-[85%] text-sm ${m.role === 'user' ? 'ml-auto bg-blue-600' : 'bg-zinc-800 border border-zinc-700'}`}>{m.text}</div>
                ))}
             </div>
             <div className="flex gap-2 bg-zinc-900 p-2 rounded-2xl border border-zinc-800">
                <input id="msg" onKeyDown={(e) => e.key === 'Enter' && sendMessage()} placeholder="Message..." className="flex-1 p-3 bg-transparent outline-none text-sm" />
                <button onClick={sendMessage} className="p-3 bg-white text-black rounded-xl font-bold">SEND</button>
             </div>
          </div>
        )}

        {/* VIEW: CRUD */}
        {view === "crud" && (
          <div className="space-y-6">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold">Directory</h1>
              <button onClick={() => setView("chat")} className="text-xs bg-zinc-800 px-4 py-2 rounded-xl">Back to Agent</button>
            </div>
            
            <div className="bg-zinc-900 p-6 rounded-3xl border border-zinc-800 space-y-4">
              <div className="grid grid-cols-2 gap-2">
                <input id="emp-name" placeholder="Name" className="p-3 bg-black rounded-xl border border-zinc-800 text-sm" />
                <input id="emp-role" placeholder="Role" className="p-3 bg-black rounded-xl border border-zinc-800 text-sm" />
                <input id="emp-dept" placeholder="Dept" className="p-3 bg-black rounded-xl border border-zinc-800 text-sm" />
                <input id="emp-sal" type="number" placeholder="Salary" className="p-3 bg-black rounded-xl border border-zinc-800 text-sm" />
              </div>
              <button onClick={handleAddEmployee} className="w-full p-3 bg-green-600 rounded-xl font-bold">Add to Oracle DB</button>
            </div>

            <div className="space-y-2 max-h-[40vh] overflow-y-auto">
              {employees.length === 0 && <p className="text-center text-zinc-600">No employees found in DB.</p>}
              {employees.map(emp => (
                <div key={emp.id} className="flex justify-between items-center p-4 bg-zinc-900 rounded-2xl border border-zinc-800">
                  <div>
                    <p className="font-bold text-sm">{emp.name}</p>
                    <p className="text-[10px] text-zinc-500 uppercase font-bold">{emp.role} • {emp.department} • ${emp.salary}</p>
                  </div>
                  <button onClick={async () => {
                    await fetch(`${BACKEND_URL}/employees/${emp.id}`, { method: "DELETE" });
                    fetchEmployees();
                  }} className="text-red-500 text-xs font-bold">Delete</button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </main>
  );
}