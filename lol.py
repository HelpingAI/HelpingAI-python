from HelpingAI import HAI

hai = HAI(api_key="")

response = hai.chat.completions.create(
    model="Dhanishtha-2.0-preview",
    messages=[
        {"role": "system", "content": "You are an expert in emotional intelligence."},
        {"role": "user", "content": "What makes a good leader?"}
    ],
    stream=True,  # Test streaming response
    hide_think=True
)
for chunk in response:
    if chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
