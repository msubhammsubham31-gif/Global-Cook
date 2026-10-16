# Global Cooking Coach

Discover dishes from around the world, adjust ingredients for your serving size,
get step-by-step cooking guidance, and keep a record of what you've cooked.

## Run locally

Requirements: Python 3.10 or newer and [Ollama](https://ollama.com/download)
for the recipe generator and cooking assistant.

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
ollama pull gemma3:1b
streamlit run main.py
```

Open the local address printed by Streamlit, usually
[`http://localhost:8501`](http://localhost:8501).

To use a different Ollama model or server, set `OLLAMA_MODEL` and
`OLLAMA_BASE_URL` before starting the app, or edit them in the app sidebar.

## Deploy to Render

This repository includes a `render.yaml` Blueprint for a Streamlit web service.

1. Push this repository to GitHub.
2. In the [Render Dashboard](https://dashboard.render.com/), choose **New >
   Blueprint**, connect the GitHub repository, and deploy.
3. Render will build the app and provide its public `onrender.com` URL.

The service can display and search the bundled recipe catalogue without AI.
AI generation and chat require an Ollama server reachable by the Render service;
your computer's `localhost` is not reachable from Render. Configure
`OLLAMA_BASE_URL` and `OLLAMA_MODEL` in the Render service environment if you
have a separately hosted Ollama server. Do not put credentials in this file.

Cooking progress is saved to `progress.json` on the app server. Render's
ephemeral filesystem can lose this data when a service restarts or redeploys,
and the file is not a shared, multi-user database.

## Vercel

Vercel does not run this Streamlit app as a persistent web service. The
included deployment configuration targets Render. Publishing a separate
Vercel frontend would require building a frontend and API integration; that
is not part of this Streamlit starter.

## Project files

- `main.py`: Streamlit interface.
- `model.py`: Ollama/Gemma recipe generation and cooking Q&A.
- `tools.py`: sample recipe catalogue, search, scaling, and local progress.
- `render.yaml`: Render Blueprint deployment configuration.
- `SKILLS.md`: product scope and development guidelines.

The catalogue is a small sample, not an exhaustive collection or a guarantee
of a single authentic recipe. AI-generated recipes are drafts: check
ingredients, allergens, doneness, and food-safety guidance before cooking.
