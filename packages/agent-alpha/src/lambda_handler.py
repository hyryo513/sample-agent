"""AWS Lambda handler for Agent Alpha.

This handler integrates with AWS Lambda runtime and orchestrates agent
invocation through Strands SDK. Configuration is validated at cold start
per 12-factor principles.
"""
from typing import Any, Dict
import json
import logging

from lib1 import AgentConfig
from agent_alpha import create_agent

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Cold-start initialization and configuration validation
try:
    _config = AgentConfig.from_env()
    _agent = create_agent(config=_config)
    logger.info(f"Agent Alpha initialized: {_config.agent_name}")
except Exception as e:
    logger.error(f"Cold-start initialization failed: {e}")
    _config = None
    _agent = None


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler for Agent Alpha.
    
    Args:
        event: Lambda event containing agent input.
        context: Lambda context object.
        
    Returns:
        Response dict with statusCode, headers, and body.
        
    Raises:
        ValueError: If config validation fails at cold start.
    """
    # Validate cold-start initialization
    if _agent is None or _config is None:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": "Agent initialization failed at cold start"})
        }
    
    try:
        # Extract message from event
        message = event.get("message", "default message")
        
        # Invoke Strands agent
        response = _agent.invoke(message)
        
        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "agent": _config.agent_name,
                "message": message,
                "response": response
            })
        }
    
    except Exception as e:
        logger.exception(f"Error processing request: {e}")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }
    
    finally:
        # Optional: clean shutdown (Lambda may reuse container)
        pass
