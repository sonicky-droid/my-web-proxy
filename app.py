import os
import re
import urllib.parse
import requests
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

TMDB_API_KEY = "15d2fb6fe02810145405a2682f028b27"  # TMDB API Key

# 100% Working English HTML5 Games (Google Official Content CDN)
GAMES_DATABASE = [
    {
        "id": "subway-surfers",
        "title": "Subway Surfers",
        "category": "Runner",
        "poster": "https://img.gamepix.com/games/subway-surfers/cover/subway-surfers.png?width=300",
        "url": "https://images-opensocial.googleusercontent.com/gadgets/ifr?url=https://cdn.jsdelivr.net/gh/bobydope/g@main/ss/ss.xml",
    },
    {
        "id": "moto-x3m",
        "title": "Moto X3M",
        "category": "Racing",
        "poster": "https://img.gamepix.com/games/moto-x3m/cover/moto-x3m.png?width=300",
        "url": "https://images-opensocial.googleusercontent.com/gadgets/ifr?url=https://cdn.jsdelivr.net/gh/bobydope/g@main/moto-x3m/moto-x3m.xml",
    },
    {
        "id": "drive-mad",
        "title": "Drive Mad",
        "category": "Driving",
        "poster": "https://img.gamepix.com/games/drive-mad/cover/drive-mad.png?width=300",
        "url": "https://images-opensocial.googleusercontent.com/gadgets/ifr?url=https://cdn.jsdelivr.net/gh/bobydope/g@main/drive-mad/drive-mad.xml",
    },
    {
        "id": "basketball-stars",
        "title": "Basketball Stars",
        "category": "Sports",
        "poster": "https://img.gamepix.com/games/basketball-legends-2020/cover/basketball-legends-2020.png?width=300",
        "url": "https://images-opensocial.googleusercontent.com/gadgets/ifr?url=https://cdn.jsdelivr.net/gh/bobydope/g@main/bs/bs.xml",
    },
    {
        "id": "geometry-dash",
        "title": "Geometry Dash",
        "category": "Arcade",
        "poster": "https://img.gamepix.com/games/geometry-jump/cover/geometry-jump.png?width=300",
        "url": "https://images-opensocial.googleusercontent.com/gadgets/ifr?url=https://cdn.jsdelivr.net/gh/bobydope/g@main/gd/gd.xml",
    },
    {
        "id": "retro-bowl",
        "title": "Retro Bowl",
        "category": "Sports",
        "poster": "https://img.gamepix.com/games/tunnel-rush/cover/tunnel-rush.png?width=300",
        "url": "https://images-opensocial.googleusercontent.com/gadgets/ifr?url=https://cdn.jsdelivr.net/gh/bobydope/g@main/rb/rb.xml",
    },
]

COMMON_CSS = """
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
        background: linear-gradient(rgba(10, 10, 18, 0.82), rgba(10, 10, 18, 0.90));
    }

    .container {
        width: 100%;
        max-width: 950px;
        text-align: center;
        background: rgba(18, 18, 28, 0.82);
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.12);
        border-radius: 20px;
        padding: 30px;
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

    button, .server-btn, .site-btn {
        padding: 12px 20px;
        font-size: 14px;
        background: linear-gradient(135deg, #ff0055, #ff5500);
        color: white;
        border: none;
        border-radius: 10px;
        cursor: pointer;
        font-weight: 700;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(255, 0, 85, 0.3);
    }

    button:hover, .server-btn:hover, .site-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(255, 0, 85, 0.5);
    }

    .server-btn, .site-btn { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); }
    .server-btn:hover, .site-btn:hover { background: #ff0055; }

    .nav-links { margin-bottom: 20px; display: flex; justify-content: center; gap: 10px; flex-wrap: wrap; }
    .nav-links a {
        color: #99bbff;
        text-decoration: none;
        font-size: 15px;
        font-weight: 600;
        padding: 8px 16px;
        border-radius: 20px;
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(255,255,255,0.1);
        transition: all 0.2s;
    }
    .nav-links a:hover, .nav-links a.active {
        color: white;
        background: #ff0055;
        border-color: #ff0055;
        box-shadow: 0 0 12px rgba(255,0,85,0.5);
    }

    .player-container {
        width: 100%;
        aspect-ratio: 16 / 9;
        background: #000;
        border-radius: 14px;
        overflow: hidden;
        margin-top: 15px;
        box-shadow: 0 10px 30px rgba(255, 0, 85, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    iframe { width: 100%; height: 100%; border: none; }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(170px, 1fr));
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
        aspect-ratio: 2 / 3;
        object-fit: cover;
        background: #000;
    }

    .card-body { padding: 12px; }
    .card-title { font-size: 14px; font-weight: 600; line-height: 1.3; }
    .card-sub { font-size: 12px; color: #ff0055; margin-top: 4px; font-weight: bold; }
"""

