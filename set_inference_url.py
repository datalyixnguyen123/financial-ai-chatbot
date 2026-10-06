
from pathlib import Path
import sys
import requests

PROJECT_ROOT = Path(__file__).resolve().parent
ENV_FILE = PROJECT_ROOT / ".env"

def update_env(public_url: str):
    public_url = public_url.strip().rstrip("/")
    if not public_url.startswith("https://"):
        raise ValueError("URL must begin with https://")

    if ".trycloudflare.com" not in public_url:
        raise ValueError("Not an URL Cloudflare Quick Tunnel!")

    health_url = public_url + "/health"
    print(f"Testing: {health_url}")
    response = requests.get(health_url, timeout=30)
    response.raise_for_status()
    data = response.json()
    if data.get("status") != "ok":
        raise RuntimeError(f"Health check failed: {data}")
    print("✓ Cloudflare inference API is healthy")
    print(data)

    if ENV_FILE.exists():
        lines = ENV_FILE.read_text(encoding="utf-8").splitlines()
    else:
        lines = []
    new_lines = []
    found = False
    for line in lines:
        if line.startswith("INFERENCE_API_URL="):
            new_lines.append(f"INFERENCE_API_URL={public_url}")
            found = True
        else:
            new_lines.append(line)

    if not found:
        if new_lines and new_lines[-1].strip():
            new_lines.append("")
        new_lines.append(f"INFERENCE_API_URL={public_url}")

    ENV_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    print("\n✓ .env updated")
    print(f"INFERENCE_API_URL={public_url}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(
            "Usage:\n"
            "  python set_inference_url.py "
            "https://xxxxx.trycloudflare.com"
        )
        sys.exit(1)
    update_env(sys.argv[1])

    