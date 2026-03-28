import os
import uuid
from engram_sdk import EngramSDK

def run_translation_demo():
    # Initialize SDK (assumes backend is running locally)
    sdk = EngramSDK(
        base_url="http://localhost:8000/api/v1",
        agent_id=str(uuid.uuid4()),
        supported_protocols=["A2A"]
    )
    
    # Example A2A payload to be translated to MCP
    a2a_payload = {
        "id": "task_001",
        "payload": {
            "intent": "dispatch",
            "delivery_window": {
                "start": "2026-03-30T09:00:00Z",
                "end": "2026-03-30T11:00:00Z"
            }
        },
        "data": {
            "task": "logistics_thermal_check"
        }
    }
    
    print(f"Original A2A Payload:\n{a2a_payload}\n")
    
    # Use the Translation Layer to convert A2A -> MCP
    try:
        # Note: Sandbox / Playground doesn't require a real agent registry
        # but the standard /translate does. Let's try playground first.
        response = sdk.translation.playground_translate(
            payload=a2a_payload,
            source_protocol="A2A",
            target_protocol="MCP"
        )
        
        print(f"Translation Response Message: {response.message}")
        print(f"Translated MCP Payload:\n{response.payload}\n")
        
        # Demonstrating integration with TaskClient (Beta/Enterprise mode)
        # Developers can also call .translate() directly from the SDK main class
        # response = sdk.translate(a2a_payload, source_protocol="A2A", target_protocol="MCP", beta=True)
        # print("Beta Translation:", response)
        
    except Exception as e:
        print(f"Translation Error: {e}")
        print("Note: Ensure the Engram backend is running at http://localhost:8000")

if __name__ == "__main__":
    run_translation_demo()