SLIDESHOW_SCRIPT = """
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
"""

# Home Page Template with KissKH, Poki, CrazyGames, and Gogoanime Quick Launch
HOME_TEMPLATE = (
    """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web Proxy Hub</title>
    <style>"""
    + COMMON_CSS
    + """</style>
</head>
<body>
    <div id="bg-slideshow"></div>

    <div class="container">
        <h1>Web Proxy & Media Hub</h1>
        <p>Search using <b>Yandex Search</b>, stream Anime, Movies, YouTube, or launch featured portals!</p>

        <div class="nav-links">
            <a href="/anime" class="active">⛩️ Anime Center</a>
            <a href="/movies">🎬 Movies & TV Shows</a>
            <a href="/games">🎮 Games Arcade</a>
            <a href="/youtube">▶️ YouTube Portal</a>
        </div>

        <div style="margin-bottom: 20px; display: flex; gap: 10px; justify-content: center; flex-wrap: wrap;">
            <a class="site-btn" href="/proxy?url=https://kisskh.do" style="text-decoration:none;">💋 KissKH.do</a>
            <a class="site-btn" href="/proxy?url=https://poki.com" style="text-decoration:none;">🎮 Poki.com</a>
            <a class="site-btn" href="/proxy?url=https://www.crazygames.com" style="text-decoration:none;">🕹️ CrazyGames</a>
            <a class="site-btn" href="/proxy?url=https://gogoanime.or.at" style="text-decoration:none;">⛩️ Gogoanime</a>
        </div>

        <form class="input-group" action="/proxy" method="GET">
            <input type="text" name="url" placeholder="Search Yandex or type a website address..." required />
            <button type="submit" style="padding: 16px 28px; font-size:16px;">Search Yandex / Go</button>
        </form>

        <div style="margin-top:25px; text-align:left;">
            <h3 style="color:#ff0055;">✨ Quick Access Portals:</h3>
            <ul style="color:#ccc; line-height:1.8;">
                <li><b>💋 KissKH.do:</b> Asian dramas, anime & movies.</li>
                <li><b>🎮 Poki.com:</b> Direct Poki games library.</li>
                <li><b>🕹️ CrazyGames.com:</b> CrazyGames unblocked games library.</li>
                <li><b>⛩️ Gogoanime:</b> Direct Gogoanime stream portal (gogoanime.or.at).</li>
                <li><b>⛩️ Anime Center:</b> Native HD stream player for Dragon Ball, Naruto, One Piece, etc.</li>
            </ul>
        </div>
    </div>
"""
    + SLIDESHOW_SCRIPT
    + """
</body>
</html>
"""
)

