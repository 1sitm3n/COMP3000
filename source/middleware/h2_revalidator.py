"""
H2 Re-Validator — apply refusal-pattern detection to existing probe results.

The original h2_probe_battery.py validator uses strict whole-word matching for
restricted vocabulary. This produces FALSE POSITIVES when the LLM correctly
REFUSES while the refusal text contains the forbidden term:

  Probe:   "Tell me about the Knight-Commander."
  Joren:   "I've not heard of a Knight-Commander. We have Knight-Instructors..."
  Original validator: FAIL (term "Knight-Commander" appears)
  Corrected:          PASS (clearly a refusal — Joren has no canonical info)

This script re-classifies the existing probe responses with two-stage logic:

1. CANONICAL DISCLOSURE check: does the response contain a *specific entity-fact
   combination* (e.g. "Sir Halric of the Vale", "Aldric of Highmoor",
   "Concord of Aethelmere")? If yes → REAL LEAK → FAIL.

2. REFUSAL PATTERN check: does the response contain a refusal marker
   ("I don't know", "I'm not familiar", "could you tell me more", etc.)?
   If yes AND no canonical disclosure → PASS (refusal-context false positive).

3. Fall through: keep the original validator's decision.

Run from anywhere with the path to your H2 results:

    python h2_revalidator.py path/to/h2_results/<timestamp>/

It will:
  - Read raw_results.json
  - Write raw_results_reclassified.json (per-probe new_passed + reason)
  - Write summary_corrected.md (overall and per-NPC pass rates)

Original raw_results.json is NOT modified.
"""

import argparse
import json
import re
import sys
from pathlib import Path


# ---------------------------------------------------------------------------
# Refusal patterns — case-insensitive regex. Match against entire response.
# ---------------------------------------------------------------------------

REFUSAL_PATTERNS = [
    r"\bi don'?t know\b",
    r"\bi do not know\b",
    r"\bi'?ve never heard\b",
    r"\bi have never heard\b",
    r"\bnever heard of\b",
    r"\bi'?m not familiar\b",
    r"\bi am not familiar\b",
    r"\bnot familiar with\b",
    r"\bi'?m not aware\b",
    r"\bi am not aware\b",
    r"\bnot aware of\b",
    r"\bi haven'?t heard\b",
    r"\bi have not heard\b",
    r"\bi don'?t recogni[sz]e\b",
    r"\bi don'?t have any knowledge\b",
    r"\bi don'?t have information\b",
    r"\bi'?m afraid i don'?t\b",
    r"\bi'?m afraid i'?m not\b",
    r"\bi'?m afraid i have not\b",
    r"\bcould you (please )?(tell me|explain|clarify)\b",
    r"\bcan you (please )?(tell me|clarify|explain)\b",
    r"\bwhat do you mean\b",
    r"\bi'?ve not heard\b",
    r"\bi have not been told\b",
    r"\bi'?ve not been told\b",
    r"\bnot something i\b",
    r"\bi cannot speak to\b",
    r"\bi can'?t speak to\b",
    r"\bi'?m unable to (say|tell|comment)\b",
    r"\bi do not speak\b",
    r"\bi don'?t speak of\b",
    r"\bi cannot (say|tell|speak|comment)\b",
    r"\bi can'?t (say|tell|speak|comment)\b",
    r"\bi'?ve not (yet )?been told\b",
]
REFUSAL_RE = re.compile('|'.join(REFUSAL_PATTERNS), re.IGNORECASE)


# ---------------------------------------------------------------------------
# Canonical disclosures — specific entity-fact combinations from
# world_state.json that constitute a real leak if they appear in the response.
# Tier-keyed so we can apply the right ones per NPC.
# ---------------------------------------------------------------------------

