import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
import subprocess

# Import the function we want to test
from src.assistant.agents.tools.system_shell import run_shell_command


class TestSystemShellTool(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    @patch('src.assistant.agents.tools.system_shell.execute_command_interactive')
    def test_run_shell_command_interactive_success(self, mock_execute):
        """Test running shell command in interactive mode - success case."""
        mock_execute.return_value = 0
        result = run_shell_command("ls", interactive=True)
        self.assertEqual(result, "Command exited with code: 0")
        mock_execute.assert_called_once_with("ls", shell=True, env=os.environ)
        
    @patch('src.assistant.agents.tools.system_shell.execute_command_realtime_combined')
    def test_run_shell_command_non_interactive_success(self, mock_execute):
        """Test running shell command in non-interactive mode - success case."""
        mock_execute.return_value = (0, "output")
        result = run_shell_command("ls", interactive=False)
        self.assertEqual(result, "output")
        
    @patch('src.assistant.agents.tools.system_shell.execute_command_realtime_combined')
    def test_run_shell_command_non_interactive_with_timeout_none(self, mock_execute):
        """Test running shell command in non-interactive mode with timeout=None."""
        mock_execute.return_value = (0, "output")
        result = run_shell_command("ls", interactive=False, timeout=None)
        self.assertEqual(result, "output")
        
    def test_run_shell_command_invalid_parameters(self):
        """Test that invalid parameters raise appropriate errors."""
        # Test invalid command_string type
        with self.assertRaises(TypeError):
            run_shell_command(123)  # Should be string
            
        # Test invalid interactive type  
        with self.assertRaises(TypeError):
            run_shell_command("ls", interactive="true")  # Should be boolean
            
        # Test invalid timeout value
        with self.assertRaises(ValueError):
            run_shell_command("ls", timeout=-5)  # Should be positive integer or None
            
        with self.assertRaises(ValueError):
            run_shell_command("ls", timeout=0)  # Should be positive integer or None
            
    @patch('src.assistant.agents.tools.system_shell.subprocess.run')
    def test_run_shell_command_timeout_success(self, mock_subprocess_run):
        """Test running shell command with timeout - success case."""
        # Mock successful subprocess execution
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "output"
        mock_result.stderr = ""
        mock_subprocess_run.return_value = mock_result
        
        result = run_shell_command("ls", interactive=False, timeout=10)
        self.assertEqual(result, "output")
        
    @patch('src.assistant.agents.tools.system_shell.subprocess.run')
    def test_run_shell_command_timeout_expired(self, mock_subprocess_run):
        """Test running shell command with timeout - expired case."""
        # Mock subprocess that times out
        mock_subprocess_run.side_effect = subprocess.TimeoutExpired("ls", 5)
        
        with self.assertRaises(TimeoutError) as context:
            run_shell_command("sleep 10", interactive=False, timeout=5)
            
        self.assertIn("Command timed out after 5 seconds", str(context.exception))
        
    @patch('src.assistant.agents.tools.system_shell.subprocess.run')
    def test_run_shell_command_file_not_found(self, mock_subprocess_run):
        """Test running shell command that results in file not found error."""
        # Mock subprocess that raises FileNotFoundError
        mock_subprocess_run.side_effect = FileNotFoundError("Command not found")
        
        with self.assertRaises(RuntimeError) as context:
            run_shell_command("nonexistentcommand", interactive=False)
            
        self.assertIn("Command not found", str(context.exception))
        
    @patch('src.assistant.agents.tools.system_shell.subprocess.run')
    def test_run_shell_command_permission_denied(self, mock_subprocess_run):
        """Test running shell command that results in permission denied error."""
        # Mock subprocess that raises PermissionError
        mock_subprocess_run.side_effect = PermissionError("Permission denied")
        
        with self.assertRaises(RuntimeError) as context:
            run_shell_command("/root/protected_file", interactive=False)
            
        self.assertIn("Permission denied executing command", str(context.exception))
        
    def test_backward_compatibility(self):
        """Test that existing code patterns still work."""
        # Test default behavior (no timeout parameter)
        with patch('src.assistant.agents.tools.system_shell.execute_command_realtime_combined') as mock_execute:
            mock_execute.return_value = (0, "output")
            result = run_shell_command("ls")  # No timeout specified
            self.assertEqual(result, "output")
            
        # Test explicit interactive=False (default behavior)
        with patch('src.assistant.agents.tools.system_shell.execute_command_realtime_combined') as mock_execute:
            mock_execute.return_value = (0, "output")
            result = run_shell_command("ls", interactive=False)  # Explicit False
            self.assertEqual(result, "output")


if __name__ == '__main__':
    unittest.main()