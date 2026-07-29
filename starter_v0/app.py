from __future__ import annotations

import html
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

from chat import now_iso, run_model_tool_loop, safe_slug, trim_history, write_transcript
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import artifact_version_dict, build_artifact_version


ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
SYSTEM_PROMPT_PATH = ARTIFACTS_DIR / "system_prompt.md"
TOOLS_PATH = ARTIFACTS_DIR / "tools.yaml"
TRANSCRIPTS_DIR = ROOT / "transcripts"

PROVIDERS = ("openrouter", "openai", "gemini", "anthropic")
VERSIONS = ("v0", "v1", "v2", "v3")
PROVIDER_ENV = {
    "openrouter": "OPENROUTER_API_KEY",
    "openai": "OPENAI_API_KEY",
    "gemini": "GEMINI_API_KEY",
    "anthropic": "ANTHROPIC_API_KEY",
}
SAMPLE_PROMPTS = (
    "Tìm 5 bài báo mới nhất về Retrieval-Augmented Generation.",
    "Đọc và tóm tắt bài báo https://arxiv.org/abs/1706.03762 thành 5 ý chính.",
    "Tìm các paper nền tảng về AI agent, rồi tạo một research digest có trích nguồn.",
)


st.set_page_config(
    page_title="Paper Scout — AI Research Desk",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Libre+Franklin:wght@400;500;600;700&family=Newsreader:ital,opsz,wght@0,6..72,500;1,6..72,500&display=swap');

        :root {
            --paper: #f4f0e6;
            --paper-deep: #e9e1d2;
            --ink: #201c14;
            --muted: #6d665a;
            --rule: #cfc4b2;
            --red: #b63820;
            --blue: #315c79;
            --white: #fbf9f2;
        }
        .stApp {
            background: var(--paper);
            color: var(--ink);
            font-family: 'Libre Franklin', sans-serif;
        }
        .stApp::before {
            content: "";
            position: fixed;
            inset: 0;
            pointer-events: none;
            opacity: .28;
            background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 180 180' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='.9' numOctaves='2' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='.05'/%3E%3C/svg%3E");
        }
        [data-testid="stHeader"] { background: rgba(244,240,230,.88); }
        [data-testid="stSidebar"] {
            background: #e9e1d2;
            border-right: 1px solid var(--ink);
        }
        [data-testid="stSidebar"] * { color: var(--ink); }
        [data-testid="stSidebar"] hr { border-color: var(--rule); }
        .block-container { max-width: 1120px; padding-top: 2.2rem; padding-bottom: 7rem; }

        .brand-lockup {
            font-family: 'DM Mono', monospace;
            letter-spacing: .12em;
            font-size: .74rem;
            text-transform: uppercase;
            margin-bottom: 1.35rem;
        }
        .brand-mark {
            display: inline-grid;
            place-items: center;
            width: 2rem;
            height: 2rem;
            margin-right: .7rem;
            color: var(--paper);
            background: var(--red);
            border: 1px solid var(--ink);
            font-weight: 700;
        }
        .eyebrow {
            color: var(--red);
            font-family: 'DM Mono', monospace;
            font-size: .72rem;
            font-weight: 500;
            letter-spacing: .22em;
            text-transform: uppercase;
            margin: .75rem 0 .65rem;
        }
        .hero-title {
            font-family: 'Newsreader', Georgia, serif;
            font-size: clamp(3.2rem, 7vw, 6.4rem);
            line-height: .86;
            letter-spacing: -.055em;
            max-width: 880px;
            margin: 0;
        }
        .hero-title em { color: var(--red); font-weight: 500; }
        .hero-copy {
            max-width: 710px;
            color: var(--muted);
            font-size: 1rem;
            line-height: 1.75;
            margin: 1.35rem 0 1.2rem;
        }
        .rule-double { border-top: 1px solid var(--ink); border-bottom: 1px solid var(--ink); height: 5px; margin: 1.45rem 0; }
        .artifact-row { display: flex; flex-wrap: wrap; gap: .45rem; margin: .8rem 0 1.1rem; }
        .artifact-badge {
            border: 1px solid var(--rule);
            background: rgba(251,249,242,.7);
            padding: .38rem .55rem;
            font-family: 'DM Mono', monospace;
            font-size: .67rem;
            letter-spacing: .03em;
        }
        .artifact-badge strong { color: var(--red); font-weight: 500; }
        .section-label {
            font-family: 'DM Mono', monospace;
            font-size: .72rem;
            letter-spacing: .16em;
            text-transform: uppercase;
            border-bottom: 1px solid var(--ink);
            padding-bottom: .55rem;
            margin: 1.4rem 0 .8rem;
        }
        .empty-desk {
            border: 1px solid var(--rule);
            background: rgba(251,249,242,.5);
            padding: 1.15rem 1.3rem;
            color: var(--muted);
            line-height: 1.65;
        }
        [data-testid="stChatMessage"] {
            background: rgba(251,249,242,.72);
            border: 1px solid var(--rule);
            border-radius: 0;
            margin: .7rem 0;
            padding: .45rem .7rem;
            box-shadow: 4px 4px 0 rgba(32,28,20,.05);
        }
        [data-testid="stChatMessage"] p { line-height: 1.68; }
        [data-testid="stChatInput"] { border-radius: 0; border-color: var(--ink); background: var(--white); }
        [data-testid="stChatInput"]:focus-within { box-shadow: 0 0 0 2px rgba(182,56,32,.22); }
        .stButton > button {
            border-radius: 0;
            border: 1px solid var(--ink);
            background: transparent;
            color: var(--ink);
            min-height: 2.65rem;
            font-weight: 600;
            transition: background .15s ease, color .15s ease, transform .15s ease;
        }
        .stButton > button:hover { background: var(--ink); color: var(--paper); transform: translateY(-1px); }
        [data-testid="stExpander"] { border: 1px solid var(--rule); border-radius: 0; background: rgba(251,249,242,.5); }
        .trace-meta { font-family: 'DM Mono', monospace; font-size: .7rem; color: var(--muted); }
        .status-ready, .status-missing {
            display: inline-block;
            padding: .22rem .42rem;
            border: 1px solid currentColor;
            font: .66rem 'DM Mono', monospace;
            text-transform: uppercase;
        }
        .status-ready { color: #35623e; }
        .status-missing { color: var(--red); }
        div[data-baseweb="select"] > div, .stTextInput input, .stNumberInput input { border-radius: 0 !important; }
        @media (max-width: 740px) {
            .block-container { padding: 1.2rem 1rem 7rem; }
            .hero-title { font-size: 3.3rem; }
            .hero-copy { font-size: .92rem; }
            [data-testid="stSidebar"] { min-width: 290px; }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


@st.cache_data(show_spinner=False)
def load_agent_artifacts(prompt_mtime: int, tools_mtime: int) -> tuple[str, list[dict[str, Any]]]:
    del prompt_mtime, tools_mtime
    system_prompt = SYSTEM_PROMPT_PATH.read_text(encoding="utf-8")
    declarations = load_tool_declarations(TOOLS_PATH)
    return system_prompt, to_openai_tools(declarations)


def init_state() -> None:
    defaults: dict[str, Any] = {
        "chat_messages": [],
        "transcript": None,
        "transcript_path": None,
        "session_signature": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def clear_session() -> None:
    st.session_state.chat_messages = []
    st.session_state.transcript = None
    st.session_state.transcript_path = None
    st.session_state.session_signature = None


def make_transcript(
    provider_name: str,
    selected_model: str,
    version: str,
    history_window: int,
    max_tool_rounds: int,
    artifact: Any,
) -> tuple[dict[str, Any], Path]:
    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S%f")
    transcript_id = "_".join((safe_slug(version), safe_slug(provider_name), timestamp))
    path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
    transcript = {
        "transcript_id": transcript_id,
        **artifact_version_dict(artifact),
        "provider": provider_name,
        "model": selected_model,
        "system_prompt": str(SYSTEM_PROMPT_PATH),
        "tools": str(TOOLS_PATH),
        "history_window": history_window,
        "max_tool_rounds": max_tool_rounds,
        "created_at": now_iso(),
        "updated_at": now_iso(),
        "turns": [],
    }
    return transcript, path


def get_or_create_transcript(
    signature: tuple[Any, ...],
    provider_name: str,
    selected_model: str,
    version: str,
    history_window: int,
    max_tool_rounds: int,
    artifact: Any,
) -> tuple[dict[str, Any], Path]:
    if st.session_state.transcript is None or st.session_state.session_signature != signature:
        transcript, path = make_transcript(
            provider_name,
            selected_model,
            version,
            history_window,
            max_tool_rounds,
            artifact,
        )
        st.session_state.transcript = transcript
        st.session_state.transcript_path = path
        st.session_state.session_signature = signature
    return st.session_state.transcript, st.session_state.transcript_path


def render_tool_trace(result: dict[str, Any]) -> None:
    rounds = result.get("rounds", [])
    events = result.get("tool_events", [])
    label = f"🔧 Tool Trace · {len(events)} call{'s' if len(events) != 1 else ''} · {result.get('status', 'unknown')}"
    with st.expander(label, expanded=False):
        if not rounds:
            st.caption("Không có tool round được ghi nhận.")
            return
        for round_item in rounds:
            calls = round_item.get("tool_calls", [])
            tool_results = round_item.get("tool_results", [])
            round_number = round_item.get("round", "?")
            round_status = "answer" if not calls else "completed"
            st.markdown(f"**Round {round_number}** · `{round_status}`")
            if round_item.get("assistant_text"):
                st.caption(f"Model note: {round_item['assistant_text']}")
            if not calls:
                st.caption("Model trả lời trực tiếp, không gọi tool trong round này.")
            for index, call in enumerate(calls):
                event = tool_results[index] if index < len(tool_results) else {}
                event_result = event.get("result", {})
                has_error = isinstance(event_result, dict) and bool(event_result.get("error"))
                status = "error" if has_error else "success"
                st.markdown(f"**{index + 1}. `{call.get('name', 'unknown')}`** · `{status}`")
                left, right = st.columns(2)
                with left:
                    st.caption("Arguments")
                    st.json(call.get("args", {}), expanded=True)
                with right:
                    st.caption("Result / Error")
                    st.json(event_result if event else {"error": "missing_tool_result"}, expanded=True)
            if round_item is not rounds[-1]:
                st.divider()
        st.caption(f"Final status: {result.get('status', 'unknown')} · Total events: {len(events)}")


def render_message(message: dict[str, Any]) -> None:
    with st.chat_message(message["role"], avatar="🔬" if message["role"] == "assistant" else "👤"):
        st.markdown(message["content"])
        if message.get("error"):
            st.error(message["error"], icon="⚠️")
        if message.get("result"):
            render_tool_trace(message["result"])


inject_styles()
init_state()

try:
    system_prompt, openai_tools = load_agent_artifacts(
        SYSTEM_PROMPT_PATH.stat().st_mtime_ns,
        TOOLS_PATH.stat().st_mtime_ns,
    )
except Exception as exc:
    st.error(f"Không thể nạp agent artifacts: {type(exc).__name__}: {exc}")
    st.stop()

with st.sidebar:
    st.markdown('<div class="brand-lockup"><span class="brand-mark">PS</span>Paper Scout</div>', unsafe_allow_html=True)
    st.markdown("### Research console")
    provider_name = st.selectbox("Provider", PROVIDERS, index=0, help="API provider dùng cho phiên chat này.")
    provider = make_provider(provider_name)
    default_model = getattr(provider, "default_model", "")
    model_input = st.text_input(
        "Model",
        value="",
        placeholder=default_model,
        help="Để trống để dùng model mặc định hiển thị bên dưới.",
    ).strip()
    selected_model = model_input or default_model
    st.caption(f"Default: `{default_model}`")
    version = st.selectbox("Artifact version", VERSIONS, index=3)
    max_tool_rounds = st.slider("Max tool rounds", min_value=1, max_value=8, value=4)
    history_window = st.slider("History window", min_value=1, max_value=10, value=5, help="Số cặp hội thoại gần nhất gửi lại cho model.")
    st.divider()
    env_name = PROVIDER_ENV[provider_name]
    key_ready = bool(os.getenv(env_name))
    key_class = "status-ready" if key_ready else "status-missing"
    key_text = "API key ready" if key_ready else f"Missing {env_name}"
    st.markdown(f'<span class="{key_class}">{key_text}</span>', unsafe_allow_html=True)
    st.caption("API key chỉ được đọc từ `.env`; giao diện không hiển thị hoặc lưu giá trị bí mật.")
    if st.button("New research session", use_container_width=True):
        clear_session()
        st.rerun()
    if st.session_state.transcript_path:
        st.caption(f"Transcript: `{Path(st.session_state.transcript_path).name}`")

artifact = build_artifact_version(version, SYSTEM_PROMPT_PATH, TOOLS_PATH)
safe_selected_model = html.escape(selected_model)
current_signature = (
    provider_name,
    selected_model,
    version,
    history_window,
    max_tool_rounds,
    artifact.artifact_version,
)
if st.session_state.session_signature and st.session_state.session_signature != current_signature:
    clear_session()
    st.info("Cấu hình agent đã thay đổi. Paper Scout đã mở một research session mới; transcript cũ vẫn được giữ trên đĩa.")
st.markdown('<div class="eyebrow">AI research workspace · evidence first</div>', unsafe_allow_html=True)
st.markdown('<h1 class="hero-title">Find the signal.<br><em>Read beyond</em> the abstract.</h1>', unsafe_allow_html=True)
st.markdown(
    '<p class="hero-copy">Paper Scout tìm kiếm, đọc, tóm tắt và tổ chức bằng chứng khoa học — '
    'với toàn bộ tool call, arguments và kết quả luôn có thể kiểm tra.</p>',
    unsafe_allow_html=True,
)
st.markdown('<div class="rule-double"></div>', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="artifact-row">
      <span class="artifact-badge"><strong>artifact</strong> {artifact.artifact_version}</span>
      <span class="artifact-badge"><strong>prompt</strong> {artifact.prompt_hash[:12]}</span>
      <span class="artifact-badge"><strong>tools</strong> {artifact.tools_hash[:12]}</span>
      <span class="artifact-badge"><strong>model</strong> {safe_selected_model}</span>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="section-label">Start with a research question</div>', unsafe_allow_html=True)
sample_columns = st.columns(3)
sample_prompt: str | None = None
for column, prompt_text in zip(sample_columns, SAMPLE_PROMPTS):
    with column:
        if st.button(prompt_text, key=f"sample_{prompt_text}", use_container_width=True):
            sample_prompt = prompt_text

st.markdown('<div class="section-label">Research log</div>', unsafe_allow_html=True)
if not st.session_state.chat_messages:
    st.markdown(
        '<div class="empty-desk">Bàn nghiên cứu đang trống. Chọn một câu hỏi mẫu hoặc nhập chủ đề, URL arXiv, '
        'yêu cầu tóm tắt hay định dạng digest ở bên dưới.</div>',
        unsafe_allow_html=True,
    )
for stored_message in st.session_state.chat_messages:
    render_message(stored_message)

typed_prompt = st.chat_input("Ask about a topic, paper, author, or arXiv URL…")
user_prompt = sample_prompt or typed_prompt

if user_prompt:
    st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
    render_message(st.session_state.chat_messages[-1])

    transcript, transcript_path = get_or_create_transcript(
        current_signature,
        provider_name,
        selected_model,
        version,
        history_window,
        max_tool_rounds,
        artifact,
    )
    turn_record: dict[str, Any] = {
        "turn_index": len(transcript["turns"]) + 1,
        "started_at": now_iso(),
        "user": user_prompt,
        "status": "started",
        "assistant_text": None,
        "rounds": [],
        "tool_events": [],
    }

    prior_history = [
        {"role": item["role"], "content": item["content"]}
        for item in st.session_state.chat_messages[:-1]
        if item["role"] in {"user", "assistant"} and not item.get("error")
    ]
    messages = [
        {"role": "system", "content": system_prompt},
        *trim_history(prior_history, history_window),
        {"role": "user", "content": user_prompt},
    ]

    try:
        with st.spinner("Paper Scout đang lần theo nguồn và kiểm tra bằng chứng…"):
            result = run_model_tool_loop(
                provider=provider,
                messages=messages,
                tools=openai_tools,
                model=model_input or None,
                max_tool_rounds=max_tool_rounds,
            )
        assistant_text = result.get("assistant_text") or "Agent không trả về nội dung. Hãy thử diễn đạt lại câu hỏi."
        turn_record.update(result)
        assistant_message = {"role": "assistant", "content": assistant_text, "result": result}
    except Exception as exc:
        error_text = f"{type(exc).__name__}: {exc}"
        turn_record.update({"status": "provider_error", "error": error_text})
        assistant_message = {
            "role": "assistant",
            "content": "Mình chưa thể hoàn tất lượt nghiên cứu này.",
            "error": error_text,
        }

    turn_record["ended_at"] = now_iso()
    transcript["turns"].append(turn_record)
    try:
        write_transcript(transcript_path, transcript)
    except Exception as exc:
        assistant_message["error"] = (
            f"{assistant_message.get('error', '')}\nTranscript save failed: {type(exc).__name__}: {exc}"
        ).strip()

    st.session_state.chat_messages.append(assistant_message)
    render_message(assistant_message)

if st.session_state.transcript:
    transcript_json = json.dumps(st.session_state.transcript, ensure_ascii=False, indent=2, default=str)
    st.download_button(
        "Download current transcript",
        data=transcript_json,
        file_name=Path(st.session_state.transcript_path).name,
        mime="application/json",
    )
