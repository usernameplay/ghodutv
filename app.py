import requests
from flask import Flask, Response, request, render_template_string

app = Flask(__name__)

# നിങ്ങളുടെ ക്രെഡൻഷ്യൽ ലിങ്ക്
CREDS_URL = "http://jiologin.unaux.com/temp/-creds.json?i=1"

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
    # സിമ്പിൾ പ്ലേയർ പേജ് ലോഡ് ചെയ്യാൻ
    with open("index.html", "r", encoding="utf-8") as f:
        return render_template_string(f.read())

@app.route('/playlist.m3u')
def generate_playlist():
    creds = get_live_creds()
    if not creds:
        return "Failed to fetch credentials", 500
    
    host_url = request.host_url
    
    # വളരെ ലളിതമായ ഒരു M3U പ്ലേലിസ്റ്റ് ഘടന (ഉദാഹരണത്തിന് 1-2 ചാനലുകൾ)
    m3u_content = "#EXTM3U\n"
    
    # ചാനൽ 1
    m3u_content += '#EXTINF:-1 tvg-id="144" tvg-logo="https://jiotv.catchup.cdn.jio.com/dare_images/images/Asianet_HD.png" group-title="Malayalam",Asianet HD\n'
    m3u_content += f"{host_url}live/Asianet_HD.m3u8?id=144\n"
    
    # ചാനൽ 2
    m3u_content += '#EXTINF:-1 tvg-id="150" tvg-logo="https://jiotv.catchup.cdn.jio.com/dare_images/images/Surya_TV_HD.png" group-title="Malayalam",Surya TV HD\n'
    m3u_content += f"{host_url}live/Surya_TV_HD.m3u8?id=150\n"
    
    return Response(m3u_content, mimetype='application/vnd.apple.mpegurl')

@app.route('/live/<channel_name>.m3u8')
def live_stream(channel_name):
    channel_id = request.args.get('id')
    creds = get_live_creds()
    if not creds:
        return "Auth failed", 401
    
    # JSON-ൽ നിന്നുള്ള ടോക്കണുകൾ വേർതിരിച്ചെടുക്കുന്നു
    auth_token = creds.get("authToken")
    j_token = creds.get("jToken")
    
    # ജിയോ സർവറിലേക്ക് അയക്കേണ്ട ഹെഡ്ഡറുകൾ
    headers = {
        "User-Agent": "plaYtv/7.1.3 (Linux;Android 14) ExoPlayerLib/2.11.7",
        "Connection": "keep-alive",
        "Accept-Encoding": "gzip",
        "jToken": j_token,
        "authToken": auth_token
    }
    
    # ലൈവ് സ്ട്രീം ലിങ്ക് റീഡയറക്ട് ചെയ്യുകയോ പ്രോക്സി ചെയ്യുകയോ ചെയ്യാം
    target_url = f"https://jiotvmblive.cdn.jio.com/bpk-tv/{channel_name}/Fallback/{channel_name}.m3u8"
    
    try:
        res = requests.get(target_url, headers=headers, timeout=10)
        return Response(res.content, mimetype='application/vnd.apple.mpegurl')
    except Exception as e:
        return str(e), 500

if __name__ == '__main__':
    # സർവർ റൺ ചെയ്യുക
    app.run(host='0.0.0.0', port=5000, debug=True)
