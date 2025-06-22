from HelpingAI import HAI
from rich import print
hai = HAI(api_key="hl-7d62542a-a836-4e2d-930b-32a0a72232e4")

response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        # {"role": "system", "content": "You are an expert in emotional intelligence."},
        {"role": "user", "content": "Is there a sixth Fermat prime?"},
    ],
    hide_think=True,
    stream=True
)

for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="")
