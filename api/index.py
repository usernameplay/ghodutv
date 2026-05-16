import os
import json
import base64
import requests
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

DATA_FILE = "/tmp/creds.json"
CREDS_URL = "http://jiologin.unaux.com/temp/-creds.json?i=1"

DEFAULT_CREDS = {
    "authToken": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImF1dGhUb2tlbklkIjoiODIzOWRjZDUtNmVmYS00MTIzLThmNDgtYjllNjc3MTI3ZGYyIiwidXNlcklkIjoiNzY5MzhkYTItYmRkZi00NGE4LWFlMmUtZDY1YzQ1OGIzYmJhIiwidXNlclR5cGUiOiJKSU8iLCJvcyI6ImFuZHJvaWQiLCJkZXZpY2VUeXBlIjoicGhvbmUiLCJhY2Nlc3NMZXZlbCI6IjkiLCJkZXZpY2VJZCI6IjZmY2FkZWI3YjRiMTBkNzciLCJleHRyYSI6IntcIm51bWJlclwiOlwiVEtiTjZ4QjQ4cUhxajcxOHpZZ3J4VGNuNHhWRVJ1NmZQNVE2aGVJVm9WVGRmOGFVcitScmdoTT1cIixcInBsYW5kZXRhaWxzXCI6e1wiUGFja2FnZUluZm9cIjpbe1wicGxhbmlkXCI6XCIxXCIsXCJzdWJzY3JpcHRpb25zdGFydFwiOjE2ODY0ODUyNjMsXCJzdWJzY3JpcHRpb25lbmRcIjoxODEwMDU3MDE4LFwicGxhbnR5cGVcIjpcIlwiLFwiYnVzaW5lc3NUeXBlXCI6XCJqaW9cIixcIm5vdGVzXCI6XCJcIn1dfSxcImpUb2tlblwiOlwiOGU2ZWJjNmEzOTdmMWE4MzdiMmZhOTBhZTE3NGFkMWUuY2Q4MTZlZGFhYjYwMmEyMWI2YjlhYTBmNzllYTk5MWVkMjA4ZjY0NmYwYThmNGZhT2ZhN2M2ODRlMjZiODkwNjJkZDg1NzI0YjZjY2IzNjczMzdkY2RhY2EyYWYwMjIwZjJjZjNjtext...",
    "refreshToken": "4d669ff3-f2f6-4b9f-ae58-c3d29273b6a1",
    "ssoToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkRm9yIjoiSmlvVFYiLCJkZXZpY2VJeCI6IjZmY2FkZWI3YjRiMTBkNzciLCJpYXQiOjE3Nzg1MjEwMTgsInNJZCI6IlUyRnNkR1ZrWDEvQ0g5QXlWRC8yVW5zK0c3dmlYMCtYRld0RDJkb3ljeVU9IiwidW5pcXVlIjoiNzY5MzhkYTItYmRkZi00NGE4LWFlMmUtZDY1YzQ1OGIzYmJhIiwidXNlclR5cGUiOiJKSU8ifQ.t3ZuMrk5sQRvL7Oxv3i0yVc5OybGMSJ7sCUzD87n0TQ"
}

