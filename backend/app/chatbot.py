# backend/app/chatbot.py
import cohere
import os
import json
from dotenv import load_dotenv

load_dotenv()

cohere_api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_api_key)

def extract_tasks_from_text(text: str):
    prompt = f"""
You are an intelligent assistant. Extract all TODO tasks from the message below.
Return the result strictly as a JSON array like:
[
  {{"title": "...", "description": "..."}},
  ...
]

Input message: "{text}"
"""

    response = co.generate(
        model='command',
        prompt=prompt,
        max_tokens=200,
        temperature=0.5
    )

    raw_output = response.generations[0].text.strip()

    try:
        tasks = json.loads(raw_output)
        return [(task["title"], task["description"]) for task in tasks if "title" in task]
    except Exception as e:
        print("❌ Error parsing tasks from Cohere:", e)
        return []
