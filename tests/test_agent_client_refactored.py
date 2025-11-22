"""
Test suite for the refactored AgentOrchestrator class.
"""

import unittest
from unittest.mock import Mock, patch

# Import the refactored module
from assistant.llm.agent_client_refactored import (
    AgentOrchestrator,
    ToolExecutionHandler,
    ParameterAdjuster
)


class TestToolExecutionHandler(unittest.TestCase):
    
    def setUp(self):
        self.handler = ToolExecutionHandler()
        
    def test_execute_tool_success(self):
        # Mock a simple tool function
        def mock_tool(name: str, value: int) -> dict:
            return {"result": f"Processed {name} with {value}"}
            
        result = self.handler.execute_tool(
            tool=mock_tool,
            assistant_content="Test content",
            tool_call_id="call_123",
            tool_type="function",
            tool_name="mock_tool",
            tool_json_args='{"name": "test", "value": 42}'
        )
        
        # Verify the result structure
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertEqual(result[1]["role"], "tool")
        self.assertEqual(result[1]["name"], "mock_tool")
        self.assertIn("Processed test with 42", result[1]["content"])
        
    def test_execute_tool_error(self):
        # Mock a tool that raises an exception
        def failing_tool() -> None:
            raise ValueError("Test error")
            
        result = self.handler.execute_tool(
            tool=failing_tool,
            assistant_content="Test content",
            tool_call_id="call_456",
            tool_type="function", 
            tool_name="failing_tool",
            tool_json_args='{}'
        )
        
        # Verify error handling
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertIn("Error executing tool failing_tool", result[1]["content"])


class TestParameterAdjuster(unittest.TestCase):
    
    def test_adjust_parameters_for_bad_request(self):
        adjuster = ParameterAdjuster()
        
        # Test with basic parameters
        chat_params = {"temperature": 0.5, "max_tokens": 100}
        original_messages = [{"role": "user", "content": "test"}]
        
        adjusted_params, adjusted = adjuster.adjust_parameters_for_bad_request(
            chat_params, original_messages
        )
        
        # Should return same parameters (no adjustment in this basic case)
        self.assertEqual(adjusted_params, chat_params)
        self.assertFalse(adjusted)
        
    def test_adjust_parameters_for_token_limit(self):
        adjuster = ParameterAdjuster()
        
        # Test with basic parameters  
        chat_params = {"temperature": 0.5, "max_tokens": 100}
        original_messages = [{"role": "user", "content": "test"}]
        
        adjusted_params, adjusted = adjuster.adjust_parameters_for_token_limit(
            chat_params, original_messages
        )
        
        # Should return same parameters (no adjustment in this basic case)
        self.assertEqual(adjusted_params, chat_params)
        self.assertFalse(adjusted)


class TestAgentOrchestrator(unittest.TestCase):
    
    def setUp(self):
        # Mock the config to avoid actual file system access
        mock_config = Mock()
        mock_config.get_option.return_value = None
        
        with patch('assistant.llm.agent_client_refactored.LLMClient.__init__'):
            self.orchestrator = AgentOrchestrator(config=mock_config)
            
    def test_initialization(self):
        # Test that the orchestrator initializes correctly
        self.assertIsNotNone(self.orchestrator)
        self.assertIsNotNone(self.orchestrator.tool_handler)
        
    @patch('assistant.llm.agent_client_refactored.openai.OpenAI')
    def test_with_real_openai_client(self, mock_openai):
        """Test initialization with a real OpenAI client"""
        # Mock the OpenAI client
        mock_client = Mock()
        mock_openai.return_value = mock_client
        
        # Test that we can create orchestrator with actual client
        mock_config = Mock()
        mock_config.get_option.return_value = None
        
        with patch('assistant.llm.agent_client_refactored.LLMClient.__init__'):
            orchestrator = AgentOrchestrator(
                openai_client=mock_client,
                config=mock_config
            )
            
        self.assertIsNotNone(orchestrator)
        self.assertEqual(orchestrator.client, mock_client)


if __name__ == '__main__':
    unittest.main()