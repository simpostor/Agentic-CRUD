import asyncio
import os
import dotenv
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiCompatibleConfig
from wayflowcore.agentspec import AgentSpecLoader

dotenv.load_dotenv()

async def run_groq_chat():
    # 1. Groq Auth Setup
    groq_key = os.getenv("GROQ_API_KEY")
    groq_model = os.getenv("GROQ_MODEL",)
    
    if not groq_key:
        print("❌ Error: GROQ_API_KEY not found in .env")
        return

    # Injected for WayFlow's underlying HTTP client compatibility
    os.environ["OPENAI_API_KEY"] = groq_key
    print(f"✅ Groq Active: {groq_model}")

    # 2. Agent Spec Config (Pointing to Groq)
    # The base URL for Groq's OpenAI-compatible API is /v1
    llm_config = OpenAiCompatibleConfig(
        name="Groq-Config",
        model_id=groq_model,
        url="https://api.groq.com/openai/v1",
        api_key=groq_key
    )

    agent_def = Agent(
        name="GroqAgent",
        llm_config=llm_config,
        system_prompt="You are a helpful assistant running on Groq's high-speed inference engine."
    )

    # 3. Initialize Runtime
    loader = AgentSpecLoader()
    runtime_agent = loader.load_component(agent_def)
    conversation = runtime_agent.start_conversation()

    # 4. Chat Loop
    print(f"--- Groq Chat Started (Type 'exit' to stop) ---")
    while True:
        user_input = input("\nYOU >>> ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Closing Groq session. Goodbye!")
            break

        conversation.append_user_message(user_input)
        
        print(f"🤖 Groq is thinking ({groq_model})...")
        
        # Execute via WayFlow
        runtime_agent.execute(conversation)

        # Print result
        last_msg = conversation.get_last_message()
        if last_msg:
            print(f"\nASSISTANT >>> {last_msg.content}")
        else:
            print("⚠️ No response from Groq.")

if __name__ == "__main__":
    try:
        asyncio.run(run_groq_chat())
    except KeyboardInterrupt:
        print("\nSession ended.")