import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from pathlib import Path

# Import the functions we want to test
from src.assistant.tools.core_tools import (
    download_web_file,
    get_current_local_time,
    run_shell_command
)

class TestCoreTools(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.test_dir, ignore_errors=True)
        
    @patch('src.assistant.tools.core_tools.execute_command_realtime_combined')
    def test_download_web_file_success(self, mock_execute):
        """Test successful file download."""
        # Mock a successful curl execution
        mock_execute.return_value = (0, "Success")
        
        destination = os.path.join(self.test_dir, "test_file.txt")
        result = download_web_file("http://example.com/file.txt", destination)
        
        self.assertIn("Successfully downloaded file", result)
        mock_execute.assert_called_once()
        
    @patch('src.assistant.tools.core_tools.execute_command_realtime_combined')
    def test_download_web_file_failure(self, mock_execute):
        """Test failed file download."""
        # Mock a failed curl execution
        mock_execute.return_value = (1, "Error")
        
        destination = os.path.join(self.test_dir, "test_file.txt")
        result = download_web_file("http://example.com/file.txt", destination)
        
        self.assertIn("Failed to download file", result)
        mock_execute.assert_called_once()
        
    def test_get_current_local_time_format(self):
        """Test that get_current_local_time returns properly formatted time."""
        time_str = get_current_local_time()
        # Should contain date and time components
        self.assertTrue(len(time_str) > 0)
        self.assertIn("-", time_str)  # Should have date separators
        
    @patch('src.assistant.tools.core_tools.execute_command_interactive')
    def test_run_shell_command_interactive(self, mock_execute):
        """Test running shell command in interactive mode."""
        mock_execute.return_value = 0
        result = run_shell_command("ls", interactive=True)
        self.assertEqual(result, 0)
        
    @patch('src.assistant.tools.core_tools.execute_command_realtime_combined')
    def test_run_shell_command_non_interactive(self, mock_execute):
        """Test running shell command in non-interactive mode."""
        mock_execute.return_value = (0, "output")
        result = run_shell_command("ls", interactive=False)
        self.assertEqual(result, "output")

if __name__ == '__main__':
    unittest.main()