"""
SHAIK-AI — Global Voice Assistant Web App + PWA
Deployable on Railway / Render / Fly.io
Installable as app on Android, iOS, Windows, Mac
"""

import os, re, random
from datetime import datetime
from flask import Flask, render_template, request, jsonify, send_from_directory

app = Flask(__name__)
application = app

WEBSITE_MAP = {
    "youtube":       "https://www.youtube.com",
    "google":        "https://www.google.com",
    "gmail":         "https://mail.google.com",
    "github":        "https://www.github.com",
    "stackoverflow": "https://stackoverflow.com",
    "netflix":       "https://www.netflix.com",
    "twitter":       "https://www.twitter.com",
    "x":             "https://www.twitter.com",
    "linkedin":      "https://www.linkedin.com",
    "instagram":     "https://www.instagram.com",
    "facebook":      "https://www.facebook.com",
    "reddit":        "https://www.reddit.com",
    "wikipedia":     "https://www.wikipedia.org",
    "maps":          "https://maps.google.com",
    "translate":     "https://translate.google.com",
    "chatgpt":       "https://chat.openai.com",
    "spotify":       "https://open.spotify.com",
    "amazon":        "https://www.amazon.in",
    "flipkart":      "https://www.flipkart.com",
    "news":          "https://news.google.com",
    "drive":         "https://drive.google.com",
    "meet":          "https://meet.google.com",
    "calendar":      "https://calendar.google.com",
    "docs":          "https://docs.google.com",
    "sheets":        "https://sheets.google.com",
    "slides":        "https://slides.google.com",
    "hotstar":       "https://www.hotstar.com",
    "prime":         "https://www.primevideo.com",
    "whatsapp":      "https://web.whatsapp.com",
    "telegram":      "https://web.telegram.org",
    "zoom":          "https://zoom.us/join",
    "teams":         "https://teams.microsoft.com",
    "notion":        "https://www.notion.so",
    "canva":         "https://www.canva.com",
    "figma":         "https://www.figma.com",
    "replit":        "https://replit.com",
    "stackoverflow": "https://stackoverflow.com",
    "leetcode":      "https://leetcode.com",
    "udemy":         "https://www.udemy.com",
    "coursera":      "https://www.coursera.org",
    "wikipedia":     "https://www.wikipedia.org",
}

JOKES = [
    "Why do programmers prefer dark mode? Because light attracts bugs!",
    "Why did the programmer quit? He didn't get arrays!",
    "I told my computer I needed a break. Now it won't stop sending me Kit-Kat ads.",
    "Why do Java developers wear glasses? Because they don't C sharp!",
    "A SQL query walks into a bar and asks two tables: Can I join you?",
    "Why was the developer unhappy at their job? They wanted arrays!",
    "How do you comfort a JavaScript bug? You console it.",
    "Why do Python programmers wear glasses? Because they cannot C!",
]

def parse(text: str) -> dict:
    t = text.lower().strip()

    # Greet
    if any(w in t for w in ["hello", "hi shaik", "hey shaik", "good morning", "good evening", "good night", "wake up"]):
        h = datetime.now().hour
        g = "Good morning" if h < 12 else "Good afternoon" if h < 18 else "Good evening"
        return {"action": "speak", "text": f"{g}! I am SHAIK-AI. How can I help you today?"}

    # Time
    if any(w in t for w in ["what time", "current time", "tell me the time", "time now"]):
        return {"action": "speak", "text": f"The time is {datetime.now().strftime('%I:%M %p')}"}

    # Date
    if any(w in t for w in ["what date", "today's date", "what day", "today is"]):
        return {"action": "speak", "text": f"Today is {datetime.now().strftime('%A, %d %B %Y')}"}

    # Joke
    if any(w in t for w in ["joke", "funny", "make me laugh", "tell me something funny"]):
        return {"action": "speak", "text": random.choice(JOKES)}

    # Math
    math = re.search(r"(?:what is|calculate|compute)?\s*(\d+)\s*(plus|minus|times|divided by|multiplied by|\+|\-|\*|\/)\s*(\d+)", t)
    if math:
        a, op, b = int(math.group(1)), math.group(2), int(math.group(3))
        ops = {"plus":"+","minus":"-","times":"*","multiplied by":"*","divided by":"/","+":"+","-":"-","*":"*","/":"/"}
        try:
            result = eval(f"{a}{ops.get(op,op)}{b}")
            return {"action": "speak", "text": f"{a} {op} {b} equals {result}"}
        except: pass

    # WhatsApp message to number
    wa = re.search(r"(?:send|whatsapp|message|text)\s+(?:to\s+)?(\+?\d[\d\s]{8,})\s+(?:say\s+)?(.+)", t)
    if wa:
        num = wa.group(1).replace(" ","").replace("+","")
        msg = wa.group(2).strip()
        return {"action": "open_url",
                "url": f"https://web.whatsapp.com/send?phone={num}&text={msg.replace(' ','%20')}",
                "label": f"WhatsApp to +{num}"}

    # Weather
    if "weather" in t:
        m = re.search(r"weather\s+(?:in|of|at|for)?\s*(.+)", t)
        city = m.group(1).strip() if m else "my+location"
        return {"action": "open_url",
                "url": f"https://www.google.com/search?q=weather+{city.replace(' ','+')}",
                "label": f"Weather in {city}"}

    # Search
    m = re.search(r"(?:search(?:\s+for)?|google|find|look\s+up)\s+(.+)", t)
    if m:
        q = m.group(1).strip()
        return {"action": "open_url",
                "url": f"https://www.google.com/search?q={q.replace(' ','+')}",
                "label": f"Searching: {q}"}

    # YouTube search
    yt = re.search(r"(?:play|search on youtube|youtube search)\s+(.+)", t)
    if yt:
        q = yt.group(1).strip()
        return {"action": "open_url",
                "url": f"https://www.youtube.com/results?search_query={q.replace(' ','+')}",
                "label": f"YouTube: {q}"}

    # Website open
    for trigger in ["open", "go to", "browse", "navigate to", "launch", "show me", "take me to"]:
        if trigger in t:
            for site, url in WEBSITE_MAP.items():
                if site in t:
                    return {"action": "open_url", "url": url, "label": f"Opening {site.title()}"}

    for site, url in WEBSITE_MAP.items():
        if site in t:
            return {"action": "open_url", "url": url, "label": f"Opening {site.title()}"}

    # Fallback: search it
    if len(t) > 2:
        return {"action": "open_url",
                "url": f"https://www.google.com/search?q={t.replace(' ','+')}",
                "label": f"Searching: {text}"}

    return {"action": "unknown", "text": "Sorry, I didn't understand that. Try: open YouTube, search cricket score, what time is it."}


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("pwa.html")

@app.route("/api/command", methods=["POST"])
def command():
    data = request.get_json()
    text = (data or {}).get("command", "").strip()
    if not text:
        return jsonify({"action": "unknown", "text": "No command."}), 400
    return jsonify(parse(text))

@app.route("/static/sw.js")
def sw():
    return send_from_directory("static", "sw.js",
                               mimetype="application/javascript")

@app.route("/health")
def health():
    return jsonify({"status": "ok", "app": "SHAIK-AI"})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"\n SHAIK-AI → http://localhost:{port}\n")
    app.run(host="0.0.0.0", port=port)
