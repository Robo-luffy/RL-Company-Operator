# starX Company Operator 

## Stack
- LLM tool calling: `ChatOpenAI(...).bind_tools(TOOLS)`
- LangGraph: `StateGraph`, `ToolNode`, `tools_condition`
- LangChain RAG: `TextLoader` → `RecursiveCharacterTextSplitter` → `HuggingFaceEmbeddings` → `FAISS` → retriever
- Playwright: browser UI submission and independent verification
- Human approval: write action only after explicit approval in Streamlit
- Streamlit + FastAPI + SQLite: user interface and mock company workspace

## Setup
Python 3.10+ recommended.

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\Activate.ps1
```
macOS/Linux:
```bash
source .venv/bin/activate
```

Install:
```bash
pip install -r requirements.txt
playwright install chromium
```
The first RAG query downloads `sentence-transformers/all-MiniLM-L6-v2` if it is not cached.

## Run
Terminal 1:
```bash
uvicorn company_app:app --reload --port 8000
```
Terminal 2:
```bash
streamlit run app.py
```
Open the Streamlit URL, usually `http://localhost:8501`. The mock website is `http://127.0.0.1:8000`.

## Demo
1. Enter a task and click **Investigate task**.
2. The LLM requests read-only tools through `bind_tools()`.
3. LangGraph routes tool calls through `ToolNode` and loops results back to the model.
4. The policy tool runs the conventional LangChain RAG pipeline.
5. Review the expense and retrieved policy evidence.
6. Click **Approve and submit via browser**.
7. Playwright submits through the website and independently verifies the rendered status.

## Safety
The LLM only receives read tools. The browser write action is invoked only after the human approval button. This is a demo, not production-ready; add authentication, authorization, audit logs, persistent state, tests, and robust error handling before connecting real systems.

## Reset
we have a Reset feature on streamlit UI to bring back default condition of db 
