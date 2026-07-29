from __future__ import annotations

import os
from typing import Any

from openai import OpenAI

from tools._shared import err


def fallback(question: str = "", model: str = "gpt-4o-mini") -> dict[str, Any]:
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            api_key = os.getenv("OPENROUTER_API_KEY")
            base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        else:
            base_url = None

        if not api_key:
            raise RuntimeError("Missing OPENAI_API_KEY or OPENROUTER_API_KEY env var")

        client = OpenAI(api_key=api_key, base_url=base_url) if base_url else OpenAI(api_key=api_key)

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "Bạn là trợ lý hữu ích. LUÔN trả lời bằng tiếng Việt. Trả lời trực tiếp và ngắn gọn."},
                {"role": "user", "content": question},
            ],
            temperature=0.0,
        )

        answer = response.choices[0].message.content or ""
        return {
            "tool": "fallback",
            "question": question,
            "response": answer,
            "model": model,
        }
    except Exception as exc:
        return err("fallback", exc)
