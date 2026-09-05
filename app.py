from flask import Flask, jsonify, send_from_directory, request
app = Flask(__name__, static_folder=".", static_url_path="")
schemes = [
    {
        "name": "PM-KISAN",
        "min_age": 0,
        "max_age": 100,
        "max_income": None,
        "states": "All",
        "occupation": "Farmer",
        "category": "Any",
        "benefit": "Rs. 6,000/year income support for farmer families"
    },
    {
        "name": "IGNOAPS",
        "min_age": 60,
        "max_age": 150,
        "max_income": 100000,
        "states": "All",
        "occupation": "Any",
        "category": "Any",
        "benefit": "Monthly pension of Rs. 200-500 for senior citizens"
    },
    {
        "name": "PMMY",
        "min_age": 18,
        "max_age": 65,
        "max_income": None,
        "states": "All",
        "occupation": "Business Owner",
        "category": "Any",
        "benefit": "Collateral-free business loans up to Rs. 10 lakh"
    },
    {
        "name": "NMMS",
        "min_age": 0,
        "max_age": 100,
        "max_income": 350000,
        "states": "All",
        "occupation": "Student",
        "category": "Any",
        "benefit": "Rs. 12,000/year scholarship for meritorious students"
    }
]
def check_match(scheme, user):
    age = int(user["age"])          # convert "18" (text) into 18 (number)
    income = int(user["income"])    # same for income

    # Age check
    if age < scheme["min_age"] or age > scheme["max_age"]:
        return False

    # Income check (only matters if the scheme has an income limit)
    if scheme["max_income"] is not None and income > scheme["max_income"]:
        return False

    # State check (skip if scheme applies to all states)
    if scheme["states"] != "All" and scheme["states"] != user["state"]:
        return False

    # Occupation check (skip if scheme has no occupation restriction)
    if scheme["occupation"] != "Any" and scheme["occupation"] != user["occupation"]:
        return False

    # Category check (skip if scheme has no category restriction)
    if scheme["category"] != "Any" and scheme["category"] != user["category"]:
        return False

    # If none of the above returned False, every condition passed
    return True
@app.route("/")
def home():
    return send_from_directory(".", "eligibility.html")
@app.route("/api/check-eligibility", methods=["POST"])
def check_eligibility():
    data = request.get_json()
    print(data)

    matched_schemes = []
    for scheme in schemes:
        if check_match(scheme, data):
            matched_schemes.append(scheme)

    return jsonify({"matches": matched_schemes})
if __name__ == "__main__":
    app.run(debug=True, port=5000)
