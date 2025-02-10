from crewai import Crew, Agent, Task
#from langchain.chat_models import ChatOpenAI
from flask import Flask, request, jsonify
from langchain_community.chat_models import ChatOpenAI


from flask_ngrok import run_with_ngrok # import run_with_ngrok
import redis
import boto3
from flask import Flask, request, jsonify

from dotenv import load_dotenv
import openai
load_dotenv()
import os

openai_api_key = os.getenv("OPENAI_API_KEY")

# ✅ Connect to Local Redis (Ensure Redis is Running Locally)
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# ✅ AI Model for CrewAI
llm = ChatOpenAI(model="gpt-4-turbo", api_key=openai_api_key)

# 🛡️ 1️⃣ MFA Risk Analyzer - Determines whether MFA is required
mfa_risk_analyzer = Agent(
    role="MFA Risk Analyzer",
    goal="Analyze login risk and decide if MFA is required.",
    backstory="A security AI monitoring login behavior to dynamically enforce MFA.",
    llm=llm
)

# 🔑 2️⃣ MFA Challenge Generator - Creates OTP & sends via Email (Local Test)
def generate_otp(user_id):
    """Generate an OTP and store it in Redis for local testing."""
    import random
    otp = str(random.randint(100000, 999999))
    redis_client.setex(f"OTP_{user_id}", 300, otp)  # Store OTP for 5 mins
    return otp

mfa_challenge_generator = Agent(
    role="MFA Challenge Generator",
    goal="Generate OTP and deliver it securely.",
    backstory="Handles OTP generation & secure delivery.",
    llm=llm
)

# ✅ 3️⃣ MFA Validator - Verifies OTP against Redis cache
def verify_otp(user_id, entered_otp):
    """Check if user-entered OTP matches stored OTP in Redis."""
    stored_otp = redis_client.get(f"OTP_{user_id}")
    if stored_otp and entered_otp == stored_otp.decode("utf-8"):
        return "✅ OTP Verified! Login Successful."
    return "❌ OTP Verification Failed! Try again."

mfa_validator = Agent(
    role="MFA Validator",
    goal="Verify user OTP and authenticate login.",
    backstory="Checks OTP validity and grants access upon correct verification.",
    llm=llm
)

# 🔍 4️⃣ MFA Security Monitor - Logs & flags anomalies
mfa_security_monitor = Agent(
    role="MFA Security Monitor",
    goal="Log authentication events and detect suspicious login attempts.",
    backstory="Monitors failed MFA attempts and triggers alerts.",
    llm=llm
)

# ✅ Define CrewAI Tasks
task1 = Task(
    description="Analyze login request and determine if MFA is needed.",
    agent=mfa_risk_analyzer,
    expected_output="A string indicating whether MFA is required or not."
)

task2 = Task(
    description="Generate an OTP and send it to the user.",
    agent=mfa_challenge_generator,
    expected_output="A confirmation message that OTP has been sent."
)

task3 = Task(
    description="Verify OTP and allow login.",
    agent=mfa_validator,
    expected_output="A success or failure message for OTP validation."
)

task4 = Task(
    description="Log authentication attempts and flag suspicious logins.",
    agent=mfa_security_monitor,
    expected_output="A log entry confirming authentication event."
)

# 🚀 CrewAI Authentication Pipeline
crew = Crew(
    agents=[mfa_risk_analyzer, mfa_challenge_generator, mfa_validator, mfa_security_monitor],
    tasks=[task1, task2, task3, task4]
)

# ✅ Flask API for Local Testing
app = Flask(__name__)
#run_with_ngrok(app)

@app.route("/")
def home():
    return "✅ MFA CrewAI API is Live on Render!"

# ✅ Login API - Calls Risk-Based MFA Analysis
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    user_id = data.get("user_id")

    # Call CrewAI MFA Risk Analyzer
    risk_decision = "⚠️ MFA Required"  # Forcing MFA for testing
    return jsonify({"message": risk_decision, "user_id": user_id}), 200

# ✅ MFA Challenge API - Generates OTP Locally
@app.route('/mfa/challenge', methods=['POST'])
def mfa_challenge():
    data = request.json
    user_id = data.get("user_id")

    otp = generate_otp(user_id)
    return jsonify({"message": f"OTP for {user_id} is {otp} (Local Testing)"}), 200

# ✅ MFA Verify API - Validates OTP Locally
@app.route('/mfa/verify', methods=['POST'])
def mfa_verify():
    data = request.json
    user_id = data.get("user_id")
    otp = data.get("otp")

    result = verify_otp(user_id, otp)
    return jsonify({"message": result}), 200

#if __name__ == '__main__':
#    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    #app.run()  # Remove host and port arguments
    import os
    port = int(os.environ.get("PORT", 10000))  # Ensure it binds to the correct port
    app.run(host='0.0.0.0', port=port, debug=True)
    # or app.run(port=5000, debug=True) if you need to specify a port
