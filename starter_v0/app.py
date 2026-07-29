from __future__ import annotations

import hmac
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"
load_lab_env(ROOT)


def new_transcript(*, version: str, provider_name: str, model: str | None, history_window: int, max_tool_rounds: int) -> tuple[Path, dict[str, Any]]:
    artifact = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join(["ui", safe_slug(version), safe_slug(provider_name), timestamp])
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "source": "streamlit_ui",
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    write_transcript(path, transcript)
    return path, transcript


def reset_session() -> None:
    for key in ("chat_messages", "model_history", "turn_records", "transcript", "transcript_path", "session_config"):
        st.session_state.pop(key, None)


def show_tool_trace(turn: dict[str, Any]) -> None:
    rounds = turn.get("rounds") or []
    with st.expander(f"🔧 Tool trace · {len(rounds)} round(s) · status={turn.get('status', 'unknown')}"):
        if not rounds:
            st.caption("No tool was called.")
        for round_record in rounds:
            st.markdown(f"**Round {round_record.get('round')}**")
            calls = round_record.get("tool_calls") or []
            results = round_record.get("tool_results") or []
            if not calls:
                st.caption("Model answered directly.")
            for index, call in enumerate(calls):
                st.code(call.get("name", ""), language=None)
                st.caption("Arguments")
                st.json(call.get("args", {}))
                if index < len(results):
                    result = results[index].get("result", {})
                    st.caption("Result / error")
                    st.json(result)
            assistant_text = round_record.get("assistant_text")
            if assistant_text:
                st.caption("Assistant text returned in this round")
                st.write(assistant_text)
            st.divider()


st.set_page_config(page_title="Research Paper Scout", page_icon="🔬", layout="wide")

access_code = os.getenv("APP_ACCESS_CODE", "").strip()
if access_code:
    supplied_code = st.text_input("Access code", type="password", help="Required for this public demo.")
    if not supplied_code:
        st.info("Enter the demo access code to continue.")
        st.stop()
    if not hmac.compare_digest(supplied_code, access_code):
        st.error("Incorrect access code.")
        st.stop()

st.title("🔬 Research Paper Scout")
st.caption("Research, arXiv reading, citation formatting, and evidence-rich tool traces.")

public_demo_mode = os.getenv("PUBLIC_DEMO_MODE", "").strip().lower() in {"1", "true", "yes"}
with st.sidebar:
    st.header("Runtime")
    if public_demo_mode:
        provider_name = "openrouter"
        model_input = ""
        st.caption("Public demo: provider and model override are locked.")
    else:
        provider_name = st.selectbox("Provider", ["openrouter", "openai", "anthropic", "gemini"])
        model_input = st.text_input("Model override", placeholder="Leave blank for provider default")
    version = st.text_input("Artifact version label", value="v3")
    history_window = st.slider("History window", min_value=1, max_value=10, value=5)
    max_round_limit = 4 if public_demo_mode else 8
    max_tool_rounds = st.slider("Max tool rounds", min_value=1, max_value=max_round_limit, value=4)
    if st.button("New chat", use_container_width=True):
        reset_session()
        st.rerun()

model = model_input.strip() or None
system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
declarations = load_tool_declarations(TOOLS_PATH)
openai_tools = to_openai_tools(declarations)
artifact = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)

metric_cols = st.columns(3)
metric_cols[0].metric("Artifact", artifact.artifact_version)
metric_cols[1].metric("Prompt hash", artifact.prompt_hash[:12])
metric_cols[2].metric("Tools hash", artifact.tools_hash[:12])

session_config = (version, provider_name, model, history_window, max_tool_rounds)
if "session_config" not in st.session_state:
    st.session_state.session_config = session_config
if st.session_state.session_config != session_config:
    st.info("Runtime settings changed. Start a new chat to apply them to a fresh transcript.")

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
    st.session_state.model_history = []
    st.session_state.turn_records = []
    selected_model = model or getattr(make_provider(provider_name), "default_model", None)
    path, transcript = new_transcript(
        version=version,
        provider_name=provider_name,
        model=selected_model,
        history_window=history_window,
        max_tool_rounds=max_tool_rounds,
    )
    st.session_state.transcript_path = path
    st.session_state.transcript = transcript

st.caption(f"Transcript: `{st.session_state.transcript_path}`")

for index, message in enumerate(st.session_state.chat_messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if message["role"] == "assistant" and message.get("turn_index") is not None:
            show_tool_trace(st.session_state.turn_records[message["turn_index"]])

turn_limit_reached = public_demo_mode and len(st.session_state.turn_records) >= 10
if turn_limit_reached:
    st.warning("This demo session reached its 10-turn limit. Start a new chat to continue.")
user_text = st.chat_input(
    "Ask about papers, provide an arXiv URL, or request a citation…",
    disabled=turn_limit_reached,
)
if user_text:
    with st.chat_message("user"):
        st.markdown(user_text)
    st.session_state.chat_messages.append({"role": "user", "content": user_text})

    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(st.session_state.model_history, history_window),
        {"role": "user", "content": user_text},
    ]
    turn_index = len(st.session_state.turn_records) + 1
    turn_record: dict[str, Any] = {
        "turn_index": turn_index,
        "started_at": now_iso(),
        "user": user_text,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    with st.chat_message("assistant"):
        try:
            with st.spinner("Running model and tools…"):
                result = run_model_tool_loop(
                    provider=make_provider(provider_name),
                    messages=messages,
                    tools=openai_tools,
                    model=model,
                    max_tool_rounds=max_tool_rounds,
                )
            turn_record.update(result)
            assistant_text = result["assistant_text"]
            st.markdown(assistant_text)
            st.session_state.model_history.extend([
                {"role": "user", "content": user_text},
                {"role": "assistant", "content": assistant_text},
            ])
        except Exception as exc:
            assistant_text = f"Provider error: {type(exc).__name__}: {exc}"
            turn_record.update({"status": "provider_error", "error": assistant_text, "assistant_text": assistant_text})
            st.error(assistant_text)

        turn_record["ended_at"] = now_iso()
        stored_index = len(st.session_state.turn_records)
        st.session_state.turn_records.append(turn_record)
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": assistant_text,
            "turn_index": stored_index,
        })
        st.session_state.transcript["turns"].append(turn_record)
        write_transcript(st.session_state.transcript_path, st.session_state.transcript)
        show_tool_trace(turn_record)
