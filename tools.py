"""Recipe data, scaling, search, and local progress persistence."""
from copy import deepcopy
from datetime import date
import json
import os
import re
from typing import Any, Dict, List

DATA_DIR = os.path.dirname(os.path.abspath(__file__))
PROGRESS_FILE = os.path.join(DATA_DIR, "progress.json")

# Starter collection, not an exhaustive catalogue of every dish in the world.
# Add recipes here or connect a licensed recipe database/API for a larger catalogue.
RECIPE_CATALOG: List[Dict[str, Any]] = [
    {
        "id": "indian-dal-tadka", "name": "Dal Tadka", "emoji": "🍛", "cuisine": "Indian",
        "description": "Comforting lentils finished with a fragrant spiced tempering.",
        "difficulty": "Easy", "servings": 2, "prep_minutes": 10, "cook_minutes": 30,
        "diet": ["Vegetarian", "Vegan", "Gluten-free"],
        "ingredients": [
            {"name": "red lentils or split pigeon peas", "quantity": 150, "unit": "g"},
            {"name": "water", "quantity": 600, "unit": "ml"},
            {"name": "onion, finely chopped", "quantity": 1, "unit": "small"},
            {"name": "tomato, chopped", "quantity": 1, "unit": "medium"},
            {"name": "garlic, minced", "quantity": 2, "unit": "clove"},
            {"name": "cumin seeds", "quantity": 1, "unit": "tsp"},
            {"name": "turmeric", "quantity": 0.25, "unit": "tsp"},
            {"name": "oil or ghee", "quantity": 1, "unit": "tbsp"},
            {"name": "salt", "quantity": 0.5, "unit": "tsp"},
        ],
        "steps": [
            "Rinse the lentils until the water runs mostly clear.",
            "Simmer lentils with water and turmeric until soft, about 20–30 minutes; add water if needed.",
            "Heat oil or ghee in a pan. Add cumin seeds, then onion and cook until softened.",
            "Add garlic and tomato; cook until the tomato breaks down. Stir this mixture into the lentils.",
            "Season with salt, simmer for 3–5 minutes, and serve hot with rice or flatbread."
        ],
        "video_search": "https://www.youtube.com/results?search_query=dal+tadka+recipe",
    },
    {
        "id": "italian-tomato-pasta", "name": "Tomato Basil Pasta", "emoji": "🍝", "cuisine": "Italian",
        "description": "A simple pasta with tomato, garlic, olive oil, and basil.",
        "difficulty": "Easy", "servings": 2, "prep_minutes": 10, "cook_minutes": 20,
        "diet": ["Vegetarian", "Vegan"],
        "ingredients": [
            {"name": "pasta", "quantity": 180, "unit": "g"},
            {"name": "ripe tomatoes or canned tomatoes", "quantity": 300, "unit": "g"},
            {"name": "garlic, sliced", "quantity": 2, "unit": "clove"},
            {"name": "olive oil", "quantity": 1, "unit": "tbsp"},
            {"name": "fresh basil", "quantity": 8, "unit": "leaf"},
            {"name": "salt", "quantity": 0.5, "unit": "tsp"},
            {"name": "black pepper", "quantity": 0.25, "unit": "tsp"},
        ],
        "steps": [
            "Bring a pot of water to a boil, salt it, and cook pasta according to its packet instructions.",
            "Meanwhile, warm olive oil in a pan over medium-low heat and cook garlic for about 30 seconds without browning it.",
            "Add chopped tomatoes and simmer for 10–15 minutes until saucy.",
            "Reserve a little pasta water, drain the pasta, and toss it with the sauce. Add a splash of pasta water if needed.",
            "Season with pepper and torn basil. Taste and adjust salt before serving."
        ],
        "video_search": "https://www.youtube.com/results?search_query=Italian+tomato+basil+pasta+recipe",
    },
    {
        "id": "mexican-bean-tacos", "name": "Black Bean Tacos", "emoji": "🌮", "cuisine": "Mexican-inspired",
        "description": "Quick bean tacos with fresh toppings; a practical home version.",
        "difficulty": "Easy", "servings": 2, "prep_minutes": 10, "cook_minutes": 15,
        "diet": ["Vegetarian", "Vegan"],
        "ingredients": [
            {"name": "cooked black beans, drained", "quantity": 250, "unit": "g"},
            {"name": "small tortillas", "quantity": 4, "unit": "piece"},
            {"name": "onion, chopped", "quantity": 0.5, "unit": "small"},
            {"name": "cumin", "quantity": 0.5, "unit": "tsp"},
            {"name": "oil", "quantity": 1, "unit": "tsp"},
            {"name": "lime", "quantity": 1, "unit": "piece"},
            {"name": "tomato, chopped", "quantity": 1, "unit": "medium"},
            {"name": "salt", "quantity": 0.25, "unit": "tsp"},
        ],
        "steps": [
            "Warm oil in a pan and cook onion for 3–4 minutes.",
            "Add beans, cumin, salt, and a splash of water. Warm through and lightly mash some beans.",
            "Warm tortillas in a dry pan according to packet directions.",
            "Fill tortillas with beans and tomato. Finish with lime juice and any preferred toppings."
        ],
        "video_search": "https://www.youtube.com/results?search_query=black+bean+tacos+recipe",
    },
    {
        "id": "japanese-vegetable-fried-rice", "name": "Vegetable Fried Rice", "emoji": "🍚", "cuisine": "Japanese-inspired",
        "description": "A flexible fried-rice dish using chilled cooked rice and vegetables.",
        "difficulty": "Easy", "servings": 2, "prep_minutes": 10, "cook_minutes": 10,
        "diet": ["Vegetarian", "Vegan"],
        "ingredients": [
            {"name": "cooked, chilled rice", "quantity": 350, "unit": "g"},
            {"name": "mixed vegetables", "quantity": 150, "unit": "g"},
            {"name": "spring onion, sliced", "quantity": 2, "unit": "piece"},
            {"name": "soy sauce", "quantity": 1, "unit": "tbsp"},
            {"name": "neutral oil", "quantity": 1, "unit": "tbsp"},
            {"name": "garlic, minced", "quantity": 1, "unit": "clove"},
        ],
        "steps": [
            "Use rice that was cooled promptly and kept refrigerated; do not leave cooked rice at room temperature for long periods.",
            "Heat oil in a wide pan. Stir-fry vegetables until hot and tender-crisp.",
            "Add garlic and spring onion; cook briefly.",
            "Add rice and break up clumps. Stir-fry until steaming hot throughout.",
            "Add soy sauce, mix well, and serve immediately."
        ],
        "video_search": "https://www.youtube.com/results?search_query=vegetable+fried+rice+recipe",
    },
    {
        "id": "thai-coconut-chickpea-curry", "name": "Coconut Chickpea Curry", "emoji": "🥥", "cuisine": "Thai-inspired",
        "description": "A creamy coconut curry with chickpeas and vegetables.",
        "difficulty": "Easy", "servings": 2, "prep_minutes": 10, "cook_minutes": 20,
        "diet": ["Vegetarian", "Vegan", "Gluten-free"],
        "ingredients": [
            {"name": "cooked chickpeas, drained", "quantity": 240, "unit": "g"},
            {"name": "coconut milk", "quantity": 200, "unit": "ml"},
            {"name": "curry paste, check label for dietary needs", "quantity": 1, "unit": "tbsp"},
            {"name": "mixed vegetables", "quantity": 200, "unit": "g"},
            {"name": "oil", "quantity": 1, "unit": "tsp"},
            {"name": "lime juice", "quantity": 1, "unit": "tsp"},
        ],
        "steps": [
            "Warm oil in a pan and cook the curry paste for about a minute, following the paste label.",
            "Add vegetables and stir for 2–3 minutes.",
            "Add chickpeas and coconut milk. Simmer until the vegetables are cooked and the curry is hot throughout.",
            "Finish with lime juice. Taste and adjust seasoning; serve with rice."
        ],
        "video_search": "https://www.youtube.com/results?search_query=coconut+chickpea+curry+recipe",
    },
    {
        "id": "middle-eastern-hummus", "name": "Hummus", "emoji": "🧆", "cuisine": "Levantine",
        "description": "A smooth chickpea and tahini dip.",
        "difficulty": "Easy", "servings": 4, "prep_minutes": 10, "cook_minutes": 0,
        "diet": ["Vegetarian", "Vegan", "Gluten-free"],
        "ingredients": [
            {"name": "cooked chickpeas, drained", "quantity": 400, "unit": "g"},
            {"name": "tahini", "quantity": 3, "unit": "tbsp"},
            {"name": "lemon juice", "quantity": 2, "unit": "tbsp"},
            {"name": "garlic", "quantity": 1, "unit": "clove"},
            {"name": "olive oil", "quantity": 1, "unit": "tbsp"},
            {"name": "cold water", "quantity": 3, "unit": "tbsp"},
            {"name": "salt", "quantity": 0.5, "unit": "tsp"},
        ],
        "steps": [
            "Blend chickpeas, tahini, lemon juice, garlic, olive oil, and salt.",
            "Add cold water a little at a time until smooth and creamy.",
            "Taste and adjust lemon and salt. Refrigerate promptly and serve chilled or cool."
        ],
        "video_search": "https://www.youtube.com/results?search_query=traditional+hummus+recipe",
    },
    {
        "id": "french-vegetable-ratatouille", "name": "Vegetable Ratatouille", "emoji": "🥘", "cuisine": "French",
        "description": "A rustic stew of summer vegetables, tomato, and herbs.",
        "difficulty": "Medium", "servings": 3, "prep_minutes": 15, "cook_minutes": 35,
        "diet": ["Vegetarian", "Vegan", "Gluten-free"],
        "ingredients": [
            {"name": "aubergine, cubed", "quantity": 250, "unit": "g"},
            {"name": "courgette, cubed", "quantity": 250, "unit": "g"},
            {"name": "bell pepper, chopped", "quantity": 1, "unit": "piece"},
            {"name": "tomatoes, chopped", "quantity": 300, "unit": "g"},
            {"name": "onion, chopped", "quantity": 1, "unit": "small"},
            {"name": "olive oil", "quantity": 2, "unit": "tbsp"},
            {"name": "dried thyme", "quantity": 0.5, "unit": "tsp"},
        ],
        "steps": [
            "Heat half the oil in a large pan and brown the aubergine in batches; set aside.",
            "Add remaining oil and cook onion and pepper until softened.",
            "Add courgette, tomatoes, thyme, and the aubergine. Stir gently.",
            "Cover partially and simmer for 25–35 minutes, stirring occasionally, until vegetables are tender.",
            "Season to taste and serve warm."
        ],
        "video_search": "https://www.youtube.com/results?search_query=French+ratatouille+recipe",
    },
    {
        "id": "ethiopian-inspired-red-lentil-stew", "name": "Spiced Red Lentil Stew", "emoji": "🥣", "cuisine": "Ethiopian-inspired",
        "description": "A warming red lentil stew with aromatics and spice; a home adaptation.",
        "difficulty": "Easy", "servings": 3, "prep_minutes": 10, "cook_minutes": 30,
        "diet": ["Vegetarian", "Vegan", "Gluten-free"],
        "ingredients": [
            {"name": "red lentils, rinsed", "quantity": 200, "unit": "g"},
            {"name": "onion, finely chopped", "quantity": 1, "unit": "medium"},
            {"name": "tomato paste", "quantity": 1, "unit": "tbsp"},
            {"name": "garlic, minced", "quantity": 2, "unit": "clove"},
            {"name": "paprika", "quantity": 1, "unit": "tsp"},
            {"name": "ground cumin", "quantity": 0.5, "unit": "tsp"},
            {"name": "water or vegetable stock", "quantity": 700, "unit": "ml"},
            {"name": "oil", "quantity": 1, "unit": "tbsp"},
        ],
        "steps": [
            "Cook onion in oil over medium heat until soft.",
            "Add garlic, tomato paste, paprika, and cumin; stir for 1 minute.",
            "Add rinsed lentils and water or stock. Bring to a boil, then reduce to a simmer.",
            "Cook for 20–25 minutes, stirring occasionally, until lentils are soft; add water if needed.",
            "Season to taste and serve with rice or flatbread."
        ],
        "video_search": "https://www.youtube.com/results?search_query=Ethiopian+red+lentil+stew+recipe",
    },
    {
        "id": "american-pancakes", "name": "Fluffy Pancakes", "emoji": "🥞", "cuisine": "American",
        "description": "Soft breakfast pancakes made from a simple batter.",
        "difficulty": "Easy", "servings": 2, "prep_minutes": 10, "cook_minutes": 15,
        "diet": ["Vegetarian"],
        "ingredients": [
            {"name": "plain flour", "quantity": 125, "unit": "g"},
            {"name": "milk", "quantity": 180, "unit": "ml"},
            {"name": "egg", "quantity": 1, "unit": "piece"},
            {"name": "baking powder", "quantity": 1.5, "unit": "tsp"},
            {"name": "sugar", "quantity": 1, "unit": "tbsp"},
            {"name": "melted butter or oil", "quantity": 1, "unit": "tbsp"},
        ],
        "steps": [
            "Whisk flour, baking powder, and sugar in a bowl.",
            "In another bowl, whisk milk, egg, and melted butter or oil.",
            "Combine wet and dry ingredients just until mixed; a few small lumps are fine.",
            "Cook small portions on a lightly greased pan over medium heat. Flip when bubbles appear and edges look set.",
            "Cook the other side until golden and cooked through. Serve with preferred toppings."
        ],
        "video_search": "https://www.youtube.com/results?search_query=fluffy+American+pancakes+recipe",
    },
    {
        "id": "korean-vegetable-bibimbap", "name": "Vegetable Bibimbap Bowl", "emoji": "🥗", "cuisine": "Korean-inspired",
        "description": "Rice topped with separate seasoned vegetables and a flavorful sauce.",
        "difficulty": "Medium", "servings": 2, "prep_minutes": 20, "cook_minutes": 15,
        "diet": ["Vegetarian"],
        "ingredients": [
            {"name": "cooked rice", "quantity": 350, "unit": "g"},
            {"name": "carrot, cut into thin strips", "quantity": 1, "unit": "medium"},
            {"name": "spinach", "quantity": 100, "unit": "g"},
            {"name": "mushrooms, sliced", "quantity": 100, "unit": "g"},
            {"name": "soy sauce", "quantity": 1, "unit": "tbsp"},
            {"name": "sesame oil", "quantity": 1, "unit": "tsp"},
            {"name": "gochujang or another chili paste", "quantity": 1, "unit": "tbsp"},
        ],
        "steps": [
            "Prepare rice and keep it hot for serving.",
            "Cook carrot and mushrooms separately in a lightly oiled pan until tender.",
            "Wilt spinach, then season it lightly. Keep vegetables separate for presentation.",
            "Mix gochujang with a little water and sesame oil; add soy sauce to taste.",
            "Arrange vegetables over rice and serve with sauce. Check condiment labels for allergens and dietary restrictions."
        ],
        "video_search": "https://www.youtube.com/results?search_query=vegetable+bibimbap+recipe",
    },
    {
        "id": "greek-village-salad", "name": "Greek Village Salad", "emoji": "🥒", "cuisine": "Greek",
        "description": "A fresh salad with tomato, cucumber, olives, and feta.",
        "difficulty": "Easy", "servings": 2, "prep_minutes": 15, "cook_minutes": 0,
        "diet": ["Vegetarian", "Gluten-free"],
        "ingredients": [
            {"name": "tomatoes, cut into wedges", "quantity": 2, "unit": "medium"},
            {"name": "cucumber, sliced", "quantity": 1, "unit": "medium"},
            {"name": "red onion, thinly sliced", "quantity": 0.25, "unit": "piece"},
            {"name": "feta cheese", "quantity": 100, "unit": "g"},
            {"name": "olives", "quantity": 50, "unit": "g"},
            {"name": "olive oil", "quantity": 1, "unit": "tbsp"},
            {"name": "dried oregano", "quantity": 0.5, "unit": "tsp"},
        ],
        "steps": [
            "Cut the vegetables and place them in a serving bowl.",
            "Add olives and crumble or place feta on top.",
            "Drizzle with olive oil and sprinkle with oregano. Toss gently just before serving."
        ],
        "video_search": "https://www.youtube.com/results?search_query=Greek+village+salad+recipe",
    },
]


