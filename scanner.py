"""
SHAIK-AI System Scanner
Auto-discovers all installed apps and indexes your files.
Run this once to build the app/file database.
"""

import os
import json
import glob
import winreg
import subprocess

# ── Output cache files ─────────────────────────────────────────────────────────
CACHE_DIR   = os.path.dirname(os.path.abspath(__file__))
APPS_CACHE  = os.path.join(CACHE_DIR, "cache_apps.json")
FILES_CACHE = os.path.join(CACHE_DIR, "cache_files.json")

# ── Folders to scan for user files ────────────────────────────────────────────
USER_SCAN_DIRS = [
    os.path.expanduser("~\\Desktop"),
    os.path.expanduser("~\\Documents"),
    os.path.expanduser("~\\Downloads"),
    os.path.expanduser("~\\Pictures"),
    os.path.expanduser("~\\Videos"),
    os.path.expanduser("~\\Music"),
]

# File types to index
INDEXED_EXTENSIONS = {
    ".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".ppt",
    ".txt", ".py", ".js", ".html", ".css", ".json", ".csv",
    ".mp4", ".mp3", ".mkv", ".avi", ".wav",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp",
    ".zip", ".rar", ".7z",
}


# ── App Discovery ──────────────────────────────────────────────────────────────

def discover_apps() -> dict:
    """Scans Windows registry + common folders to find all installed apps."""
    apps = {}

    # 1. Windows Registry — Installed Programs
    reg_paths = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall",
    ]
    for reg_path in reg_paths:
        try:
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            for i in range(winreg.QueryInfoKey(key)[0]):
                try:
                    sub = winreg.OpenKey(key, winreg.EnumKey(key, i))
                    name = _reg_val(sub, "DisplayName")
                    exe  = _reg_val(sub, "DisplayIcon") or _reg_val(sub, "InstallLocation")
                    if name and exe:
                        exe = exe.split(",")[0].strip('"').strip()
                        if exe.endswith(".exe") and os.path.exists(exe):
                            key_name = name.lower().strip()
                            apps[key_name] = exe
                except Exception:
                    pass
        except Exception:
            pass

    # 2. Start Menu shortcuts (.lnk files)
    start_menu_paths = [
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
        os.path.expanduser(r"~\AppData\Roaming\Microsoft\Windows\Start Menu\Programs"),
    ]
    for sm_path in start_menu_paths:
        for lnk in glob.glob(os.path.join(sm_path, "**", "*.lnk"), recursive=True):
            try:
                name = os.path.splitext(os.path.basename(lnk))[0].lower().strip()
                if name and name not in apps:
                    apps[name] = lnk   # store .lnk path — Windows can open it
            except Exception:
                pass

    # 3. Common install folders
    search_dirs = [
        r"C:\Program Files",
        r"C:\Program Files (x86)",
        os.path.expanduser(r"~\AppData\Local\Programs"),
        os.path.expanduser(r"~\AppData\Local"),
        os.path.expanduser(r"~\AppData\Roaming"),
    ]
    for base in search_dirs:
        if not os.path.exists(base):
            continue
        for exe in glob.glob(os.path.join(base, "**", "*.exe"), recursive=True):
            name = os.path.splitext(os.path.basename(exe))[0].lower().strip()
            if name and name not in apps:
                apps[name] = exe

    print(f"[Scanner] Found {len(apps)} apps")
    return apps


def _reg_val(key, name: str) -> str | None:
    try:
        val, _ = winreg.QueryValueEx(key, name)
        return str(val) if val else None
    except Exception:
        return None


# ── File Indexer ───────────────────────────────────────────────────────────────

def index_files() -> dict:
    """Indexes all user files by name → full path."""
    files = {}
    for base_dir in USER_SCAN_DIRS:
        if not os.path.exists(base_dir):
            continue
        for root, dirs, filenames in os.walk(base_dir):
            # Skip hidden/system folders
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for fname in filenames:
                ext = os.path.splitext(fname)[1].lower()
                if ext in INDEXED_EXTENSIONS:
                    key  = fname.lower()
                    path = os.path.join(root, fname)
                    files[key] = path
                    # Also index without extension
                    no_ext = os.path.splitext(fname)[0].lower()
                    files[no_ext] = path
    print(f"[Scanner] Indexed {len(files)} files")
    return files


# ── Cache Save/Load ────────────────────────────────────────────────────────────

def save_cache(apps: dict, files: dict):
    with open(APPS_CACHE,  "w") as f:
        json.dump(apps,  f, indent=2)
    with open(FILES_CACHE, "w") as f:
        json.dump(files, f, indent=2)
    print(f"[Scanner] Cache saved → {APPS_CACHE}")


def load_apps() -> dict:
    if os.path.exists(APPS_CACHE):
        with open(APPS_CACHE) as f:
            return json.load(f)
    return {}


def load_files() -> dict:
    if os.path.exists(FILES_CACHE):
        with open(FILES_CACHE) as f:
            return json.load(f)
    return {}


def search_app(query: str, apps: dict) -> tuple[str, str] | None:
    """Fuzzy search for an app by name. Returns (name, path) or None."""
    q = query.lower().strip()

    # Exact match
    if q in apps:
        return q, apps[q]

    # Starts-with match
    for name, path in apps.items():
        if name.startswith(q) or q.startswith(name):
            return name, path

    # Contains match
    for name, path in apps.items():
        if q in name or name in q:
            return name, path

    return None


def search_file(query: str, files: dict) -> tuple[str, str] | None:
    """Fuzzy search for a file by name. Returns (name, path) or None."""
    q = query.lower().strip()

    if q in files:
        return q, files[q]

    for name, path in files.items():
        if q in name or name in q:
            return name, path

    return None


# ── Run standalone ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\n[ SHAIK-AI System Scanner ]")
    print("Scanning installed apps...")
    apps  = discover_apps()
    print("Indexing your files...")
    files = index_files()
    save_cache(apps, files)
    print(f"\n✅ Done! {len(apps)} apps  |  {len(files)} files indexed.")
    print("SHAIK-AI can now open any of them by voice.\n")
