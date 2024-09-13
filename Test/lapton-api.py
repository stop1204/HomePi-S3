import os
import openai
# CLI command: export LEPTON_API_TOKEN="xhwg2y4dpim3vqu16z8ijtjxk12e93u6"
LEPTON_API_TOKEN="xhwg2y4dpim3vqu16z8ijtjxk12e93u6"
client = openai.OpenAI(
    base_url="https://llama3-1-405b.lepton.run/api/v1/",
    # api_key=os.environ.get('LEPTON_API_TOKEN')
    api_key = LEPTON_API_TOKEN
)

completion = client.chat.completions.create(
    model="llama3-1-405b",
    messages=[
        {"role": "user", "content": "say hello"},
    ],
    max_tokens=128,
    stream=True,
)

for chunk in completion:
    if not chunk.choices:
        continue
    content = chunk.choices[0].delta.content
    if content:
        print(content, end="")