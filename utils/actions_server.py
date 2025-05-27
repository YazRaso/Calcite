import subprocess
import requests
import time


def start_action_server() -> None:
    """
    Start the action server on port 5055
    :return: None
    """
    subprocess.Popen(["rasa", "run", "actions"])


def check_health() -> bool:
    """
    Poll action server to see if the action server is healthy
    :return: bool
    """
    for _ in range(30):
        try:
            r = requests.get("http://localhost:5055/health")
            if r.status_code == 200 and r.json()["status"] == "ok":
                return True
        except requests.exceptions.RequestException:
            pass
        time.sleep(1)
    return False
