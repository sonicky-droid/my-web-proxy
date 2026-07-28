import os
import re
import urllib.parse
import requests
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

# List of 100% Working Unblocked HTML5 Games
GAMES_DATABASE = [
    {
        "id": "subway-surfers",
        "title": "Subway Surfers",
        "category": "Runner",
        "poster": "https://img.gamepix.com/games/subway-surfers/cover/subway-surfers.png?width=300",
        "url": "https://play.gamepix.com/subway-surfers/embed",
    },
    {
        "id": "moto-x3m",
        "title": "Moto X3M",
        "category": "Racing",
        "poster": "https://img.gamepix.com/games/moto-x3m/cover/moto-x3m.png?width=300",
        "url": "https://play.gamepix.com/moto-x3m/embed",
    },
    {
        "id": "drive-mad",
        "title": "Drive Mad",
        "category": "Driving",
        "poster": "https://img.gamepix.com/games/drive-mad/cover/drive-mad.png?width=300",
        "url": "https://play.gamepix.com/drive-mad/embed",
    },
    {
        "id": "basketball-legends",
        "title": "Basketball Legends",
        "category": "Sports",
        "poster": "https://img.gamepix.com/games/basketball-legends-2020/cover/basketball-legends-2020.png?width=300",
        "url": "https://play.gamepix.com/basketball-legends-2020/embed",
    },
    {
        "id": "stickman-hook",
        "title": "Stickman Hook",
        "category": "Action",
        "poster": "https://img.gamepix.com/games/stickman-hook/cover/stickman-hook.png?width=300",
        "url": "https://play.gamepix.com/stickman-hook/embed",
    },
    {
        "id": "tomb-runner",
        "title": "Temple / Tomb Runner",
        "category": "Runner",
        "poster": "https://img.gamepix.com/games/tomb-runner/cover/tomb-runner.png?width=300",
        "url": "https://play.gamepix.com/tomb-runner/embed",
    },
    {
        "id": "geometry-jump",
        "title": "Geometry Dash",
        "category": "Arcade",
        "poster": "https://img.gamepix.com/games/geometry-jump/cover/geometry-jump.png?width=300",
        "url": "https://play.gamepix.com/geometry-jump/embed",
    },
    {
        "id": "tunnel-rush",
        "title": "Tunnel Rush",
        "category": "Skill",
        "poster": "https://img.gamepix.com/games/tunnel-rush/cover/tunnel-rush.png?width=300",
        "url": "https://play.gamepix.com/tunnel-rush/embed",
    },
]

