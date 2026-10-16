# Global Cooking Coach — Project Skills and Guidelines

## Product goal
Help people learn to cook dishes from different regions, adjust ingredient quantities for different serving counts, follow tutorials, ask cooking questions, and track progress.

## Current capabilities
- Streamlit user interface.
- Starter recipe catalogue containing examples from several cuisines.
- Search by dish, cuisine, or ingredient.
- Vegetarian, vegan, and gluten-free filters for recipes explicitly tagged that way.
- Proportional ingredient scaling.
- Recipe generation and cooking Q&A through Ollama.
- Local progress tracking in `progress.json`.
- Links to YouTube search results for tutorial discovery.

## Important scope note
The included catalogue is a small starter dataset, not every dish in the world and not a guarantee of a single "perfect" or universally authentic recipe. Recipes vary by region, family, ingredient availability, equipment, and taste. Grow the catalogue using tested recipes and appropriately licensed data.

## AI behaviour
- Use Gemma 3 through Ollama for recipe drafts, substitutions, explanations, and troubleshooting.
- Prefer structured recipe data for known recipes.
- Treat model-generated recipes as drafts that require human review.
- Do not invent nutrition figures, health benefits, or claims of authenticity.
- For allergies, clearly surface ingredients and cross-contamination concerns.
- For meat, seafood, eggs, leftovers, and preservation, give conservative food-safety guidance.
- Never claim a recipe or safety instruction is guaranteed.

## Recommended development skills
1. Python fundamentals and virtual environments.
2. Streamlit UI and session state.
3. REST APIs and Ollama's `/api/chat` endpoint.
4. JSON schema validation and data cleaning.
5. Recipe data modelling and unit conversion.
6. Database fundamentals; migrate from local JSON to SQLite/PostgreSQL as the app grows.
7. Testing with `pytest`.
8. Privacy and secure handling of user data.
9. Accessibility and responsive interface design.
10. Copyright-aware use of tutorial videos, images, and recipe datasets.

## Next steps
- Add unit tests for recipe scaling and progress persistence.
- Add a recipe detail page with timers and checkboxes for completed steps.
- Add a proper recipe database with source attribution, tested quantities, allergens, and licensing metadata.
- Replace YouTube search links with videos from sources that permit embedding.
- Add account-based persistence only when needed; do not store passwords in plain text.
- For a public deployment, avoid shared-file write conflicts and move progress data to a database.
