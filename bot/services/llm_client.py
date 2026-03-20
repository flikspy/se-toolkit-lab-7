"""LLM client with tool calling support."""

import json
import sys
from typing import Any

import httpx


class LLMClient:
    """LLM client that supports tool calling.
    
    Sends user messages with tool definitions to the LLM,
    parses tool calls, executes them, and feeds results back.
    """
    
    def __init__(self, api_key: str, base_url: str, model: str) -> None:
        """Initialize the LLM client.
        
        Args:
            api_key: API key for authentication.
            base_url: Base URL of the LLM API.
            model: Model name to use.
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )
    
    def chat_with_tools(
        self,
        messages: list[dict],
        tools: list[dict],
        max_iterations: int = 5,
        lms_client=None,
    ) -> str:
        """Chat with the LLM using tool calling.
        
        Args:
            messages: Conversation history with user message.
            tools: List of tool definitions (JSON schemas).
            max_iterations: Maximum tool call iterations.
            lms_client: Optional LMS client for tool execution.
            
        Returns:
            Final response from the LLM.
        """
        global _lms_client_for_tools
        if lms_client:
            _lms_client_for_tools = lms_client
        
        conversation = list(messages)
        
        for iteration in range(max_iterations):
            print(f"[loop] Iteration {iteration + 1}/{max_iterations}", file=sys.stderr)
            
            # Call LLM
            response = self._call_llm(conversation, tools)
            
            # Check for tool calls
            tool_calls = self._parse_tool_calls(response)
            
            if not tool_calls:
                # No tool calls — return the response
                return response.get("content", "I don't have information about that.")
            
            # Execute tool calls
            tool_results = []
            for tool_call in tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call.get("arguments", {})
                
                print(f"[tool] LLM called: {tool_name}({tool_args})", file=sys.stderr)
                
                # Execute the tool
                result = self._execute_tool(tool_name, tool_args)
                tool_results.append({
                    "name": tool_name,
                    "arguments": tool_args,
                    "result": result,
                })
                
                print(f"[tool] Result: {str(result)[:100]}...", file=sys.stderr)
            
            # Feed tool results back to LLM
            print(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM", file=sys.stderr)
            
            # Add assistant message with tool calls
            assistant_message = {
                "role": "assistant",
                "content": "",
                "tool_calls": [
                    {
                        "id": f"call_{i}",
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"]),
                        },
                    }
                    for i, tc in enumerate(tool_calls)
                ],
            }
            conversation.append(assistant_message)
            
            # Add tool results
            for i, tr in enumerate(tool_results):
                conversation.append({
                    "role": "tool",
                    "tool_call_id": f"call_{i}",
                    "content": json.dumps(tr["result"], default=str),
                })
        
        # Max iterations reached — ask LLM to summarize
        conversation.append({
            "role": "user",
            "content": "Please provide a final answer based on the tool results above.",
        })
        
        response = self._call_llm(conversation, [])
        return response.get("content", "I couldn't process your request.")
    
    def _call_llm(self, messages: list[dict], tools: list[dict]) -> dict:
        """Call the LLM API.
        
        Args:
            messages: Conversation history.
            tools: Tool definitions (empty for final response).
            
        Returns:
            LLM response message.
        """
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = "auto"
        
        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        
        return data["choices"][0]["message"]
    
    def _parse_tool_calls(self, message: dict) -> list[dict]:
        """Parse tool calls from LLM response.
        
        Args:
            message: LLM response message.
            
        Returns:
            List of tool calls with name and arguments.
        """
        tool_calls = message.get("tool_calls", [])
        
        if not tool_calls:
            # Check if there's a function_call (older API format)
            if "function_call" in message:
                fc = message["function_call"]
                return [{
                    "name": fc.get("name", ""),
                    "arguments": json.loads(fc.get("arguments", "{}")),
                }]
            return []
        
        result = []
        for tc in tool_calls:
            func = tc.get("function", {})
            try:
                args = json.loads(func.get("arguments", "{}"))
            except json.JSONDecodeError:
                args = {}
            
            result.append({
                "name": func.get("name", ""),
                "arguments": args,
            })
        
        return result
    
    def _execute_tool(self, name: str, arguments: dict) -> Any:
        """Execute a tool by name.
        
        Args:
            name: Tool name.
            arguments: Tool arguments.
            
        Returns:
            Tool execution result.
        """
        # Import here to avoid circular imports
        from services.lms_api import get_lms_client
        
        # Get the global LMS client
        # The client should be initialized by the LLMClient caller
        global _lms_client_for_tools
        if _lms_client_for_tools is None:
            return {"error": "LMS client not initialized"}
        
        tools = {
            "get_items": _lms_client_for_tools.get_items,
            "get_learners": _lms_client_for_tools.get_learners,
            "get_scores": lambda lab: _lms_client_for_tools.get_scores(lab),
            "get_pass_rates": lambda lab: _lms_client_for_tools.get_pass_rates(lab),
            "get_timeline": lambda lab: _lms_client_for_tools.get_timeline(lab),
            "get_groups": lambda lab: _lms_client_for_tools.get_groups(lab),
            "get_top_learners": lambda lab, limit=5: _lms_client_for_tools.get_top_learners(lab, limit),
            "get_completion_rate": lambda lab: _lms_client_for_tools.get_completion_rate(lab),
            "trigger_sync": _lms_client_for_tools.trigger_sync,
        }
        
        if name not in tools:
            return {"error": f"Unknown tool: {name}"}
        
        try:
            return tools[name](**arguments)
        except Exception as e:
            return {"error": str(e)}
    
    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()


# Global client instance
_client: LLMClient | None = None
_lms_client_for_tools: Any = None


def get_llm_client(api_key: str, base_url: str, model: str) -> LLMClient:
    """Get or create the global LLM client.
    
    Args:
        api_key: API key for authentication.
        base_url: Base URL of the LLM API.
        model: Model name to use.
        
    Returns:
        LLMClient instance.
    """
    global _client
    if _client is None:
        _client = LLMClient(api_key, base_url, model)
    return _client
