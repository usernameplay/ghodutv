import requests
from flask import Flask, Response, request, render_template_string

app = Flask(__name__)

CREDS_URL = "http://jiologin.unaux.com/temp/-creds.json?i=1"

# Frontend Player HTML ഇവിടെ നേരിട്ട് നൽകുന്നു (Vercel-ൽ എളുപ്പത്തിൽ ലോഡ് ആകാൻ)
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Simple Live TV Player</title>
    <link rel="stylesheet" href="https://cdn.plyr.io/3.7.8/plyr.css" />
    <style>
        body { background-color: #111; color: #fff; font-family: sans-serif; text-align: center; margin: 0; padding: 20px; }
        .player-container { max-width: 800px; margin: 0 auto; }
        .controls { margin-top: 20px; }
        button { background: #e50914; color: white; border: none; padding: 10px 20px; margin: 5px; cursor: pointer; font-weight: bold; border-radius: 5px; }
        button:hover { background: #b81d24; }
    </style>
</head>
<body>
    <h1>Live TV Simple Player</h1>
    <div class="player-container">
        <video id="player" controls crossorigin playsinline></video>
    </div>
    <div class="controls">
        <h3>Channels</h3>
        <button onclick="playStream('/live/Asianet_HD.m3u8?id=144')">Asianet HD</button>
        <button onclick="playStream('/live/Surya_TV_HD.m3u8?id=150')">Surya TV HD</button>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
    <script src="https://cdn.plyr.io/3.7.8/plyr.polyfilled.js"></script>
    <script>
        const video = document.getElementById('player');
        function playStream(url) {
            if (Hls.isSupported()) {
                const hls = new Hls();
                hls.loadSource(url);
                hls.attachMedia(video);
                window.hls = hls;
            } else if (video.canPlayType('application/vnd.apple.mpegurl')) {
                video.src = url;
            }
            video.play();
        }
        document.addEventListener('DOMContentLoaded', () => { const player = new Plyr(video); });
    </script>
</body>
</html>
"""

def get_live_creds():
    try:
        response = requests.get(CREDS_URL, timeout=10)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        print(f"Error fetching credentials: {e}")
    return None

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/playlist.m3u')
def generate_playlist():
    creds = get_live_creds()
    if not creds:
        return "Failed to fetch credentials", 500
    
    host_url = request.host_url
    m3u_content = "#EXTM3U\n"
    
    m3u_content += '#EXTINF:-1 tvg-id="144" tvg-logo="https://jiotv.catchup.cdn.jio.com/dare_images/images/Asianet_HD.png" group-title="Malayalam",Asianet HD\n'
    m3u_content += f"{host_url}live/Asianet_HD.m3u8?id=144\n"
    
    m3u_content += '#EXTINF:-1 tvg-id="150" tvg-logo="https://jiotv.catchup.cdn.jio.com/dare_images/images/Surya_TV_HD.png" group-title="Malayalam",Surya TV HD\n'
    m3u_content += f"{host_url}live/Surya_TV_HD.m3u8?id=150\n"
    
    return Response(m3u_content, mimetype='application/vnd.apple.mpegurl')

@app.route('/live/<channel_name>.m3u8')
def live_stream(channel_name):
    creds = get_live_creds()
    if not creds:
        return "Auth failed", 401
    
    auth_token = creds.get("authToken")
    j_token = creds.get("jToken")
    
    headers = {
        "User-Agent": "plaYtv/7.1.3 (Linux;Android 14) ExoPlayerLib/2.11.7",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "jToken": j_token,
        "authToken": auth_token
    }
    
    target_url = f"https://jiotvmblive.cdn.jio.com/bpk-tv/{channel_name}/Fallback/{channel_name}.m3u8"
    
    try:
        res = requests.get(target_url, headers=headers, timeout=10)
        return Response(res.content, mimetype='application/vnd.apple.mpegurl')
    except Exception as e:
        return str(e), 500
                                
