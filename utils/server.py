import subprocess
import requests
import time
from pathlib import Path
import json
import aiohttp
import asyncio


def start_server() -> None:
    """
    Starts the docker container
    If it is the user's first time running the server,
    the docker image will be built first.
    :return: None
    """
    config_file_path = Path(__file__).parent.parent / "config" / "config.json"
    with open(config_file_path, "r") as f:
        data = json.load(f)
        first_time = data["user"]["firstTime"]

    docker_dir = (Path(__file__).parent.parent / "docker").resolve()
    if first_time:
        # if first time build the docker image
        bot_dir = (Path(__file__).parent.parent / "bot").resolve()
        actions_dir = (Path(__file__).parent.parent / "actions").resolve()
        sheet_dir = (Path(__file__).parent.parent / "sheet_data").resolve()
        core_dir = (Path(__file__).parent.parent / "core").resolve()

        env_content = (
            f"BOT_PATH={bot_dir}\n"
            f"ACTIONS_PATH={actions_dir}\n"
            f"CORE_PATH={core_dir}\n"
            f"SHEET_PATH={sheet_dir}\n"
        )

        with open(docker_dir / ".env", "w") as f:
            f.write(env_content)

        subprocess.run(["docker", "compose", "build", "--no-cache"],
                         cwd=docker_dir.resolve())

    subprocess.Popen(["docker", "compose", "up"], cwd=docker_dir.resolve())


def check_servers_sync():
    """Synchronously checks the health of both servers."""
    try:
        core_res = requests.get("http://localhost:5005/status", timeout=5)
        actions_res = requests.get("http://localhost:5055/health", timeout=5)
        return core_res.status_code == 200 and actions_res.status_code == 200
    except requests.exceptions.RequestException:
        return False
