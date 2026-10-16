"""Ollama/Gemma 3 integration for Global Cooking Coach."""
import json
import re
from typing import Any, Dict, List, Optional

import requests


class OllamaError(RuntimeError):
    """Raised when Ollama is unavailable or returns an unusable response."""


class CookingAI:
    def __init__(self, base_url: str = "http://localhost:11434", model: str = "gemma3:1b", timeout: int = 120):
        self.base_url = base_url.rstrip("/")
        self.model = model
        self.timeout = timeout

    def _chat(self, messages: List[Dict[str, str]], temperature: float = 0.4) -> str:
        url = f"{self.base_url}/api/chat"
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature},
        }
        try:
            response = requests.post(url, json=payload, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.ConnectionError as exc:
            raise OllamaError(
                "Could not connect to Ollama. Start Ollama, check the server URL, and run `ollama pull gemma3`."
            ) from exc
        except requests.exceptions.Timeout as exc:
            raise OllamaError("Ollama took too long to respond. Try a smaller model or increase the timeout.") from exc
        except requests.exceptions.HTTPError as exc:
            detail = ""
            try:
                detail = response.text[:500]
            except Exception:
                pass
            raise OllamaError(
                f"Ollama returned an HTTP error ({response.status_code}). "
                f"Confirm the model '{self.model}' is installed with `ollama list`. {detail}"
            ) from exc
        except (requests.exceptions.RequestException, ValueError) as exc:
            raise OllamaError(f"Could not read Ollama's response: {exc}") from exc

        content = data.get("message", {}).get("content")
        if not isinstance(content, str) or not content.strip():
            raise OllamaError("Ollama returned an empty response. Please try again.")
        return content.strip()

    def generate_recipe(
        self,
        dish: str,
        ingredients: str,
        cuisine: str,
        servings: int,
        max_minutes: int,
        diet: str,
    ) -> Dict[str, Any]:
        schema = {
            "name": "Dish name",
            "emoji": "🍲",
            "cuisine": "Cuisine or region",
            "description": "Short description",
            "difficulty": "Easy",
            "servings": servings,
            "prep_minutes": 10,
            "cook_minutes": 20,
            "ingredients": [
                {"name": "ingredient", "quantity": 1, "unit": "cup"}
            ],
            "steps": ["Clear, numbered cooking instruction"],
            "video_search": "https://www.youtube.com/results?search_query=Dish+name+recipe",
        }
        prompt = f"""
You are a careful, practical cooking instructor with knowledge of cuisines worldwide.
Create one feasible recipe. The user requests:
- Dish or idea: {dish}
- Available ingredients: {ingredients or "not specified"}
- Cuisine: {cuisine}
- Servings: {servings}
- Maximum total time: {max_minutes} minutes
- Dietary preference: {diet}

Requirements:
1. Return ONLY valid JSON matching this schema, with no Markdown fences:
{json.dumps(schema, ensure_ascii=False)}
2. Use realistic quantities and clear numbered steps. Ingredients should be specific.
3. Set prep_minutes + cook_minutes near or below the time limit where feasible; never pretend a long process is quick.
4. Do not claim a dish is authentic if you are unsure; describe adaptations honestly.
5. If available ingredients are given, prioritize them and clearly include any essential additional ingredients.
6. Use metric-friendly units (g, ml, tbsp, tsp, piece, clove, cup) and explain any special technique in the steps.
7. Include food-safety details when relevant (especially meat, seafood, eggs, and leftovers).
8. Do not invent nutrition values. Do not provide medical advice.
9. video_search must be a YouTube search URL with URL-encoded query terms.
10. Avoid unsafe wild ingredients or unverified preservation/canning instructions.
"""
        raw = self._chat(
            [
                {"role": "system", "content": "Return valid JSON only. Do not wrap it in Markdown."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
        )
        return self._extract_json(raw)

    def ask_cooking_question(self, question: str, history: Optional[List[Dict[str, str]]] = None) -> str:
        system = (
            "You are a friendly, careful cooking coach for beginners and experienced home cooks. "
            "Give practical, concise, step-by-step guidance. Ask a clarifying question when essential details "
            "are missing. Be honest about uncertainty and distinguish traditional recipes from adaptations. "
            "For food safety, prioritize conservative guidance from recognized food-safety authorities. "
            "Do not invent precise nutrition facts, guarantee outcomes, or recommend tasting food that may be unsafe. "
            "For severe burns, allergic reactions, or other emergencies, tell the user to seek appropriate urgent help."
        )
        messages = [{"role": "system", "content": system}]
        if history:
            for item in history[-8:]:
                role = item.get("role")
                content = item.get("content", "")
                if role in ("user", "assistant") and isinstance(content, str):
                    messages.append({"role": role, "content": content[:4000]})
        if not history or history[-1].get("content") != question:
            messages.append({"role": "user", "content": question})
        return self._chat(messages, temperature=0.5)

    @staticmethod
    def _extract_json(text: str) -> Dict[str, Any]:
        cleaned = text.strip()
        cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s*```$", "", cleaned)
        try:
            result = json.loads(cleaned)
        except json.JSONDecodeError:
            start, end = cleaned.find("{"), cleaned.rfind("}")
            if start < 0 or end <= start:
                raise OllamaError("The model did not return valid recipe JSON. Please try again.")
            try:
                result = json.loads(cleaned[start:end + 1])
            except json.JSONDecodeError as exc:
                raise OllamaError("The model returned malformed recipe data. Please retry with a simpler request.") from exc
        if not isinstance(result, dict):
            raise OllamaError("The model's recipe response must be a JSON object.")
        return result