def get_stored_creds():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
            
    try:
        res = requests.get(CREDS_URL, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
        
    return DEFAULT_CREDS

# --- JIO CHANNELS FETCHER WITH BYPASS HEADERS ---
def fetch_jio_channels():
    url = "https://jiotvapi.media.jio.com/userservice/apis/v1/channels"
    
    headers = {
        "User-Agent": "plaYtv/7.1.3 (Linux;Android 14) ExoPlayerLib/2.11.7",
        "os": "android",
        "devicetype": "phone",
        "accept": "application/json",
        "accept-encoding": "gzip",
        "appkey": "NzNiMDhlYzQyNjJm",
        "connection": "Keep-Alive",
        "X-Forwarded-For": "49.36.0.1",
        "Accept-Language": "en-IN,en;q=0.9,ml-IN;q=0.8"
    }
    
    try:
        res = requests.get(url, headers=headers, timeout=12)
        if res.status_code == 200:
            data = res.json()
            channel_list = data.get("result", [])
            if len(channel_list) > 0:
                return channel_list
    except Exception as e:
        print(f"Primary fetch error: {e}")
        
    # Backup Route if primary down or blocked
    try:
        backup_url = "https://jiotvapi.cdn.jio.com/jiotvapi/v1/channels"
        res = requests.get(backup_url, headers=headers, timeout=10)
        if res.status_code == 200:
            return res.json().get("result", [])
    except:
        pass
        
    return []

# --- ROUTES ---

@app.route('/playlist.m3u')
def generate_playlist():
    creds = get_stored_creds()
    if not creds:
        return "#EXTM3U\n#EXTINF:-1, Login Required\nhttp://error.mp4", 200
    
    protocol = request.headers.get('X-Forwarded-Proto', 'https')
    host_url = f"{protocol}://{request.host}/"
    
    m3u_content = "#EXTM3U x-tvg-url=\"https://avapi.live/epg/jiotv.xml.gz\"\n"
    
    channels = fetch_jio_channels()
    
    if channels:
        for ch in channels:
            ch_id = ch.get("channel_id")
            if not ch_id:
                continue
                
            # Clean channel name for URLs
            ch_name = ch.get("channel_name", "").replace(" ", "_").replace("&", "and").replace("'", "").replace('"', '')
            display_name = ch.get("channel_name", f"Channel {ch_id}")
            
            group = ch.get("channelCategoryName", "Entertainment")
            lang = ch.get("channelLanguageName", "Languages")
            
            if "HD" in display_name.upper():
                group = f"{group} HD"
                
            logo_id = ch.get('logoUrl', '')
            logo = f"https://jiotv.catchup.cdn.jio.com/dare_images/images/{logo_id}" if logo_id else ""
            
            # Formatted group-title syntax for IPTV Apps (Tivimate / OTT Navigator)
            m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}" tvg-logo="{logo}" group-title="{lang};{group}" tvg-language="{lang}",{display_name}\n'
            m3u_content += f"{host_url}live/{ch_name}.m3u8?id={ch_id}\n"
    else:
        # Fallback channel when empty
        m3u_content += '#EXTINF:-1 tvg-id="144" tvg-logo="https://jiotv.catchup.cdn.jio.com/dare_images/images/Asianet_HD.png" group-title="Malayalam",Asianet HD\n'
        m3u_content += f"{host_url}live/Asianet_HD.m3u8?id=144\n"
            
    return Response(m3u_content, mimetype='application/x-mpegurl')

@app.route('/live/<channel_name>.m3u8')
def live_stream(channel_name):
    ch_id = request.args.get('id')
    if not ch_id:
        return "Channel ID missing", 400
        
    creds = get_stored_creds()
    if not creds:
        return "Auth failed", 401
    
    auth_token = creds.get("authToken")
    j_token = creds.get("jToken") or creds.get("sessionAttributes", {}).get("jToken", "")
    subscriber_id = creds.get("sessionAttributes", {}).get("user", {}).get("subscriberId", "")

    # Crucial headers targeting Indian Jio Net IPs to bypass 451
    headers = {
        "User-Agent": "plaYtv/7.1.3 (Linux;Android 14) ExoPlayerLib/2.11.7",
        "jToken": j_token if j_token else creds.get("jToken"),
        "authToken": auth_token,
        "os": "android",
        "devicetype": "phone",
        "appkey": "NzNiMDhlYzQyNjJm",
        "crmid": subscriber_id,
        "userid": subscriber_id,
        "X-Forwarded-For": "49.36.0.1",
        "Accept-Language": "en-IN,en;q=0.9,ml-IN;q=0.8"
    }
    
    target_url = f"https://jiotvmblive.cdn.jio.com/bpk-tv/{channel_name}/Fallback/{channel_name}.m3u8"
    
    try:
        res = requests.get(target_url, headers=headers, timeout=12)
        if res.status_code == 200:
            return Response(res.content, mimetype='application/vnd.apple.mpegurl')
        elif res.status_code == 451:
            # Fallback Route 2 if 451 triggers on Primary CDN
            alt_url = f"https://jiotvapi.cdn.jio.com/bpk-tv/{channel_name}/Fallback/{channel_name}.m3u8"
            alt_res = requests.get(alt_url, headers=headers, timeout=10)
            if alt_res.status_code == 200:
                return Response(alt_res.content, mimetype='application/vnd.apple.mpegurl')
                
            return "Jio Region Blocked (451). Indian Proxy/VPN required on your cloud server.", 451
        else:
            return f"Jio Server returned error status {res.status_code}", res.status_code
    except Exception as e:
        return str(e), 500

@app.route('/api/channels-list', methods=['GET'])
def get_channels_json_route():
    channels = fetch_jio_channels()
    return jsonify({"status": "success", "count": len(channels), "channels": channels})
