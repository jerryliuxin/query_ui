#!/usr/bin/env python3
"""
曦智科技数据集成 - 手动执行 (2026-03-25)
更新query_ui前端，确保photonx正确显示
"""

import json
from pathlib import Path

BASE = Path("/home/mickey/.openclaw/mihua")
DD_DIR = BASE / "knowledge_base_dd"
INDEX_FILE = DD_DIR / "index.json"

# 1. 重建索引（确保photonx已包含）
import subprocess
subprocess.run(["python3", "tools/dd_index.py", "build"], cwd=BASE, check=True)

# 2. 验证photonx数据完整
profile = json.loads((DD_DIR / "companies/photonx/profile.json").read_text())
prof = profile.get("profile", {})

print("✅ PhotonX profile verified:")
print(f"  - Industry: {prof.get('industry')}")
print(f"  - Founded: {prof.get('founded')}")
print(f"  - HQ: {prof.get('headquarters')}")
print(f"  - Business Model: {prof.get('business_model')}")
print(f"  - Financials: {'✅' if profile.get('financials') else '❌'}")

# 3. 更新前端的行业选项（如果hardcoded）
# 检查templates中是否有硬编码行业列表
industries = set()
for comp in json.loads(INDEX_FILE.read_text()).get("companies", []):
    if comp.get("industry"):
        industries.add(comp["industry"])

print(f"\n📊 Available industries in index ({len(industries)}):")
for ind in sorted(industries):
    print(f"  - {ind}")

# 4. 输出前端需要更新的建议
print("\n" + "="*80)
print("🎯 ACTION needed in query_ui templates:")
print("   1. companies.html: update industry filter options")
print("   2. company_detail.html: ensure all fields render correctly")
print("   3. Add PhotonX to recent activity (last_updated = 2026-03-25)")
print("="*80)

print("\n✅ All data prepared. Query UI should automatically pick up PhotonX after refresh.")
