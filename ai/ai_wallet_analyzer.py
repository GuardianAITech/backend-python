import openai
from dotenv import load_dotenv
import os
from openai import OpenAI
load_dotenv()
openai_api_key = os.getenv("OPEN_AI_KEY")
client = OpenAI(api_key=openai_api_key)


def check_wallet_with_ai(wallet_details):
    
    prompt = f"Analyze the data and write a summary:  {wallet_details}"

    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": f"You are a developer.",
                },
                {
                    "role": "user",
                    "content": prompt,
                },
            ],
            model="gpt-3.5-turbo-16k",
            temperature=0.7
        )
        content = chat_completion.choices[0].message.content
        print("API Response:", content)
        # response_object = json.loads(content)
        return content
    except Exception as e:
        print(f"An error occurred: {e}")
        return None