import os
import json
import base64
import requests
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

# Vercel-ൽ താല്കാലികമായി ഡാറ്റ സേവ് ചെയ്യാനുള്ള പാത്ത്
DATA_FILE = "/tmp/creds.json"
CREDS_URL = "http://jiologin.unaux.com/temp/-creds.json?i=1"

# നിങ്ങൾ നൽകിയ പുതിയ ടോക്കൺ ഡാറ്റ നേരിട്ട് കോഡിൽ ബാക്കപ്പ് ആയി ചേർക്കുന്നു
DEFAULT_CREDS = {
    "authToken": "eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCJ9.eyJkYXRhIjp7ImF1dGhUb2tlbklkIjoiODIzOWRjZDUtNmVmYS00MTIzLThmNDgtYjllNjc3MTI3ZGYyIiwidXNlcklkIjoiNzY5MzhkYTItYmRkZi00NGE4LWFlMmUtZDY1YzQ1OGIzYmJhIiwidXNlclR5cGUiOiJKSU8iLCJvcyI6ImFuZHJvaWQiLCJkZXZpY2VUeXBlIjoicGhvbmUiLCJhY2Nlc3NMZXZlbCI6IjkiLCJkZXZpY2VJZCI6IjZmY2FkZWI3YjRiMTBkNzciLCJleHRyYSI6IntcIm51bWJlclwiOlwiVEtiTjZ4QjQ4cUhxajcxOHpZZ3J4VGNuNHhWRVJ1NmZQNVE2aGVJVm9WVGRmOGFVcitScmdoTT1cIixcInBsYW5kZXRhaWxzXCI6e1wiUGFja2FnZUluZm9cIjpbe1wicGxhbmlkXCI6XCIxXCIsXCJzdWJzY3JpcHRpb25zdGFydFwiOjE2ODY0ODUyNjMsXCJzdWJzY3JpcHRpb25lbmRcIjoxODEwMDU3MDE4LFwicGxhbnR5cGVcIjpcIlwiLFwiYnVzaW5lc3NUeXBlXCI6XCJqaW9cIixcIm5vdGVzXCI6XCJcIn1dfSxcImpUb2tlblwiOlwiOGU2ZWJjNmEzOTdmMWE4MzdiMmZhOTBhZTE3NGFkMWUuY2Q4MTZlZGFhYjYwMmEyMWI2YjlhYTBmNzllYTk5MWVkMjA4ZjY0NmYwYThmNGZhN2M2ODRlMjZiODkwNjJkZDg1NzI0YjZjY2IzNjczMzdkY2RhY2EyYWYwMjIwZjJjZjNjN2IxZTFlYzFjODZlZDJmZjYyNGE3ZjhhZDk5ODAwM2Q3NTkyZjA2NjY0YWU5YWVmMjNmOWNlMjAzMTNhNzRmZTc0MmM0Y2Q2OWViewI2MmFkZGQ3MDIwYzMyNTRhMjk0MzFkZGJjNGQ3NDA0NDI5MTE1ZTJiMDU1YjM0ZmJlZTYyZDgxMGQ1N2QwODRkZjk5NjVlZGZkNTAyZWZmMjViY2M0OGQzNGM1MzE0YjExN2M2MTYyZDk0ZTIzNGUwYzhkZTJmZjQ2MWM3YTFkYzAyMzliMTI3NDg4MTc4NmM1YTE1Y2YyZjAxYTI3Yjc2N2QwZmE3OGY1ZjI4ZGFlMzA1NWM4ODEwMGVlYWFkMmMzMjdjNDY0NmNjMDllM2RiZGNkNmNkYjliMWNhMGQ2YjI2MGU4M2Q0ODQ0NjllN2NlNzY5Yzg1NWZjMTk4ODMxYmMxMmFiYjEzNTI5NzI1Yjc1MzhhZWUyMDM4ODQyZGZlYmRlODM0NTI4ZjkwODgyMTE0ZTYwN2E2OTNjZmNiOWExYmVjNjIxYjc2Y2RkZjcxYmJmYzgwNjQ5ZDU2NmJlZGQ3OGRjYWE2ZDY2NjNiMmVlOTZlMDBiNDg4MDg2NzhiNzU4NTRiNzhlMjBkNjEzMzI2ZmU0NzAxOWM2MmQ3MWY2Nzc2NGRlNzZlMGQyMTIwY2I4Y2NkYTc5ZDgzN2E4Y2MxOGY2MjY0MzkyZjljMDdiMTllZWJjMzQxMDlhNzZkMTIxNThmZTJmMDNlYzMwZTY2OTU2ZDhlMDIwYjZkZGJiNDI0ZDNhZmUzYjcwZmNiY1wiLFwidXNlckRldGFpbHNcIjoiNTNiRFdpYU5RYjloeXZEdHluVjUrbGdRdVdOQ3U2SjFkdTdYN055dk9qM0JPVElWREQ0dDhkRlRKZXliNlVDc1VrNTQzd081QVJmUTJocUxsc2NXY2RPTTBMRWc5djZrT2FaOGZtcExpM0ZBdU1ESzlkendVVXdTcDFJVGdhYVFkYlh1RlhYWmVESER3eEl5YW5Ndk51UXhmcy9rUXhFdnJHbjJ3amlEYllQcVBUZkxUNjJ5bTdEMUg5eWtuWWZhQnA4eklNeWdZbTNwYWc2TnAzOXVpWGM3VUF5MW1jUXVPeHVmK1YwQzJrKzQ2c0orNlhZWVVxeGFJT2ZMeThzaFBQaW1JYlJUQ2hvQ1BTYWU0MDNUM2V6dUVIMW1zRmliaS9PalwifSIsInN1YnNjcmliZXJJZCI6IjEyNjE4MTMzMDgiLCJhcHBOYW1lIjoiUkpJTF9KaW9UViIsInZlcnNpb24iOiJ2MS4xIiwicGxhdGZvcm0iOiIifSwiZXhwIjoxNzc5Mzg1MDE4LCJpYXQiOjE3Nzg1MjEwMTh9.1SL3vj_TqCuoVxqzd7msHlYxjun-P6mAqfew83_7e1E7LOt3xvEk5uUcUb5SB-Ma6rk4wKGgYAO886BDK8wh-Q",
    "refreshToken": "4d669ff3-f2f6-4b9f-ae58-c3d29273b6a1",
    "ssoToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJjcmVhdGVkRm9yIjoiSmlvVFYiLCJkZXZpY2VJZCI6IjZmY2FkZWI3YjRiMTBkNzciLCJpYXQiOjE3Nzg1MjEwMTgsInNJZCI6IlUyRnNkR1ZrWDEvQ0g5QXlWRC8yVW5zK0c3dmlYMCtYRld0RDJkb3ljeVU9IiwidW5pcXVlIjoiNzY5MzhkYTItYmRkZi00NGE4LWFlMmUtZDY1YzQ1OGIzYmJhIiwidXNlclR5cGUiOiJKSU8ifQ.t3ZuMrk5sQRvL7Oxv3i0yVc5OybGMSJ7sCUzD87n0TQ",
    "sessionAttributes": {
        "user": {
            "commonName": "Sneh Kumar",
            "mobile": "+918294068585",
            "preferredLocale": "en-US",
            "ssoLevel": "20",
            "subscriberId": "1261813308",
            "uid": "snehkumar297",
            "unique": "76938da2-bddf-44a8-ae2e-d65c458b3bba"
        }
    },
    "jToken": "8e6ebc6a397f1a837b2fa90ae174ad1e.cd816edaab602a21b6b9aa0f79ea991ed208f646f0a8f4fa7c684e26b89062dd85724b6ccb367337dcdaca2af0220f2cf3c7b1e1ec1c86ed2ff624a7f8ad998003d7592f06664ae9aef23f9ce20313a74fe742c4cd69c262addd7020c3254a29431ddbc4d7404429115e2b055b34fbee62d810d57d084df9965edfd502eff25bcc48d34c5314b117c6162d94e234e0c8de2ff461c7a1dc0239b1274881786c5a15cf2f01a27b767d0fa78f5f28dae3055c88100eeaad2c327c4646cc09e3dbdcd6cdb9b1ca0d6b260e83d484469e7ce769c855fc198831bc12abb13529725b7538aee2038842dfebde834528f90882114e607a693cfcb9a1bec621b76cddf71bbfc80649d566bedd78dcaa6d6663b2ee96e00b48808678b75854b78e20d613326fe47019c62d71f67764de76e0d2120cb8ccda79d837a8cc18f6264392f9c07b19eebc34109a76d12158fe2f03ec30e66956d8e020b6ddbb424d3afe3b70fcbc"
}

