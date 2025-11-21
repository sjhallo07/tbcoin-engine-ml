import os
import requests
from typing import Any, Dict, List, Optional


class AIML_API:
    def __init__(self, api_key: Optional[str] = None, base_url: Optional[str] = None, timeout: int = 60):
        self.api_key = api_key or os.getenv("DEEPSEEK_API_KEY") or os.getenv("OPENAI_API_KEY")
        self.base_url = (base_url or os.getenv("OPENAI_BASE_URL") or os.getenv("DEEPSEEK_API_BASE") or "https://api.deepseek.com").rstrip("/")
        self.timeout = timeout
        self.chat = self.Chat(self)

    class Chat:
        def __init__(self, client: "AIML_API"):
            self.completions = AIML_API.Completions(client)

    class Completions:
        def __init__(self, client: "AIML_API"):
            self.client = client

        def create(self, model: str, messages: List[Dict[str, Any]], temperature: float = 0.7, max_tokens: int = 256):
            if not self.client.api_key:
                raise RuntimeError("Missing API key: set DEEPSEEK_API_KEY or OPENAI_API_KEY")
            url = f"{self.client.base_url}/v1/chat/completions"
            payload = {
                "model": model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
            }
            headers = {
                "Authorization": f"Bearer {self.client.api_key}",
                "Content-Type": "application/json",
            }
            resp = requests.post(url, json=payload, headers=headers, timeout=self.client.timeout)
            resp.raise_for_status()
            data = resp.json()

            class Message:
                def __init__(self, content: str):
                    self.content = content

            class Choice:
                def __init__(self, msg: "Message"):
                    self.message = msg

            class Response:
                def __init__(self, content: str):
                    self.choices = [Choice(Message(content))]

            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return Response(content)


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