# Dedicated Anime Page Template
ANIME_TEMPLATE = (
    """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dedicated Anime Center</title>
    <style>"""
    + COMMON_CSS
    + """</style>
</head>
<body>
    <div id="bg-slideshow"></div>

    <div class="container">
        <h1>⛩️ Dedicated Anime Center</h1>
        <p>Search any Anime title to watch full series and episodes in HD!</p>

        <div class="nav-links">
            <a href="/">🏠 Home</a>
            <a href="/anime" class="active">⛩️ Anime Center</a>
            <a href="/movies">🎬 Movies & TV</a>
            <a href="/games">🎮 Games</a>
            <a href="/youtube">▶️ YouTube</a>
        </div>

        <form class="input-group" action="/anime" method="GET">
            <input type="text" name="q" placeholder="Type Anime Name (e.g. Dragon Ball, Naruto, One Piece, Solo Leveling)..." value="{{ query }}" required />
            <button type="submit" style="padding: 16px 28px; font-size:16px;">Search Anime</button>
        </form>

        {% if player_url %}
        <h3 style="color:#ff0055; margin-top:20px;">Watching: {{ selected_title }}</h3>
        <p style="font-size:13px; color:#aaa; margin-bottom:10px;">If player fails, switch backup servers below:</p>

        <div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-bottom:15px;">
            <button class="server-btn" onclick="switchServer('https://autoembed.co/tv/tmdb/{{ selected_id }}-1-1')">Server 1 (AutoEmbed HD)</button>
            <button class="server-btn" onclick="switchServer('https://vidsrc.xyz/embed/tv/{{ selected_id }}/1/1')">Server 2 (VidSrc XYZ)</button>
            <button class="server-btn" onclick="switchServer('https://player.smashystream.com/tv/{{ selected_id }}?s=1&e=1')">Server 3 (SmashyStream)</button>
        </div>

        <div class="player-container">
            <iframe 
                id="animePlayer"
                src="{{ player_url }}" 
                referrerpolicy="no-referrer"
                allow="autoplay; encrypted-media; fullscreen" 
                allowfullscreen>
            </iframe>
        </div>

        <script>
            function switchServer(url) {
                document.getElementById('animePlayer').src = url;
            }
        </script>
        {% endif %}

        {% if results %}
        <h2 style="text-align:left; color:#ff0055; margin-top:30px; font-size:20px;">Anime Search Results</h2>
        <div class="grid">
            {% for item in results %}
            <a class="card" href="/anime?play_id={{ item.id }}&title={{ item.title | urlencode }}">
                <img src="{{ item.poster }}" alt="poster" loading="lazy" />
                <div class="card-body">
                    <div class="card-title">{{ item.title }}</div>
                    <div class="card-sub">ANIME ({{ item.year }})</div>
                </div>
            </a>
            {% endfor %}
        </div>
        {% endif %}
    </div>
"""
    + SLIDESHOW_SCRIPT
    + """
</body>
</html>
"""
)

# Dedicated Movies Page Template
MOVIES_TEMPLATE = (
    """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dedicated Movies & TV Center</title>
    <style>"""
    + COMMON_CSS
    + """</style>
</head>
<body>
    <div id="bg-slideshow"></div>

    <div class="container">
        <h1>🎬 Dedicated Movies & TV Center</h1>
        <p>Search any Hollywood Movie or Netflix/HBO Show to stream in full HD!</p>

        <div class="nav-links">
            <a href="/">🏠 Home</a>
            <a href="/anime">⛩️ Anime Center</a>
            <a href="/movies" class="active">🎬 Movies & TV</a>
            <a href="/games">🎮 Games</a>
            <a href="/youtube">▶️ YouTube</a>
        </div>

        <form class="input-group" action="/movies" method="GET">
            <input type="text" name="q" placeholder="Type Movie or Show Name (e.g. Avatar, Avengers, Spider-Man)..." value="{{ query }}" required />
            <button type="submit" style="padding: 16px 28px; font-size:16px;">Search Movies</button>
        </form>

        {% if player_url %}
        <h3 style="color:#ff0055; margin-top:20px;">Watching: {{ selected_title }}</h3>
        <p style="font-size:13px; color:#aaa; margin-bottom:10px;">If stream fails, switch backup servers below:</p>

        <div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-bottom:15px;">
            <button class="server-btn" onclick="switchServer('https://autoembed.co/{{ media_type }}/tmdb/{{ selected_id }}{% if media_type == \"tv\" %}-1-1{% endif %}')">Server 1 (AutoEmbed HD)</button>
            <button class="server-btn" onclick="switchServer('https://vidsrc.xyz/embed/{{ media_type }}/{{ selected_id }}{% if media_type == \"tv\" %}/1/1{% endif %}')">Server 2 (VidSrc XYZ)</button>
            <button class="server-btn" onclick="switchServer('https://player.smashystream.com/{{ media_type }}/{{ selected_id }}')">Server 3 (SmashyStream)</button>
        </div>

        <div class="player-container">
            <iframe 
                id="moviePlayer"
                src="{{ player_url }}" 
                referrerpolicy="no-referrer"
                allow="autoplay; encrypted-media; fullscreen" 
                allowfullscreen>
            </iframe>
        </div>

        <script>
            function switchServer(url) {
                document.getElementById('moviePlayer').src = url;
            }
        </script>
        {% endif %}

        {% if results %}
        <h2 style="text-align:left; color:#ff0055; margin-top:30px; font-size:20px;">Movie & Show Results</h2>
        <div class="grid">
            {% for item in results %}
            <a class="card" href="/movies?play_id={{ item.id }}&type={{ item.type }}&title={{ item.title | urlencode }}">
                <img src="{{ item.poster }}" alt="poster" loading="lazy" />
                <div class="card-body">
                    <div class="card-title">{{ item.title }}</div>
                    <div class="card-sub">{{ item.type | upper }} ({{ item.year }})</div>
                </div>
            </a>
            {% endfor %}
        </div>
        {% endif %}
    </div>
"""
    + SLIDESHOW_SCRIPT
    + """
</body>
</html>
"""
)

