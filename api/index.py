import os
import json
import base64
import requests
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

DATA_FILE = "/tmp/creds.json"
CREDS_URL = "http://jiologin.unaux.com/temp/-creds.json?i=1"

DEFAULT_CREDS = {
    "authToken": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImF1dGhUb2tlbklkIjoiODIzOWRjZDUtNmVmYS00MTIzLThmNDgtYjllNjc3MTI3ZGYyIiwidXNlcklkIjoiNzY5MzhkYTItYmRkZi00NGE4LWFlMmUtZDY1YzQ1OGIzYmJhIiwidXNlclR5cGUiOiJKSU8iLCJvcyI6ImFuZHJvaWQiLCJkZXZpY2VUeXBlIjoicGhvbmUiLCJhY2Nlc3NMZXZlbCI6IjkiLCJkZXZpY2VJZCI6IjZmY2FkZWI3YjRiMTBkNzciLCJleHRyYSI6IntcIm51bWJlclwiOlwiVEtiTjZ4QjQ4cUhxajcxOHpZZ3J4VGNuNHhWRVJ1NmZQNVE2aGVJVm9WVGRmOGFVcitScmdoTT1cIixcInBsYW5kZXRhaWxzXCI6e1wiUGFja2FnZUluZm9cIjpbe1wicGxhbmlkXCI6XCIxXCIsXCJzdWJzY3JpcHRpb25zdGFydFwiOjE2ODY0ODUyNjMsXCJzdWJzY3JpcHRpb25lbmRcIjoxODEwMDU3MDE4LFwicGxhbnR5cGVcIjpcIlwiLFwiYnVzaW5lc3NUeXBlXCI6XCJqaW9cIixcIm5vdGVzXCI6XCJcIn1dfSxcImpUb2tlblwiOlwiOGU2ZWJjNmEzOTdmMWE4MzdiMmZhOTBhZTE3NGFkMWUuY2Q4MTZlZGFhYjYwMmEyMWI2YjlhYTBmNzllYTk5MWVkMjA4ZjY0NmYwYThmNGZhT2ZhN2M2ODRlMjZiODkwNjJkZDg1NzI0YjZjY2IzNjczMzdkY2RhY2EyYWYwMjIwZjJjZjNjN2IxZTFlYzFjODZlZDJmZjYyNGE3ZjhhZDk9OThAwM2Q3NTkyZjA2NjY0YWU5YWVmMjNmOWNlMjAzMTNhNzRmZTc0MmM0Y2Q2OWMyNjJhZGRkNzAyMGMzMjU0YTI5NDMxZGRiYzRkNzQwNDQyOTExNWUyYjA1NWIzNGZiZWU2MmQ4MTBkNTdkMDg4ZGY5OTY1ZWRmZDUwMmVmZjI1YmNjNDhkMzRjNTMxNGIxMTdjNjE2MmQ5NGUyMzRlMGM4ZGUyZmY0NjFjT2ExZGMwMjM5YjEyNzQ4ODE3ODZjNWExNWNmMmYwMWEyT2I3NjdkMGZhNzhmNWYyOGRhZTMwNTVjODgxMDBlZWFhZDJjMzI3YzQ2NDZjYzA5ZTNkYmRjZDZjZGI5YjFjYTBkNmIyNjBlODNkNDg0NDY5ZTdjZTc2OWM4NTVmYzE5ODgzMWJjMTJhYmIxMzUyOTcyNWI3NTM4YWVlMjAzODg0MmRmZWJkZTgzNDUyOGY5MDg4MjExNGU2MDdhNjkzY2ZjYjlhMWJlYzYyMWI3NmNkZGY3MWJiZmM4MDY0OWQ1NjZiZWRkNzhkY2FhNmQ2NjYzYjJlZTk2ZTAwYjQ4ODA4Njc4Yjc1ODU0Yjc4ZTIwZDYxMzMyNmZlNDcwMTljNjJkNzFmNjc3NjRkZTc2ZTBkMjEyMGNiOGNjZGE3OWQ4MzdhOGNjMThmNjI2NDM5MmY5YzA3YjE5ZWViYzM0MTA5YTc2ZDEyMTU4ZmUyZjAzZWMzMGU2Njk1NmQ4ZTAyMGI2ZGRiYjQyNGQzYWZlM2I3MGZjYmNcIixcInVzZXJEZXRhaWxzXCI6XCI1M2JkV2lhTlFiOWl5dkR0eW5WNStsZ1F1V05DdTZKMWR1N1g3Tnl2T2ozQk9USVZERDR0OGRGVEpleWI2VUNzVWs1NDN3TzVBUmZRMmhxTGxzY1djZE9BMExFZzl2NmtPYVo4Zm1wTGkzRkF1TURLOWR6elVVd1NwMUlUZ2FhUWRiWHVGWCtacURIRHd4SXlhbk12TnVReGZzL2tReEV2ckduMndqaURiWVBxUFRmTFQ2MnltN0QxSDl5a25ZZmFCcDh6SU15Z1ltM3BhZzZOcDM5dWlYYzdVQXkxbWNRdU94dWYrVjBDMmsrNDZzSis2WFlXVXF4YUlPZkx5OHNoUFBpbUliUlRDaG9DUFNhZTQwM1QzZXp1RUgxbXNGaWJpL09qXCJ9Iiwic3Vic2NyaWJlcklkIjoiMTI2MTgxMzMwOCIsImFwcE5hbWUiOiJSSklMX0ppb1RWIiwidmVyc2lvbiI6InYxLjEiLCJwbGF0Zm9ybSI6IiJ9LCJleHAiOjE3NzkzODUwMTgsImlhdCI6MTc3ODUxMTAxOH0.1SL3vj_TqCuoVxqzd7msHlYxjun-P6mAqfew83_7e1E7LOt3xvEk5uUcUb5SB-Ma6rk4wKGgYAO886BDK8wh-Q",
    "refreshToken": "4d669ff3-f2f6-4b9f-ae58-c3d29273b6a1",
    "ssoToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkRm9yIjoiSmlvVFYiLCJkZXZpY2VJZCI6IjZmY2FkZWI3YjRiMTBkNzciLCJpYXQiOjE3Nzg1MjEwMTgsInNJZCI6IlUyRnNkR1ZrWDEvQ0g5QXlWRC8yVW5zK0c3dmlYMCtYRld0RDJkb3ljeVU9IiwidW5pcXVlIjoiNzY5MzhkYTItYmRkZi00NGE4LWFlMmUtZDY1YzQ1OGIzYmJhIiwidXNlclR5cGUiOiJKSU8ifQ.t3ZuMrk5sQRvL7Oxv3i0yVc5OybGMSJ7sCUzD87n0TQ"
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

# --- JIO ALL CHANNELS FETCH API ---
def fetch_jio_channels():
    # Poornamaayum ellam channelsum edukkunna official API endpoint
    url = "https://jiotvapi.media.jio.com/userservice/apis/v1/channels"
    headers = {
        "User-Agent": "plaYtv/7.1.3 (Linux;Android 14) ExoPlayerLib/2.11.7",
        "os": "android",
        "devicetype": "phone",
        "accept-encoding": "gzip",
        "appkey": "NzNiMDhlYzQyNjJm" # Jio official App Key
    }
    try:
        # Ivide ninnu langId cut cheythu, appol ellam languagesum (Hindi, English, Tamil, Sports...) labhikkyum
        res = requests.get(url, headers=headers, timeout=15)
        if res.status_code == 200:
            data = res.json()
            return data.get("result", [])
    except Exception as e:
        print(f"Error fetching ALL channel list: {e}")
    return []

# --- ROUTES ---

@app.route('/playlist.m3u')
def generate_playlist():
    creds = get_stored_creds()
    if not creds:
        return "#EXTM3U\n#EXTINF:-1, Login Required\nhttp://error.mp4", 200
    
    protocol = request.headers.get('X-Forwarded-Proto', 'https')
    host_url = f"{protocol}://{request.host}/"
    
    # Unified EPG and standard headers
    m3u_content = "#EXTM3U x-tvg-url=\"https://avapi.live/epg/jiotv.xml.gz\"\n"
    
    channels = fetch_jio_channels()
    
    if channels:
        for ch in channels:
            ch_id = ch.get("channel_id")
            # Spaces sanitize cheyyunnu live stream links potti pokathirikkaan
            ch_name = ch.get("channel_name", "").replace(" ", "_").replace("&", "and")
            display_name = ch.get("channel_name")
            
            # Category and Language mapping for smart grouping inside apps like Tivimate or OTT Navigator
            group = ch.get("channelCategoryName", "General")
            lang = ch.get("channelLanguageName", "Unknown")
            
            logo = f"https://jiotv.catchup.cdn.jio.com/dare_images/images/{ch.get('logoUrl', '')}"
            
            # group-title aayi Category use cheyyunnu (eg: Sports, Movies, News)
            m3u_content += f'#EXTINF:-1 tvg-id="{ch_id}" tvg-logo="{logo}" group-title="{group}" tvg-language="{lang}",{display_name}\n'
            m3u_content += f"{host_url}live/{ch_name}.m3u8?id={ch_id}\n"
    else:
        # Enthinum vendi ulla basic fallback response
        m3u_content += '#EXTINF:-1 tvg-id="144" tvg-logo="https://jiotv.catchup.cdn.jio.com/dare_images/images/Asianet_HD.png" group-title="Fallback",Asianet HD\n'
        m3u_content += f"{host_url}live/Asianet_HD.m3u8?id=144\n"
            
    return Response(m3u_content, mimetype='application/x-mpegurl')

@app.route('/live/<channel_name>.m3u8')
def live_stream(channel_name):
    ch_id = request.args.get('id')
    if not ch_id:
        return "Channel ID missing", 400
        
    creds = get_stored_creds()
    if not creds:
        return "Auth failed - Login required", 401
    
    auth_token = creds.get("authToken")
    j_token = creds.get("jToken") or creds.get("sessionAttributes", {}).get("jToken", "")
    
    if not j_token and "extra" in auth_token:
         try:
             payload = auth_token.split('.')[1]
             decoded = json.loads(base64.b64decode(payload + "==").decode("utf-8"))
             extra_str = decoded.get("data", {}).get("extra", "{}")
             extra_data = json.loads(extra_str)
             j_token = extra_data.get("jToken", "")
         except:
             pass

    headers = {
        "User-Agent": "plaYtv/7.1.3 (Linux;Android 14) ExoPlayerLib/2.11.7",
        "jToken": j_token if j_token else creds.get("jToken"),
        "authToken": auth_token
    }
    
    target_url = f"https://jiotvmblive.cdn.jio.com/bpk-tv/{channel_name}/Fallback/{channel_name}.m3u8"
    
    try:
        res = requests.get(target_url, headers=headers, timeout=10)
        return Response(res.content, mimetype='application/vnd.apple.mpegurl')
    except Exception as e:
        return str(e), 500

@app.route('/api/channels-list', methods=['GET'])
def get_channels_json_route():
    channels = fetch_jio_channels()
    return jsonify({"status": "success", "count": len(channels), "channels": channels})
    
