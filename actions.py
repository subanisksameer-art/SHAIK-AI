"""
SHAIK-AI Action Executor
Parses commands and returns JSON action blocks, then executes them.
"""

import os
import json
import subprocess
import webbrowser
import re
import datetime
from config import PATH_SHORTCUTS, APP_MAP, WEBSITE_MAP
from contacts import get_number, get_name


# ── JSON Action Builder ────────────────────────────────────────────────────────

def build_action(action: str, target: str, extra: dict = None) -> dict:
    block = {"action": action, "target": target}
    if extra:
        block.update(extra)
    return block


def print_action(block: dict):
    print("\n" + json.dumps(block, indent=2) + "\n")


# ── Command Parser ─────────────────────────────────────────────────────────────

def parse_command(text: str) -> dict | None:
    t = text.lower().strip()

    # ── EXIT / SLEEP ──────────────────────────────────────────────────────
    if any(w in t for w in ["exit", "quit", "goodbye", "bye", "stop listening"]):
        return build_action("system", "exit")

    if any(w in t for w in ["sleep", "pause", "standby"]):
        return build_action("system", "sleep")

    # ── WHATSAPP MESSAGE ──────────────────────────────────────────────────
    # "send message to mom say I am coming home"
    # "whatsapp dad I will be late"
    # "text mom hello"
    wa_match = re.search(
        r"(?:send\s+(?:whatsapp\s+)?(?:message|msg|text)|whatsapp|text|message)\s+(?:to\s+)?(\w+)\s+(?:say\s+|saying\s+)?(.+)",
        t
    )
    if wa_match:
        contact_name = wa_match.group(1).strip()
        message      = wa_match.group(2).strip()
        return build_action("whatsapp_message", contact_name,
                            {"message": message, "contact": contact_name})

    # ── WHATSAPP CALL ─────────────────────────────────────────────────────
    # "call mom on whatsapp" / "whatsapp call dad"
    call_wa = re.search(
        r"(?:whatsapp\s+call|call\s+(?:\w+\s+)?on\s+whatsapp|video\s+call)\s+(\w+)|(\w+)\s+(?:on\s+whatsapp|whatsapp\s+call)",
        t
    )
    if call_wa:
        contact_name = (call_wa.group(1) or call_wa.group(2) or "").strip()
        if contact_name:
            return build_action("whatsapp_call", contact_name,
                                {"contact": contact_name})

    # ── REGULAR CALL (phone dialer) ───────────────────────────────────────
    # "call mom" (without whatsapp keyword)
    call_match = re.search(r"^(?:call|ring|phone|dial)\s+(\w+)$", t)
    if call_match:
        contact_name = call_match.group(1).strip()
        return build_action("whatsapp_call", contact_name,
                            {"contact": contact_name})

    # ── OPEN WHATSAPP ─────────────────────────────────────────────────────
    if t in ["open whatsapp", "launch whatsapp", "start whatsapp"]:
        return build_action("launch_app", "whatsapp", {"name": "whatsapp"})

    # ── TELL ME THE TIME ─────────────────────────────────────────────────
    if any(p in t for p in ["what time", "current time", "tell me time", "what's the time"]):
        return build_action("system_info", "time")

    # ── TELL ME THE DATE ─────────────────────────────────────────────────
    if any(p in t for p in ["what date", "today's date", "what day", "tell me date"]):
        return build_action("system_info", "date")

    # ── WEATHER ───────────────────────────────────────────────────────────
    if "weather" in t:
        city_match = re.search(r"weather\s+(?:in|of|at|for)?\s*(\w[\w\s]*)", t)
        city = city_match.group(1).strip() if city_match else "my location"
        url  = f"https://www.google.com/search?q=weather+{city.replace(' ', '+')}"
        return build_action("open_url", url, {"query": f"weather {city}"})

    # ── OPEN WEBSITE ──────────────────────────────────────────────────────
    for trigger in ["open website", "go to", "browse to", "navigate to",
                    "open", "launch", "start"]:
        if t.startswith(trigger):
            remainder = t[len(trigger):].strip()
            for site_key, url in WEBSITE_MAP.items():
                if site_key in remainder:
                    return build_action("open_url", url, {"site": site_key})

    for site_key, url in WEBSITE_MAP.items():
        if site_key in t and any(w in t for w in ["open", "go", "launch", "show", "browse"]):
            return build_action("open_url", url, {"site": site_key})

    # ── GOOGLE SEARCH ─────────────────────────────────────────────────────
    search_match = re.search(
        r"(?:search(?:\s+for)?|google|look up|find)\s+(.+)", t
    )
    if search_match:
        query = search_match.group(1).strip()
        url   = f"https://www.google.com/search?q={query.replace(' ', '+')}"
        return build_action("open_url", url, {"query": query})

    # ── LAUNCH APPLICATION ────────────────────────────────────────────────
    for trigger in ["open", "launch", "start", "run"]:
        if trigger in t:
            for app_key, app_exec in APP_MAP.items():
                if app_key in t:
                    return build_action("launch_app", app_exec, {"name": app_key})

    # ── OPEN PATH / FOLDER ────────────────────────────────────────────────
    for trigger in ["open", "go to", "show me", "navigate to"]:
        if trigger in t:
            for shortcut, path in PATH_SHORTCUTS.items():
                if shortcut in t:
                    return build_action("open_path", path, {"label": shortcut})

    # ── OPEN SPECIFIC FILE ────────────────────────────────────────────────
    file_match = re.search(r"open(?:\s+file)?\s+([A-Za-z]:\\[\w\\.\-\s]+\.\w+)", text, re.IGNORECASE)
    if file_match:
        return build_action("open_file", file_match.group(1).strip())

    # ── VOLUME CONTROL ────────────────────────────────────────────────────
    if "volume up" in t or "increase volume" in t:
        return build_action("system_control", "volume_up")
    if "volume down" in t or "decrease volume" in t or "lower volume" in t:
        return build_action("system_control", "volume_down")
    if "mute" in t:
        return build_action("system_control", "mute")

    # ── SCREENSHOT ────────────────────────────────────────────────────────
    if "screenshot" in t or "take a screen" in t or "capture screen" in t:
        return build_action("system_control", "screenshot")

    # ── SHUTDOWN / RESTART / LOCK ─────────────────────────────────────────
    if "shutdown" in t or "shut down" in t or "power off" in t:
        return build_action("system_control", "shutdown")
    if "restart" in t or "reboot" in t:
        return build_action("system_control", "restart")
    if "lock" in t and ("screen" in t or "computer" in t or "pc" in t or t == "lock"):
        return build_action("system_control", "lock")

    return None