# Dedicated YouTube Portal Template
YOUTUBE_TEMPLATE = (
    """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dedicated YouTube Portal</title>
    <style>"""
    + COMMON_CSS
    + """</style>
</head>
<body>
    <div id="bg-slideshow"></div>

    <div class="container">
        <h1>▶️ Dedicated YouTube Portal</h1>
        <p>Search YouTube videos or paste a YouTube video link to play ad-free in HD!</p>

        <div class="nav-links">
            <a href="/">🏠 Home</a>
            <a href="/anime">⛩️ Anime Center</a>
            <a href="/movies">🎬 Movies & TV</a>
            <a href="/games">🎮 Games</a>
            <a href="/youtube" class="active">▶️ YouTube</a>
        </div>

        <form class="input-group" action="/youtube" method="GET">
            <input type="text" name="q" placeholder="Search YouTube or paste video link..." value="{{ query }}" required />
            <button type="submit" style="padding: 16px 28px; font-size:16px;">Search YouTube</button>
        </form>

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
        <h2 style="text-align:left; color:#ff0055; margin-top:30px; font-size:20px;">YouTube Video Results</h2>
        <div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));">
            {% for vid in yt_results %}
            <a class="card" href="/youtube?v={{ vid.id }}&q={{ query | urlencode }}">
                <img src="https://i.ytimg.com/vi/{{ vid.id }}/hqdefault.jpg" alt="thumbnail" loading="lazy" style="aspect-ratio: 16/9;" />
                <div class="card-body">
                    <div class="card-title">{{ vid.title }}</div>
                </div>
            </a>
            {% endfor %}
        </div>
        {% endif %}
    </div>
"""
    + SLIDESHOW_SCRIPT
    + """
</body>
</html>
"""
)

# Dedicated Games Template
GAMES_TEMPLATE = (
    """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unblocked Games Arcade</title>
    <style>"""
    + COMMON_CSS
    + """</style>
</head>
<body>
    <div id="bg-slideshow"></div>

    <div class="container">
        <h1>🎮 Unblocked Games Arcade</h1>
        <p>Click any game below to play in full screen in 100% English!</p>

        <div class="nav-links">
            <a href="/">🏠 Home</a>
            <a href="/anime">⛩️ Anime Center</a>
            <a href="/movies">🎬 Movies & TV</a>
            <a href="/games" class="active">🎮 Games</a>
            <a href="/youtube">▶️ YouTube</a>
        </div>

        {% if game_url %}
        <h3 style="color:#ff0055; margin-top:20px;">Playing: {{ game_title }}</h3>
        <div class="player-container" style="aspect-ratio: 16/10;">
            <iframe 
                src="{{ game_url }}" 
                allow="autoplay; gamepad; fullscreen; keyboard; focus-without-user-activation" 
                allowfullscreen>
            </iframe>
        </div>
        {% endif %}

        <h2 style="text-align:left; color:#ff0055; margin-top:30px; font-size:20px;">All Games (Google Official CDN)</h2>
        <div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));">
            {% for game in games_list %}
            <a class="card" href="/games?play={{ game.id }}">
                <img src="{{ game.poster }}" alt="game" loading="lazy" style="aspect-ratio: 1/1;" />
                <div class="card-body">
                    <div class="card-title">{{ game.title }}</div>
                    <div class="card-sub">{{ game.category }}</div>
                </div>
            </a>
            {% endfor %}
        </div>
    </div>
"""
    + SLIDESHOW_SCRIPT
    + """
</body>
</html>
"""
)


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


