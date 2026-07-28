import os
import re
import urllib.parse
import requests
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

# Main HTML Template with Slideshow Background
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web, YouTube & Streaming Proxy</title>
    <style>
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            color: #ffffff;
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            min-height: 100vh;
            box-sizing: border-box;
            background-color: #0d0d11;
        }

        #bg-slideshow {
            position: fixed;
            top: 0; left: 0; width: 100vw; height: 100vh;
            z-index: -1;
            background-size: cover;
            background-position: center;
            transition: background-image 1.5s ease-in-out;
        }

        #bg-slideshow::after {
            content: '';
            position: absolute;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(rgba(10, 10, 18, 0.78), rgba(10, 10, 18, 0.88));
        }

        .container {
            width: 100%;
            max-width: 900px;
            text-align: center;
            background: rgba(18, 18, 28, 0.78);
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.12);
            border-radius: 20px;
            padding: 35px;
            box-shadow: 0 15px 35px rgba(0, 0, 0, 0.6), 0 0 30px rgba(255, 0, 85, 0.2);
            margin-top: auto;
            margin-bottom: auto;
        }

        h1 {
            background: linear-gradient(135deg, #ff0055, #ff5500, #ff00cc);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 38px;
            font-weight: 800;
            margin-bottom: 8px;
            letter-spacing: -0.5px;
        }

        p { color: #d0d0e0; margin-bottom: 25px; font-size: 15px; }

        .input-group { display: flex; gap: 12px; margin-bottom: 20px; }

        input[type="text"] {
            flex: 1;
            padding: 16px 20px;
            font-size: 16px;
            border: 1px solid rgba(255, 255, 255, 0.2);
            border-radius: 12px;
            background: rgba(0, 0, 0, 0.5);
            color: white;
            outline: none;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus {
            border-color: #ff0055;
            box-shadow: 0 0 15px rgba(255, 0, 85, 0.4);
            background: rgba(0, 0, 0, 0.7);
        }

        button {
            padding: 16px 28px;
            font-size: 16px;
            background: linear-gradient(135deg, #ff0055, #ff5500);
            color: white;
            border: none;
            border-radius: 12px;
            cursor: pointer;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(255, 0, 85, 0.3);
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 0, 85, 0.5);
        }

        .nav-links { margin-bottom: 25px; }
        .nav-links a {
            color: #99bbff;
            text-decoration: none;
            margin: 0 10px;
            font-size: 15px;
            font-weight: 600;
            transition: color 0.2s;
        }
        .nav-links a:hover { color: #ff0055; text-shadow: 0 0 8px rgba(255, 0, 85, 0.6); }

        .player-container {
            width: 100%;
            aspect-ratio: 16 / 9;
            background: #000;
            border-radius: 14px;
            overflow: hidden;
            margin-top: 25px;
            box-shadow: 0 10px 30px rgba(255, 0, 85, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        iframe { width: 100%; height: 100%; border: none; }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
            gap: 20px;
            text-align: left;
            margin-top: 25px;
        }

        .card {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 12px;
            overflow: hidden;
            text-decoration: none;
            color: white;
            transition: all 0.3s ease;
            border: 1px solid rgba(255, 255, 255, 0.1);
            display: block;
        }

        .card:hover {
            transform: translateY(-6px);
            background: rgba(255, 255, 255, 0.12);
            border-color: #ff0055;
            box-shadow: 0 8px 25px rgba(255, 0, 85, 0.3);
        }

        .card img {
            width: 100%;
            aspect-ratio: 16 / 9;
            object-fit: cover;
            background: #000;
        }

        .card-body { padding: 14px; }
        .card-title { font-size: 14px; font-weight: 600; line-height: 1.4; }
    </style>
</head>
<body>
    <div id="bg-slideshow"></div>

    <div class="container">
        <h1>Web, YouTube & Movies</h1>
        <p>Browse websites, search YouTube videos, or click below for Movies & Anime!</p>
        
        <form class="input-group" action="/proxy" method="GET">
            <input type="text" name="url" placeholder="Search YouTube, type youtube.com, or enter a website..." value="{{ last_query }}" required />
            <button type="submit">Search / Go</button>
        </form>

        <div class="nav-links">
            <a href="/proxy?url=youtube.com">▶️ YouTube</a> | 
            <a href="/movies" style="color:#ff0055; font-size:16px;">🎬 Direct Movies & Anime Site</a> | 
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
        <h2 style="text-align:left; color:#ff0055; margin-top:30px; font-size:20px;">YouTube Videos</h2>
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

    <script>
        const bgImages = [
            'https://i.postimg.cc/jw4cM2Sx/1.jpg',
            'https://i.postimg.cc/xCWZTbrX/2.jpg',
            'https://i.postimg.cc/Y9JPqmc4/3.jpg',
            'https://i.postimg.cc/vBpKH6Rx/4.jpg',
            'https://i.postimg.cc/zB9QXRmV/5.jpg',
            'https://i.postimg.cc/PxB7r8Gt/6.jpg'
        ];

        let currentIndex = 0;
        const bgDiv = document.getElementById('bg-slideshow');

        function updateSlideshow() {
            bgDiv.style.backgroundImage = `url('${bgImages[currentIndex]}')`;
            currentIndex = (currentIndex + 1) % bgImages.length;
        }

        updateSlideshow();
        setInterval(updateSlideshow, 5000);
    </script>
</body>
</html>
"""

# Dedicated Direct Movies & Anime Portal Template (100% Allowed Embed Engine)
MOVIE_PORTAL_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Movies & Anime Portal</title>
    <style>
        body { font-family: 'Inter', -apple-system, sans-serif; background: #0d0d11; color: #fff; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; min-height: 100vh; box-sizing: border-box; }
        .header { width: 100%; max-width: 900px; display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .header a { color: #ff0055; text-decoration: none; font-weight: bold; font-size: 16px; }
        .card-box { width: 100%; max-width: 900px; background: rgba(20,20,30,0.85); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.12); border-radius: 20px; padding: 30px; text-align: center; box-sizing: border-box; box-shadow: 0 15px 35px rgba(0,0,0,0.6); }
        h1 { background: linear-gradient(135deg, #ff0055, #ff5500); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 8px; font-size: 32px; font-weight: 800; }
        .search-row { display: flex; gap: 10px; margin-bottom: 20px; }
        input[type="text"] { flex: 1; padding: 14px 18px; font-size: 16px; border-radius: 10px; border: 1px solid rgba(255,255,255,0.2); background: rgba(0,0,0,0.5); color: white; outline: none; }
        input[type="text"]:focus { border-color: #ff0055; }
        button { padding: 14px 24px; background: linear-gradient(135deg, #ff0055, #ff5500); color: white; border: none; border-radius: 10px; font-weight: bold; cursor: pointer; font-size: 16px; }
        button:hover { opacity: 0.9; }
        .player-frame { width: 100%; aspect-ratio: 16 / 9; background: #000; border-radius: 12px; overflow: hidden; border: 1px solid rgba(255,255,255,0.1); margin-top: 15px; box-shadow: 0 10px 30px rgba(255,0,85,0.25); }
        iframe { width: 100%; height: 100%; border: none; }
        .quick-tags { display: flex; flex-wrap: wrap; gap: 10px; justify-content: center; margin-top: 15px; }
        .tag { background: rgba(255,255,255,0.08); padding: 8px 16px; border-radius: 20px; font-size: 14px; color: #ddd; cursor: pointer; border: 1px solid rgba(255,255,255,0.1); transition: 0.2s; }
        .tag:hover { background: #ff0055; color: white; border-color: #ff0055; }
    </style>
</head>
<body>
    <div class="header">
        <a href="/">⬅️ Back to Main Proxy</a>
        <span style="color:#aaa; font-size:14px;">HD Movie & Anime Stream Engine</span>
    </div>

    <div class="card-box">
        <h1>🎬 HD Movie & Anime Stream</h1>
        <p style="color:#bbb; font-size:14px; margin-bottom:20px;">Search any Movie, TV Show, or Anime title below to load the HD player:</p>
        
        <form class="search-row" onsubmit="event.preventDefault(); searchAndPlay();">
            <input type="text" id="movieSearch" placeholder="Type a Movie or Anime (e.g. Naruto, Avatar, Spider-Man)..." required />
            <button type="submit">Play Stream</button>
        </form>

        <div class="quick-tags">
            <span class="tag" onclick="loadByTmdb('19995')">🌌 Avatar</span>
            <span class="tag" onclick="loadByTmdb('299536')">🎬 Avengers: Endgame</span>
            <span class="tag" onclick="loadByTmdb('372058')">⚔️ Your Name (Anime)</span>
            <span class="tag" onclick="loadByTmdb('31910', true)">🍃 Naruto</span>
            <span class="tag" onclick="loadByTmdb('1429', true)">⚔️ Attack on Titan</span>
            <span class="tag" onclick="loadByTmdb('634649')">🕷️ Spider-Man: No Way Home</span>
        </div>

        <div class="player-frame">
            <iframe id="videoPlayer" src="https://vidsrc.cc/v2/embed/movie/19995" allow="autoplay; encrypted-media; fullscreen" allowfullscreen></iframe>
        </div>
    </div>

    <script>
        async function searchAndPlay() {
            const query = document.getElementById('movieSearch').value.trim();
            if (!query) return;
            try {
                const res = await fetch(`https://api.themoviedb.org/3/search/multi?api_key=15d2fb6fe02810145405a2682f028b27&query=${encodeURIComponent(query)}`);
                const data = await res.json();
                if (data.results && data.results.length > 0) {
                    const item = data.results[0];
                    if (item.media_type === 'tv') {
                        document.getElementById('videoPlayer').src = `https://vidsrc.cc/v2/embed/tv/${item.id}/1/1`;
                    } else {
                        document.getElementById('videoPlayer').src = `https://vidsrc.cc/v2/embed/movie/${item.id}`;
                    }
                } else {
                    alert("No title found. Try typing the exact movie or anime name!");
                }
            } catch (e) {
                alert("Search error. Please try again.");
            }
        }

        function loadByTmdb(tmdbId, isTv = false) {
            if (isTv) {
                document.getElementById('videoPlayer').src = `https://vidsrc.cc/v2/embed/tv/${tmdbId}/1/1`;
            } else {
                document.getElementById('videoPlayer').src = `https://vidsrc.cc/v2/embed/movie/${tmdbId}`;
            }
        }
    </script>
</body>
</html>
"""


def extract_youtube_id(url_or_id):
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
    try:
        search_url = f"https://www.youtube.com/results?search_query={urllib.parse.quote(query)}"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
        }
        resp = requests.get(search_url, headers=headers, timeout=10)
        html = resp.text

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


@app.route("/movies")
def movies():
    """Direct Movies & Anime Streaming Portal"""
    return render_template_string(MOVIE_PORTAL_TEMPLATE)


@app.route("/proxy", methods=["GET"])
def proxy():
    user_input = request.args.get("url", "").strip()

    if not user_input:
        return "Search query or URL is missing.", 400

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

    yt_id = extract_youtube_id(user_input)
    if yt_id:
        return render_template_string(
            HTML_TEMPLATE, video_id=yt_id, yt_results=None, last_query=user_input
        )

    is_url = user_input.startswith(("http://", "https://")) or (
        "." in user_input and " " not in user_input
    )

    if is_url:
        if not user_input.startswith(("http://", "https://")):
            target_url = "https://" + user_input
        else:
            target_url = user_input
    else:
        results = search_youtube(user_input)
        if results:
            return render_template_string(
                HTML_TEMPLATE,
                video_id=None,
                yt_results=results,
                last_query=user_input,
            )
        else:
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
