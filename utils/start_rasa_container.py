import subprocess
import requests
import time
from pathlib import Path
import json


def start_rasa_container() -> None:
    """
    Starts the docker container
    :return: None
    """
    config_file_path = Path(__file__).parent / "config" / "config.yml"
    with open(config_file_path, "r") as f:
        data = json.load(f)
        first_time = data["user"]["firstTime"]

    docker_dir = Path(__file__).parent / "docker"
    if first_time:
        # Since it is the users first time, we need to build the docker container
        subprocess.Popen(["docker-compose", "build", "--no-cache"], cwd=docker_dir.resolve())
    subprocess.Popen(["docker-compose", "up"], cwd=docker_dir.resolve())


def check_server_health(url: str) -> bool:
    """
    Checks if the server is healthy
    :param url: URL to check
    :return: True if healthy, False otherwise
    """
    for _ in range(300):
        try:
            response = requests.get(url)
            if response.status_code == 200:
                return True
        except requests.ConnectionError:
            pass
        time.sleep(1)
    return False
