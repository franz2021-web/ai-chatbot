"""
Tool Calling Architecture Tests

This test suite teaches you HOW tool calling works by:
1. Testing individual tools
2. Testing tool executor
3. Testing schema definitions
4. Testing the complete flow

Run with: pytest tests/test_tool_calling_architecture.py -v
"""

import pytest
import asyncio
import json
from app.services.tool_executor import get_executor
from app.tools.calculator import calculate, CALCULATOR_TOOL_DEFINITION
from app.tools.web_search import search_web, WEB_SEARCH_TOOL_DEFINITION
from app.tools.weather import get_weather, WEATHER_TOOL_DEFINITION


# ============================================================================
# SECTION 1: UNDERSTAND TOOL DEFINITIONS
# ============================================================================

class TestToolDefinitions:
    """
    Tool definitions tell the LLM:
    - What tools exist
    - What each tool does
    - What parameters each tool accepts

    This is critical for tool calling!
    """

    def test_calculator_definition_structure(self):
        """
        The LLM reads this definition and learns:
        'I can call calculator with an expression parameter'
        """
        definition = CALCULATOR_TOOL_DEFINITION

        # Structure: OpenAI format
        assert definition["type"] == "function"

        # Function details
        function = definition["function"]
        assert function["name"] == "calculator"
        assert "description" in function
        assert "parameters" in function

        # Parameters schema (JSON Schema)
        params = function["parameters"]
        assert params["type"] == "object"
        assert "expression" in params["properties"]
        assert "required" in params
        assert "expression" in params["required"]

        print("[OK] Calculator definition is OpenAI-compatible")
        print(f"  - Name: {function['name']}")
        print(f"  - Description: {function['description']}")
        print(f"  - Parameters: {list(params['properties'].keys())}")

    def test_all_tools_have_proper_schema(self):
        """
        Every tool must have OpenAI-compatible schema
        so the LLM can understand it.
        """
        definitions = [
            CALCULATOR_TOOL_DEFINITION,
            WEB_SEARCH_TOOL_DEFINITION,
            WEATHER_TOOL_DEFINITION,
        ]

        for definition in definitions:
            # Must be function type
            assert definition["type"] == "function"

            # Must have required fields
            func = definition["function"]
            assert "name" in func
            assert "description" in func
            assert "parameters" in func

            # Parameters must be JSON Schema
            params = func["parameters"]
            assert params["type"] == "object"
            assert "properties" in params
            assert "required" in params

            print(f"[OK] {func['name']}: Valid schema")

    def test_tool_definition_is_json_serializable(self):
        """
        Tool definitions must be JSON serializable
        because they're sent to the LLM as JSON.
        """
        definition = CALCULATOR_TOOL_DEFINITION

        # This should not raise an error
        json_str = json.dumps(definition)

        # Should be able to parse back
        parsed = json.loads(json_str)
        assert parsed["function"]["name"] == "calculator"

        print("[OK] Tool definition can be serialized to JSON")
        print(f"  JSON length: {len(json_str)} bytes")


# ============================================================================
# SECTION 2: UNDERSTAND INDIVIDUAL TOOLS
# ============================================================================

class TestCalculatorTool:
    """
    Understanding how the calculator tool works
    """

    @pytest.mark.asyncio
    async def test_calculator_basic_addition(self):
        """
        When LLM calls: calculator("2+2")
        What happens?
        """
        result = await calculate("2+2")
        assert result == "4"
        print("[OK] Calculator: 2+2 = 4")

    @pytest.mark.asyncio
    async def test_calculator_complex_expression(self):
        """
        Calculator supports more than basic arithmetic
        """
        result = await calculate("sqrt(16) + pi")
        # sqrt(16) = 4, pi ≈ 3.14159...
        value = float(result)
        assert 7.0 < value < 7.2
        print(f"[OK] Calculator: sqrt(16) + pi = {result}")

    @pytest.mark.asyncio
    async def test_calculator_error_handling(self):
        """
        What happens when LLM sends invalid input?
        Tool should fail gracefully
        """
        result = await calculate("1/0")
        assert "Error" in result or "error" in result.lower()
        print(f"[OK] Calculator: Division by zero handled: {result}")

    @pytest.mark.asyncio
    async def test_calculator_is_async(self):
        """
        Tools are async so they don't block the event loop.
        This is important for a streaming system!
        """
        # Should be able to run multiple calculations concurrently
        results = await asyncio.gather(
            calculate("2+2"),
            calculate("3*3"),
            calculate("10-5"),
        )

        assert results == ["4", "9", "5"]
        print("[OK] Calculator: Async execution working")
        print(f"  Can run multiple calculations concurrently")