# Main HTML Page Template
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Web, YouTube, Movies & Games Arcade</title>
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

        button, .server-btn {
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

        button:hover, .server-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(255, 0, 85, 0.5);
        }

        .server-btn { background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); }
        .server-btn:hover { background: #ff0055; }

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
            margin-top: 15px;
            box-shadow: 0 10px 30px rgba(255, 0, 85, 0.3);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }

        iframe { width: 100%; height: 100%; border: none; }

        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
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
            aspect-ratio: 1 / 1;
            object-fit: cover;
            background: #000;
        }

        .card-body { padding: 12px; }
        .card-title { font-size: 14px; font-weight: 600; line-height: 1.3; }
        .card-sub { font-size: 12px; color: #ff0055; margin-top: 4px; font-weight: bold; }
    </style>
</head>
<body>
    <div id="bg-slideshow"></div>

    <div class="container">
        <h1>Web, Games, YouTube & Anime</h1>
        <p>Browse websites, stream anime/movies, or play <b>Unblocked HTML5 Games</b>!</p>
        
        <form class="input-group" action="/proxy" method="GET">
            <input type="text" name="url" placeholder="Search Games, Anime/Movies, YouTube, or type a website address..." value="{{ last_query }}" required />
            <button type="submit" style="padding: 16px 28px; font-size:16px;">Search / Play</button>
        </form>

        <div class="nav-links">
            <a href="/proxy?url=anime">⛩️ Anime & Movies</a> | 
            <a href="/proxy?url=games">🎮 Unblocked Games</a> | 
            <a href="/proxy?url=youtube.com">▶️ YouTube</a> | 
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

        {% if game_url %}
        <h3 style="color:#ff0055; margin-top:20px;">Playing Game (Full Screen)</h3>
        <div class="player-container" style="aspect-ratio: 16/10;">
            <iframe 
                src="{{ game_url }}" 
                referrerpolicy="no-referrer"
                allow="autoplay; gamepad; fullscreen; keyboard; focus-without-user-activation" 
                sandbox="allow-scripts allow-same-origin allow-forms allow-popups"
                allowfullscreen>
            </iframe>
        </div>
        {% endif %}

        {% if stream_url %}
        <h3 style="color:#ff0055; margin-top:20px;">Ad-Free Stream Player</h3>
        <p style="font-size:13px; color:#aaa; margin-bottom:10px;">If stream fails, click a backup server below:</p>
        
        <div style="display:flex; gap:8px; justify-content:center; flex-wrap:wrap; margin-bottom:15px;">
            <button class="server-btn" onclick="switchServer('https://vidsrc.pro/embed/anime/{{ anime_id }}')">Server 1 (VidSrc Pro)</button>
            <button class="server-btn" onclick="switchServer('https://autoembed.cc/embed/anime/{{ anime_id }}')">Server 2 (AutoEmbed)</button>
            <button class="server-btn" onclick="switchServer('https://2embed.cc/embed/anime/{{ anime_id }}')">Server 3 (2Embed)</button>
            <button class="server-btn" onclick="switchServer('https://vidsrc.in/embed/anime/{{ anime_id }}')">Server 4 (VidSrc In)</button>
        </div>

        <div class="player-container">
            <iframe 
                id="streamPlayer"
                src="{{ stream_url }}" 
                referrerpolicy="no-referrer"
                allow="autoplay; encrypted-media; fullscreen" 
                allowfullscreen>
            </iframe>
        </div>

        <script>
            function switchServer(newUrl) {
                document.getElementById('streamPlayer').src = newUrl;
            }
        </script>
        {% endif %}

        {% if games_list %}
        <h2 style="text-align:left; color:#ff0055; margin-top:30px; font-size:20px;">🎮 Unblocked HTML5 Games</h2>
        <div class="grid">
            {% for game in games_list %}
            <a class="card" href="/play-game?id={{ game.id }}">
                <img src="{{ game.poster }}" alt="game" loading="lazy" />
                <div class="card-body">
                    <div class="card-title">{{ game.title }}</div>
                    <div class="card-sub">{{ game.category }}</div>
                </div>
            </a>
            {% endfor %}
        </div>
        {% endif %}

        {% if anime_results %}
        <h2 style="text-align:left; color:#ff0055; margin-top:30px; font-size:20px;">Anime & Movie Results</h2>
        <div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));">
            {% for show in anime_results %}
            <a class="card" href="/watch-anime?id={{ show.id }}&title={{ show.title | urlencode }}">
                <img src="{{ show.poster }}" alt="poster" loading="lazy" style="aspect-ratio: 2/3;" />
                <div class="card-body">
                    <div class="card-title">{{ show.title }}</div>
                    <div class="card-sub">{{ show.episodes }} Ep</div>
                </div>
            </a>
            {% endfor %}
        </div>
        {% endif %}

        {% if yt_results %}
        <h2 style="text-align:left; color:#ff0055; margin-top:30px; font-size:20px;">YouTube Videos</h2>
        <div class="grid" style="grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));">
            {% for vid in yt_results %}
            <a class="card" href="/proxy?url=https://www.youtube.com/watch?v={{ vid.id }}">
                <img src="https://i.ytimg.com/vi/{{ vid.id }}/hqdefault.jpg" alt="thumbnail" loading="lazy" style="aspect-ratio: 16/9;" />
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


