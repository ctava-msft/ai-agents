import asyncio
import os
import jwt
from dotenv import load_dotenv
from azure.identity import (
    DefaultAzureCredential,
    InteractiveBrowserCredential
)
from azure.ai.projects.models import (
    FileSearchTool,
    OpenAIFile,
    VectorStore
)
from semantic_kernel.agents.azure_ai import AzureAIAgent, AzureAIAgentSettings
from semantic_kernel.contents.chat_message_content import ChatMessageContent
from semantic_kernel.contents.utils.author_role import AuthorRole

async def main() -> None:
    load_dotenv()
    ai_agent_settings = AzureAIAgentSettings.create()

    # Load forced tenant from environment variable (e.g., AZURE_FORCED_TENANT_ID)
    forced_tenant_id = os.getenv("AZURE_FORCED_TENANT_ID")
    if forced_tenant_id:
        print(f"Forcing tenant: {forced_tenant_id}")
        credential = InteractiveBrowserCredential(tenant_id=forced_tenant_id)
    else:
        credential = DefaultAzureCredential()

    async with AzureAIAgent.create_client(
        credential,
        conn_str=ai_agent_settings.project_connection_string.get_secret_value(),
    ) as client:
        file_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.realpath(__file__))), "ai-agents", "files", "data.html"
        )

        # Wrap file upload to catch authentication errors
        try:
            file: OpenAIFile = await client.agents.upload_file_and_poll(file_path=file_path, purpose="assistants")
        except Exception as err:
            # Check for unauthorized error
            if "Unauthorized" in str(err):
                print("Authentication failed. Please verify that AZURE_OPENAI_KEY is correctly set and valid.")
            raise

        vector_store: VectorStore = await client.agents.create_vector_store_and_poll(
            file_ids=[file.id], name="my_vectorstore"
        )

        # Create file search tool with resources followed by creating agent
        file_search = FileSearchTool(vector_store_ids=[vector_store.id])

        # Create agent definition with error handling for permissions issues
        try:
            agent_definition = await client.agents.create_agent(
                model=ai_agent_settings.model_deployment_name,
                tools=file_search.definitions,
                tool_resources=file_search.resources,
            )
        except Exception as err:
            if "Microsoft.MachineLearningServices/workspaces/agents/action" in str(err):
                print("Permission error: The identity does not have required permissions for Microsoft.MachineLearningServices/workspaces/agents/action actions.")
                print("Please verify that the identity (oid: identity_object_id has been assigned the proper roles in your Azure Machine Learning workspace.")
                print("Refer to https://aka.ms/azureml-auth-troubleshooting for more information.")
            raise

        # Create the AzureAI Agent
        agent = AzureAIAgent(
            client=client,
            definition=agent_definition,
        )

        # Create a new thread
        thread = await client.agents.create_thread()

        # Add user inputs and get responses
        user_inputs = [
            "How much RAM does Surface Pro 4 can support?"
        ]

        try:
            for user_input in user_inputs:
                await agent.add_chat_message(
                    thread_id=thread.id, message=ChatMessageContent(role=AuthorRole.USER, content=user_input)
                )
                print(f"# User: '{user_input}'")
                async for content in agent.invoke(thread_id=thread.id):
                    if content.role != AuthorRole.TOOL:
                        print(f"# Agent: {content.content}")
        finally:
            print(f"# Your done")
            #await client.agents.delete_thread(thread.id)
            #await client.agents.delete_agent(agent.id)


if __name__ == "__main__":
    asyncio.run(main())