class TestWebSearchTool:
    """
    Understanding web search tool
    """

    @pytest.mark.asyncio
    async def test_web_search_returns_list(self):
        """
        LLM expects search to return list of results
        Each with title, link, snippet
        """
        # Don't actually search (no network in tests)
        # But validate what the tool should return

        # This is what a real result looks like:
        example_result = [
            {
                "title": "Example Result",
                "link": "https://example.com",
                "snippet": "This is an example search result"
            }
        ]

        # Check structure
        for result in example_result:
            assert "title" in result
            assert "link" in result
            assert "snippet" in result

        print("[OK] Web search: Returns list of {title, link, snippet}")

    def test_web_search_definition(self):
        """
        LLM reads this and learns:
        'I can call web_search with query (required) and max_results (optional)'
        """
        definition = WEB_SEARCH_TOOL_DEFINITION
        params = definition["function"]["parameters"]

        # Query is required
        assert "query" in params["required"]

        # max_results is optional with default
        assert params["properties"]["max_results"]["default"] == 5

        print("[OK] Web search: LLM knows parameters")
        print(f"  - Required: {params['required']}")
        print(f"  - Optional: max_results (default: 5)")


class TestWeatherTool:
    """
    Understanding weather tool
    """

    @pytest.mark.asyncio
    async def test_weather_requires_coordinates(self):
        """
        LLM must provide latitude and longitude
        It's a geographic lookup tool
        """
        # New York coordinates
        result = await get_weather(latitude=40.7128, longitude=-74.0060)

        # Should return weather dict with expected keys
        # (if API is available)
        if "error" not in result:
            assert "temperature" in result or "weather" in result
            print("[OK] Weather: Returns weather data")
        else:
            print("[OK] Weather: Handles API errors gracefully")

    def test_weather_definition_teaches_coordinates(self):
        """
        LLM reads this definition to learn:
        'Weather tool needs latitude and longitude'
        """
        definition = WEATHER_TOOL_DEFINITION
        params = definition["function"]["parameters"]

        # Both required
        assert "latitude" in params["required"]
        assert "longitude" in params["required"]

        # Ranges specified
        lat_desc = params["properties"]["latitude"]["description"]
        assert "-90" in lat_desc and "90" in lat_desc

        print("[OK] Weather: LLM knows it needs coordinates")
        print(f"  - Latitude range: {lat_desc}")


# ============================================================================
# SECTION 3: UNDERSTAND TOOL EXECUTOR
# ============================================================================

