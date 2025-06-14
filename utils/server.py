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

    if first_time:
        # if first time build the docker image
        docker_dir = (Path(__file__).parent.parent / "docker").resolve()
        bot_dir = (Path(__file__).parent.parent / "bot").resolve()
        actions_dir = (Path(__file__).parent.parent / "actions").resolve()
        sheet_dir = (Path(__file__).parent.parent / "sheet_data").resolve()
        core_dir = (Path(__file__).parent.parent / "core").resolve()

        env_content = (
            f"BOT_PATH={bot_dir}\n"
            f"ACTIONS_PATH={actions_dir}\n"
            f"CORE_PATH={core_dir}\n"
            f"SHEET_DATA={sheet_dir}\n"
        )

        with open(docker_dir / ".env", "w") as f:
            f.write(env_content)

        subprocess.Popen(["docker", "compose", "build", "--no-cache"],
                         cwd=docker_dir.resolve())

    subprocess.Popen(["docker", "compose", "up"], cwd=docker_dir.resolve())


async def check_server_health(url: str) -> bool:
    """
    Checks if the server is healthy
    :param url: URL to poll
    :return: True if healthy, False otherwise
    """
    async with aiohttp.ClientSession() as session:
        for _ in range(300):
            try:
                async with session.get(url) as response:
                    if response.status == 200:
                        return True
            except aiohttp.ClientConnectionError:
                pass
            await asyncio.sleep(1)
    return False
