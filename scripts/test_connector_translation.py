import asyncio
import json
import sys
import os
from typing import Any, Dict

# Ensure app is in path
sys.path.append(os.getcwd())

# Import connectors
from app.messaging.connectors.claude import ClaudeConnector
from app.messaging.connectors.perplexity import PerplexityConnector
from app.messaging.connectors.slack import SlackConnector
from app.messaging.connectors.openclaw import OpenClawConnector
from app.messaging.connectors.mirofish import MiroFishConnector

async def test_connector_translation(name: str, connector: Any, task: Dict[str, Any], mock_tool_response: Dict[str, Any]):
    print(f"\n{'='*20} {name} {'='*20}")
    
    # 1. Test translation to tool format
    print(f"Task Input (MCP): {json.dumps(task, indent=2)}")
    tool_request = connector.translate_to_tool(task)
    print(f"Translated to {name} API: {json.dumps(tool_request, indent=2)}")
    
    # 2. Test translation from tool format
    print(f"\nTool Response: {json.dumps(mock_tool_response, indent=2)}")
    engram_response = connector.translate_from_tool(mock_tool_response)
    print(f"Translated to Engram Response: {json.dumps(engram_response, indent=2)}")
    
    # Validation logic
    status = "PASSED"
    errors = []
    
    if name == "CLAUDE":
        if "messages" not in tool_request: errors.append("Missing 'messages' in tool request")
        if engram_response.get("status") != "success": errors.append("Engram response status is not 'success'")
        if "content" not in engram_response.get("payload", {}): errors.append("Missing 'content' in engram payload")
    
    elif name == "PERPLEXITY":
        if "messages" not in tool_request: errors.append("Missing 'messages' in tool request")
        if engram_response.get("status") != "success": errors.append("Engram response status is not 'success'")
        if "citations" not in engram_response.get("payload", {}): errors.append("Missing 'citations' in engram payload")
        
    elif name == "SLACK":
        if "channel" not in tool_request: errors.append("Missing 'channel' in tool request")
        if "text" not in tool_request: errors.append("Missing 'text' in tool request")
        if engram_response.get("status") != "success" and mock_tool_response.get("ok"): 
            errors.append("Incorrect error status for successful slack response")
        
    elif name == "OPENCLAW":
        if tool_request.get("payload") != task: errors.append("Task was not correctly passed in OpenClaw payload")
        if engram_response.get("status") != "success": errors.append("Engram response status is not 'success'")
        
    elif name == "MIROFISH":
        if "seedText" not in tool_request: errors.append("Missing 'seedText' in tool request")
        if engram_response.get("status") != "success": errors.append("Engram response status is not 'success'")

    if errors:
        status = "FAILED"
        for err in errors:
            print(f"ERROR: {err}")
    
    print(f"\nResult: {status}")
    return status == "PASSED"

async def run_all_tests():
    results = {}
    
    # Claude
    claude = ClaudeConnector(api_key="sk-ant-test")
    claude_task = {"content": "Explain quantum entanglement.", "model": "claude-3-sonnet", "instructions": "Use analogies."}
    claude_mock_resp = {
        "content": [{"type": "text", "text": "Quantum entanglement is like a pair of magic dice..."}],
        "model": "claude-3-sonnet",
        "usage": {"input_tokens": 15, "output_tokens": 40}
    }
    results["CLAUDE"] = await test_connector_translation("CLAUDE", claude, claude_task, claude_mock_resp)
    
    # Perplexity
    perplexity = PerplexityConnector(api_key="pplx-test")
    perplexity_task = {"content": "What is the price of Bitcoin today?", "model": "llama-3-sonar-large"}
    perplexity_mock_resp = {
        "choices": [{"message": {"content": "Bitcoin is currently trading at $70,000."}}],
        "citations": ["https://coinmarketcap.com"],
        "model": "llama-3-sonar-large"
    }
    results["PERPLEXITY"] = await test_connector_translation("PERPLEXITY", perplexity, perplexity_task, perplexity_mock_resp)
    
    # Slack
    slack = SlackConnector(api_token="xoxb-test")
    slack_task = {"content": "Server backup completed successfully.", "channel": "#devops", "title": "Deployment Status"}
    slack_mock_resp = {"ok": True, "ts": "1711620000.000001", "channel": "C12345"}
    results["SLACK"] = await test_connector_translation("SLACK", slack, slack_task, slack_mock_resp)
    
    # OpenClaw
    openclaw = OpenClawConnector(endpoint_url="http://openclaw:8001")
    openclaw_task = {"coord": "fetch_logs", "service": "auth"}
    openclaw_mock_resp = {"status": "success", "logs": ["Login attempt at 12:00", "Token issued"]}
    results["OPENCLAW"] = await test_connector_translation("OPENCLAW", openclaw, openclaw_task, openclaw_mock_resp)
    
    # MiroFish
    mirofish = MiroFishConnector(base_url="http://mirofish:5000")
    mirofish_task = {
        "seed_text": "large scale test", 
        "mirofish_config": {"numAgents": 500, "swarmId": "test_swarm"}
    }
    mirofish_mock_resp = {"swarm_id": "test_swarm", "status": "active", "agents_spawned": 500}
    results["MIROFISH"] = await test_connector_translation("MIROFISH", mirofish, mirofish_task, mirofish_mock_resp)
    
    print("\n" + "="*50)
    print("FINAL SUMMARY")
    print("="*50)
    for connector, passed in results.items():
        print(f"{connector:<15}: {'PASSED' if passed else 'FAILED'}")
    
    if all(results.values()):
        print("\nAll connectors passed translation tests!")
    else:
        print("\nSome connectors failed translation tests.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(run_all_tests())