def get_stored_creds():
    # 1. ആദ്യം ലോക്കൽ ഫയലിൽ ഡാറ്റ ഉണ്ടോ എന്ന് നോക്കും
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
            
    # 2. ഇല്ലെങ്കിൽ ഓൺലൈൻ ലിങ്കിൽ നിന്ന് എടുക്കാൻ ശ്രമിക്കും
    try:
        res = requests.get(CREDS_URL, timeout=5)
        if res.status_code == 200:
            return res.json()
    except:
        pass
        
    # 3. രണ്ട് വഴിയും പരാജയപ്പെട്ടാൽ കോഡിനുള്ളിലെ ഡിഫോൾട്ട് ഡാറ്റ റിട്ടേൺ ചെയ്യും
    return DEFAULT_CREDS

def send_jio_otp(mobile):
    url = "https://jiotvapi.media.jio.com/userservice/apis/v1/login/otp"
    headers = {
        "Content-Type": "application/json",
        "appkey": "NzNiMDhlYzQyNjJm",
        "devicetype": "phone",
        "os": "android"
    }
    
    b64_mobile = base64.b64encode(mobile.encode('utf-8')).decode('utf-8')
    body = {"number": b64_mobile}
    
    try:
        res = requests.post(url, json=body, headers=headers, timeout=10)
        if not res.text or not res.text.strip():
            return {"status": "error", "message": "Jio Server returned an empty response."}
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def verify_jio_otp(mobile, otp):
    url = "https://jiotvapi.media.jio.com/userservice/apis/v1/login/verify"
    headers = {
        "Content-Type": "application/json",
        "appkey": "NzNiMDhlYzQyNjJm",
        "devicetype": "phone",
        "os": "android"
    }
    
    b64_mobile = base64.b64encode(mobile.encode('utf-8')).decode('utf-8')
    body = {"number": b64_mobile, "otp": str(otp)}
    
    try:
        res = requests.post(url, json=body, headers=headers, timeout=10)
        if not res.text or not res.text.strip():
            return {"status": "error", "message": "Jio Server returned an empty response during verification."}
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# --- ROUTES ---

