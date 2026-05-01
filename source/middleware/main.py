"""
Numen: Knightfall — Dialogue Middleware

A FastAPI service that mediates between the Unreal client and the local LLM.
The middleware's core responsibility is the knowledge gating architecture:
each NPC has a permitted set of epistemic tiers, and only facts from those
tiers are included in the prompt sent to the LLM. Tier-restricted facts are
structurally absent from the prompt — not present-but-forbidden — which is
the central robustness claim of this project.

"""

import json
from pathlib import Path

import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

# -----------------------------------------------------------------------------
# LLM inference endpoint. llama-server runs locally on port 8080, exposing an
# OpenAI-compatible /v1/chat/completions endpoint.
# -----------------------------------------------------------------------------

LLAMA_SERVER_URL = "http://127.0.0.1:8080/v1/chat/completions"
LLAMA_REQUEST_TIMEOUT_SECONDS = 30.0  # generous; typical inference is <1s on RTX 4090

# -----------------------------------------------------------------------------
# Configuration: load world state and NPC profiles from disk on startup.
# -----------------------------------------------------------------------------

BASE_DIR = Path(__file__).parent

with open(BASE_DIR / "world_state.json", "r", encoding="utf-8") as f:
    WORLD_STATE = json.load(f)

with open(BASE_DIR / "npc_profiles.json", "r", encoding="utf-8") as f:
    NPC_PROFILES = json.load(f)


# -----------------------------------------------------------------------------
# Request/response schemas. FastAPI uses these for automatic validation,
# OpenAPI documentation generation, and JSON parsing.
# -----------------------------------------------------------------------------

class DialogueRequest(BaseModel):
    npc_id: str
    utterance: str


class DialogueResponse(BaseModel):
    response: str
    npc_id: str
    debug_prompt: str | None = None  # included so we can inspect what would be sent to the LLM


# -----------------------------------------------------------------------------
# Core gating logic: given an NPC profile and the world state, construct the
# prompt that the LLM would see. Tier-restricted facts are simply not included.
# -----------------------------------------------------------------------------

def construct_prompt(npc_id: str, utterance: str) -> str:
    """
    Build the LLM prompt for this NPC. The structural claim of this project is
    that facts outside the NPC's permitted tiers are *absent from the prompt*,
    not present-but-forbidden. This function enforces that.
    """
    if npc_id not in NPC_PROFILES:
        raise KeyError(f"Unknown NPC: {npc_id}")

    profile = NPC_PROFILES[npc_id]
    permitted_tiers = profile["permitted_tiers"]

    # Gather only the facts from permitted tiers.
    permitted_facts: list[str] = []
    for tier_name in permitted_tiers:
        if tier_name == "tier_0_personal":
            # tier_0 personal facts come from the NPC's own profile, not world_state
            permitted_facts.extend(profile["personal_facts"])
        else:
            tier_data = WORLD_STATE.get(tier_name, {})
            permitted_facts.extend(tier_data.get("facts", []))

    # Build the prompt. Sections separated for readability — the LLM sees this
    # as one continuous string but the structure helps the model parse roles.
    prompt_parts = [
        f"You are {profile['name']}, {profile['rank']} at St. Damson's training institute for knights.",
        "",
        "Speech directives:",
    ]
    for directive in profile["speech_directives"]:
        prompt_parts.append(f"- {directive}")

    prompt_parts.extend([
        "",
        "What you know:",
    ])
    for fact in permitted_facts:
        prompt_parts.append(f"- {fact}")

    prompt_parts.extend([
        "",
        "If the traveller asks about something outside what you know, say honestly that you do not know. Do not invent facts. Do not speculate beyond your knowledge.",
        "",
        "If the traveller mentions a name, place, title, institution, or event that you have not been told about above, treat it as unfamiliar. Do not pretend to recognise it, do not speculate about it, do not invent details. Ask the traveller what they mean, or simply say you have not heard of it. Even if the term sounds plausible for your world, if it is not in what you know, you do not know it.",
        "",
        f"A traveller addresses you: \"{utterance}\"",
        "",
        "Your response (one or two sentences, in character):",
    ])

    return "\n".join(prompt_parts)


def _stub_llm_call(prompt: str, utterance: str) -> str:
    """
    Day 3 stub. Returns a hardcoded response for testing the round-trip.
    Kept in the file for offline testing when llama-server is not running.
    """
    return f"[stub] You said: {utterance}"


async def _call_llama_server(prompt: str) -> str:
    """
    Send the constructed prompt to llama-server and return the model's response.

    Uses the OpenAI-compatible /v1/chat/completions endpoint. The full prompt
    is sent as a single user message — we deliberately do not split into
    system/user roles here, because the gating architecture has already done
    its job by the time the prompt is constructed: tier-restricted facts are
    structurally absent. The LLM's role is generation, not gatekeeping.
    """
    payload = {
        "model": "local",  # llama-server ignores this field; included for OpenAI compat
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.7,
        "max_tokens": 200,
    }

    async with httpx.AsyncClient(timeout=LLAMA_REQUEST_TIMEOUT_SECONDS) as client:
        try:
            llm_response = await client.post(LLAMA_SERVER_URL, json=payload)
            llm_response.raise_for_status()
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=503,
                detail=f"LLM server unreachable: {exc}",
            )
        except httpx.HTTPStatusError as exc:
            raise HTTPException(
                status_code=502,
                detail=f"LLM server returned error: {exc.response.status_code} {exc.response.text}",
            )

    data = llm_response.json()
    try:
        return data["choices"][0]["message"]["content"].strip()
    except (KeyError, IndexError) as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM response malformed: {exc}",
        )


# -----------------------------------------------------------------------------
# FastAPI application and endpoints.
# -----------------------------------------------------------------------------

app = FastAPI(
    title="Numen Dialogue Middleware",
    description="Knowledge-gated LLM NPC dialogue for Numen: Knightfall",
    version="0.1.0",
)


@app.get("/")
def root():
    """Health check / sanity ping."""
    return {
        "service": "Numen Dialogue Middleware",
        "status": "running",
        "npcs_loaded": list(NPC_PROFILES.keys()),
        "world_tiers_loaded": list(WORLD_STATE.keys()),
    }


@app.post("/dialogue", response_model=DialogueResponse)
async def dialogue(request: DialogueRequest):
    """
    Main endpoint. Receives an NPC id and player utterance, returns the NPC's
    response.
    """
    print(f"[REQUEST] npc_id={request.npc_id!r} utterance={request.utterance!r}")

    try:
        prompt = construct_prompt(request.npc_id, request.utterance)
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e))

    response_text = await _call_llama_server(prompt)

    return DialogueResponse(
        response=response_text,
        npc_id=request.npc_id,
        debug_prompt=prompt,  # remove or gate behind a flag before final submission
    )