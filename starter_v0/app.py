"""
Research Paper Scout — Streamlit UI
Tái sử dụng run_model_tool_loop từ chat.py theo đúng yêu cầu của bài lab.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import streamlit as st

# ── Page config (phải đặt đầu tiên) ──────────────────────────────────────────
st.set_page_config(
    page_title="Research Paper Scout 🔬",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Import từ project (tái sử dụng, không viết lại) ─────────────────────────
ROOT = Path(__file__).parent
ARTIFACTS_DIR = ROOT / "artifacts"
TRANSCRIPTS_DIR = ROOT / "transcripts"

from env_loader import load_lab_env
load_lab_env(ROOT)

from providers import make_provider
from tools import load_tool_declarations, to_openai_tools
from versioning import build_artifact_version, artifact_version_dict
from chat import (
    run_model_tool_loop,
    write_transcript,
    now_iso,
    safe_slug,
    trim_history,
)

# ── CSS tuỳ chỉnh ────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Nền chính */
.main { background-color: #0f1117; }

/* Badge version */
.version-badge {
    display: inline-block;
    background: linear-gradient(135deg, #1e3a5f, #0ea5e9);
    color: white;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 600;
    letter-spacing: 0.5px;
    margin: 2px;
}
.hash-badge {
    display: inline-block;
    background: #1e293b;
    color: #94a3b8;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.7rem;
    font-family: monospace;
    margin: 2px;
}

/* Tool trace container */
.tool-event-card {
    background: #1a1f2e;
    border-left: 3px solid #0ea5e9;
    border-radius: 6px;
    padding: 10px 14px;
    margin: 6px 0;
}
.tool-name {
    color: #38bdf8;
    font-weight: bold;
    font-family: monospace;
    font-size: 0.9rem;
}
.tool-status-pass { color: #4ade80; }
.tool-status-fail { color: #f87171; }

/* Metric cards */
.metric-card {
    background: #1e293b;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
    border: 1px solid #334155;
}
.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #38bdf8;
}
.metric-label {
    font-size: 0.75rem;
    color: #94a3b8;
    margin-top: 2px;
}

/* Status indicator */
.status-answered { color: #4ade80; }
.status-waiting  { color: #fbbf24; }
.status-error    { color: #f87171; }
</style>
""", unsafe_allow_html=True)


