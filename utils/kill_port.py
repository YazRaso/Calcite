import subprocess
import sys


def port_killer(port="5005") -> None:
    """
    port killer shuts down Port
    :param port: Port to kill, default 5005 - Rasa Core Server
    :return: None
    """
    if sys.platform.startswith("win"):
        try:
            # Find the PID(s) using the port
            result = subprocess.check_output(f'netstat -ano | findstr :{port}', shell=True)
            lines = result.decode().splitlines()
            pids = {line.strip().split()[-1] for line in lines}
            for pid in pids:
                subprocess.run(f'taskkill /PID {pid} /F', shell=True)
            print(f"Killed process(es) on port {port} (Windows)")
        except subprocess.CalledProcessError:
            print(f"No process is using port {port} on Windows.")
    else:
        try:
            result = subprocess.check_output(["lsof", "-t", f"-i:{port}"])
            pids = result.decode().split()
            for pid in pids:
                subprocess.run(["kill", "-9", pid])
            print(f"Killed process(es) on port {port} (Unix)")
        except subprocess.CalledProcessError:
            print(f"No process is using port {port} on Unix.")
