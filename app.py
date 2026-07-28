import os
import re
import requests
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web & YouTube Proxy</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; padding: 20px; box-sizing: border-box; }
        .container { background: white; padding: 30px; border-radius: 8px; box-shadow: 0 4px 10px rgba(0,0,0,0.1); text-align: center; width: 100%; max-width: 800px; }
        h1 { margin-bottom: 10px; color: #333; }
        p { color: #666; font-size: 14px; margin-bottom: 20px; }
        .input-group { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex: 1; padding: 12px; font-size: 16px; border: 1px solid #ccc; border-radius: 4px; }
        button { padding: 12px 20px; font-size: 16px; background-color: #007bff; color: white; border: none; border-radius: 4px; cursor: pointer; font-weight: bold; }
        button:hover { background-color: #0056b3; }
        .player-container { width: 100%; aspect-ratio: 16 / 9; background: #000; border-radius: 8px; overflow: hidden; margin-top: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.2); }
        iframe { width: 100%; height: 100%; border: none; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Web & YouTube Proxy</h1>
        <p>Paste any <b>Website address</b> (e.g. <i>wikipedia.org</i>) or a <b>YouTube video link</b> below:</p>
        <form class="input-group" action="/proxy" method="GET">
            <input type="text" name="url" placeholder="https://example.com or YouTube Video Link" required />
            <button type="submit">Browse</button>
        </form>

        {% if video_id %}
        <h3>YouTube Stream Player</h3>
        <div class="player-container">
            <iframe 
                src="https://www.youtube-nocookie.com/embed/{{ video_id }}?autoplay=1&rel=0" 
                allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture" 
                allowfullscreen>
            </iframe>
        </div>
        {% endif %}
    </div>
</body>
</html>
"""


def extract_youtube_id(url_or_id):
    """Detects if input is a YouTube URL and extracts the video ID"""
    pattern = r"(?:v=|\/|youtu\.be\/|shorts\/)([a-zA-Z0-9_-]{11})"
    match = re.search(pattern, url_or_id)
    if match:
        return match.group(1)
    elif len(url_or_id.strip()) == 11 and " " not in url_or_id:
        return url_or_id.strip()
    return None


@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, video_id=None)


@app.route("/proxy", methods=["GET"])
def proxy():
    target_url = request.args.get("url", "").strip()

    if not target_url:
        return "URL parameter is missing.", 400

    # 1. If it's a YouTube link, load the unblocked video player
    yt_id = extract_youtube_id(target_url)
    if yt_id:
        return render_template_string(HTML_TEMPLATE, video_id=yt_id)

    # 2. Otherwise, treat as a standard web proxy request
    if not target_url.startswith("http://") and not target_url.startswith(
        "https://"
    ):
        target_url = "https://" + target_url

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
