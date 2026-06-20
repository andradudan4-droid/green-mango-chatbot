
from flask import Flask, request, jsonify, render_template_string, session
import os
import uuid
from groq import Groq

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-this-later"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are the friendly virtual assistant for "Green Mango Natural Salon",
an eco-friendly, vegan and cruelty-free hair salon in Portsmouth, UK.

Facts about the salon:
- Address: 18 Ordnance Row, Portsmouth, PO1 3DN
- Phone: 023 9283 3344, Email: enquiries@greenmangosalon.co.uk
- Hours: Tuesday 9:30am-6pm, Wednesday 9:30am-6pm, Thursday 9:30am-7:30pm,
  Friday 9:30am-7pm, Saturday 9am-4pm. Closed Sunday and Monday.
- Services: precision cutting (everything from pixies to mullets and
  shags), bespoke colouring (balayage, creative colour, lightening),
  curly hair specialists, and treatments. They use Davines, an Italian
  sustainable, vegan and cruelty-free haircare brand.
- They offer FREE colour consultations.
- A patch test is legally required at least 48 hours before any colour
  service, for anyone who hasn't been patch tested with them before.

YOUR JOB is to act like a real, thoughtful salon receptionist doing a
proper pre-booking consultation chat - not just take a booking time.
Have a natural conversation that covers (don't just fire off a robotic
checklist - ask naturally, one or two things at a time, and follow up
on what they say):

1. What are they looking to get done? (cut, colour, both, treatment)
2. What's their hair like currently? (length, current colour/condition,
   texture - straight/wavy/curly)
3. What's their goal / inspiration? (a look, a photo they have in mind,
   how they want it to feel)
4. If colour is involved: have they had a patch test with Green Mango
   before? If not, gently explain one is needed at least 48 hours
   before the appointment, and ask if they're happy to pop in for that
   first.
5. Any allergies, sensitivities, or scalp conditions worth knowing
   about ahead of time? (Always ask this gently and explain it's just
   so the stylist can take good care of them.)
6. Suggest this sounds like a good fit for a free consultation with
   one of the stylists, and ask if they'd like to be booked in for one.
7. Collect their name and best contact number or email so the team can
   confirm.