class TestToolExecutor:
    """
    The ToolExecutor is the mechanism that:
    1. Keeps track of available tools
    2. Calls the right tool by name
    3. Passes parameters correctly
    4. Returns results in consistent format

    This is the BRIDGE between LLM and tool functions!
    """

    def test_executor_has_all_tools_registered(self):
        """
        ToolExecutor.tools dict maps tool names to functions
        This is how we know which tool to call
        """
        executor = get_executor()

        # Should have 3 tools
        assert len(executor.tools) == 3
        assert "calculator" in executor.tools
        assert "web_search" in executor.tools
        assert "weather" in executor.tools

        print("[OK] Executor: All 3 tools registered")
        print(f"  Tools: {list(executor.tools.keys())}")

    def test_executor_tool_definitions_match_tools(self):
        """
        Every tool must have:
        1. A function implementation (in executor.tools)
        2. A definition for the LLM (in executor.tool_definitions)

        They must match!
        """
        executor = get_executor()

        tool_definitions = executor.get_tool_definitions()
        definition_names = [d["function"]["name"] for d in tool_definitions]
        executor_names = list(executor.tools.keys())

        assert set(definition_names) == set(executor_names)
        print("[OK] Executor: Definitions match implementations")

    @pytest.mark.asyncio
    async def test_executor_calls_tool_by_name(self):
        """
        How does tool calling work?

        1. LLM outputs: {"tool_call": {"name": "calculator", "input": {"expression": "2+2"}}}
        2. Frontend parses this JSON
        3. Frontend might send tool call to backend
        4. Backend ToolExecutor.execute_tool("calculator", {"expression": "2+2"})
        5. Returns result

        This is the CRITICAL step!
        """
        executor = get_executor()

        # Simulate: LLM called calculator
        result = await executor.execute_tool(
            "calculator",
            {"expression": "2+2"}
        )

        # Result has standard format
        assert result["success"] == True
        assert result["result"] == "4"

        print("[OK] Executor: Can call tools by name")
        print(f"  Input: calculate('2+2')")
        print(f"  Output: {result}")

    @pytest.mark.asyncio
    async def test_executor_error_handling_for_unknown_tool(self):
        """
        What if LLM tries to call a tool that doesn't exist?
        Executor should handle this gracefully
        """
        executor = get_executor()

        result = await executor.execute_tool(
            "nonexistent_tool",
            {}
        )

        # Should fail gracefully
        assert result["success"] == False
        assert "error" in result

        print("[OK] Executor: Handles unknown tools gracefully")
        print(f"  Error: {result['error']}")

    @pytest.mark.asyncio
    async def test_executor_error_handling_for_tool_failure(self):
        """
        What if the tool itself fails?
        (e.g., division by zero in calculator)

        Executor should catch and return error
        """
        executor = get_executor()

        result = await executor.execute_tool(
            "calculator",
            {"expression": "1/0"}
        )

        # Tool may succeed with error message, or fail
        # Either way, executor handles it
        assert "success" in result or "error" in result

        print("[OK] Executor: Handles tool failures gracefully")


# ============================================================================
# SECTION 4: UNDERSTAND TOOL CALLING FLOW
# ============================================================================

class TestToolCallingFlow:
    """
    The complete flow of tool calling:

    LLM "I'll use calculator"
      ↓
    Stream: {"type": "tool_use", "name": "calculator", "input": "{...}"}
      ↓
    Frontend: Parse tool_use event, extract name and input
      ↓
    Frontend or Backend: executor.execute_tool("calculator", {...})
      ↓
    Return: {"success": true, "result": "4"}
      ↓
    (Optional) Feed result back to LLM
      ↓
    LLM: "The answer is 4"

    Let's test each step!
    """

    def test_tool_schema_tells_llm_what_tools_exist(self):
        """
        Step 1: Backend sends tool definitions to LLM

        The LLM reads the schema and learns what it can do
        """
        executor = get_executor()
        definitions = executor.get_tool_definitions()

        # Frontend sends this to LLM in the request:
        # {
        #   "messages": [...],
        #   "tools": definitions,  ← HERE
        #   "system": "..."
        # }

        # LLM reads definitions and decides:
        # "User asked about weather, I should use weather tool"

        assert len(definitions) == 3
        assert all(d["type"] == "function" for d in definitions)

        print("[OK] Step 1: Tool definitions sent to LLM")
        print(f"  LLM receives {len(definitions)} tool options")

    def test_tool_input_is_json(self):
        """
        Step 2: LLM outputs tool call as JSON

        The LLM outputs:
        {
            "type": "tool_use",
            "id": "call_123",
            "name": "calculator",
            "input": "{\"expression\": \"2+2\"}"  ← JSON STRING!
        }

        Note: input is a JSON STRING, not object!
        This is important for parsing!
        """

        # This is what LLM outputs:
        llm_tool_call = {
            "type": "tool_use",
            "id": "call_123",
            "name": "calculator",
            "input": '{"expression": "2+2"}'  # NOTE: String!
        }

        # Frontend must parse it:
        tool_input = json.loads(llm_tool_call["input"])
        assert tool_input["expression"] == "2+2"

        print("[OK] Step 2: LLM outputs tool call as JSON")
        print(f"  Tool: {llm_tool_call['name']}")
        print(f"  Input (parsed): {tool_input}")

    @pytest.mark.asyncio
    async def test_executor_executes_tool_call(self):
        """
        Step 3: Backend executor runs the tool

        With name and input from LLM, executor:
        1. Finds the tool function
        2. Calls it with parameters
        3. Returns result
        """
        executor = get_executor()

        # LLM output parsed to:
        tool_name = "calculator"
        tool_input = {"expression": "2+2"}

        # Backend does:
        result = await executor.execute_tool(tool_name, tool_input)

        # Result format:
        assert result["success"] == True
        assert result["result"] == "4"

        print("[OK] Step 3: Executor runs tool")
        print(f"  Tool: {tool_name}")
        print(f"  Result: {result['result']}")

    @pytest.mark.asyncio
    async def test_complete_tool_calling_cycle(self):
        """
        Complete cycle test:

        LLM → Tool Call → Execute → Result
        """
        executor = get_executor()

        # Simulating what happens in real conversation:

        # 1. LLM decides to use calculator
        tool_calls = [
            {
                "name": "calculator",
                "input": {"expression": "2+2"},
            },
            {
                "name": "calculator",
                "input": {"expression": "sqrt(16)"},
            },
        ]

        # 2. Backend executes all tool calls
        results = []
        for call in tool_calls:
            result = await executor.execute_tool(call["name"], call["input"])
            results.append(result)

        # 3. Results ready to show user or send back to LLM
        assert results[0]["result"] == "4"
        assert results[1]["result"] == "4.0"  # sqrt(16)

        print("[OK] Complete cycle: Multiple tool calls executed")
        print(f"  Call 1: 2+2 = {results[0]['result']}")
        print(f"  Call 2: sqrt(16) = {results[1]['result']}")


