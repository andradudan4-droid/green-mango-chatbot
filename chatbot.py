"""
Simple AI Chatbot - Starter Version (using Groq, free)
--------------------------------------------------------
"""

import os
from groq import Groq

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY")
)

SYSTEM_PROMPT = """
You are a friendly assistant for "Sunny Side Salon", a hair salon in Portsmouth.

Facts about the salon:
- Open Tuesday to Saturday, 9am to 5:30pm. Closed Sunday and Monday.
- Services: Haircut (£25), Colour (£60), Cut & Colour (£75), Blow dry (£15)
- Address: 12 High Street, Portsmouth
- To book, ask the customer for their name, preferred service, and
  preferred day/time, then tell them you've noted it down and the
  salon will confirm shortly.

Keep your replies short, warm, and helpful - like a real receptionist
texting back, not a formal essay.
"""

conversation_history = [{"role": "system", "content": SYSTEM_PROMPT}]

def chat():
    print("Chatbot is running! Type 'quit' to stop.\n")

    while True:
        user_message = input("You: ")

        if user_message.lower() == "quit":
            print("Goodbye!")
            break

        conversation_history.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history,
            max_tokens=300
        )

        ai_reply = response.choices[0].message.content
        print(f"Bot: {ai_reply}\n")

        conversation_history.append({"role": "assistant", "content": ai_reply})


if __name__ == "__main__":
    chat()
