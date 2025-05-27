import subprocess


def start_core_server() -> None:
    """
    Start the Rasa Core server on port 5005,
    pointing to endpoints (action server).
    """
    subprocess.Popen([
        "rasa", "run",
        "--endpoints", "endpoints.yml",
        "--enable-api",
        "--port", "5005"
    ])
