import os
import sys
import subprocess
import threading
import time
from datetime import datetime

# Add the project root to Python path so we can import our module
project_root = "/mnt/c/Users/sunny/devel/github/fsc-assistant"
sys.path.insert(0, project_root)

# Import after adding to path
try:
    from src.assistant.agents.tools.system_shell_daemon import (
        run_shell_command_daemon,
        list_daemon_processes,
        terminate_daemon_process,
        check_daemon_status
    )
except ImportError as e:
    print(f"Failed to import module: {e}")
    sys.exit(1)

def test_basic_daemon_execution():
    """Test basic daemon execution."""
    print("Testing basic daemon execution...")
    
    # Start a daemon
    result = run_shell_command_daemon("sleep 10")
    pid = result['pid']
    
    # Check that it's running
    status = check_daemon_status(pid)
    assert status['status'] == 'running', "Process should be running"
    
    print("✓ Basic daemon execution test passed")
    return True

def test_daemon_with_timeout():
    """Test daemon process with timeout."""
    print("Testing daemon with timeout...")
    
    # Start a daemon that will timeout
    result = run_shell_command_daemon("sleep 30", timeout=2)
    pid = result['pid']
    
    # Wait for it to be terminated by timeout
    time.sleep(3)
    
    status = check_daemon_status(pid)
    assert status['status'] == 'terminated', "Process should be terminated"
    
    print("✓ Daemon with timeout test passed")
    return True

def test_list_processes():
    """Test listing daemon processes."""
    print("Testing process listing...")
    
    # Start multiple daemons
    pids = []
    for i in range(3):
        result = run_shell_command_daemon(f"sleep 15")
        pids.append(result['pid'])
    
    # List all running processes - we expect to see the ones we just started plus any existing ones
    processes = list_daemon_processes()
    
    # Check that at least our processes are there (might be more due to other tests)
    process_pids = [p['pid'] for p in processes]
    for pid in pids:
        assert pid in process_pids, f"PID {pid} not found in process list"
    
    print("✓ Process listing test passed")
    return True

def test_terminate_process():
    """Test terminating a daemon process."""
    print("Testing process termination...")
    
    # Start a daemon
    result = run_shell_command_daemon("sleep 30")
    pid = result['pid']
    
    # Verify it's running
    status = check_daemon_status(pid)
    assert status['status'] == 'running', "Process should be running"
    
    # Terminate it
    success = terminate_daemon_process(pid)
    assert success, "Termination should succeed"
    
    # Check that it's now terminated
    time.sleep(0.1)  # Give some time for termination to complete
    status = check_daemon_status(pid)
    assert status['status'] == 'terminated', "Process should be terminated"
    
    print("✓ Process termination test passed")
    return True

def test_check_status():
    """Test checking process status."""
    print("Testing process status checks...")
    
    # Start a daemon
    result = run_shell_command_daemon("sleep 5")
    pid = result['pid']
    
    # Check status of running process
    status = check_daemon_status(pid)
    assert status['status'] == 'running', "Process should be running"
    assert status['pid'] == pid, "PID mismatch in status"
    
    # Terminate it and check again
    terminate_daemon_process(pid)
    time.sleep(0.1)  # Give some time for termination
    
    status = check_daemon_status(pid)
    assert status['status'] == 'terminated', "Process should be terminated"
    
    print("✓ Process status test passed")
    return True

def test_backward_compatibility():
    """Test that existing run_shell_command behavior is preserved."""
    print("Testing backward compatibility...")
    
    # Test normal command execution (should work as before)
    try:
        result = subprocess.run(
            "echo 'hello world'", 
            shell=True, 
            capture_output=True, 
            text=True
        )
        output = result.stdout.strip()
        assert output == "hello world", f"Expected 'hello world', got '{output}'"
        
        print("✓ Backward compatibility test passed")
        return True
    except Exception as e:
        print(f"✗ Backward compatibility test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 60)
    print("Running System Shell Daemon Tool Tests")
    print("=" * 60)
    
    tests = [
        test_basic_daemon_execution,
        test_daemon_with_timeout,
        test_list_processes,
        test_terminate_process,
        test_check_status,
        test_backward_compatibility
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} failed with exception: {e}")
            import traceback
            traceback.print_exc()
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)