# ── Action Executor ────────────────────────────────────────────────────────────

def execute_action(block: dict) -> str:
    action = block.get("action")
    target = block.get("target")

    if action == "open_url":
        webbrowser.open(target)
        site = block.get("site") or block.get("query", target)
        return f"Opening {site}"

    elif action == "launch_app":
        name = block.get("name", target)
        try:
            if target.endswith(":"):
                os.startfile(target)
            else:
                subprocess.Popen(target, shell=True,
                                 stdout=subprocess.DEVNULL,
                                 stderr=subprocess.DEVNULL)
            return f"Launching {name}"
        except Exception as e:
            return f"Could not launch {name}: {e}"

    elif action == "open_path":
        label = block.get("label", target)
        if os.path.exists(target):
            os.startfile(target)
            return f"Opening {label} folder"
        return f"Path not found: {target}"

    elif action == "open_file":
        if os.path.exists(target):
            os.startfile(target)
            return "Opening file"
        return f"File not found: {target}"

    elif action == "whatsapp_message":
        return _send_whatsapp_message(
            block.get("contact", target),
            block.get("message", "")
        )

    elif action == "whatsapp_call":
        return _whatsapp_call(block.get("contact", target))

    elif action == "system_info":
        return _handle_system_info(target)

    elif action == "system_control":
        return _handle_system_control(target)

    elif action == "system":
        if target == "exit":
            return "__EXIT__"
        elif target == "sleep":
            return "__SLEEP__"

    return "Command executed"


# ── WhatsApp Actions ───────────────────────────────────────────────────────────

