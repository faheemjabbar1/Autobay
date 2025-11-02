from flask import Flask, request, jsonify, abort
import os, hashlib

app = Flask(__name__)

# These must be set in Render -> Environment
VERIFICATION_TOKEN = os.environ.get("VERIFICATION_TOKEN")
ENDPOINT_URL = os.environ.get("ENDPOINT_URL")  # exact URL you enter in eBay

if not VERIFICATION_TOKEN or not ENDPOINT_URL:
    raise RuntimeError("Set VERIFICATION_TOKEN and ENDPOINT_URL env vars in Render")

@app.route("/healthz", methods=["GET"])
def healthz():
    return "ok", 200

@app.route("/api/ebay/notifications", methods=["GET", "POST"])
def ebay_notifications():
    if request.method == "GET":
        # eBay's challenge uses challenge_code (underscore)
        challenge_code = request.args.get("challenge_code")
        if not challenge_code:
            return abort(400, "missing challenge_code")

        # SHA256(challengeCode + verificationToken + endpointURL)
        m = hashlib.sha256()
        m.update(challenge_code.encode("utf-8"))
        m.update(VERIFICATION_TOKEN.encode("utf-8"))
        m.update(ENDPOINT_URL.encode("utf-8"))
        return jsonify({"challengeResponse": m.hexdigest()}), 200

    # POST: acknowledge fast; (optional) verify X-EBAY-SIGNATURE later
    _ = request.get_json(silent=True)
    return ("", 200)

if __name__ == "__main__":
    # for local runs only; Render uses gunicorn
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
