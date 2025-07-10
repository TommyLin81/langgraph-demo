import pytest
from langchain_core.messages import HumanMessage

from agent import graph
from agent.state import AgentState

pytestmark = pytest.mark.anyio


@pytest.mark.langsmith
async def test_agent_simple_passthrough() -> None:
    inputs = AgentState(messages=[HumanMessage(content="What is AWS Lambda?")])
    res = await graph.ainvoke(inputs)
    assert res is not None
    assert "messages" in res
    assert len(res["messages"]) > 0
