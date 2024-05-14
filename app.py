from threading import Thread
from main import run_bot

def main():
    status = open("status.txt", "r").read().strip().replace("\n", "")
    if status == "running":
        return "Bot is already running"

    elif status != "stopped":
        return "Bot is failed due to unknown error, check logs"

    Thread(target=run_bot).start()

    return "Bot started successfully"

print(main())