Tone: warm, relaxed, a little eco-conscious personality (they care
about sustainability) but not over the top. Keep replies short -
2-4 sentences at a time, like a real text conversation, not an essay.
Never invent specific prices - mention that pricing is discussed at
the free consultation since it depends on hair length/condition.
"""

all_conversations = {}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>Green Mango Salon - Demo Site</title>
    <style>
        * { box-sizing: border-box; }
        body { font-family: -apple-system, 'Helvetica Neue', Arial, sans-serif; margin: 0; background: #f0ede4; }
        .site-header { background: #2f4a3c; color: white; padding: 48px 20px; text-align: center; }
        .site-header h1 { margin: 0; font-weight: 300; letter-spacing: 3px; font-size: 28px; }
        .site-header p { opacity: 0.85; margin-top: 8px; }
        .site-body { max-width: 700px; margin: 60px auto; padding: 0 20px; color: #333; line-height: 1.6; }

        #chatBubble {
            position: fixed;
            bottom: 24px;
            right: 24px;
            width: 60px;
            height: 60px;
            border-radius: 50%;
            background: #2f4a3c;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            box-shadow: 0 4px 16px rgba(0,0,0,0.2);
            z-index: 1000;
            transition: transform 0.15s ease;
        }
        #chatBubble:hover { transform: scale(1.06); }

        #chatWindow {
            position: fixed;
            bottom: 96px;
            right: 24px;
            width: 350px;
            height: 480px;
            background: white;
            border-radius: 16px;
            box-shadow: 0 12px 40px rgba(0,0,0,0.22);
            display: none;
            flex-direction: column;
            overflow: hidden;
            z-index: 1000;
            border: 1px solid #eee;
        }
        #chatHeader {
            background: #2f4a3c;
            color: white;
            padding: 16px 18px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        #chatHeader .title { font-size: 15px; font-weight: 600; }
        #chatHeader .subtitle { font-size: 12px; opacity: 0.75; }
        #chatbox {
            flex: 1;
            padding: 16px;
            overflow-y: auto;
            background: #faf9f5;
        }
        .msg { margin: 8px 0; padding: 10px 13px; border-radius: 14px; max-width: 82%; font-size: 14px; line-height: 1.4; }
        .user { background: #2f4a3c; color: white; margin-left: auto; }
        .bot { background: #ECECEC; color: #222; }
        #inputRow { display: flex; border-top: 1px solid #eee; padding: 8px; background: white; }
        #userInput {
            flex: 1;
            padding: 10px 12px;
            border: 1px solid #ddd;
            border-radius: 20px;
            font-size: 14px;
            outline: none;
        }
        #userInput:focus { border-color: #2f4a3c; }
        #sendBtn {
            border: none;
            background: #2f4a3c;
            color: white;
            width: 38px;
            height: 38px;
            border-radius: 50%;
            margin-left: 8px;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            flex-shrink: 0;
        }
        #sendBtn:hover { background: #25382c; }
    </style>
</head>
<body>

    <div class="site-header">
        <h1>GREEN MANGO</h1>
        <p>Sustainable Hair Salon &middot; Portsmouth</p>
    </div>
    <div class="site-body">
        <h2>Welcome</h2>
        <p>This is a stand-in for the real Green Mango website, just so you can see
        how the chat widget would sit in the corner of an actual page. Click the
        bubble in the bottom right to start a chat.</p>
    </div>

    <div id="chatBubble" onclick="toggleChat()">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <path d="M21 11.5C21.0034 12.8199 20.6951 14.1219 20.1 15.3C19.3944 16.7118 18.3098 17.8992 16.9674 18.7293C15.6251 19.5594 14.0782 19.9994 12.5 20C11.1801 20.0035 9.87812 19.6951 8.7 19.1L3 21L4.9 15.3C4.30493 14.1219 3.99656 12.8199 4 11.5C4.00061 9.92179 4.44061 8.37488 5.27072 7.03258C6.10083 5.69028 7.28825 4.6056 8.7 3.90003C9.87812 3.30496 11.1801 2.99659 12.5 3.00003H13C15.0843 3.11502 17.053 3.99479 18.5291 5.47089C20.0052 6.94699 20.885 8.91568 21 11V11.5Z"
                stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
    </div>

    <div id="chatWindow">
        <div id="chatHeader">
            <div>
                <div class="title">Green Mango Salon</div>
                <div class="subtitle">Usually replies in a few minutes</div>
            </div>
        </div>
        <div id="chatbox"></div>
        <div id="inputRow">
            <input type="text" id="userInput" placeholder="Type a message..." onkeypress="if(event.key==='Enter') sendMessage()">
            <button id="sendBtn" onclick="sendMessage()">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="white" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 11L21 3L13 21L11 13L3 11Z" stroke="white" stroke-width="2" stroke-linejoin="round"/>
                </svg>
            </button>
        </div>
    </div>

    <script>
        let chatStarted = false;

        function toggleChat() {
            const win = document.getElementById('chatWindow');
            const isOpen = win.style.display === 'flex';
            win.style.display = isOpen ? 'none' : 'flex';

            if (!isOpen && !chatStarted) {
                chatStarted = true;
                addMessage("Hi there! Welcome to Green Mango. Are you looking to book in for a cut, colour, or both?", 'bot');
            }
        }

        function addMessage(text, sender) {
            const chatbox = document.getElementById('chatbox');
            const div = document.createElement('div');
            div.className = 'msg ' + sender;
            div.textContent = text;
            chatbox.appendChild(div);
            chatbox.scrollTop = chatbox.scrollHeight;
        }

        async function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (!message) return;

            addMessage(message, 'user');
            input.value = '';

            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message }),
                credentials: 'same-origin'
            });
            const data = await response.json();
            addMessage(data.reply, 'bot');
        }
    </script>
</body>
</html>
"""

@app.route("/")
def home():
    if "session_id" not in session:
        session["session_id"] = str(uuid.uuid4())
    return render_template_string(HTML_PAGE)

@app.route("/chat", methods=["POST"])
def chat_endpoint():
    session_id = session.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
        session["session_id"] = session_id

    if session_id not in all_conversations:
        all_conversations[session_id] = [{"role": "system", "content": SYSTEM_PROMPT}]

    conversation = all_conversations[session_id]

    user_message = request.json.get("message", "")
    conversation.append({"role": "user", "content": user_message})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=conversation,
        max_tokens=300
    )

    ai_reply = response.choices[0].message.content
    conversation.append({"role": "assistant", "content": ai_reply})

    return jsonify({"reply": ai_reply})


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)
