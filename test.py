import asyncio
import os
import dotenv
from pyagentspec.agent import Agent
from pyagentspec.llms import OpenAiCompatibleConfig
from wayflowcore.agentspec import AgentSpecLoader

dotenv.load_dotenv()

async def run_chat():
    # 1. Auth Setup
    gemini_key = os.getenv("GEMINI_API_KEY")
    os.environ["OPENAI_API_KEY"] = gemini_key
    print(f"✅ Gemini Session Active. Type 'exit' to stop.")

    # 2. Agent Spec Config
    llm_config = OpenAiCompatibleConfig(
        name="Gemini-Lite-Config",
        model_id="gemini-2.5-flash-lite",
        url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=gemini_key
    )

    agent_def = Agent(
        name="GeminiTester",
        llm_config=llm_config,
        system_prompt="You are a helpful assistant"
    )

    # 3. Initialize Runtime
    loader = AgentSpecLoader()
    runtime_agent = loader.load_component(agent_def)
    conversation = runtime_agent.start_conversation()

    # 4. Chat Loop
    while True:
        user_input = input("\nYOU >>> ")
        
        if user_input.lower() in ["exit", "quit", "q"]:
            print("Closing session. Goodbye!")
            break

        conversation.append_user_message(user_input)
        
        print("🤖 Thinking...")
        # WayFlow execution
        runtime_agent.execute(conversation)

        # Print result
        last_msg = conversation.get_last_message()
        print(f"\nASSISTANT >>> {last_msg.content}")

if __name__ == "__main__":
    try:
        asyncio.run(run_chat())
    except KeyboardInterrupt:
        print("\nSession ended.")