@app.route('/api/send-otp', methods=['POST'])
def send_otp_route():
    data = request.json or {}
    mobile = data.get('mobile', '')
    if not mobile:
        return jsonify({"status": "error", "message": "Mobile number required"}), 400
        
    result = send_jio_otp(str(mobile))
    if result.get("status") == "success" or "success" in result.get("message", "").lower():
        return jsonify({"status": "success", "message": "OTP sent successfully"})
        
    return jsonify({"status": "error", "message": result.get("message", "Failed to send OTP")})

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.json or {}
    mobile = data.get('mobile', '')
    otp = data.get('otp', '')
    if not mobile or not otp:
        return jsonify({"status": "error", "message": "Mobile and OTP required"}), 400
    
    result = verify_jio_otp(str(mobile), str(otp))
    if "authToken" in result:
        try:
            with open(DATA_FILE, "w") as f:
                json.dump(result, f)
            return jsonify({"status": "success", "message": "Login Successful"})
        except Exception as file_err:
            return jsonify({"status": "error", "message": f"Failed to save tokens locally: {str(file_err)}"})
    
    return jsonify({"status": "error", "message": result.get("message", "Verification Failed")})

@app.route('/playlist.m3u')
def generate_playlist():
    creds = get_stored_creds()
    if not creds:
        return "#EXTM3U\n#EXTINF:-1, Login Required\nhttp://error.mp4", 200
    
    protocol = request.headers.get('X-Forwarded-Proto', 'https')
    host_url = f"{protocol}://{request.host}/"
    
    m3u_content = "#EXTM3U x-tvg-url=\"https://avapi.live/epg/jiotv.xml.gz\"\n"
    m3u_content += '#EXTINF:-1 tvg-id="144" tvg-logo="https://jiotv.catchup.cdn.jio.com/dare_images/images/Asianet_HD.png" group-title="Malayalam",Asianet HD\n'
    m3u_content += f"{host_url}live/Asianet_HD.m3u8?id=144\n"
    
    m3u_content += '#EXTINF:-1 tvg-id="150" tvg-logo="https://jiotv.catchup.cdn.jio.com/dare_images/images/Surya_TV_HD.png" group-title="Malayalam",Surya TV HD\n'
    m3u_content += f"{host_url}live/Surya_TV_HD.m3u8?id=150\n"
    
    return Response(m3u_content, mimetype='application/x-mpegurl')

@app.route('/live/<channel_name>.m3u8')
def live_stream(channel_name):
    creds = get_stored_creds()
    if not creds:
        return "Auth failed - Login required", 401
    
    auth_token = creds.get("authToken")
    j_token = creds.get("jToken")
    
    headers = {
        "User-Agent": "plaYtv/7.1.3 (Linux;Android 14) ExoPlayerLib/2.11.7",
        "jToken": j_token,
        "authToken": auth_token
    }
    
    target_url = f"https://jiotvmblive.cdn.jio.com/bpk-tv/{channel_name}/Fallback/{channel_name}.m3u8"
    
    try:
        res = requests.get(target_url, headers=headers, timeout=10)
        return Response(res.content, mimetype='application/vnd.apple.mpegurl')
    except Exception as e:
        return str(e), 500
    
