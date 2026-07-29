import json
from pathlib import Path

from agent import ResearchAgent
from chat import run_model_tool_loop, write_transcript
from env_loader import load_lab_env
from providers import make_provider
from tools import load_tool_declarations, to_openai_tools, TOOL_FUNCTIONS
from versioning import build_artifact_version, artifact_version_dict

decls = load_tool_declarations(Path("artifacts/tools.yaml"))
tools = to_openai_tools(decls)
print(f"OK: {len(tools)} tools loaded from YAML")
print(f"OK: {len(TOOL_FUNCTIONS)} implementations registered")

av = build_artifact_version("v3", Path("artifacts/system_prompt.md"), Path("artifacts/tools.yaml"))
print(f"OK: artifact_version={av.artifact_version}")

eg = json.loads(Path("data/eval_group.json").read_bytes())
print(f"OK: eval_group.json has {len(eg['cases'])} cases")
eb = json.loads(Path("data/eval_base.json").read_bytes())
print(f"OK: eval_base.json has {len(eb['cases'])} cases")

print("\nAll checks passed!")
