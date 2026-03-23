"""
HostFlow Agent Backend — FastAPI Server
Accepts POST /chat from the Next.js admin portal and runs the ADK agent pipeline.
"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types
from agents.root_agent import create_root_agent

load_dotenv()


# --- Request / Response Models ---
class ChatRequest(BaseModel):
    room_context: dict          # Full room object from Supabase
    message: str                # Guest's current message
    session_id: str             # Unique session ID per guest chat


class ChatResponse(BaseModel):
    response: str
    success: bool


# --- ADK Session Service (in-memory for now) ---
session_service = InMemorySessionService()
APP_NAME = "hostflow-concierge"


# --- FastAPI App ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("✅ HostFlow Agent Backend starting up...")
    yield
    print("🔴 HostFlow Agent Backend shutting down.")


app = FastAPI(title="HostFlow Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Lock this down to your Cloud Run URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint for Cloud Run."""
    return {"status": "ok"}


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    """
    Main chat endpoint. Receives room context + guest message,
    runs the ADK multi-agent pipeline, and returns the response.
    """
    try:
        # Dynamically build the root agent with the room's context
        root_agent = create_root_agent(req.room_context)

        # Create or reuse a session for this guest
        try:
            # Always try creating first
            session = await session_service.create_session(
                app_name=APP_NAME,
                user_id=req.session_id,
                session_id=req.session_id,
            )
        except Exception as e:
            # If it already exists, just get it
            if "already exists" in str(e).lower():
                session = await session_service.get_session(
                    app_name=APP_NAME,
                    user_id=req.session_id,
                    session_id=req.session_id,
                )
            else:
                # Rethrow if it's a different error
                raise e

        runner = Runner(
            agent=root_agent,
            app_name=APP_NAME,
            session_service=session_service,
        )

        # Run the agent pipeline
        user_message = genai_types.Content(
            role="user",
            parts=[genai_types.Part(text=req.message)]
        )

        final_response = ""
        async for event in runner.run_async(
            user_id=req.session_id,
            session_id=req.session_id,
            new_message=user_message,
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response = event.content.parts[0].text
                break

        return ChatResponse(response=final_response, success=True)

    except Exception as e:
        print(f"[Agent Error]: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
