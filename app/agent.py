import os, asyncio, dotenv, json, time
from datetime import datetime
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiCompatibleConfig
from wayflowcore.agentspec import AgentSpecLoader
from app.security import decrypt_key
from app.database import pool

dotenv.load_dotenv()

class MultiLLMOrchestrator:
    def __init__(self, username):
        self.username = username
        self.keys = self._get_keys()

    def _get_keys(self):
        keys = {}
        with pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute("SELECT service_name, encrypted_api_key FROM vault_credentials WHERE username = :1", [self.username])
                for row in cursor.fetchall():
                    keys[row[0]] = decrypt_key(row[1])
        return keys

    def _log_event(self, title, data, color="\033[94m"):
        reset = "\033[0m"
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"\n{color}[{timestamp}] === {title} ==={reset}")
        print(json.dumps(data, indent=2))
        print(f"{color}{'=' * (len(title) + 14)}{reset}\n")

    async def chat_stream(self, user_prompt, history=[]):
        """Asynchronous generator that yields tokens in real-time."""
        short_term_history = history[-30:]
        
        tiers = [
            {"name": "Llama 4 (Main)", "model": os.getenv("GROQ_LLM_MODEL_MAIN"), "url": os.getenv("GROQ_URL"), "key": self.keys.get("GROQ")},
            {"name": "Trinity (FailSafe)", "model": os.getenv("OPENROUTER_MODEL_FAILSAFE"), "url": os.getenv("OPENROUTER_URL"), "key": self.keys.get("OPENROUTER")},
            {"name": "Llama 3.1 8B (Final)", "model": os.getenv("GROQ_MODEL_FAILSAFE"), "url": os.getenv("GROQ_URL"), "key": self.keys.get("GROQ")}
        ]

        loader = AgentSpecLoader()
        
        for tier in tiers:
            if not tier["key"]: continue
            
            start_time = time.time()
            self._log_event(f"STREAM START: {tier['name']}", {
                "user": self.username,
                "model": tier["model"],
                "history_active": f"{len(short_term_history)}/30"
            }, color="\033[93m")

            try:
                os.environ["OPENAI_API_KEY"] = tier["key"]
                config = OpenAiCompatibleConfig(
                    name=tier["name"], 
                    model_id=tier["model"], 
                    url=tier["url"], 
                    api_key=tier["key"]
                )
                
                agent_def = Agent(
                    name="Assistant", 
                    llm_config=config, 
                    system_prompt="You are a helpful assistant made by Atharva Sankhe to demo Tool Calling ability of Agentspec Agents."
                )
                
                runtime = loader.load_component(agent_def)
                conversation = runtime.start_conversation()
                
                for msg in short_term_history:
                    if msg['role'] == 'user': conversation.append_user_message(msg['text'])
                    else: conversation.append_agent_message(msg['text'])
                
                conversation.append_user_message(user_prompt)

                # Use WayFlow's execute_async to get a stream of chunks
                full_reply = ""
                async for event in runtime.execute_async(conversation):
                    # In WayFlow, tokens are usually in the event.content
                    if hasattr(event, 'content') and event.content:
                        token = event.content
                        full_reply += token
                        yield token  # Actual token streaming
                
                latency = round(time.time() - start_time, 2)
                self._log_event(f"STREAM COMPLETE: {tier['name']}", {
                    "latency": f"{latency}s",
                    "total_length": len(full_reply)
                }, color="\033[92m")
                
                return # Exit the tier loop on success

            except Exception as e:
                self._log_event(f"STREAM ERROR: {tier['name']}", {"error": str(e)}, color="\033[91m")
                continue # Try next tier
        
        yield "ERROR: All models failed to respond."