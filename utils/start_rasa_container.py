import subprocess
import requests
import time
from pathlib import Path


def start_rasa_container() -> None:
    """
    Starts the docker container
    :return: None
    """
    docker_dir = Path(__file__).parent.parent / "docker"
    subprocess.Popen(["docker-compose", "up"], cwd=docker_dir.resolve())


def check_actions_health() -> bool:
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
