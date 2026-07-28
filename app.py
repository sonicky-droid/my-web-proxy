import os
import re
import urllib.parse
import requests
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

# Main HTML Page Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web & YouTube Proxy</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0f0f0f; color: #fff; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; box-sizing: border-box; }
        .container { width: 100%; max-width: 900px; text-align: center; }
        h1 { color: #ff0000; margin-bottom: 10px; font-size: 32px; }
        p { color: #aaa; margin-bottom: 25px; font-size: 15px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 25px; }
        input[type="text"] { flex: 1; padding: 14px; font-size: 16px; border: 1px solid #333; border-radius: 6px; background: #1f1f1f; color: white; outline: none; }
        input[type="text"]:focus { border-color: #ff0000; }
        button { padding: 14px 28px; font-size: 16px; background-color: #ff0000; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; transition: 0.2s; }
        button:hover { background-color: #cc0000; }
        .nav-links { margin-bottom: 25px; }
        .nav-links a { color: #0088ff; text-decoration: none; margin: 0 10px; font-size: 15px; font-weight: 500; }
        .nav-links a:hover { text-decoration: underline; }
        .player-container { width: 100%; aspect-ratio: 16 / 9; background: #000; border-radius: 12px; overflow: hidden; margin-top: 20px; box-shadow: 0 8px 25px rgba(255,0,0,0.25); }
        iframe { width: 100%; height: 100%; border: none; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 20px; text-align: left; margin-top: 20px; }
        .card { background: #181818; border-radius: 8px; overflow: hidden; text-decoration: none; color: white; transition: transform 0.2s, background 0.2s; border: 1px solid #282828; display: block; }
        .card:hover { transform: translateY(-4px); background: #222; border-color: #ff0000; }
        .card img { width: 100%; aspect-ratio: 16 / 9; object-fit: cover; background: #000; }
        .card-body { padding: 12px; }
        .card-title { font-size: 14px; font-weight: bold; line-height: 1.4; max-height: 2.8em; overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web & YouTube Proxy</h1>
        <p>Browse websites, search YouTube videos, and watch full ad-free streams!</p>
        
        <form class="input-group" action="/proxy" method="GET">
            <input type="text" name="url" placeholder="Search YouTube, type youtube.com, or enter a website..." value="{{ last_query }}" required />
            <button type="submit">Search / Go</button>
        </form>

        <div class="nav-links">
            <a href="/proxy?url=youtube.com">▶️ YouTube Portal</a> | 
            <a href="/proxy?url=wikipedia.org">🌐 Wikipedia</a>
        </div>

        {% if video_id %}
        <div class="player-container">
            <iframe 
                src="https://www.youtube-nocookie.com/embed/{{ video_id }}?autoplay=1&rel=0&modestbranding=1" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        </div>
        {% endif %}

        {% if yt_results %}
        <h2 style="text-align:left; color:#ff0000; margin-top:30px;">YouTube Video Search Results</h2>
        <div class="grid">
            {% for vid in yt_results %}
            <a class="card" href="/proxy?url=https://www.youtube.com/watch?v={{ vid.id }}">
                <img src="https://i.ytimg.com/vi/{{ vid.id }}/hqdefault.jpg" alt="thumbnail" loading="lazy" />
                <div class="card-body">
                    <div class="card-title">{{ vid.title }}</div>
                </div>
            </a>
            {% endfor %}
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


def extract_youtube_id(url_or_id):
    """Detects YouTube video URL or ID"""
    pattern = r"(?:v=|\/|youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url_or_id)
    if match:
        return match.group(1)
    elif (
        len(url_or_id.strip()) == 11
        and " " not in url_or_id
        and not url_or_id.startswith("http")
    ):
        return url_or_id.strip()
    return None


def search_youtube(query):
    """Scrapes YouTube search results for a clean video grid"""
    try:
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        resp = requests.get(search_url, headers=headers, timeout=10)
        html = resp.text

        # Extract video IDs and titles using regex
        video_matches = re.findall(
            r'"videoId":"([a-zA-Z0-9_-]{11})".*?"title":\{"runs":\[\{"text":"([^"]+)"\}',
            html,
        )

        results = []
        seen = set()
        for vid_id, title in video_matches:
            if vid_id not in seen:
                seen.add(vid_id)
                clean_title = (
                    title.encode("utf-8").decode("unicode-escape", errors="ignore")
                )
                results.append({"id": vid_id, "title": clean_title})
                if len(results) >= 12:
                    break
        return results
    except Exception:
        return []


@app.route("/")
def index():
    return render_template_string(
        HTML_TEMPLATE, video_id=None, yt_results=None, last_query=""
    )


@app.route("/proxy", methods=["GET"])
def proxy():
    user_input = request.args.get("url", "").strip()

    if not user_input:
        return "Search query or URL is missing.", 400

    # 1. User typed 'youtube.com' or 'youtube'
    if user_input.lower() in [
        "youtube",
        "youtube.com",
        "https://youtube.com",
        "http://youtube.com",
        "www.youtube.com",
        "https://www.youtube.com",
    ]:
        results = search_youtube("trending videos")
        return render_template_string(
            HTML_TEMPLATE,
            video_id=None,
            yt_results=results,
            last_query="youtube.com",
        )

    # 2. User pasted a direct YouTube Video link
    yt_id = extract_youtube_id(user_input)
    if yt_id:
        return render_template_string(
            HTML_TEMPLATE, video_id=yt_id, yt_results=None, last_query=user_input
        )

    # 3. Check if input is a direct Website URL vs Search Term
    is_url = user_input.startswith(("http://", "https://")) or (
        "." in user_input and " " not in user_input
    )

    if is_url:
        if not user_input.startswith(("http://", "https://")):
            target_url = "https://" + user_input
        else:
            target_url = user_input
    else:
        # Search YouTube for video queries
        results = search_youtube(user_input)
        if results:
            return render_template_string(
                HTML_TEMPLATE,
                video_id=None,
                yt_results=results,
                last_query=user_input,
            )
        else:
            # Fallback to DuckDuckGo search if no YouTube videos found
            encoded_query = urllib.parse.quote(user_input)
            target_url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        }

        resp = requests.get(
            target_url, headers=headers, timeout=20, allow_redirects=True
        )

        content_type = resp.headers.get("Content-Type", "")
        content = resp.content

        if "text/html" in content_type:
            html_text = resp.text
            base_tag = f'<base href="{target_url}">'

            if "<head>" in html_text:
                html_text = html_text.replace("<head>", f"<head>{base_tag}", 1)
            else:
                html_text = base_tag + html_text

            content = html_text.encode("utf-8")

        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        response_headers = [
            (name, value)
            for (name, value) in resp.raw.headers.items()
            if name.lower() not in excluded_headers
        ]

        return Response(content, resp.status_code, response_headers)

    except Exception as e:
        return f"Proxy Error: {str(e)}", 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
