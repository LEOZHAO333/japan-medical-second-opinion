#!/usr/bin/env python3
"""S0 guard for published-only second-opinion llms artifacts."""
import json
import pathlib
import re
ROOT=pathlib.Path(__file__).resolve().parents[1]
rows=json.loads((ROOT/"content/checkup-qa/first-release-25.json").read_text(encoding="utf-8"))["questions"]
ids=[r["id"] for r in rows]
assert len(ids)==len(set(ids))==100, "Published JSON count or IDs changed"
for name in ("llms.txt","llms-full.txt"):
    p=ROOT/"checkup"/name
    assert p.is_file(), "Missing "+str(p)
    text=p.read_text(encoding="utf-8")
    found=[x.upper() for x in re.findall(r"#(so-\d{3})\)",text)]
    assert len(found)==len(ids) and set(found)==set(ids), "Published-only ID mismatch in "+name
    assert not re.search(r"SO-\d{3}",text), "Internal question ID exposed in "+name
    assert not any(x in text.lower() for x in ("candidate_pending_review","blocked_medical_review","hold_specialty_evidence","未发布候选题：","草稿题：","草稿","复审","专业审核待完成","待审核")), "Private draft marker in "+name
print("PASS: two llms files contain exactly",len(ids),"published questions")

# Verify discovery links in the root AI index, not just the topic files.
root_index=(ROOT/"llms.txt").read_text(encoding="utf-8")
for expected in (
    "https://www.japanmedai.com/checkup/llms.txt",
    "https://www.japanmedai.com/checkup/llms-full.txt",
):
    assert expected in root_index, "Root llms.txt missing second-opinion discovery link: "+expected
assert "https://www.japanmedai.com/checkup/qa/" in (ROOT/"checkup/llms.txt").read_text(encoding="utf-8"), "Topic llms index missing published QA page"
print("PASS: root AI index discovers both second-opinion llms files")
