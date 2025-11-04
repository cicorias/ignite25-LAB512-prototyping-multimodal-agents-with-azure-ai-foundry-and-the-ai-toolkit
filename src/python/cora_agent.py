"""Build Agent using Microsoft Agent Framework in Python
# Run this python script
> pip install agent-framework --pre
> python <this-script-path>.py
"""

import asyncio
import os

from agent_framework import ChatAgent, MCPStdioTool, MCPStreamableHTTPTool, ToolProtocol
from agent_framework_azure_ai import AzureAIAgentClient
from azure.identity.aio import DefaultAzureCredential

from azure.ai.projects.aio import AIProjectClient
# from azure.identity import DefaultAzureCredential

### Set up for OpenTelemetry tracing ###
from agent_framework.observability import setup_observability
### Set up for OpenTelemetry tracing ###


os.environ["AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED"] = "true"
os.environ["AZURE_SDK_TRACING_IMPLEMENTATION"] = "opentelemetry"

# Azure AI Foundry Agent Configuration
ENDPOINT = "https://lab512-scicoria.services.ai.azure.com/api/projects/lab512"
MODEL_DEPLOYMENT_NAME = "gpt-5-mini"

AGENT_NAME = "mcp-agent"
AGENT_INSTRUCTIONS = "You are Cora, an intelligent and friendly AI assistant for Zava, a home improvement brand. You help customers with their DIY projects by understanding their needs and recommending the most suitable products from Zava’s catalog.​\n\nYour role is to:​\n\n- Engage with the customer in natural conversation to understand their DIY goals.​\n\n- Ask thoughtful questions to gather relevant project details.​\n\n- Be brief in your responses.​\n\n- Provide the best solution for the customer's problem and only recommend a relevant product within Zava's product catalog.​\n\n- Search Zava’s product database to identify 1 product that best match the customer’s needs.​\n\n- Clearly explain what each recommended Zava product is, why it’s a good fit, and how it helps with their project.​\n​\nYour personality is:​\n\n- Warm and welcoming, like a helpful store associate​\n\n- Professional and knowledgeable, like a seasoned DIY expert​\n\n- Curious and conversational—never assume, always clarify​\n\n- Transparent and honest—if something isn’t available, offer support anyway​\n\nIf no matching products are found in Zava’s catalog, say:​\n“Thanks for sharing those details! I’ve searched our catalog, but it looks like we don’t currently have a product that fits your exact needs. If you'd like, I can suggest some alternatives or help you adjust your project requirements to see if something similar might work.”​"

# User inputs for the conversation
USER_INPUTS = [
    # "Here’s a photo of my living room. Based on the lighting and layout, recommend a Zava eggshell paint.",
    "How much is Zava's eggshell paint?",
    # "What are the current inventory levels for Zava's eggshell paint?",
    # "What are the current inventory levels for Zava's eggshell paint?",
    # "What are the current inventory levels for Zava's eggshell paint?",
]

# project_client = AIProjectClient(
#      credential=DefaultAzureCredential(),
#      endpoint=ENDPOINT,
# )
# connection_string = await project_client.telemetry.get_connection_string() #.get_application_insights_connection_string()



def create_mcp_tools() -> list[ToolProtocol]:
    return [
        MCPStdioTool(
            name="VSCode Tools".replace("-", "_"),
            description="MCP server for VSCode Tools",
            command="python",
            args=[
                "mcp_server/customer_sales/customer_sales.py",
                "--stdio",
                "--RLS_USER_ID=00000000-0000-0000-0000-000000000000"
         ]
        ),
    ]

async def main() -> None:
    ### Set up for OpenTelemetry tracing ###
    setup_observability(
        otlp_endpoint="http://aspire-dashboard:18889",  # AI Toolkit gRPC endpoint
        enable_sensitive_data=True  # Enable capturing prompts and completions
    )
    ### Set up for OpenTelemetry tracing ###
    
    async with (
        DefaultAzureCredential() as credential,
        ChatAgent(
            chat_client=AzureAIAgentClient(
                project_endpoint=ENDPOINT,
                model_deployment_name=MODEL_DEPLOYMENT_NAME,
                async_credential=credential,
                agent_name=AGENT_NAME,
                agent_id=None,  # Since no Agent ID is provided, the agent will be automatically created and deleted after getting response
            ),
            instructions=AGENT_INSTRUCTIONS,
            tools=create_mcp_tools(),
        ) as agent
        # AIProjectClient(
        #     credential=credential,
        #     endpoint=ENDPOINT,
        # ) as project_client
        
    ):
        # Create a new thread that will be reused
        thread = agent.get_new_thread()

        # Process user messages
        await run_prompts(agent, thread)
        
        print("\n--- All tasks completed successfully ---")

    # Give additional time for all async cleanup to complete
    await asyncio.sleep(1.0)

async def run_prompts(agent, thread):
    for user_input in USER_INPUTS:
        print(f"\n# User: '{user_input}'")
        async for chunk in agent.run_stream([user_input], thread=thread):
            if chunk.text:
                print(chunk.text, end="")
            elif (
                    chunk.raw_representation
                    and chunk.raw_representation.raw_representation
                    and hasattr(chunk.raw_representation.raw_representation, "status")
                    and hasattr(chunk.raw_representation.raw_representation, "type")
                    and chunk.raw_representation.raw_representation.status == "completed"
                    and hasattr(chunk.raw_representation.raw_representation, "step_details")
                    and hasattr(chunk.raw_representation.raw_representation.step_details, "tool_calls")
                ):
                print("")
                print("Tool calls: ", chunk.raw_representation.raw_representation.step_details.tool_calls)
        print("")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nProgram interrupted by user")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("Program finished.")