def _send_whatsapp_message(contact_name: str, message: str) -> str:
    number = get_number(contact_name)
    if not number:
        return (f"Contact '{contact_name}' not found. "
                f"Please add them to contacts.py")
    if not message:
        return "No message content. Say: send message to mom say hello"

    try:
        import pywhatkit as pwk
        # Send instantly — opens WhatsApp Web, sends after 15 sec
        pwk.sendwhatmsg_instantly(
            phone_no=number,
            message=message,
            wait_time=15,
            tab_close=True,
            close_time=5
        )
        display_name = get_name(contact_name)
        return f"Sending WhatsApp message to {display_name}: {message}"
    except ImportError:
        # Fallback: open WhatsApp Web with pre-filled message
        encoded_msg = message.replace(" ", "%20")
        clean_number = number.replace("+", "").replace(" ", "")
        url = f"https://web.whatsapp.com/send?phone={clean_number}&text={encoded_msg}"
        webbrowser.open(url)
        return f"Opened WhatsApp Web to message {contact_name}. Click Send."
    except Exception as e:
        return f"WhatsApp error: {e}"


def _whatsapp_call(contact_name: str) -> str:
    number = get_number(contact_name)
    if not number:
        return f"Contact '{contact_name}' not found. Add them to contacts.py"

    try:
        clean_number = number.replace("+", "").replace(" ", "")
        url = f"https://web.whatsapp.com/send?phone={clean_number}"
        webbrowser.open(url)
        display_name = get_name(contact_name)
        return (f"Opened WhatsApp for {display_name}. "
                f"Click the call button to start the call.")
    except Exception as e:
        return f"Call error: {e}"


# ── System Info ────────────────────────────────────────────────────────────────

def _handle_system_info(target: str) -> str:
    now = datetime.datetime.now()
    if target == "time":
        return f"Current time is {now.strftime('%I:%M %p')}"
    elif target == "date":
        return f"Today is {now.strftime('%A, %d %B %Y')}"
    return ""


# ── System Controls ────────────────────────────────────────────────────────────

def _handle_system_control(target: str) -> str:
    if target == "screenshot":
        desktop = os.path.join(os.environ.get("USERPROFILE", "C:\\Users\\pc"), "Desktop")
        ts      = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        path    = os.path.join(desktop, f"screenshot_{ts}.png")
        try:
            subprocess.run(
                ["powershell", "-Command",
                 f"Add-Type -AssemblyName System.Windows.Forms; "
                 f"$bmp = New-Object System.Drawing.Bitmap("
                 f"[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,"
                 f"[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); "
                 f"$g = [System.Drawing.Graphics]::FromImage($bmp); "
                 f"$g.CopyFromScreen(0,0,0,0,$bmp.Size); "
                 f"$bmp.Save('{path}')"],
                capture_output=True
            )
            return "Screenshot saved to Desktop"
        except Exception:
            subprocess.Popen("snippingtool", shell=True)
            return "Opening Snipping Tool"

    elif target == "volume_up":
        subprocess.run(["powershell", "-Command",
                        "$o=New-Object -ComObject WScript.Shell;$o.SendKeys([char]175)"],
                       capture_output=True)
        return "Volume increased"

    elif target == "volume_down":
        subprocess.run(["powershell", "-Command",
                        "$o=New-Object -ComObject WScript.Shell;$o.SendKeys([char]174)"],
                       capture_output=True)
        return "Volume decreased"

    elif target == "mute":
        subprocess.run(["powershell", "-Command",
                        "$o=New-Object -ComObject WScript.Shell;$o.SendKeys([char]173)"],
                       capture_output=True)
        return "Toggled mute"

    elif target == "shutdown":
        subprocess.run(["shutdown", "/s", "/t", "10"], capture_output=True)
        return "Shutting down in 10 seconds"

    elif target == "restart":
        subprocess.run(["shutdown", "/r", "/t", "10"], capture_output=True)
        return "Restarting in 10 seconds"

    elif target == "lock":
        subprocess.run(["rundll32.exe", "user32.dll,LockWorkStation"],
                       capture_output=True)
        return "Locking screen"

    return f"Unknown control: {target}"
