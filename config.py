"""
SHAIK-AI Configuration
Customize paths, apps, and wake word here.
"""

# ── Wake Word ──────────────────────────────────────────────────────────────────
WAKE_WORD = "shaik"          # Say "Shaik, open Chrome" to trigger

# ── User Profile ───────────────────────────────────────────────────────────────
USERNAME = "User"
USER_HOME = "C:\\Users\\pc"

# ── Common Path Shortcuts ──────────────────────────────────────────────────────
PATH_SHORTCUTS = {
    "desktop":      f"{USER_HOME}\\Desktop",
    "documents":    f"{USER_HOME}\\Documents",
    "downloads":    f"{USER_HOME}\\Downloads",
    "pictures":     f"{USER_HOME}\\Pictures",
    "videos":       f"{USER_HOME}\\Videos",
    "music":        f"{USER_HOME}\\Music",
    "project":      f"{USER_HOME}\\Documents\\Projects",
    "projects":     f"{USER_HOME}\\Documents\\Projects",
}

# ── App Launch Map ─────────────────────────────────────────────────────────────
# Maps spoken words → executable names or full paths
APP_MAP = {
    "chrome":           "chrome",
    "google chrome":    "chrome",
    "firefox":          "firefox",
    "edge":             "msedge",
    "notepad":          "notepad",
    "notepad++":        "notepad++",
    "word":             "WINWORD",
    "excel":            "EXCEL",
    "powerpoint":       "POWERPNT",
    "calculator":       "calc",
    "paint":            "mspaint",
    "vlc":              "vlc",
    "vs code":          "code",
    "visual studio code": "code",
    "terminal":         "wt",          # Windows Terminal
    "powershell":       "powershell",
    "cmd":              "cmd",
    "file explorer":    "explorer",
    "explorer":         "explorer",
    "task manager":     "taskmgr",
    "spotify":          "spotify",
    "discord":          "discord",
    "zoom":             "zoom",
    "teams":            "teams",
    "telegram":         "telegram",
    "whatsapp":         "whatsapp",
    "settings":         "ms-settings:",  # Opens Windows Settings
    "camera":           "microsoft.windows.camera:",
}

# ── Website Map ────────────────────────────────────────────────────────────────
WEBSITE_MAP = {
    "youtube":      "https://www.youtube.com",
    "google":       "https://www.google.com",
    "gmail":        "https://mail.google.com",
    "github":       "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "netflix":      "https://www.netflix.com",
    "twitter":      "https://www.twitter.com",
    "linkedin":     "https://www.linkedin.com",
    "instagram":    "https://www.instagram.com",
    "facebook":     "https://www.facebook.com",
    "reddit":       "https://www.reddit.com",
    "wikipedia":    "https://www.wikipedia.org",
    "maps":         "https://maps.google.com",
    "translate":    "https://translate.google.com",
    "chatgpt":      "https://chat.openai.com",
}

# ── Speech Settings ────────────────────────────────────────────────────────────
TTS_RATE   = 175        # Words per minute (150–200 is natural)
TTS_VOLUME = 1.0        # 0.0 – 1.0
TTS_VOICE  = "female"   # "male" or "female" (picks first matching SAPI voice)

# ── Microphone ─────────────────────────────────────────────────────────────────
MIC_TIMEOUT      = 5    # Seconds to wait for speech to start
MIC_PHRASE_LIMIT = 8    # Max seconds per phrase
ENERGY_THRESHOLD = 300  # Mic sensitivity (lower = more sensitive)
