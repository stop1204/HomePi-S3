# api key: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


import os

from groq import Groq

os.environ["GROQ_API_KEY"] = "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"

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    messages=[
        {
            "role": "user",
            "content": "Explain the importance of fast language models",
        }
    ],
    model="llama3-8b-8192",
)

print(chat_completion.choices[0].message.content)