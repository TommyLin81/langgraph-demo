import os

import pytest
from langchain_core.messages import HumanMessage

from agent import graph
from agent.state import AgentState

pytestmark = pytest.mark.anyio


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_agent_simple_passthrough() -> None:
    inputs = AgentState(messages=[HumanMessage(content="What is AWS Lambda?")])
    res = await graph.ainvoke(inputs)

    # Basic structure validation
    assert res is not None
    assert "messages" in res
    assert len(res["messages"]) > 0

    # Validate routing decision
    assert "route_decision" in res
    assert res["route_decision"] == "aws_docs"

    # Validate documents were retrieved
    assert "documents" in res
    assert res["documents"] is not None
    assert len(res["documents"]) > 0

    # Validate response content
    response_content = res["messages"][-1].content
    assert isinstance(response_content, str)
    assert len(response_content.strip()) > 0
    assert "lambda" in response_content.lower()  # Should mention Lambda


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="OPENAI_API_KEY not set")
async def test_agent_direct_response() -> None:
    """Test that the agent can handle non-AWS questions with direct response."""
    inputs = AgentState(
        messages=[HumanMessage(content="What is the capital of France?")]
    )
    res = await graph.ainvoke(inputs)

    # Basic structure validation
    assert res is not None
    assert "messages" in res
    assert len(res["messages"]) > 0

    # Validate routing decision
    assert "route_decision" in res
    assert res["route_decision"] == "direct_response"

    # Validate no documents were retrieved for direct response
    assert res.get("documents") is None

    # Validate response content
    response_content = res["messages"][-1].content
    assert isinstance(response_content, str)
    assert len(response_content.strip()) > 0
    assert "paris" in response_content.lower()  # Should mention Paris
