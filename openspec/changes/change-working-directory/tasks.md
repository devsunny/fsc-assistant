# Tasks: Change Working Directory Tool Function

1. **Create new tool function** `change_working_directory` in `src/assistant/agents/tools/file_system.py`:
   - Implement directory change functionality using os.chdir()
   - Add proper validation for target path existence and accessibility
   - Include comprehensive error handling for invalid paths or permission issues

2. **Add documentation and examples**:
   - Enhance docstring with detailed usage scenarios
   - Add practical examples for different use cases
   - Document return value format and error conditions

3. **Implement unit tests**:
   - Test successful directory change functionality  
   - Test error handling for invalid paths
   - Test permission-related errors
   - Test edge cases (non-existent directories, etc.)

4. **Update tool registration**:
   - Register the new function in `src/assistant/agents/agent_repo.py`
   - Ensure proper metadata and description are included

5. **Verify integration with existing tools**:
   - Confirm that shell commands can be executed from changed directory
   - Test that other file system operations work correctly after directory change

6. **Update documentation**:
   - Update any relevant documentation files
   - Add to project README if needed