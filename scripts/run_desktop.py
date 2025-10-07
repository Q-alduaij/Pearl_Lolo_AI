import subprocess
import sys
import time
import socket


def port_open(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.3)
        return sock.connect_ex((host, port)) == 0


def main() -> None:
    host, port = "127.0.0.1", 8777
    backend = None
    if not port_open(host, port):
        print("Starting backend …")
        backend = subprocess.Popen(
            [sys.executable, "-m", "uvicorn", "api.server:app", "--host", host, "--port", str(port)]
        )
        time.sleep(1.5)
    try:
        from ui.main import main as ui_main

        ui_main()
    finally:
        if backend:
            backend.terminate()
            try:
                backend.wait(timeout=3)
            except Exception:  # noqa: BLE001
                backend.kill()


if __name__ == "__main__":
    main()
