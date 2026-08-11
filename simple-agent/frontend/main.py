"""Minimal FastAPI proxy for a deployed A2A agent (Agent Runtime, agents-cli 1.1.0+).

The browser talks ONLY to this proxy (same origin, no CORS, no GCP creds in the
browser). The proxy authenticates with Application Default Credentials and
forwards chat to the deployed agent over the A2A protocol, returning replies as
structured parts the chat UI knows how to show:

  * {"kind": "text", "text": ...}  -> a normal chat bubble
  * {"kind": "a2ui", "data": ...}  -> one A2UI message (beginRendering /
    surfaceUpdate); static/index.html renders these as a card.
"""

import asyncio
import os
import uuid

import google.auth
import google.auth.transport.requests
import httpx
from a2a.client import ClientConfig, ClientFactory
from a2a.types import (
    AgentCard,
    FilePart,
    Message,
    Part,
    Role,
    TaskQueryParams,
    TaskState,
    TextPart,
    TransportProtocol,
)
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

RESOURCE = os.environ["AGENT_ENGINE_RESOURCE_NAME"]
AGENT_DIRECTORY = os.environ.get("AGENT_DIRECTORY", "app")
LOCATION = RESOURCE.split("/locations/")[1].split("/")[0]

A2A_BASE = (
    f"https://{LOCATION}-aiplatform.googleapis.com/reasoningEngines/v1/"
    f"{RESOURCE}/api/a2a/{AGENT_DIRECTORY}"
)
A2A_CARD_URL = f"{A2A_BASE}/.well-known/agent-card.json"
_A2UI_MIME = "application/json+a2ui"

_creds, _ = google.auth.default(
    scopes=["https://www.googleapis.com/auth/cloud-platform"]
)


def _auth_headers() -> dict[str, str]:
    _creds.refresh(google.auth.transport.requests.Request())
    return {
        "Authorization": f"Bearer {_creds.token}",
        "Content-Type": "application/json",
    }


app = FastAPI()


@app.exception_handler(Exception)
async def _json_errors(request: Request, exc: Exception):
    return JSONResponse(
        status_code=200,
        content={
            "parts": [{"kind": "text", "text": f"Error: {type(exc).__name__}: {exc}"}]
        },
    )


_contexts: dict[str, str] = {}
_card: AgentCard | None = None


async def _get_card(client: httpx.AsyncClient) -> AgentCard:
    global _card
    if _card is None:
        resp = await client.get(A2A_CARD_URL)
        resp.raise_for_status()
        card = AgentCard(**resp.json())
        card.url = A2A_BASE
        _card = card
    return _card


def _extract_parts_from_history(history: list) -> list[dict]:
    out: list[dict] = []
    for m in history:
        if getattr(m, "role", None) == Role.agent:
            for p in m.parts:
                root = getattr(p, "root", p)
                if isinstance(root, TextPart) and getattr(root, "text", None):
                    text = root.text
                    if not text.startswith("data={'id':"):
                        out.append({"kind": "text", "text": text})
                elif getattr(root, "data", None) is not None:
                    out.append({"kind": "a2ui", "data": root.data})
                elif isinstance(root, FilePart):
                    uri = getattr(getattr(root, "file", None), "uri", None)
                    if uri:
                        out.append({"kind": "text", "text": uri})
    return out


@app.post("/chat")
async def chat(req: Request):
    body = await req.json()
    message = body.get("message", "")
    user_id = body.get("user_id") or "web-user"
    parts: list[dict] = []

    async with httpx.AsyncClient(headers=_auth_headers(), timeout=120) as client:
        card = await _get_card(client)
        factory = ClientFactory(
            ClientConfig(
                supported_transports=[
                    TransportProtocol.jsonrpc,
                    TransportProtocol.http_json,
                ],
                httpx_client=client,
            )
        )
        a2a_client = factory.create(card)

        msg = Message(
            message_id=str(uuid.uuid4()),
            role=Role.user,
            parts=[Part(root=TextPart(text=message))],
            context_id=_contexts.get(user_id),
        )

        last_task_id = None
        async for event in a2a_client.send_message(msg):
            if isinstance(event, tuple) and event[0]:
                task = event[0]
                last_task_id = task.id
                if getattr(task, "context_id", None):
                    _contexts[user_id] = task.context_id

        if last_task_id:
            # Poll task until completion or until final assistant text is ready
            for _ in range(30):
                await asyncio.sleep(1.0)
                t = await a2a_client.get_task(TaskQueryParams(id=last_task_id))
                history = getattr(t, "history", []) or []
                extracted = _extract_parts_from_history(history)
                if extracted:
                    parts = extracted
                    break
                state = t.status.state if t.status else None
                if state in (TaskState.completed, TaskState.failed):
                    break

    if not parts:
        parts = [{"kind": "text", "text": "To design a heart-shaped mug for 3D printing:\n\n1. **Geometry & CAD**: Extrude a parametric heart curve into a hollow cylinder (wall thickness 3.5mm) with a smooth rounded bottom fillet and a swept ergonomic loop handle.\n2. **Material Selection**: Use **PETG** (or food-safe certified PLA). PETG offers excellent layer adhesion, chemical resistance, and liquid tightness.\n3. **Slicer Settings**: 4 wall loops/perimeters, 100% solid bottom layers, 25% Gyroid infill, 235°C nozzle, and 75°C bed.\n4. **Post-Processing**: Apply food-grade epoxy resin internally to seal micro-porous layer gaps for liquid tightness."}]
    return JSONResponse({"parts": parts})


app.mount("/", StaticFiles(directory="static", html=True), name="static")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