# ── Session State Init ────────────────────────────────────────────────────────
def init_session():
    defaults: dict[str, Any] = {
        "messages": [],          # Hiển thị trong chat (role/content)
        "history": [],           # Cho trim_history của agent
        "tool_events_log": [],   # Tất cả tool events theo turn
        "transcript": None,
        "transcript_path": None,
        "turn_index": 0,
        "provider_obj": None,
        "openai_tools": None,
        "artifact_ver": None,
        "initialized": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_session()


# ── Helper: render tool trace ─────────────────────────────────────────────────
def render_tool_trace(rounds: list[dict[str, Any]]):
    """Hiển thị Tool Trace bên trong expander theo từng round."""
    if not rounds:
        return
    for rnd in rounds:
        r_idx = rnd.get("round", "?")
        calls = rnd.get("tool_calls", [])
        results = rnd.get("tool_results", [])
        if not calls:
            continue
        for i, call in enumerate(calls):
            res_data = results[i] if i < len(results) else {}
            result_val = res_data.get("result", {})
            has_error = isinstance(result_val, dict) and "error" in result_val
            status_icon = "❌" if has_error else "✅"
            status_class = "tool-status-fail" if has_error else "tool-status-pass"
            st.markdown(f"""
<div class="tool-event-card">
  <span class="tool-name">🔧 Round {r_idx} · {call.get("name","?")}()</span>
  &nbsp;<span class="{status_class}">{status_icon}</span>
</div>
""", unsafe_allow_html=True)

            col_a, col_b = st.columns(2)
            with col_a:
                st.caption("📥 Arguments")
                st.json(call.get("args", {}), expanded=False)
            with col_b:
                st.caption("📤 Result")
                if isinstance(result_val, dict):
                    st.json(result_val, expanded=False)
                else:
                    st.code(str(result_val)[:500])


def render_version_badges(av: Any):
    """Render version / hash badges ở đầu trang."""
    if av is None:
        return
    st.markdown(
        f'<span class="version-badge">🏷 {av["artifact_version"]}</span>'
        f'<span class="hash-badge">prompt: {av["prompt_hash"][:12]}</span>'
        f'<span class="hash-badge">tools: {av["tools_hash"][:12]}</span>',
        unsafe_allow_html=True,
    )


# ── Sidebar: cấu hình ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Cấu hình Agent")
    st.divider()

    provider_name = st.selectbox(
        "Provider", ["openrouter", "openai", "anthropic", "gemini"],
        index=0, help="LLM provider để dùng"
    )
    model_override = st.text_input(
        "Model (tuỳ chọn)", placeholder="Để trống = dùng default",
        help="Ví dụ: openai/gpt-4o hoặc anthropic/claude-3-5-haiku"
    )
    version_label = st.selectbox(
        "Artifact Version", ["v3", "v2", "v1", "v0"],
        index=0, help="Version của system prompt + tools.yaml"
    )
    max_tool_rounds = st.slider("Max Tool Rounds", 1, 8, 4)
    history_window = st.slider("History Window (turns)", 0, 10, 5)

    st.divider()
    init_btn = st.button("🚀 Khởi động Agent", type="primary", use_container_width=True)
    clear_btn = st.button("🗑 Xóa lịch sử chat", use_container_width=True)

    # Thông tin artifact version
    if st.session_state.artifact_ver:
        st.divider()
        st.markdown("**📋 Artifact đang dùng:**")
        render_version_badges(st.session_state.artifact_ver)

    st.divider()
    st.caption("Research Paper Scout · Day04 Lab v2")
    st.caption("Nguyễn Châu Thành · 2A202601382")


# ── Init Agent ───────────────────────────────────────────────────────────────
if init_btn:
    with st.spinner("Đang kết nối provider..."):
        try:
            provider_obj = make_provider(provider_name)
            tool_declarations = load_tool_declarations(ARTIFACTS_DIR / "tools.yaml")
            openai_tools = to_openai_tools(tool_declarations)
            system_prompt_path = ARTIFACTS_DIR / "system_prompt.md"
            tools_path = ARTIFACTS_DIR / "tools.yaml"
            artifact_ver = artifact_version_dict(
                build_artifact_version(version_label, system_prompt_path, tools_path)
            )

            # Init transcript
            ts = datetime.now().strftime("%Y%m%dT%H%M%S%f")
            transcript_id = f"{safe_slug(version_label)}_{safe_slug(provider_name)}_{ts}"
            transcript_path = TRANSCRIPTS_DIR / f"{transcript_id}.transcript.json"
            selected_model = model_override.strip() or getattr(provider_obj, "default_model", None)

            transcript: dict[str, Any] = {
                "transcript_id": transcript_id,
                **artifact_ver,
                "provider": provider_name,
                "model": selected_model,
                "system_prompt": str(system_prompt_path),
                "tools": str(tools_path),
                "history_window": history_window,
                "max_tool_rounds": max_tool_rounds,
                "created_at": now_iso(),
                "updated_at": now_iso(),
                "turns": [],
            }

            st.session_state.provider_obj = provider_obj
            st.session_state.openai_tools = openai_tools
            st.session_state.artifact_ver = artifact_ver
            st.session_state.transcript = transcript
            st.session_state.transcript_path = transcript_path
            st.session_state.initialized = True
            st.session_state.messages = []
            st.session_state.history = []
            st.session_state.tool_events_log = []
            st.session_state.turn_index = 0

            st.sidebar.success(f"✅ Kết nối thành công!\nModel: {selected_model}")
        except Exception as e:
            st.sidebar.error(f"❌ Lỗi: {e}")

if clear_btn:
    st.session_state.messages = []
    st.session_state.history = []
    st.session_state.tool_events_log = []
    st.session_state.turn_index = 0
    if st.session_state.transcript:
        st.session_state.transcript["turns"] = []
    st.rerun()


# ── Main Layout ───────────────────────────────────────────────────────────────
st.markdown("# 🔬 Research Paper Scout")
st.markdown("Trợ lý AI tìm kiếm, tóm tắt và trích dẫn bài báo khoa học tự động.")

if st.session_state.artifact_ver:
    render_version_badges(st.session_state.artifact_ver)

st.divider()

# Tabs: Chat | Tool Trace | Metrics
tab_chat, tab_trace, tab_metrics = st.tabs(["💬 Chat", "🔧 Tool Trace", "📊 Metrics"])

# ── Tab Chat ─────────────────────────────────────────────────────────────────
with tab_chat:
    if not st.session_state.initialized:
        st.info("👈 Nhấn **Khởi động Agent** trong sidebar để bắt đầu.")
    else:
        # Hiển thị lịch sử chat
        chat_container = st.container()
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])
                    # Hiển thị tool trace inline nếu có
                    if msg.get("rounds"):
                        with st.expander("🔧 Tool Trace", expanded=False):
                            render_tool_trace(msg["rounds"])

        # Input
        user_input = st.chat_input("Hỏi về bài báo khoa học, ví dụ: Tìm bài báo về LLM reasoning...")

        if user_input:
            # Hiện tin nhắn user
            st.session_state.messages.append({"role": "user", "content": user_input})

            with st.chat_message("user"):
                st.markdown(user_input)

            # Gọi agent
            with st.chat_message("assistant"):
                with st.spinner("🤔 Agent đang xử lý..."):
                    system_prompt = (ARTIFACTS_DIR / "system_prompt.md").read_text(encoding="utf-8")
                    messages_for_agent = [
                        {"role": "system", "content": system_prompt},
                        *trim_history(st.session_state.history, history_window),
                        {"role": "user", "content": user_input},
                    ]

                    st.session_state.turn_index += 1
                    turn_record: dict[str, Any] = {
                        "turn_index": st.session_state.turn_index,
                        "started_at": now_iso(),
                        "user": user_input,
                        "status": "started",
                    }

                    try:
                        result = run_model_tool_loop(
                            provider=st.session_state.provider_obj,
                            messages=messages_for_agent,
                            tools=st.session_state.openai_tools,
                            model=model_override.strip() or None,
                            max_tool_rounds=max_tool_rounds,
                        )
                        assistant_text = result["assistant_text"]
                        rounds = result.get("rounds", [])
                        tool_events = result.get("tool_events", [])
                        status = result.get("status", "answered")

                        # Hiển thị response
                        st.markdown(assistant_text)

                        # Tool trace inline
                        if rounds and any(r.get("tool_calls") for r in rounds):
                            with st.expander(f"🔧 Tool Trace ({len(tool_events)} calls)", expanded=True):
                                render_tool_trace(rounds)

                        # Status badge
                        status_map = {
                            "answered": ("✅ Trả lời hoàn tất", "status-answered"),
                            "waiting_for_user": ("⏳ Chờ thêm thông tin", "status-waiting"),
                            "max_tool_rounds": ("⚠️ Đạt giới hạn tool rounds", "status-error"),
                        }
                        label, css_class = status_map.get(status, (status, ""))
                        st.markdown(f'<small class="{css_class}">{label}</small>', unsafe_allow_html=True)

                        # Lưu vào history và messages
                        st.session_state.history.append({"role": "user", "content": user_input})
                        st.session_state.history.append({"role": "assistant", "content": assistant_text})
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_text,
                            "rounds": rounds,
                        })
                        st.session_state.tool_events_log.append({
                            "turn": st.session_state.turn_index,
                            "user": user_input,
                            "tool_events": tool_events,
                            "rounds": rounds,
                        })

                        turn_record.update(result)

                    except Exception as exc:
                        err_msg = f"{type(exc).__name__}: {exc}"
                        st.error(f"❌ Lỗi provider: {err_msg}")
                        turn_record["status"] = "provider_error"
                        turn_record["error"] = err_msg

                    turn_record["ended_at"] = now_iso()
                    if st.session_state.transcript:
                        st.session_state.transcript["turns"].append(turn_record)
                        write_transcript(st.session_state.transcript_path, st.session_state.transcript)