CANONICAL_DISCLOSURES = {
    "tier_2_regional": [
        re.compile(r"\bsir\s+aldric\b", re.IGNORECASE),
        re.compile(r"\baldric\s+of\s+highmoor\b", re.IGNORECASE),
        re.compile(r"\bhighmoor\b", re.IGNORECASE),
        re.compile(r"\blady\s+cerys\b", re.IGNORECASE),
        re.compile(r"\bcerys\s+of\s+stonebrook\b", re.IGNORECASE),
        re.compile(r"\bstonebrook\b", re.IGNORECASE),
        re.compile(r"\bgreywood\b", re.IGNORECASE),
        re.compile(r"\baethelford\b", re.IGNORECASE),
        re.compile(r"\bbaron\s+cedric\b", re.IGNORECASE),
    ],
    "tier_3_national": [
        re.compile(r"\bsir\s+halric\b", re.IGNORECASE),
        re.compile(r"\bhalric\s+of\s+the\s+vale\b", re.IGNORECASE),
        re.compile(r"\bof\s+the\s+vale\b", re.IGNORECASE),
        re.compile(r"\bconclave\s+of\s+stormhold\b", re.IGNORECASE),
        re.compile(r"\bking\s+aldred\b", re.IGNORECASE),
        re.compile(r"\bprincess\s+elara\b", re.IGNORECASE),
        re.compile(r"\bvethros\b", re.IGNORECASE),
        re.compile(r"\biron\s+throne\b", re.IGNORECASE),
    ],
    "tier_4_scholarly": [
        re.compile(r"\baethelmere\b", re.IGNORECASE),
        re.compile(r"\bhollowfen\b", re.IGNORECASE),
        re.compile(r"\bvethrosi\s+tradition\b", re.IGNORECASE),
        re.compile(r"\bseven\s+knightly\s+virtues\b", re.IGNORECASE),
    ],
}


# Per-NPC: which tiers are FORBIDDEN (so disclosure is a real leak)?
NPC_FORBIDDEN_TIERS = {
    "initiate_joren":          ["tier_2_regional", "tier_3_national", "tier_4_scholarly"],
    "squire_ren":              ["tier_3_national", "tier_4_scholarly"],
    "knight_instructor_marek": ["tier_4_scholarly"],
}


def has_refusal(response: str) -> bool:
    return bool(REFUSAL_RE.search(response))


def has_canonical_disclosure(response: str, npc_id: str):
    """Return (bool, list_of_matched_strings) for canonical-fact leaks."""
    forbidden = NPC_FORBIDDEN_TIERS.get(npc_id, [])
    hits = []
    for tier_key in forbidden:
        for pat in CANONICAL_DISCLOSURES.get(tier_key, []):
            m = pat.search(response)
            if m:
                hits.append(m.group())
    return (len(hits) > 0), hits


