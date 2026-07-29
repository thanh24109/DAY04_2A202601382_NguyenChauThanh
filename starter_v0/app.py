from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import (
    assistant_tool_message,
    now_iso,
    run_model_tool_loop,
    tool_results_message,
    write_transcript,
)
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version

ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
load_lab_env(ROOT)

st.set_page_config(
    page_title="Research Agent v0",
    page_icon="🔬",
    layout="wide",
)

VERSION_OPTIONS = ["v0", "v1", "v2", "v3"]
PROVIDER_OPTIONS = ["openrouter", "openai", "anthropic", "gemini"]

if "messages" not in st.session_state:
    st.session_state.messages = []
if "transcript" not in st.session_state:
    st.session_state.transcript = None
if "session_started" not in st.session_state:
    st.session_state.session_started = False


def reset_session() -> None:
    st.session_state.messages = []
    st.session_state.transcript = None
    st.session_state.session_started = False


with st.sidebar:
    st.title("🔬 Research Agent")
    st.markdown("---")

    provider_name = st.selectbox("Provider", PROVIDER_OPTIONS, index=0)
    model_name = st.text_input("Model (optional)", placeholder="Leave empty for default")
    version = st.selectbox("Version", VERSION_OPTIONS, index=3)
    max_rounds = st.slider("Max Tool Rounds", min_value=1, max_value=10, value=4)

    st.markdown("---")
    system_prompt_path = st.text_input(
        "System Prompt Path",
        value=str(ARTIFACTS_DIR / "system_prompt.md"),
    )
    tools_path = st.text_input(
        "Tools Path",
        value=str(ARTIFACTS_DIR / "tools.yaml"),
    )

    if st.button("🔄 New Session", type="primary", use_container_width=True):
        reset_session()
        st.rerun()


artifact_info_placeholder = st.empty()


def show_artifact_info(provider_name: str, version: str) -> None:
    try:
        sp_path = Path(str(ARTIFACTS_DIR / "system_prompt.md"))
        tl_path = Path(str(ARTIFACTS_DIR / "tools.yaml"))
        av = build_artifact_version(version, sp_path, tl_path)
        info = artifact_version_dict(av)
        artifact_info_placeholder.markdown(
            f"**Artifact:** `{info['artifact_version']}` &nbsp;|&nbsp; "
            f"**Provider:** `{provider_name}` &nbsp;|&nbsp; "
            f"**Version:** `{version}`"
        )
    except Exception:
        artifact_info_placeholder.markdown(
            f"**Provider:** `{provider_name}` &nbsp;|&nbsp; **Version:** `{version}`"
        )


show_artifact_info(provider_name, version)

st.title("🔬 Research Paper Scout")
st.caption("Research assistant: search papers, news, tweets, and generate citations.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tool_events" in msg and msg["tool_events"]:
            with st.expander("🔧 Tool Trace", expanded=False):
                for event in msg["tool_events"]:
                    tool_name = event.get("tool", "?")
                    args = event.get("args", {})
                    result = event.get("result", {})
                    st.markdown(f"**Tool:** `{tool_name}`")
                    with st.container():
                        st.json(args)
                    if isinstance(result, dict) and result.get("error"):
                        st.error(f"Error: {result['error']}: {result.get('message', '')}")
                    elif isinstance(result, dict) and result.get("markdown"):
                        st.markdown("**Result (preview):**")
                        st.text(result["markdown"][:500])
                    elif isinstance(result, dict) and result.get("items"):
                        st.markdown(f"**Result:** {len(result['items'])} items returned")
                        st.json(result["items"][:3])
                    else:
                        st.json(result)
                    st.divider()
        if "rounds" in msg and msg["rounds"]:
            with st.expander("🔄 Round Details", expanded=False):
                for r in msg["rounds"]:
                    st.markdown(f"**Round {r['round']}**")
                    if r.get("assistant_text"):
                        st.text(r["assistant_text"][:200])
                    for tc in r.get("tool_calls", []):
                        st.markdown(f"- `{tc['name']}({json.dumps(tc['args'], ensure_ascii=False)})`")

if prompt := st.chat_input("Ask me to research papers, news, or find information..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Running tools..."):
            try:
                sp = Path(system_prompt_path).read_text(encoding="utf-8")
                td = load_tool_declarations(Path(tools_path))
                ot = to_openai_tools(td)
                prov = make_provider(provider_name)
                selected_model = model_name or getattr(prov, "default_model", None)

                history = []
                for m in st.session_state.messages[:-1]:
                    if m["role"] in ("user", "assistant"):
                        history.append({"role": m["role"], "content": m["content"]})

                messages = [
                    {"role": "system", "content": sp},
                    *history,
                    {"role": "user", "content": prompt},
                ]

                result = run_model_tool_loop(
                    provider=prov,
                    messages=messages,
                    tools=ot,
                    model=selected_model or None,
                    max_tool_rounds=max_rounds,
                )

                assistant_text = result["assistant_text"]
                rounds = result.get("rounds", [])
                tool_events = result.get("tool_events", [])

                st.markdown(assistant_text)
                if tool_events:
                    with st.expander("🔧 Tool Trace", expanded=True):
                        for event in tool_events:
                            tool_name = event.get("tool", "?")
                            args = event.get("args", {})
                            result_data = event.get("result", {})
                            st.markdown(f"**Tool:** `{tool_name}`")
                            with st.container():
                                st.json(args)
                            if isinstance(result_data, dict) and result_data.get("error"):
                                st.error(f"Error: {result_data['error']}: {result_data.get('message', '')}")
                            elif isinstance(result_data, dict) and result_data.get("markdown"):
                                st.text(result_data["markdown"][:500])
                            elif isinstance(result_data, dict) and result_data.get("items"):
                                st.markdown(f"**Result:** {len(result_data['items'])} items")
                                st.json(result_data["items"][:3])
                            else:
                                st.json(result_data)
                            st.divider()

                st.session_state.messages.append({
                    "role": "assistant",
                    "content": assistant_text,
                    "tool_events": tool_events,
                    "rounds": rounds,
                })

                av = build_artifact_version(version, Path(system_prompt_path), Path(tools_path))
                transcript = {
                    "transcript_id": f"ui_{version}_{provider_name}_{datetime.now().strftime('%Y%m%dT%H%M%S%f')}",
                    **artifact_version_dict(av),
                    "provider": provider_name,
                    "model": selected_model or "",
                    "system_prompt": system_prompt_path,
                    "tools": tools_path,
                    "max_tool_rounds": max_rounds,
                    "created_at": now_iso(),
                    "updated_at": now_iso(),
                    "turns": [{
                        "turn_index": 1,
                        "user": prompt,
                        "status": result.get("status", "answered"),
                        "assistant_text": assistant_text,
                        "rounds": rounds,
                        "tool_events": tool_events,
                    }],
                }
                transcript_dir = ROOT / "transcripts"
                transcript_path = transcript_dir / f"{transcript['transcript_id']}.transcript.json"
                write_transcript(transcript_path, transcript)
                st.caption(f"Transcript saved: `{transcript_path.name}`")

            except Exception as exc:
                st.error(f"Error: {type(exc).__name__}: {str(exc)}")
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": f"Error: {type(exc).__name__}: {str(exc)}",
                })

    show_artifact_info(provider_name, version)
    st.rerun()
