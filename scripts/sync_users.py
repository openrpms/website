#!/usr/bin/env python3
"""Build _data/users.json for the "Users & use cases" page from rpms-ux's product-cycle data.

rpms-ux holds the full personas, use cases, stories and journeys. This site shows a
reader's summary: the roles, the use cases grouped the way a clinic's day runs, and a
couple of real user stories under each. Rollout phases and scope, sign-on users,
profiles, hosts and repo references are left behind on purpose.

Usage: python3 scripts/sync_users.py [path-to-rpms-ux]   (default ~/workspace/rpms-ux)
Exits non-zero, saying why, if a workflow or persona is unmapped or anything internal leaks.
"""
import datetime
import json
import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_data", "users.json")
STORIES_PER_USE_CASE = 2

# Use cases as a reader sees them. Workflows split across rollout phases are merged.
GROUPS = [
    {
        "name": "At the front desk",
        "blurb": "Getting the patient in the door, on the schedule, and covered.",
        "use_cases": [
            ("registration", "Register a patient", ["W01"]),
            ("scheduling", "Schedule a visit", ["W02"]),
            ("benefits", "Check benefits and eligibility", ["W19"]),
            ("adt", "Admit, transfer, and discharge", ["W18"]),
        ],
    },
    {
        "name": "During the visit",
        "blurb": "Seeing the patient, charting, ordering, and sending them home with a plan.",
        "use_cases": [
            ("triage", "Prepare for the visit and triage", ["W03"]),
            ("visit", "See the patient and write the note", ["W04"]),
            ("prescriptions", "Prescribe and dispense medications", ["W10"]),
            ("lab", "Order labs and act on results", ["W11"]),
            ("referrals", "Refer and consult", ["W12"]),
            ("after-visit", "Give an after-visit summary and care plan", ["W06"]),
        ],
    },
    {
        "name": "Between visits",
        "blurb": "Staying in touch with patients and looking after a whole panel.",
        "use_cases": [
            ("messaging", "Message with patients", ["W14"]),
            ("population", "Manage a panel of patients", ["W20"]),
        ],
    },
    {
        "name": "Coding and paying for care",
        "blurb": "Turning a visit into a clean claim, and paying for care bought outside.",
        "use_cases": [
            ("coding", "Code diagnoses and procedures", ["W05"]),
            ("billing", "Bill and collect", ["W08", "W17"]),
            ("prc", "Pay for purchased and referred care", ["W13"]),
        ],
    },
    {
        "name": "Running the clinic",
        "blurb": "Credentialing staff, reporting on care, and protecting sensitive records.",
        "use_cases": [
            ("credentialing", "Credential providers", ["W09", "W16"]),
            ("reporting", "Report on workload and quality", ["W07", "W15"]),
            ("behavioral-health", "Keep behavioral health records private", ["W21"]),
        ],
    },
]

PERSONA_FIELDS = ["role", "surface", "responsibilities", "goals", "context"]

# "Works in", in plain words. rpms-ux uses package namespaces and "roll-and-scroll";
# a reader needs the program's name. An unknown surface fails the sync so it gets a line here.
SURFACES = {
    "BPRM, roll-and-scroll (AG)": "BPRM; the text screens for Patient Registration",
    "BPRM, IHS Windows Scheduling (BSDX), roll-and-scroll (SD)": "BPRM; IHS Windows Scheduling; the text screens for Scheduling",
    "VueCentric": "VueCentric",
    "VueCentric; BPRM for ward transfers and the census": "VueCentric; BPRM for ward transfers and the census",
    "VueCentric, roll-and-scroll (PCC data entry)": "VueCentric; the text screens for visit data entry",
    "roll-and-scroll (3P Billing, A/R)": "The text screens for Third Party Billing and Accounts Receivable",
    "VueCentric Reports tab, roll-and-scroll (PCC reports, BGP)": "VueCentric's Reports tab; the text screens for visit reports and the Clinical Reporting System",
    "iCare (BMX; IRIS stacks only)": "iCare",
    "roll-and-scroll (Kernel user management, Staff Credentials)": "The text screens for user setup and Staff Credentials",
    "roll-and-scroll (Outpatient Pharmacy)": "The text screens for Outpatient Pharmacy",
    "roll-and-scroll (Lab)": "The text screens for Lab",
    "roll-and-scroll (CHS/PRC, RCIS)": "The text screens for Purchased/Referred Care and referral tracking",
    "BPRM, roll-and-scroll (ADT)": "BPRM; the text screens for admissions",
    "BPRM, roll-and-scroll (ADT incomplete chart)": "BPRM; the text screens for incomplete charts",
    "VueCentric; the Behavioral Health System (AMH)": "VueCentric; the Behavioral Health System",
    "the clinic, a printout, the patient portal": "The clinic, a printout, and the patient portal",
}
# Plain-language fixes for role text: rollout notes and internal key and event codes come out.
TEXT_FIXES = [
    (r"^Phase \d+(?: \(W\d+\))?\.\s*", ""),
    (r";\s*messaging is Phase \d+\.", "."),
    (r"\s*\((?:AGZMGR|DGZADT|DGZSUP|DGZICE|CMET)\)", ""),
    (r"roll-and-scroll 3P Billing and A/R menus", "the text screens for Third Party Billing and Accounts Receivable"),
    (r"roll-and-scroll", "the text screens"),
]


