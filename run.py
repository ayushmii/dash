import subprocess
import signal
import sys

# List of server commands
servers = [
    "python queryserver.py",
    "python diseaseapp.py",
    "python patient_count.py",
    "python patient_count_stack.py",
    "python dashboard.py"
]

# List to store subprocess objects
processes = []

def signal_handler(sig, frame):
    """Signal handler to gracefully terminate subprocesses"""
    print("\nInterruption detected. Terminating servers...")
    for p in processes:
        p.terminate()
    sys.exit(0)

if __name__ == "__main__":
    # Set signal handler for keyboard interruption
    signal.signal(signal.SIGINT, signal_handler)

    try:
        # Start servers
        for server in servers:
            p = subprocess.Popen(server.split(), shell=False)
            processes.append(p)

        # Wait for processes to complete (or be terminated)
        for p in processes:
            p.wait()

    except KeyboardInterrupt:
        # Handle keyboard interruption
        signal_handler(None, None)