import logging

from ..llm.client import LLMClient
from .mcp_server_loader import MCPServerRepository

logger = logging.getLogger(__name__)
if __name__ == "__main__":
    client = LLMClient().native_client
    client.api_version = "2025-03-01-preview"
    mcp_repo = MCPServerRepository()
    resp = client.responses.create(
        model="gpt-4.1",
        tools=[mcp_repo.get_server_info("tavily")],
        input="who is KKR?",
    )
    print(resp.output_text)