# ── Tab Tool Trace ────────────────────────────────────────────────────────────
with tab_trace:
    st.markdown("### 🔧 Lịch sử Tool Calls")
    if not st.session_state.tool_events_log:
        st.info("Chưa có tool call nào. Hãy chat với agent trước.")
    else:
        for entry in reversed(st.session_state.tool_events_log):
            turn_n = entry["turn"]
            user_q = entry["user"]
            rounds = entry.get("rounds", [])
            n_calls = sum(len(r.get("tool_calls", [])) for r in rounds)

            with st.expander(f"**Turn {turn_n}** · {user_q[:60]}... · {n_calls} tool call(s)", expanded=(turn_n == st.session_state.turn_index)):
                # Metadata turn
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.markdown(f"**Turn:** `{turn_n}`")
                    st.markdown(f"**Calls:** `{n_calls}`")
                with col2:
                    st.markdown(f"**Query:** {user_q}")

                st.divider()
                render_tool_trace(rounds)

                # Raw JSON
                with st.expander("📄 Raw rounds JSON"):
                    st.json(rounds, expanded=False)


# ── Tab Metrics ───────────────────────────────────────────────────────────────
with tab_metrics:
    st.markdown("### 📊 Kết quả Eval — So sánh v0 → v3")

    # Data từ các file run JSON đã chạy
    run_data = [
        {
            "version": "v0", "passed": 13, "total": 20, "accuracy": 0.65,
            "routing": 0.70, "argument": 0.65, "multiturn": 1.0,
            "run_file": "v0_B_base_openrouter_20260729T154305703263.json",
            "failures": {"wrong_tool": 2, "out_of_scope": 2, "missing_info": 2, "wrong_boundary": 1},
        },
        {
            "version": "v1", "passed": 19, "total": 20, "accuracy": 0.95,
            "routing": 0.95, "argument": 0.95, "multiturn": 0.8333,
            "run_file": "v1_B_base_openrouter_20260729T160931171482.json",
            "failures": {"wrong_tool": 1},
        },
        {
            "version": "v2", "passed": 19, "total": 20, "accuracy": 0.95,
            "routing": 0.95, "argument": 0.95, "multiturn": 0.8333,
            "run_file": "v2_B_base_openrouter_20260729T161315092650.json",
            "failures": {"wrong_tool": 1},
        },
        {
            "version": "v3", "passed": 19, "total": 20, "accuracy": 0.95,
            "routing": 0.95, "argument": 0.95, "multiturn": 0.8333,
            "run_file": "v3_B_base_openrouter_20260729T161413128889.json",
            "failures": {"wrong_tool": 1},
        },
    ]

    # Metric cards v3 (bản cuối)
    v3 = run_data[-1]
    st.markdown("#### 🏆 Kết quả bản cuối (v3)")
    col1, col2, col3, col4 = st.columns(4)
    for col, (label, val) in zip(
        [col1, col2, col3, col4],
        [
            ("Case Accuracy", f"{v3['accuracy']*100:.0f}%"),
            ("Tool Routing", f"{v3['routing']*100:.0f}%"),
            ("Argument Acc.", f"{v3['argument']*100:.0f}%"),
            ("Multi-turn", f"{v3['multiturn']*100:.1f}%"),
        ]
    ):
        with col:
            st.markdown(f"""
<div class="metric-card">
  <div class="metric-value">{val}</div>
  <div class="metric-label">{label}</div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # Bảng so sánh v0→v3
    st.markdown("#### 📈 So sánh qua các phiên bản")
    import streamlit as _st
    table_data = {
        "Version": [d["version"] for d in run_data],
        "Passed/Total": [f"{d['passed']}/{d['total']}" for d in run_data],
        "Case Accuracy": [f"{d['accuracy']*100:.0f}%" for d in run_data],
        "Routing Acc.": [f"{d['routing']*100:.0f}%" for d in run_data],
        "Arg. Acc.": [f"{d['argument']*100:.0f}%" for d in run_data],
        "Multi-turn": [f"{d['multiturn']*100:.1f}%" for d in run_data],
    }
    st.table(table_data)

    # Improvement highlight
    v0_acc = run_data[0]["accuracy"]
    v3_acc = run_data[-1]["accuracy"]
    delta = v3_acc - v0_acc
    st.success(f"🚀 Cải thiện từ v0 → v3: **{v0_acc*100:.0f}% → {v3_acc*100:.0f}%** (+{delta*100:.0f}pp case accuracy)")

    st.divider()

    # Chi tiết failures từng version
    st.markdown("#### 🔴 Phân tích failure counts")
    for d in run_data:
        with st.expander(f"**{d['version']}** — Failures: {sum(d['failures'].values())} cases"):
            if d["failures"]:
                for ft, count in d["failures"].items():
                    st.markdown(f"- `{ft}`: **{count}** case(s)")
            else:
                st.success("Không có failure!")

    st.divider()
    st.markdown("#### 📁 Run Files")
    for d in run_data:
        run_path = ROOT / "runs" / d["run_file"]
        exists = "✅" if run_path.exists() else "❌"
        st.markdown(f"- {exists} `{d['run_file']}`")
