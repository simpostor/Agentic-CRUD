import asyncio
import os
import dotenv
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiCompatibleConfig
from wayflowcore.agentspec import AgentSpecLoader

dotenv.load_dotenv()

async def run_openrouter_chat():
    # 1. OpenRouter Auth Setup
    or_key = os.getenv("OPENROUTER_API_KEY")
    or_model = os.getenv("OPENROUTER_MODEL")
    
    if not or_key:
        print("❌ Error: OPENROUTER_API_KEY not found in .env")
        return

    # OpenRouter requires the key in the OPENAI_API_KEY env var for compatibility
    os.environ["OPENAI_API_KEY"] = or_key
    print(f"✅ OpenRouter Active: {or_model}")

    # 2. Agent Spec Config (Pointing to OpenRouter)
    llm_config = OpenAiCompatibleConfig(
        name="OpenRouter-Config",
        model_id=or_model,
        url="https://openrouter.ai/api/v1", # OpenRouter's V1 endpoint
        api_key=or_key
    )

    agent_def = Agent(
        name="OpenRouterAgent",
        llm_config=llm_config,
        system_prompt="You are a helpful assistant running via OpenRouter."
    )

    # 3. Initialize WayFlow Runtime
    loader = AgentSpecLoader()
    runtime_agent = loader.load_component(agent_def)
    conversation = runtime_agent.start_conversation()

    # 4. Chat Loop
    print(f"--- Chat Session Started (Type 'exit' to stop) ---")
    while True:
        user_input = input("\nYOU >>> ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Closing OpenRouter session. Goodbye!")
            break

        conversation.append_user_message(user_input)
        
        print(f"🤖 OpenRouter is thinking ({or_model})...")
        
        # WayFlow handles the API call and message management
        runtime_agent.execute(conversation)

        # Print the response
        last_msg = conversation.get_last_message()
        if last_msg:
            print(f"\nASSISTANT >>> {last_msg.content}")
        else:
            print("⚠️ No response received from OpenRouter.")

if __name__ == "__main__":
    try:
        asyncio.run(run_openrouter_chat())
    except KeyboardInterrupt:
        print("\nSession ended.")