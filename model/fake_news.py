import os
import traceback
from pathlib import Path
from typing import List, TypedDict
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, START, END

load_dotenv()

if not os.environ.get("GROQ_API_KEY"):
    print("\n❌ CONFIGURATION ERROR: GROQ_API_KEY is missing from environment variables!")

app = FastAPI(
    title="AI Multi-Agent News Detection Web App", 
    description="Debug edition using Groq LLM infrastructure."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewsInput(BaseModel):
    article_text: str

class VerdictSchema(BaseModel):
    veracity_score: float = Field(..., description="Confidence rating from 0.0 to 1.0.")
    justification: str = Field(..., description="Synthesis justification summary.")
    red_flags: List[str] = Field(..., description="List of logical or style issues found.")


class AgentState(TypedDict):
    article_text: str
    research_report: str
    style_report: str
    final_verdict: VerdictSchema | None 

llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


async def research_agent(state: AgentState) -> dict:
    text = state["article_text"]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an elite investigative journalist. Analyze if these claims lack primary sources or contradict logical reality."),
        ("user", "Analyze claims:\n\n{text}")
    ])
    response = await llm.ainvoke(prompt.format_messages(text=text))
    return {"research_report": response.content}

async def style_agent(state: AgentState) -> dict:
    text = state["article_text"]
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a linguistic analyst. Evaluate the text for clickbait syntax, emotional profiling, and extreme bias."),
        ("user", "Analyze style:\n\n{text}")
    ])
    response = await llm.ainvoke(prompt.format_messages(text=text))
    return {"style_report": response.content}

async def judge_agent(state: AgentState) -> dict:
    text = state["article_text"]
    research = state["research_report"]
    style = state["style_report"]
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Synthesize findings from Research and Style Specialists to provide a final structured verdict matching the requested schema."),
        ("user", "Text:\n{text}\n\nResearch:\n{research}\n\nStyle:\n{style}")
    ])
    
    structured_llm = llm.with_structured_output(VerdictSchema)
    verdict = await structured_llm.ainvoke(prompt.format_messages(text=text, research=research, style=style))
    return {"final_verdict": verdict}

workflow = StateGraph(AgentState)
workflow.add_node("Researcher", research_agent)
workflow.add_node("Stylist", style_agent)
workflow.add_node("Judge", judge_agent)

workflow.add_edge(START, "Researcher")
workflow.add_edge(START, "Stylist")
workflow.add_edge("Researcher", "Judge")
workflow.add_edge("Stylist", "Judge")
workflow.add_edge("Judge", END)

agent_app = workflow.compile()

@app.post("/api/verify", response_model=VerdictSchema)
async def verify_news(payload: NewsInput):
    if not payload.article_text.strip():
        raise HTTPException(status_code=400, detail="Article text cannot be blank.")
        
    try:
        inputs = {
            "article_text": payload.article_text,
            "research_report": "",
            "style_report": "",
            "final_verdict": None
        }
        
        graph_output = await agent_app.ainvoke(inputs)
        return graph_output["final_verdict"]
        
    except Exception as e:
        print("\n" + "="*60)
        print("🚨 CRITICAL BACKEND CRASH INTERCEPTED 🚨")
        print("="*60)
        traceback.print_exc()
        print("="*60 + "\n")
        
        raise HTTPException(status_code=500, detail=f"Internal Crash: {str(e)}")

current_dir = Path(__file__).parent
static_dir_path = current_dir / "static"

if not static_dir_path.exists():
    static_dir_path = current_dir.parent / "static"

if not static_dir_path.exists():
    raise RuntimeError(f"❌ CRITICAL ERROR: Could not locate 'static/' folder at {static_dir_path}")

app.mount("/", StaticFiles(directory=str(static_dir_path), html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("fake_news:app", host="127.0.0.1", port=8000, reload=True)