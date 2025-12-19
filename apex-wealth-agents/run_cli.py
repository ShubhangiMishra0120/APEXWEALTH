# run_cli.py
import os
from orchestrator import chat

def main():
	print("Apex Advisor (CLI). Type 'exit' to quit.\n")
	while True:
		try:
			msg = input("You: ").strip()
			if not msg:
				continue
			if msg.lower() in ("exit","quit"): break
			res = chat(msg, [])
			print("Apex:", (res.get("answer") or str(res))[:4000])
		except (KeyboardInterrupt, EOFError):
			print("\nBye!")
			break

if __name__ == "__main__":
	main()
