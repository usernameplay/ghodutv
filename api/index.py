import os
import json
import base64
import requests
from flask import Flask, Response, request, render_template_string, jsonify

app = Flask(__name__)

# Vercel-ൽ താല്കാലികമായി ഡാറ്റ സേവ് ചെയ്യാനുള്ള പാത്ത്
DATA_FILE = "/tmp/creds.json"
CREDS_URL = "http://jiologin.unaux.com/temp/-creds.json?i=1" # ബാക്ക്-അപ്പ് ക്രെഡൻഷ്യൽ ലിങ്ക്

# Helper: ടോക്കൺ ഡാറ്റ റീഡ് ചെയ്യാൻ
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
    return None

# Helper: ഒടിപി അയക്കാൻ
def send_jio_otp(mobile):
    url = "https://jiotvapi.media.jio.com/userservice/apis/v1/login/otp"
    headers = {
        "Content-Type": "application/json",
        "appkey": "NzNiMDhlYzQyNjJm",
        "devicetype": "phone",
        "os": "android"
    }
    body = {"number": b64encode(mobile.encode()).decode()}
    try:
        res = requests.post(url, json=body, headers=headers, timeout=10)
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

# Helper: ഒടിപി വെരിഫൈ ചെയ്യാൻ
def verify_jio_otp(mobile, otp):
    url = "https://jiotvapi.media.jio.com/userservice/apis/v1/login/verify"
    headers = {
        "Content-Type": "application/json",
        "appkey": "NzNiMDhlYzQyNjJm",
        "devicetype": "phone",
        "os": "android"
    }
    body = {"number": b64encode(mobile.encode()).decode(), "otp": otp}
    try:
        res = requests.post(url, json=body, headers=headers, timeout=10)
        return res.json()
    except Exception as e:
        return {"status": "error", "message": str(e)}

def b64encode(s):
    return base64.b64encode(s)

# --- ROUTES ---

@app.route('/')
def index_page():
    # ഫ്രണ്ട്-എൻഡ് HTML ഇൻഡക്സ് ഫയലിലേക്ക് റീഡയറക്ട് ചെയ്യുന്നു
    return app.send_static_file('index.html')

@app.route('/api/send-otp', methods=['POST'])
def send_otp_route():
    data = request.json or {}
    mobile = data.get('mobile', '')
    if not mobile:
        return jsonify({"status": "error", "message": "Mobile number required"}), 400
    result = send_jio_otp(mobile)
    return jsonify(result)

@app.route('/api/verify-otp', methods=['POST'])
def verify_otp_route():
    data = request.json or {}
    mobile = data.get('mobile', '')
    otp = data.get('otp', '')
    if not mobile or not otp:
        return jsonify({"status": "error", "message": "Mobile and OTP required"}), 400
    
    result = verify_jio_otp(mobile, otp)
    if "authToken" in result:
        with open(DATA_FILE, "w") as f:
            json.dump(result, f)
        return jsonify({"status": "success", "message": "Login Successful"})
    
    return jsonify({"status": "error", "message": result.get("message", "Verification Failed")})

@app.route('/playlist.m3u')
def generate_playlist():
    creds = get_stored_creds()
    if not creds:
        return "Failed to fetch credentials. Please login first.", 500
    
    protocol = request.headers.get('X-Forwarded-Proto', 'https')
    host_url = f"{protocol}://{request.host}/"
    
    # പ്രധാന ചാനലുകൾ ഇവിടെ ലിസ്റ്റ് ചെയ്യുന്നു (കൂടുതൽ ചാനലുകൾ ഇതേ ഫോർമാറ്റിൽ ചേർക്കാം)
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