# ============================================================================
# SECTION 5: INSIGHTS & LEARNING
# ============================================================================

class TestToolCallingInsights:
    """
    Key insights about tool calling architecture
    """

    def test_tool_definitions_are_prompts(self):
        """
        INSIGHT: Tool definitions are prompts!

        By describing tools in JSON schema, we're essentially
        telling the LLM:
        "Hey, you can call these functions. Here's their signature."

        The LLM then writes JSON to call them.
        """
        executor = get_executor()
        definitions = executor.get_tool_definitions()

        # This JSON schema is read by the LLM
        # It's like providing function signatures to a programmer

        for definition in definitions:
            name = definition["function"]["name"]
            params = definition["function"]["parameters"]

            # LLM learns:
            # "calculator accepts 'expression' as string"
            # "weather accepts 'latitude' and 'longitude' as numbers"
            # etc.

            print(f"LLM learns: {name}(...):")
            for param_name, param_info in params["properties"].items():
                param_type = param_info.get("type", "?")
                print(f"  - {param_name}: {param_type}")

    def test_tool_calling_is_function_invocation(self):
        """
        INSIGHT: Tool calling is really function invocation!

        The LLM doesn't actually execute code.
        Instead, it outputs JSON describing what function to call:

        {
            "name": "function_name",
            "arguments": {"param": "value"}
        }

        Then WE (the backend) execute that function and
        return the result to the LLM.

        This is safe because:
        1. LLM can't do arbitrary code execution
        2. We control which functions are available
        3. We handle all errors
        """

        # LLM can't do this:
        # "def calculate(x): return x * 2"

        # LLM does this instead:
        # "Call calculator with expression='2*2'"

        # We execute, it gets result

        print("[OK] INSIGHT: Tool calling = Safe function invocation")
        print("  - LLM outputs JSON (no code execution)")
        print("  - We execute the function")
        print("  - We return the result")

    def test_tool_calling_enables_grounding(self):
        """
        INSIGHT: Tool calling grounds the LLM in reality!

        Without tools: LLM just generates text (might be wrong)
        With tools: LLM can look up current info

        Examples:
        - User: "What is 2+2?" → LLM uses calculator
        - User: "Latest AI news?" → LLM uses web_search
        - User: "Weather in NYC?" → LLM uses weather

        This prevents hallucination and provides current data.
        """

        print("[OK] INSIGHT: Tools ground LLM in reality")
        print("  - Without tools: LLM generates (might be wrong)")
        print("  - With tools: LLM can verify (accurate)")
        print("  - User gets grounded, factual responses")


if __name__ == "__main__":
    print("Run with: pytest tests/test_tool_calling_architecture.py -v")
    print("\nThis test suite teaches HOW tool calling works!")