def tmdb_search(query):
    try:
        url = f"https://api.themoviedb.org/3/search/multi?api_key={TMDB_API_KEY}&query={urllib.parse.quote(query)}&include_adult=false"
        resp = requests.get(url, timeout=8).json()
        results = []
        for item in resp.get("results", [])[:12]:
            media_type = item.get("media_type")
            if media_type in ["movie", "tv"]:
                title = item.get("title") or item.get("name")
                poster_path = item.get("poster_path")
                release_date = item.get("release_date") or item.get(
                    "first_air_date", ""
                )
                year = release_date[:4] if release_date else "N/A"

                if poster_path and title:
                    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
                    results.append(
                        {
                            "id": item["id"],
                            "title": title,
                            "type": media_type,
                            "poster": poster_url,
                            "year": year,
                        }
                    )
        return results
    except Exception:
        return []


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
    return render_template_string(HOME_TEMPLATE)


@app.route("/anime", methods=["GET"])
def anime():
    query = request.args.get("q", "").strip()
    play_id = request.args.get("play_id")
    title = request.args.get("title", "Anime")

    if not query and not play_id:
        query = "Dragon Ball"

    player_url = None
    results = None

    if play_id:
        player_url = f"https://autoembed.co/tv/tmdb/{play_id}-1-1"
    else:
        results = tmdb_search(query)

    return render_template_string(
        ANIME_TEMPLATE,
        query=query if query != "Dragon Ball" else "",
        results=results,
        player_url=player_url,
        selected_id=play_id,
        selected_title=title,
    )


@app.route("/movies", methods=["GET"])
def movies():
    query = request.args.get("q", "").strip()
    play_id = request.args.get("play_id")
    media_type = request.args.get("type", "movie")
    title = request.args.get("title", "Movie")

    if not query and not play_id:
        query = "Avatar"

    player_url = None
    results = None

    if play_id:
        if media_type == "tv":
            player_url = f"https://autoembed.co/tv/tmdb/{play_id}-1-1"
        else:
            player_url = f"https://autoembed.co/movie/tmdb/{play_id}"
    else:
        results = tmdb_search(query)

    return render_template_string(
        MOVIES_TEMPLATE,
        query=query if query != "Avatar" else "",
        results=results,
        player_url=player_url,
        selected_id=play_id,
        media_type=media_type,
        selected_title=title,
    )


@app.route("/youtube", methods=["GET"])
def youtube():
    query = request.args.get("q", "").strip()
    video_id = request.args.get("v")

    if not query and not video_id:
        query = "trending videos"

    if video_id:
        return render_template_string(
            YOUTUBE_TEMPLATE, query=query, video_id=video_id, yt_results=None
        )

    yt_id = extract_youtube_id(query)
    if yt_id:
        return render_template_string(
            YOUTUBE_TEMPLATE, query=query, video_id=yt_id, yt_results=None
        )

    results = search_youtube(query)
    return render_template_string(
        YOUTUBE_TEMPLATE, query=query, video_id=None, yt_results=results
    )


@app.route("/games", methods=["GET"])
def games():
    play_id = request.args.get("play")
    game_url = None
    game_title = None

    if play_id:
        target_game = next(
            (g for g in GAMES_DATABASE if g["id"] == play_id), GAMES_DATABASE[0]
        )
        game_url = target_game["url"]
        game_title = target_game["title"]

    return render_template_string(
        GAMES_TEMPLATE,
        games_list=GAMES_DATABASE,
        game_url=game_url,
        game_title=game_title,
    )


@app.route("/proxy", methods=["GET"])
def proxy():
    user_input = request.args.get("url", "").strip()

    if not user_input:
        return "Search query or URL is missing.", 400

    if user_input.lower() in ["anime", "dragon ball"]:
        return anime()

    if user_input.lower() in ["movies", "movie", "shows", "avatar"]:
        return movies()

    if user_input.lower() in ["games", "game", "poki"]:
        return games()

    if user_input.lower() in ["youtube", "youtube.com"]:
        return youtube()

    is_url = user_input.startswith(("http://", "https://")) or (
        "." in user_input and " " not in user_input
    )

    if is_url:
        if not user_input.startswith(("http://", "https://")):
            target_url = "https://" + user_input
        else:
            target_url = user_input
    else:
        encoded_query = urllib.parse.quote(user_input)
        target_url = f"https://yandex.com/search/?text={encoded_query}"

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