def plain(value):
    if isinstance(value, list):
        return [plain(v) for v in value]
    if isinstance(value, str):
        for pattern, repl in TEXT_FIXES:
            value = re.sub(pattern, repl, value)
    return value


INTERNAL = re.compile(
    r"yotta-\d|iris-\d|rpms-ops|cloud-rpms|lakeraven|SEEDPERS|PROFILE,|staging|analyst|\.md\b|#\d"
    r"|\bPhase \d|roll-and-scroll|\b(?:AGZMGR|DGZADT|DGZSUP|DGZICE)\b",
    re.I,
)


def fail(msg):
    sys.exit(f"sync_users: FAILED: {msg}")


def main():
    src = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/workspace/rpms-ux")
    with open(os.path.join(src, "_data", "personas.json")) as f:
        personas = json.load(f)["personas"]
    with open(os.path.join(src, "_data", "use_cases.json")) as f:
        uc = json.load(f)
    source_commit = subprocess.run(
        ["git", "-C", src, "rev-parse", "--short", "HEAD"], capture_output=True, text=True
    ).stdout.strip() or "unknown"

    workflow_ids = {w["id"] for w in uc["workflows"]}
    mapped = [w for g in GROUPS for _, _, ws in g["use_cases"] for w in ws]
    if sorted(mapped) != sorted(workflow_ids):
        fail(f"workflows unmapped {sorted(workflow_ids - set(mapped))}, unknown {sorted(set(mapped) - workflow_ids)}")

    persona_ids = {p["id"] for p in personas}
    unknown = sorted({p.get("surface") for p in personas} - set(SURFACES))
    if unknown:
        fail(f"add a plain-language line to SURFACES for: {unknown}")
    roles = []
    for p in personas:
        role = {"id": p["id"], **{k: plain(p.get(k)) for k in PERSONA_FIELDS}, "use_cases": []}
        role["surface"] = SURFACES[p.get("surface")]
        roles.append(role)
    by_id = {r["id"]: r for r in roles}

    groups = []
    for g in GROUPS:
        out_cases = []
        for slug, name, ws in g["use_cases"]:
            stories = [s for s in uc["use_cases"] if s["workflow"] in ws and s.get("story")]
            if any(s["persona"] not in persona_ids for s in stories):
                fail(f"{slug}: a story names an unknown persona")
            who = [p["id"] for p in personas if set(p.get("workflows", [])) & set(ws)]
            for pid in who:
                by_id[pid]["use_cases"].append(slug)
            out_cases.append({
                "id": slug,
                "name": name,
                "who": who,
                "story_count": len(stories),
                "stories": [{"persona": s["persona"], "text": s["story"]} for s in stories[:STORIES_PER_USE_CASE]],
            })
        groups.append({"name": g["name"], "blurb": g["blurb"], "use_cases": out_cases})

    data = {
        "source": "rpms-ux product-cycle personas and use cases",
        "source_commit": source_commit,
        "synced": datetime.date.today().isoformat(),
        "use_case_count": sum(len(g["use_cases"]) for g in groups),
        # Flat id -> name list, because Jekyll's `where` does not reach into nested groups.
        "use_case_index": [{"id": c["id"], "name": c["name"]} for g in groups for c in g["use_cases"]],
        "roles": roles,
        "groups": groups,
    }
    text = json.dumps(data, indent=2, ensure_ascii=False)
    leak = INTERNAL.search(text)
    if leak:
        fail(f"internal reference in output: {text[max(0, leak.start() - 60):leak.end() + 60]!r}")

    with open(OUT, "w") as f:
        f.write(text + "\n")

    # Confirm the file on disk is what we meant to write.
    with open(OUT) as f:
        check = json.load(f)
    n_cases = sum(len(g["use_cases"]) for g in check["groups"])
    n_stories = sum(c["story_count"] for g in check["groups"] for c in g["use_cases"])
    print(f"sync_users: OK wrote {os.path.relpath(OUT, ROOT)}: {len(check['roles'])} roles, "
          f"{n_cases} use cases in {len(check['groups'])} groups, from {n_stories} stories "
          f"(rpms-ux {source_commit})")


if __name__ == "__main__":
    main()
