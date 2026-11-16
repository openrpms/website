#!/usr/bin/env python3
"""Build _data/rpcs.json for the RPCs page from the RPC catalog rpms-ux pins from rpms-rpc.

rpms-ux renders the full catalog (every RPC, its arguments and reply). This site shows the
summary: how many RPCs the build registers, how many a client can call, and which packages
answer the most. Counts are for the build the catalog was generated from, which is named.

Usage: python3 scripts/sync_rpcs.py [path-to-rpms-ux]   (default ~/workspace/rpms-ux)
Exits non-zero, saying why, if the catalog is missing, inconsistent, or the output does not check.
"""
import glob
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "_data", "rpcs.json")
TOP = 12

# Words that stay upper case when a slice's file name becomes a package name.
UPPER = {"ihs", "rpc", "cia", "bgo", "beh", "bpc", "bni", "cphd", "gui", "va", "byim", "img", "bmxnet", "ado", "net"}
# Plain-language notes for what the busiest packages are.
NOTES = {
    "ihs-clinical-reporting": "National performance reports, such as GPRA",
    "order-entry-results-reporting": "Orders and results in the chart",
    "icare-management-system": "iCare, the patient panel",
    "bgo-components": "Parts of the chart: problems, visits, education",
    "beh-components": "The EHR's VueCentric components",
    "ihs-behavioral-health": "The Behavioral Health System",
    "diabetes-management-system": "Diabetes registers and care",
    "text-integration-utilities": "Clinical notes",
    "patient-registration-gui": "Registration",
    "bpc-patient-chart": "The patient chart",
    "care-management-event-tracking": "Care-management events patients are due",
    "ihs-pharmacy-modifications": "Pharmacy",
    "ihs-windows-scheduling": "IHS Windows Scheduling",
    "prenatal-care-module": "Prenatal care",
}


def fail(msg):
    sys.exit(f"sync_rpcs: FAILED: {msg}")


def package_name(slug):
    words = slug.split("-")
    return " ".join(w.upper() if w in UPPER else w.capitalize() for w in words).replace("Bmxnet Ado Net", "BMXNet ADO.NET").replace("Icare", "iCare")


def main():
    src = os.path.expanduser(sys.argv[1] if len(sys.argv) > 1 else "~/workspace/rpms-ux")
    with open(os.path.join(src, "rpc", "pin.json")) as f:
        pin = json.load(f)
    slices = sorted(glob.glob(os.path.join(src, "rpc", "packages", "*.json")))
    if not slices:
        fail("no catalog slices in rpc/packages/")

    packages, counts = [], None
    for path in slices:
        with open(path) as f:
            doc = json.load(f)
        if counts is None:
            counts = doc["x-rpms-counts"]
        elif doc["x-rpms-counts"] != counts:
            fail(f"{os.path.basename(path)} carries different build-wide counts")
        slug = os.path.basename(path)[:-5]
        n = sum(len(ops) for ops in doc["paths"].values())
        packages.append({"slug": slug, "name": package_name(slug), "rpcs": n, "note": NOTES.get(slug, "")})

    total = sum(p["rpcs"] for p in packages)
    if total != counts["rpcs"]:
        fail(f"slices add up to {total} RPCs, the catalog says {counts['rpcs']}")
    packages.sort(key=lambda p: (-p["rpcs"], p["name"]))
    reach = counts["reach"]

    build = pin["build"]
    m = re.search(r"bcer-([\d.]+)-(\d{4})(\d{2})(\d{2})", build)
    if not m:
        fail(f"cannot read the certified line and date from build {build!r}")
    data = {
        "build": build,
        "bcer": m.group(1),
        "build_date": f"{m.group(2)}-{m.group(3)}-{m.group(4)}",
        "catalog_release": pin["source"]["release"],
        "rpcs": counts["rpcs"],
        "client_callable": reach["client-callable"],
        "not_callable": {
            "no_program": reach.get("no-routine", 0) + reach.get("no-entry-point", 0),
            "no_context": reach.get("no-context", 0),
            "other": reach.get("out-of-order", 0) + reach.get("broker-exempt", 0),
        },
        "package_count": len(packages),
        "top": [p for p in packages if p["slug"] != "unassigned"][:TOP],
        "unassigned": next((p["rpcs"] for p in packages if p["slug"] == "unassigned"), 0),
    }
    # Display strings with thousands separators; Jekyll has no number-formatting filter.
    data["fmt"] = {k: f"{data[k]:,}" for k in ("rpcs", "client_callable", "unassigned")}
    for p in data["top"]:
        p["rpcs_fmt"] = f"{p['rpcs']:,}"
    if data["client_callable"] + sum(data["not_callable"].values()) != data["rpcs"]:
        fail("reach counts do not add up to the RPC total")
    if re.search(r"lakeraven|rpms-ops|cloud-rpms", json.dumps(data), re.I):
        fail("internal reference in output")

    with open(OUT, "w") as f:
        f.write(json.dumps(data, indent=2) + "\n")
    with open(OUT) as f:
        check = json.load(f)
    print(f"sync_rpcs: OK wrote {os.path.relpath(OUT, ROOT)}: {check['rpcs']} RPCs "
          f"({check['client_callable']} client-callable) in {check['package_count']} packages, "
          f"build {check['build']} (catalog {check['catalog_release']})")


if __name__ == "__main__":
    main()
