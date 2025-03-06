from flask import Flask, request, jsonify
from flask_cors import CORS
from referral_script import add_referrer, use_referral_code, update_login_status, sheet

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# 1. Use a referral code for sign-up (called when processing a referral from a link)
@app.route("/use", methods=["POST"])
def use_code():
    data = request.get_json()
    referral_code = data.get("referralCode")
    signup_email = data.get("signupEmail")
    if not referral_code or not signup_email:
        return jsonify({"success": False, "error": "Missing referralCode or signupEmail"}), 400
    success = use_referral_code(referral_code, signup_email)
    return jsonify({"success": success})

# 2. Get referral code for a user (by their referrer email) and create a new record if not found
@app.route("/get_referral", methods=["POST"])
def get_referral():
    data = request.get_json()
    user_email = data.get("email")
    if not user_email:
        return jsonify({"success": False, "error": "Missing email"}), 400

    records = sheet.get_all_records()
    for record in records:
        if record["Referrer Email"] == user_email:
            return jsonify({"success": True, "referralCode": record["Referral Code"]})
    # If not found, create a new record
    new_code = add_referrer(user_email)
    return jsonify({"success": True, "referralCode": new_code})

# 3. New endpoint: Get all referrals for a referrer
@app.route("/get_referrals", methods=["POST"])
def get_referrals():
    data = request.get_json()
    user_email = data.get("email")
    if not user_email:
        return jsonify({"success": False, "error": "Missing email"}), 400

    records = sheet.get_all_records()
    # Filter rows for which "Referrer Email" matches user_email and "Signup Email" is present
    referrals = []
    for record in records:
        if (record.get("Referrer Email") == user_email
            and record.get("Signup Email")):
            referrals.append({
                "Signup Email": record["Signup Email"],
                "Signup Date": record["Signup Date"],
                # Add other columns if needed:
                # "Status": record.get("Status", ""),
                # "Reward": record.get("Reward", ""),
            })

    return jsonify({"success": True, "referrals": referrals})

# 4. Generate referral code for a new referrer
@app.route("/generate", methods=["POST"])
def generate_code():
    data = request.get_json()
    referrer_email = data.get("referrerEmail")
    if not referrer_email:
        return jsonify({"success": False, "error": "No referrerEmail provided"}), 400
    code = add_referrer(referrer_email)
    return jsonify({"success": True, "referralCode": code})

# 5. Update login status (from "Pending" to "Logged In")
@app.route("/status", methods=["POST"])
def update_status():
    data = request.get_json()
    signup_email = data.get("signupEmail")
    status = data.get("status", "Logged In")
    if not signup_email:
        return jsonify({"success": False, "error": "Missing signupEmail"}), 400
    success = update_login_status(signup_email, status)
    return jsonify({"success": success})

if __name__ == "__main__":
    app.run(port=5000, debug=True)