def _clean_text(value: Any, default: str = "") -> str:
    if value is None:
        return default
    return str(value).strip() or default


def normalize_recipe(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Validate and normalize model-generated recipe data before showing it."""
    if not isinstance(recipe, dict):
        raise ValueError("Recipe must be an object.")
    name = _clean_text(recipe.get("name"), "AI-created recipe")
    ingredients_in = recipe.get("ingredients", [])
    steps_in = recipe.get("steps", [])
    if not isinstance(ingredients_in, list) or not ingredients_in:
        raise ValueError("The generated recipe did not include an ingredient list. Please try again.")
    if not isinstance(steps_in, list) or not steps_in:
        raise ValueError("The generated recipe did not include cooking steps. Please try again.")

    ingredients = []
    for item in ingredients_in:
        if not isinstance(item, dict) or not _clean_text(item.get("name")):
            continue
        quantity = item.get("quantity", "")
        if isinstance(quantity, bool) or not isinstance(quantity, (int, float, str)):
            quantity = ""
        unit = _clean_text(item.get("unit"))
        ingredients.append({
            "name": _clean_text(item.get("name")),
            "quantity": quantity,
            "unit": unit,
        })
    steps = [_clean_text(s) for s in steps_in if _clean_text(s)]
    if not ingredients or not steps:
        raise ValueError("The generated recipe is incomplete. Please try again.")

    servings = _safe_int(recipe.get("servings"), 2, 1, 50)
    prep = _safe_int(recipe.get("prep_minutes"), 10, 0, 1440)
    cook = _safe_int(recipe.get("cook_minutes"), 20, 0, 1440)
    video = _clean_text(recipe.get("video_search"))
    if not video.startswith("https://www.youtube.com/"):
        video = "https://www.youtube.com/results?search_query=" + re.sub(r"\s+", "+", name)
    normalized = {
        "id": "generated-" + re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:50],
        "name": name,
        "emoji": _clean_text(recipe.get("emoji"), "🍲"),
        "cuisine": _clean_text(recipe.get("cuisine"), "Global"),
        "description": _clean_text(recipe.get("description"), "A personalized recipe draft."),
        "difficulty": _clean_text(recipe.get("difficulty"), "Easy"),
        "servings": servings,
        "prep_minutes": prep,
        "cook_minutes": cook,
        "diet": [],
        "ingredients": ingredients,
        "steps": steps,
        "video_search": video,
    }
    return normalized


def _safe_int(value: Any, default: int, low: int, high: int) -> int:
    try:
        result = int(float(value))
        return max(low, min(high, result))
    except (TypeError, ValueError, OverflowError):
        return default


def _format_number(number: Any) -> str:
    if isinstance(number, bool):
        return str(number)
    if isinstance(number, (int, float)):
        if abs(number - round(number)) < 1e-8:
            return str(int(round(number)))
        return f"{number:.2f}".rstrip("0").rstrip(".")
    return str(number)


def scale_recipe(recipe: Dict[str, Any], servings: int) -> Dict[str, Any]:
    """Scale numeric ingredient quantities proportionally."""
    result = deepcopy(recipe)
    base_servings = max(1, _safe_int(recipe.get("servings"), 1, 1, 1000))
    target_servings = max(1, _safe_int(servings, base_servings, 1, 50))
    factor = target_servings / base_servings
    result["servings"] = target_servings
    scaled = []
    for item in recipe.get("ingredients", []):
        new_item = deepcopy(item)
        qty = item.get("quantity")
        try:
            if isinstance(qty, bool):
                raise ValueError
            amount = float(qty) * factor
            new_item["quantity"] = _format_number(amount)
        except (TypeError, ValueError):
            new_item["quantity"] = _clean_text(qty)
        scaled.append(new_item)
    result["ingredients"] = scaled
    return result


def search_recipes(query: str = "", cuisine: str = "All", diet: str = "Any") -> List[Dict[str, Any]]:
    query = (query or "").strip().lower()
    found = []
    for recipe in RECIPE_CATALOG:
        if cuisine != "All" and recipe["cuisine"] != cuisine:
            continue
        if diet != "Any" and diet not in recipe.get("diet", []):
            continue
        searchable = " ".join([
            recipe["name"], recipe["cuisine"], recipe["description"],
            " ".join(item["name"] for item in recipe["ingredients"]),
        ]).lower()
        if query and query not in searchable:
            continue
        found.append(recipe)
    return found


def get_recipe(recipe_id: str) -> Dict[str, Any]:
    for recipe in RECIPE_CATALOG:
        if recipe["id"] == recipe_id:
            return recipe
    raise KeyError(f"Recipe not found: {recipe_id}")


def all_recipe_names() -> List[str]:
    return [recipe["name"] for recipe in RECIPE_CATALOG]


def _empty_progress() -> Dict[str, Any]:
    return {"history": [], "total_cooked": 0, "unique_dishes": [], "cuisines": []}


def get_progress() -> Dict[str, Any]:
    if not os.path.exists(PROGRESS_FILE):
        return _empty_progress()
    try:
        with open(PROGRESS_FILE, "r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            return _empty_progress()
        data.setdefault("history", [])
        data.setdefault("total_cooked", len(data["history"]))
        data.setdefault("unique_dishes", [])
        data.setdefault("cuisines", [])
        return data
    except (OSError, json.JSONDecodeError):
        return _empty_progress()


def _write_progress(data: Dict[str, Any]) -> None:
    temp_file = PROGRESS_FILE + ".tmp"
    with open(temp_file, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)
    os.replace(temp_file, PROGRESS_FILE)


def add_cooked_dish(recipe: Dict[str, Any], servings: int, rating: int = 0, notes: str = "") -> None:
    progress = get_progress()
    entry = {
        "id": _clean_text(recipe.get("id"), "custom-dish"),
        "name": _clean_text(recipe.get("name"), "Untitled dish"),
        "cuisine": _clean_text(recipe.get("cuisine"), "Global"),
        "servings": _safe_int(servings, 1, 1, 50),
        "rating": _safe_int(rating, 0, 0, 5),
        "notes": _clean_text(notes)[:1000],
        "date": date.today().isoformat(),
    }
    progress["history"].append(entry)
    progress["total_cooked"] = len(progress["history"])
    if entry["name"] not in progress["unique_dishes"]:
        progress["unique_dishes"].append(entry["name"])
    if entry["cuisine"] not in progress["cuisines"]:
        progress["cuisines"].append(entry["cuisine"])
    _write_progress(progress)


def save_rating(recipe_name: str, rating: int) -> None:
    """Reserved for future rating edits; ratings are currently saved when a dish is logged."""
    progress = get_progress()
    for entry in reversed(progress["history"]):
        if entry.get("name") == recipe_name:
            entry["rating"] = _safe_int(rating, 0, 0, 5)
            break
    _write_progress(progress)
