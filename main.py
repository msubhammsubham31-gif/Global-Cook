"""Global Cooking Coach — Streamlit app.

Run:
    pip install -r requirements.txt
    ollama pull gemma3
    ollama serve          # if Ollama is not already running
    streamlit run main.py
"""
import os

import streamlit as st

from model import CookingAI, OllamaError
from tools import (
    RECIPE_CATALOG,
    add_cooked_dish,
    all_recipe_names,
    get_progress,
    get_recipe,
    normalize_recipe,
    scale_recipe,
    search_recipes,
    save_rating,
)

st.set_page_config(
    page_title="Global Cooking Coach",
    page_icon="🍲",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
      .main .block-container {max-width: 1200px; padding-top: 1.5rem;}
      .hero {padding: 1.5rem; border-radius: 18px; background: linear-gradient(120deg,#fff2df,#fce8e6);}
      .hero h1, .hero p {color: #25251f !important;}
      .hero h1 {margin-bottom: .25rem;}
      .small-muted {color: #666; font-size: .9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

if "ai" not in st.session_state:
    st.session_state.ai = CookingAI(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "gemma3:1b"),
    )

st.markdown(
    """
    <div class="hero">
      <h1>🍲 Global Cooking Coach</h1>
      <p>Discover world cuisines, scale recipes for your people, learn step by step,
      and build your cooking skills with a local AI companion.</p>
    </div>
    """,
    unsafe_allow_html=True,
)
st.write("")

with st.sidebar:
    st.header("⚙️ Settings")
    ollama_url = st.text_input(
        "Ollama server URL",
        value=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
    )
    model_name = st.text_input(
        "Ollama model",
        value=os.getenv("OLLAMA_MODEL", "gemma3:1b"),
    )
    st.session_state.ai.base_url = ollama_url.rstrip("/")
    st.session_state.ai.model = model_name.strip() or "gemma3"
    st.caption("AI features need Ollama running and the selected model downloaded.")
    st.markdown("[Ollama setup guide](https://ollama.com/download)")

    st.divider()
    st.subheader("Your cooking journey")
    progress = get_progress()
    st.metric("Dishes cooked", progress["total_cooked"])
    st.metric("Unique dishes tried", len(progress["unique_dishes"]))
    st.metric("Cuisine types explored", len(progress["cuisines"]))

tab_discover, tab_create, tab_assistant, tab_progress = st.tabs(
    ["🌎 Discover recipes", "✨ Create a recipe", "👩‍🍳 Cooking assistant", "🏆 My progress"]
)

with tab_discover:
    st.subheader("Explore recipes from around the world")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        query = st.text_input("Search dish, ingredient, or cuisine", placeholder="e.g. pasta, chickpeas, Indian")
    with col2:
        cuisine_options = ["All"] + sorted({r["cuisine"] for r in RECIPE_CATALOG})
        selected_cuisine = st.selectbox("Cuisine", cuisine_options)
    with col3:
        diet_options = ["Any", "Vegetarian", "Vegan", "Gluten-free"]
        selected_diet = st.selectbox("Diet preference", diet_options)

    recipes = search_recipes(query, selected_cuisine, selected_diet)
    if not recipes:
        st.info("No matching starter recipes found. Try another search, or use **Create a recipe** to ask Gemma 3.")
    else:
        names = [r["name"] for r in recipes]
        selected_name = st.selectbox("Choose a recipe", names)
        recipe = next(r for r in recipes if r["name"] == selected_name)

        left, right = st.columns([1.25, 1])
        with left:
            st.markdown(f"### {recipe['emoji']} {recipe['name']}")
            st.write(f"**Cuisine:** {recipe['cuisine']} · **Difficulty:** {recipe['difficulty']}")
            st.write(recipe["description"])
            st.write(f"**Prep:** {recipe['prep_minutes']} min · **Cook:** {recipe['cook_minutes']} min")
            servings = st.number_input("How many people are you cooking for?", min_value=1, max_value=50, value=recipe["servings"], step=1)
            scaled = scale_recipe(recipe, int(servings))
            st.markdown("#### Ingredients")
            for item in scaled["ingredients"]:
                st.write(f"- {item['quantity']} {item['unit']} {item['name']}".strip())
            st.caption("Measurements are scaled mathematically. Adjust salt, spices, liquids, and cooking time to taste.")
        with right:
            st.markdown("#### Method")
            for i, step in enumerate(recipe["steps"], start=1):
                st.write(f"**Step {i}.** {step}")
            if recipe.get("video_search"):
                st.link_button("🎬 Find a cooking tutorial video", recipe["video_search"])
            st.caption("Video search links are suggestions, not endorsements or verification of a specific video.")

        st.divider()
        st.markdown("#### Cooked it? Save your progress")
        rating = st.slider("Rate this dish", min_value=1, max_value=5, value=4, key=f"rating_{recipe['id']}")
        notes = st.text_input("Cooking notes (optional)", key=f"notes_{recipe['id']}", placeholder="What worked? What would you change?")
        if st.button("✅ Mark as cooked", key=f"cooked_{recipe['id']}"):
            add_cooked_dish(recipe, int(servings), int(rating), notes)
            st.success(f"Saved! You cooked {recipe['name']} for {servings} people.")
            st.rerun()

with tab_create:
    st.subheader("Create a personalized recipe")
    st.write("Ask Gemma 3 to draft a recipe based on your ingredients, cuisine, time, and preferences.")
    with st.form("recipe_form"):
        dish_prompt = st.text_input("Dish or idea", placeholder="e.g. a quick Korean-inspired tofu bowl")
        ingredients_prompt = st.text_area("Ingredients you have", placeholder="e.g. rice, tofu, carrots, soy sauce")
        cuisine_prompt = st.text_input("Cuisine or region", placeholder="e.g. Mexican, Thai, West African, any")
        servings_prompt = st.number_input("Servings", min_value=1, max_value=50, value=2)
        time_prompt = st.slider("Maximum total time (minutes)", min_value=10, max_value=180, value=45, step=5)
        diet_prompt = st.selectbox("Dietary preference", ["No preference", "Vegetarian", "Vegan", "Gluten-free"])
        create_submitted = st.form_submit_button("✨ Generate recipe")
    if create_submitted:
        if not dish_prompt.strip() and not ingredients_prompt.strip():
            st.warning("Enter a dish idea or at least one ingredient.")
        else:
            with st.spinner("Gemma 3 is drafting your recipe..."):
                try:
                    generated = st.session_state.ai.generate_recipe(
                        dish=dish_prompt.strip() or "A recipe using the supplied ingredients",
                        ingredients=ingredients_prompt.strip(),
                        cuisine=cuisine_prompt.strip() or "Any cuisine",
                        servings=int(servings_prompt),
                        max_minutes=int(time_prompt),
                        diet=diet_prompt,
                    )
                    generated = normalize_recipe(generated)
                    st.session_state.generated_recipe = generated
                except (OllamaError, ValueError) as exc:
                    st.error(str(exc))
    if st.session_state.get("generated_recipe"):
        generated = st.session_state.generated_recipe
        st.markdown(f"### {generated['emoji']} {generated['name']}")
        st.caption(f"{generated['cuisine']} · {generated['prep_minutes']} min prep · {generated['cook_minutes']} min cook · {generated['servings']} servings")
        st.warning("AI-generated recipes may contain mistakes. Check ingredients, allergens, doneness, and food-safety guidance before cooking.")
        st.markdown("#### Ingredients")
        for item in generated["ingredients"]:
            st.write(f"- {item['quantity']} {item['unit']} {item['name']}".strip())
        st.markdown("#### Instructions")
        for i, step in enumerate(generated["steps"], 1):
            st.write(f"**Step {i}.** {step}")
        if generated.get("video_search"):
            st.link_button("🎬 Search for a tutorial video", generated["video_search"])
        if st.button("Save generated dish to my progress"):
            add_cooked_dish(generated, generated["servings"], 0, "Generated recipe saved")
            st.success("Saved to your cooking history.")

with tab_assistant:
    st.subheader("Ask your cooking companion")
    st.write("Ask for substitutions, troubleshooting, technique explanations, or help with the next step.")
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = [
            {"role": "assistant", "content": "Hi! Tell me what you're cooking, what ingredients you have, or what went wrong. I'll help you think through it."}
        ]
    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    user_message = st.chat_input("e.g. My soup is too salty. What can I do?")
    if user_message:
        st.session_state.chat_messages.append({"role": "user", "content": user_message})
        with st.chat_message("user"):
            st.markdown(user_message)
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    answer = st.session_state.ai.ask_cooking_question(
                        user_message,
                        history=st.session_state.chat_messages[-8:],
                    )
                except OllamaError as exc:
                    answer = str(exc)
            st.markdown(answer)
        st.session_state.chat_messages.append({"role": "assistant", "content": answer})
    if st.button("Clear chat"):
        st.session_state.chat_messages = []
        st.rerun()

with tab_progress:
    st.subheader("Your cooking progress")
    progress = get_progress()
    c1, c2, c3 = st.columns(3)
    c1.metric("Cooking sessions", progress["total_cooked"])
    c2.metric("Unique dishes", len(progress["unique_dishes"]))
    c3.metric("Cuisines explored", len(progress["cuisines"]))
    st.markdown("#### Cuisines explored")
    if progress["cuisines"]:
        st.write(" · ".join(progress["cuisines"]))
    else:
        st.info("Cook your first dish to start building your cooking journey.")
    st.markdown("#### Recent cooking history")
    if progress["history"]:
        for entry in reversed(progress["history"][-20:]):
            rating_text = f" · Rating: {entry['rating']}/5" if entry.get("rating") else ""
            st.write(f"- **{entry['name']}** — {entry['servings']} serving(s) · {entry['date']}{rating_text}")
            if entry.get("notes"):
                st.caption(entry["notes"])
    else:
        st.write("No dishes recorded yet.")
    st.caption("Progress is stored locally in progress.json on the machine running this app.")
