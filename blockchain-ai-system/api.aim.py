from aiml_api import AIML_API

api = AIML_API()

completion = api.chat.completions.create(
    model="mistralai/Mistral-7B-Instruct-v0.2",
    messages=[
        {"role": "user", "content": "Explain the importance of low-latency LLMs"},
    ],
    temperature=0.7,
    max_tokens=256,
)

response = completion.choices[0].message.content
print("AI:", response)