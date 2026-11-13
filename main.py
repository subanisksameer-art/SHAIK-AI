"""
╔══════════════════════════════════════════════════════════════════╗
║              SHAIK-AI  —  Personal Voice Assistant               ║
║         "Fast. Local. Yours."  |  Python 3.10+  |  Windows      ║
╚══════════════════════════════════════════════════════════════════╝

Usage:
    python main.py              → Voice mode (microphone)
    python main.py --text       → Text mode  (keyboard)
    python main.py --test       → Single command test
"""

import argparse
from config import WAKE_WORD, USERNAME
from voice_engine import Speaker, Listener
from actions import parse_command, execute_action, print_action
BANNER = r"""
 ____  _   _    _    ___ _  __       _    ___ 
/ ___|| | | |  / \  |_ _| |/ /      / \  |_ _|
\___ \| |_| | / _ \  | || ' /      / _ \  | | 
 ___) |  _  |/ ___ \ | || . \     / ___ \ | | 
|____/|_| |_/_/   \_\___|_|\_\   /_/   \_\___|
        Your Personal Voice OS Assistant
"""

SLEEP_MODE = False


def greet(speaker: Speaker):
    speaker.say(f"Hello {USERNAME}! SHAIK-AI is online. Say '{WAKE_WORD}' to activate me.")


def process_text(text: str, speaker: Speaker) -> bool:
    """Parse + execute one command. Returns False to exit, True to continue."""
    global SLEEP_MODE

    if not text:
        return True

    lower = text.lower().strip()

    # ── Wake word check ───────────────────────────────────────────────
    wake_detected = lower.startswith(WAKE_WORD.lower())
    if wake_detected:
        # Strip wake word from command
        lower = lower[len(WAKE_WORD):].strip(",. ").strip()
        text  = lower

    # ── Sleep / Wake ──────────────────────────────────────────────────
    if SLEEP_MODE:
        if wake_detected and any(w in lower for w in ["wake up", "hey", "hello"]):
            SLEEP_MODE = False
            speaker.say("I'm awake. What do you need?")
        return True

    if not wake_detected and WAKE_WORD.lower() != "":
        # Ignore commands without wake word (optional — set WAKE_WORD="" to disable)
        pass  # still process; wake word gating is soft in this build

    # ── Parse command ─────────────────────────────────────────────────
    action_block = parse_command(text)

    if action_block is None:
        speaker.say("I didn't catch that. Could you rephrase?")
        print(f'[UNRECOGNISED] "{text}"')
        return True

    # ── Print clean JSON block ────────────────────────────────────────
    print_action(action_block)

    # ── Execute ───────────────────────────────────────────────────────
    result = execute_action(action_block)

    if result == "__EXIT__":
        speaker.say(f"Goodbye {USERNAME}. SHAIK-AI shutting down.")
        return False
    elif result == "__SLEEP__":
        SLEEP_MODE = True
        speaker.say("Going to sleep. Say 'Shaik wake up' to resume.")
        return True

    speaker.say(result)
    return True


def run_voice_loop(speaker: Speaker, listener: Listener):
    greet(speaker)
    while True:
        try:
            text = listener.listen()
            if text is None:
                continue
            if not process_text(text, speaker):
                break
        except KeyboardInterrupt:
            speaker.say("Interrupted. Goodbye.")
            break


def run_text_loop(speaker: Speaker):
    greet(speaker)
    while True:
        try:
            cmd = input("\n> Command: ").strip()
            if not process_text(cmd, speaker):
                break
        except (KeyboardInterrupt, EOFError):
            speaker.say("Goodbye.")
            break


def run_test(speaker: Speaker, command: str):
    print(f"\n[TEST] Command: \"{command}\"")
    process_text(command, speaker)


# ── Entry Point ────────────────────────────────────────────────────────────────

def main():
    print(BANNER)

    parser = argparse.ArgumentParser(description="SHAIK-AI Voice Assistant")
    parser.add_argument("--text",  action="store_true", help="Use keyboard instead of mic")
    parser.add_argument("--test",  type=str, default=None, metavar="CMD",
                        help='Run a single test command, e.g. --test "open Chrome"')
    args = parser.parse_args()

    speaker  = Speaker()
    listener = Listener()

    if args.test:
        run_test(speaker, args.test)
    elif args.text:
        run_text_loop(speaker)
    else:
        run_voice_loop(speaker, listener)


if __name__ == "__main__":
    main()
