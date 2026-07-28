import os
import re
import urllib.parse
import requests
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

# List of Unblocked HTML5 Games (Poki style)
GAMES_DATABASE = [
    {
        "id": "subway-surfers",
        "title": "Subway Surfers",
        "category": "Runner",
        "poster": "https://img.gamedistribution.com/rvvAS300-512x512.jpeg",
        "url": "https://html5.gamedistribution.com/rvvAS300/",
    },
    {
        "id": "moto-x3m",
        "title": "Moto X3M",
        "category": "Racing",
        "poster": "https://img.gamedistribution.com/b2823a233b2848c8a141b714f3c7b64b-512x512.jpeg",
        "url": "https://html5.gamedistribution.com/b2823a233b2848c8a141b714f3c7b64b/",
    },
    {
        "id": "drive-mad",
        "title": "Drive Mad",
        "category": "Driving",
        "poster": "https://img.gamedistribution.com/6c42ddf5187d4681958b4f62fae80718-512x512.jpeg",
        "url": "https://html5.gamedistribution.com/6c42ddf5187d4681958b4f62fae80718/",
    },
    {
        "id": "basketball-stars",
        "title": "Basketball Stars",
        "category": "Sports",
        "poster": "https://img.gamedistribution.com/3931665a3964405ea7e31b4097e3a34a-512x512.jpeg",
        "url": "https://html5.gamedistribution.com/3931665a3964405ea7e31b4097e3a34a/",
    },
    {
        "id": "stickman-hook",
        "title": "Stickman Hook",
        "category": "Action",
        "poster": "https://img.gamedistribution.com/9be12a023bbf4e3fbcfceefdfd0b6754-512x512.jpeg",
        "url": "https://html5.gamedistribution.com/9be12a023bbf4e3fbcfceefdfd0b6754/",
    },
    {
        "id": "temple-run-2",
        "title": "Temple Run 2",
        "category": "Runner",
        "poster": "https://img.gamedistribution.com/a42b109b83b3420fae37c4493e820713-512x512.jpeg",
        "url": "https://html5.gamedistribution.com/a42b109b83b3420fae37c4493e820713/",
    },
    {
        "id": "geometry-dash",
        "title": "Geometry Dash",
        "category": "Arcade",
        "poster": "https://img.gamedistribution.com/a1d520be712248ceb9c6f5d84dd6146c-512x512.jpeg",
        "url": "https://html5.gamedistribution.com/a1d520be712248ceb9c6f5d84dd6146c/",
    },
    {
        "id": "tunnel-rush",
        "title": "Tunnel Rush",
        "category": "Skill",
        "poster": "https://img.gamedistribution.com/a5e8c1f938d24d27a421b8bbfbf0f772-512x512.jpeg",
        "url": "https://html5.gamedistribution.com/a5e8c1f938d24d27a421b8bbfbf0f772/",
    },
]

# Main HTML Page Template with Background Image Slideshow Engine & Glassmorphism UI
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
