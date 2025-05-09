# Chrome Extension: YouTube RAG Chatbot

This is a Vite React app for a Chrome extension side panel that communicates with a Python FastAPI backend to answer questions about YouTube videos using Retrieval-Augmented Generation (RAG).

## Features
- Detects YouTube video URL from the current tab
- Sends video URL to backend for transcript processing
- Chat UI for asking questions about the video
- Displays answers from the backend

## Development
1. Run the FastAPI backend (`backend.py`) with Uvicorn:
   ```powershell
   uvicorn backend:app --reload
   ```
2. Start the React app for development:
   ```powershell
   npm run dev
   ```
3. Load the extension in Chrome (side panel points to `/panel/index.html` in production build).

## Build
```powershell
npm run build
```

## Folder Structure
- `manifest.json`, `background.js`, `content.js`: Chrome extension logic
- `/panel`: Vite React app for the side panel

# React + Vite

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Babel](https://babeljs.io/) for Fast Refresh
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/) for Fast Refresh

## Expanding the ESLint configuration

If you are developing a production application, we recommend using TypeScript with type-aware lint rules enabled. Check out the [TS template](https://github.com/vitejs/vite/tree/main/packages/create-vite/template-react-ts) for information on how to integrate TypeScript and [`typescript-eslint`](https://typescript-eslint.io) in your project.