def search_anilist(query):
    try:
        url = "https://graphql.anilist.co"
        graphql_query = """
        query ($search: String) {
          Page(perPage: 12) {
            media(search: $search, type: ANIME) {
              id
              title { english romaji }
              coverImage { extraLarge }
              episodes
            }
          }
        }
        """
        response = requests.post(
            url,
            json={"query": graphql_query, "variables": {"search": query}},
            timeout=8,
        )
        data = response.json()
        results = []
        media_list = data.get("data", {}).get("Page", {}).get("media", [])
        for item in media_list:
            title = (
                item.get("title", {}).get("english")
                or item.get("title", {}).get("romaji")
                or "Unknown Title"
            )
            poster = item.get("coverImage", {}).get("extraLarge")
            episodes = item.get("episodes") or 1
            if poster:
                results.append(
                    {
                        "id": item["id"],
                        "title": title,
                        "poster": poster,
                        "episodes": episodes,
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
    return render_template_string(
        HTML_TEMPLATE,
        video_id=None,
        stream_url=None,
        anime_id=None,
        game_url=None,
        yt_results=None,
        anime_results=None,
        games_list=GAMES_DATABASE,
        last_query="",
    )


@app.route("/play-game")
def play_game():
    game_id = request.args.get("id")
    target_game = next(
        (g for g in GAMES_DATABASE if g["id"] == game_id), GAMES_DATABASE[0]
    )

    return render_template_string(
        HTML_TEMPLATE,
        video_id=None,
        stream_url=None,
        anime_id=None,
        game_url=target_game["url"],
        yt_results=None,
        anime_results=None,
        games_list=GAMES_DATABASE,
        last_query=target_game["title"],
    )


@app.route("/watch-anime")
def watch_anime():
    anime_id = request.args.get("id")
    anime_title = request.args.get("title", "anime")

    # Fast default server: VidSrc Pro
    stream_url = f"https://vidsrc.pro/embed/anime/{anime_id}"

    return render_template_string(
        HTML_TEMPLATE,
        video_id=None,
        stream_url=stream_url,
        anime_id=anime_id,
        game_url=None,
        yt_results=None,
        anime_results=None,
        games_list=None,
        last_query=anime_title,
    )


@app.route("/proxy", methods=["GET"])
def proxy():
    user_input = request.args.get("url", "").strip()

    if not user_input:
        return "Search query or URL is missing.", 400

    # 1. Unblocked Games Arcade Tab
    if user_input.lower() in ["games", "game", "poki", "arcade", "unblocked games"]:
        return render_template_string(
            HTML_TEMPLATE,
            video_id=None,
            stream_url=None,
            anime_id=None,
            game_url=None,
            yt_results=None,
            anime_results=None,
            games_list=GAMES_DATABASE,
            last_query="games",
        )

    # 2. Anime & Movies Tab
    if user_input.lower() in ["anime", "movies", "shows", "dragon ball"]:
        results = search_anilist(user_input if user_input != "anime" else "Dragon Ball")
        return render_template_string(
            HTML_TEMPLATE,
            video_id=None,
            stream_url=None,
            anime_id=None,
            game_url=None,
            yt_results=None,
            anime_results=results,
            games_list=None,
            last_query=user_input,
        )

    # 3. YouTube Portal
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
            stream_url=None,
            anime_id=None,
            game_url=None,
            yt_results=results,
            anime_results=None,
            games_list=None,
            last_query="youtube.com",
        )

    # 4. Direct YouTube Video Links
    yt_id = extract_youtube_id(user_input)
    if yt_id:
        return render_template_string(
            HTML_TEMPLATE,
            video_id=yt_id,
            stream_url=None,
            anime_id=None,
            game_url=None,
            yt_results=None,
            anime_results=None,
            games_list=None,
            last_query=user_input,
        )

    # 5. Search AniList for Anime & Movies
    anime_hits = search_anilist(user_input)

    is_url = user_input.startswith(("http://", "https://")) or (
        "." in user_input and " " not in user_input
    )

    if not is_url and anime_hits:
        return render_template_string(
            HTML_TEMPLATE,
            video_id=None,
            stream_url=None,
            anime_id=None,
            game_url=None,
            yt_results=None,
            anime_results=anime_hits,
            games_list=None,
            last_query=user_input,
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
                stream_url=None,
                anime_id=None,
                game_url=None,
                yt_results=results,
                anime_results=None,
                games_list=None,
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
