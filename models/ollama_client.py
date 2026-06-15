import json
import re
import time
import ollama


class OllamaClient:

    def __init__(self, model_name):
        self.model_name = model_name

    def generate_json(
        self,
        prompt,
        fallback=None,
        max_retries=2
    ):

        attempts = []
        current_prompt = prompt

        for attempt in range(max_retries + 1):

            started_at = time.perf_counter()

            try:
                response = ollama.chat(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "user",
                            "content": current_prompt
                        }
                    ],
                    format="json",
                    options={
                        "temperature": 0
                    }
                )
            except Exception as exc:
                latency = time.perf_counter() - started_at
                attempts.append(
                    {
                        "attempt": attempt + 1,
                        "latency": latency,
                        "parsed": False,
                        "error": str(exc)
                    }
                )
                continue

            latency = time.perf_counter() - started_at
            text = response["message"]["content"]
            parsed = self._parse_json(text)
            usage = self._usage_from_response(response)

            attempts.append(
                {
                    "attempt": attempt + 1,
                    "latency": latency,
                    "parsed": parsed is not None,
                    "usage": usage
                }
            )

            if parsed is not None:
                if isinstance(parsed, dict):
                    parsed.setdefault(
                        "_model_metadata",
                        {
                            "model": self.model_name,
                            "attempts": attempts,
                            "recovered": attempt > 0
                        }
                    )
                return parsed

            current_prompt = (
                "Convert the following model output into valid JSON only. "
                "Do not add explanations or markdown.\n\n"
                f"Expected JSON shape:\n{json.dumps(fallback or {}, indent=2)}\n\n"
                f"Model output:\n{text}"
            )

        recovered = dict(fallback or {})
        recovered.update(
            {
                "_error": "malformed_json",
                "_model_metadata": {
                    "model": self.model_name,
                    "attempts": attempts,
                    "recovered": False
                }
            }
        )
        return recovered

    def _parse_json(self, text):

        parsers = [
            lambda value: json.loads(value),
            self._parse_markdown_json,
            self._parse_first_json_object
        ]

        for parser in parsers:
            try:
                parsed = parser(text)
                if isinstance(parsed, (dict, list)):
                    return parsed
            except Exception:
                continue

        return None

    def _usage_from_response(self, response):

        prompt_tokens = int(
            response.get(
                "prompt_eval_count",
                0
            )
            or 0
        )
        completion_tokens = int(
            response.get(
                "eval_count",
                0
            )
            or 0
        )

        return {
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": prompt_tokens + completion_tokens
        }

    def _parse_markdown_json(self, text):

        match = re.search(
            r"```(?:json)?\s*(.*?)\s*```",
            text,
            re.DOTALL | re.IGNORECASE
        )

        if not match:
            return None

        return json.loads(
            match.group(1)
        )

    def _parse_first_json_object(self, text):

        decoder = json.JSONDecoder()

        for index, char in enumerate(text):
            if char not in "[{":
                continue

            try:
                parsed, _ = decoder.raw_decode(
                    text[index:]
                )
                return parsed
            except Exception:
                continue

        return None
