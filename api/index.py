import os
import json
import base64
import requests
from flask import Flask, Response, request, jsonify

app = Flask(__name__)

# Vercel-ൽ താല്കാലികമായി ഡാറ്റ സേവ് ചെയ്യാനുള്ള പാത്ത്
DATA_FILE = "/tmp/creds.json"
CREDS_URL = "http://jiologin.unaux.com/temp/-creds.json?i=1"

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

def send_jio_otp(mobile):
    url = "https://jiotvapi.media.jio.com/userservice/apis/v1/login/otp"
    headers = {
        "Content-Type": "application/json",
        "appkey": "NzNiMDhlYzQyNjJm",
        "devicetype": "phone",
        "os": "android"
    }
    
    # Base64 എൻകോഡിങ് കൃത്യമായ സ്ട്രിങ് ഫോർമാറ്റിലാക്കുന്നു
    b64_mobile = base64.b64encode(mobile.encode('utf-8')).decode('utf-8')
    body = {"number": b64_mobile}
    
    try:
        res = requests.post(url, json=body, headers=headers, timeout=10)
        
        # റെസ്‌പോൺസ് ശൂന്യമാണോ എന്ന് പരിശോധിക്കുന്നു
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
    # OTP എപ്പോഴും സ്ട്രിങ് ആയിട്ടാണ് API-ലേക്ക് അയക്കേണ്ടത്
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
    
    # Jio API വിജയകരമായി ഒടിപി അയച്ചാൽ
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
    
    # ലോഗിൻ ടോക്കൺ ലഭിച്ചാൽ അത് /tmp ഫോൾഡറിലേക്ക് സേവ് ചെയ്യും
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
