import sys
import os
import logging

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from app.semantic.mapper import SemanticMapper

def test_resolver():
    logging.basicConfig(level=logging.INFO)
    
    # Paths (using absolute for safety)
    ontology_path = os.path.abspath("app/semantic/protocols.owl")
    
    mapper = SemanticMapper(ontology_path)
    
    source_data = {
        "user_info": {
            "name": "John Doe",
            "email": "john@example.com"
        },
        "payload": {
            "timestamp": "2024-03-20T10:00:00Z"
        }
    }
    
    source_schema = {
        "type": "object",
        "properties": {
            "user_info": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "email": {"type": "string"}
                }
            },
            "payload": {
                "type": "object",
                "properties": {
                    "timestamp": {"type": "string"}
                }
            }
        },
        "required": ["user_info", "payload"]
    }
    
    target_schema = {
        "type": "object",
        "properties": {
            "profile": {
                "type": "object",
                "properties": {
                    "fullname": {"type": "string"}
                }
            }
        }
    }
    
    print("Testing DataSiloResolver...")
    try:
        resolved_data = mapper.DataSiloResolver(
            source_data, 
            source_schema, 
            target_schema, 
            source_protocol="A2A", 
            target_protocol="MCP"
        )
        print("\nResolved Data:")
        import json
        print(json.dumps(resolved_data, indent=2))
        
        assert "profile.fullname" in resolved_data
        assert resolved_data["profile.fullname"] == "John Doe"
        assert "data_bundle.iso_date" in resolved_data
        print("\nTest PASSED!")
    except Exception as e:
        print(f"\nTest FAILED: {e}")

if __name__ == "__main__":
    test_resolver()
