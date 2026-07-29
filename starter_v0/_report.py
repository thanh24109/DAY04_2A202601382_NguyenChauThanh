import json
from pathlib import Path

files = {
    "v0": "runs/v0_B_base_openrouter_20260729T083927967419.json",
    "v1": "runs/v1_B_base_openrouter_20260729T084252721443.json",
    "v2": "runs/v2_B_base_openrouter_20260729T084402653413.json",
    "v3": "runs/v3_B_group_openrouter_20260729T084521455530.json",
}

for ver, path in files.items():
    data = json.loads(Path(path).read_bytes())
    s = data["summary"]
    print(f"\n=== {ver} ===")
    print(f"  run_file: {path}")
    print(f"  case_accuracy: {s.get('case_accuracy')}")
    print(f"  tool_routing_accuracy: {s.get('tool_routing_accuracy')}")
    print(f"  argument_accuracy: {s.get('argument_accuracy')}")
    print(f"  multiturn_accuracy: {s.get('multiturn_accuracy')}")
    print(f"  measured_cases: {s.get('measured_cases')}")
    print(f"  passed_cases: {s.get('passed_cases')}")
    print(f"  failure_counts: {s.get('failure_counts')}")
    print(f"  observed_mismatch_counts: {s.get('observed_mismatch_counts')}")
    print(f"  artifact_version: {data.get('artifact_version')}")