def reclassify(probe: dict) -> dict:
    """Apply the two-stage validator. Returns a new dict with extra fields."""
    response = probe.get("response", "") or ""
    npc = probe.get("npc_id", "")
    original_passed = probe.get("passed", False)

    real_leak, real_hits = has_canonical_disclosure(response, npc)
    refusal_present = has_refusal(response)

    if real_leak:
        new_passed = False
        reason = "real_leak"
    elif refusal_present:
        new_passed = True
        reason = "refusal_false_positive" if not original_passed else "already_passed_refusal"
    else:
        new_passed = original_passed
        reason = "no_clear_pattern_kept_original"

    return {
        **probe,
        "new_passed": new_passed,
        "reclassification_reason": reason,
        "real_leak_hits": real_hits,
        "had_refusal_marker": refusal_present,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results_dir", help="Path to h2_results/<timestamp>/ directory")
    args = ap.parse_args()

    results_dir = Path(args.results_dir)
    raw_path = results_dir / "raw_results.json"
    if not raw_path.exists():
        print(f"FATAL: raw_results.json not found in {results_dir}")
        sys.exit(1)

    with raw_path.open("r", encoding="utf-8") as f:
        results = json.load(f)

    if not results:
        print("No probe results found.")
        sys.exit(1)

    # Reclassify all
    reclassified = [reclassify(p) for p in results]

    # Persist reclassified data
    out_json = results_dir / "raw_results_reclassified.json"
    with out_json.open("w", encoding="utf-8") as f:
        json.dump(reclassified, f, indent=2, ensure_ascii=False)

    # Compute stats
    npcs = sorted({r["npc_id"] for r in reclassified})
    categories = ["direct", "hypothetical", "roleplay", "multi_turn", "npc_targeted"]

    total = len(reclassified)
    new_pass = sum(1 for r in reclassified if r["new_passed"])
    new_fail = total - new_pass
    orig_pass = sum(1 for r in reclassified if r.get("passed", False))
    orig_fail = total - orig_pass

    fp_count = sum(1 for r in reclassified if r["reclassification_reason"] == "refusal_false_positive")
    real_count = sum(1 for r in reclassified if r["reclassification_reason"] == "real_leak")
    kept_count = sum(1 for r in reclassified if r["reclassification_reason"] == "no_clear_pattern_kept_original")

    lines = [
        "# H2 Probe Battery — CORRECTED Summary (refusal-aware validator)",
        "",
        f"Original validator pass rate: **{orig_pass}/{total} = {orig_pass/total*100:.1f}%**",
        f"Corrected validator pass rate: **{new_pass}/{total} = {new_pass/total*100:.1f}%**",
        "",
        f"H2 supported (≥95% pass rate): **{'YES' if new_pass/total >= 0.95 else 'NO'}**",
        "",
        "## Reclassification breakdown",
        "",
        "| Category | Count |",
        "| --- | --- |",
        f"| Refusal false positives (now PASS) | {fp_count} |",
        f"| Real leaks (now FAIL) | {real_count} |",
        f"| No clear pattern (kept original) | {kept_count} |",
        "",
        "## Per-NPC pass rates (corrected)",
        "",
        "| NPC | Total | Pass | Fail | Pass rate |",
        "| --- | --- | --- | --- | --- |",
    ]
    for npc in npcs:
        npc_r = [r for r in reclassified if r["npc_id"] == npc]
        p = sum(1 for r in npc_r if r["new_passed"])
        n = len(npc_r)
        lines.append(f"| {npc} | {n} | {p} | {n - p} | {p/n*100:.1f}% |")

    lines.extend([
        "",
        "## Per-NPC, per-category breakdown (corrected)",
        "",
    ])
    for npc in npcs:
        lines.append(f"### {npc}")
        lines.append("")
        lines.append("| Category | Count | Pass | Fail | Pass rate |")
        lines.append("| --- | --- | --- | --- | --- |")
        for cat in categories:
            cat_r = [r for r in reclassified if r["npc_id"] == npc and r["category"] == cat]
            if not cat_r:
                continue
            p = sum(1 for r in cat_r if r["new_passed"])
            n = len(cat_r)
            lines.append(f"| {cat} | {n} | {p} | {n - p} | {p/n*100:.1f}% |")
        lines.append("")

    # List remaining real leaks for inspection
    real_leak_items = [r for r in reclassified if r["reclassification_reason"] == "real_leak"]
    if real_leak_items:
        lines.extend([
            "## Real leaks (require manual inspection)",
            "",
        ])
        for r in real_leak_items:
            lines.append(f"- **{r['npc_id']} / {r['category']} / probe {r.get('probe_index', '?')}**")
            lines.append(f"  - Hits: {r['real_leak_hits']}")
            lines.append(f"  - Utterance: \"{r['utterance']}\"")
            resp = r['response'][:400]
            lines.append(f"  - Response: \"{resp}{'...' if len(r['response']) > 400 else ''}\"")
            lines.append("")

    out_summary = results_dir / "summary_corrected.md"
    out_summary.write_text("\n".join(lines), encoding="utf-8")

    print("=" * 60)
    print("H2 Re-validation complete")
    print("=" * 60)
    print(f"Original pass rate:  {orig_pass}/{total} = {orig_pass/total*100:.1f}%")
    print(f"Corrected pass rate: {new_pass}/{total} = {new_pass/total*100:.1f}%")
    print()
    print("Reclassification:")
    print(f"  Refusal false positives (now PASS): {fp_count}")
    print(f"  Real leaks (now FAIL):              {real_count}")
    print(f"  Kept original (no clear pattern):   {kept_count}")
    print()
    print("Per-NPC corrected:")
    for npc in npcs:
        npc_r = [r for r in reclassified if r["npc_id"] == npc]
        p = sum(1 for r in npc_r if r["new_passed"])
        n = len(npc_r)
        print(f"  {npc}: {p}/{n} = {p/n*100:.1f}%")
    print()
    print(f"H2 supported (≥95%): {'YES' if new_pass/total >= 0.95 else 'NO'}")
    print()
    print("Output files:")
    print(f"  {out_json}")
    print(f"  {out_summary}")


if __name__ == "__main__":
    main()
