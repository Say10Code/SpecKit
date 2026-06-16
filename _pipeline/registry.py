"""Spec Registry — parse .spec-registry.md and enrich via WhatTheSpec API."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from .config import ROOT
from ._resolve_spec import resolve_whatthespec

REGISTRY_PATH = ROOT / "_pipeline" / ".spec-registry.md"

# Matches a spec row: | **TS 31.102** | USIM Application | ... |
SPEC_ROW = re.compile(
    r'^\|\s*\*{0,2}((?:TS|TR|GSM)\s+[\d .A-Za-z/-]+?)\*{0,2}\s*\|'
)

# Matches a section header: ## Some Category
SECTION = re.compile(r'^## (.+)$')

# Matches external spec row: | **SGP.02** | GSMA | ... |
EXT_ROW = re.compile(
    r'^\|\s*\*{0,2}((?:SGP\.|ISO|GPC|TCA)\s*[\d .A-Za-z/-]*?)\*{0,2}\s*\|'
)


def parse_registry() -> dict[str, dict]:
    """Parse .spec-registry.md into structured data.

    Returns:
        {
            "3GPP": {  # org
                "31.102": {  # spec_number
                    "name": "USIM Application",
                    "title": "...",  # from WhatTheSpec
                    "category": "UICC / SIM / USIM",
                },
            },
            "GSMA": {...},
        }
    """
    if not REGISTRY_PATH.exists():
        return {}

    text = REGISTRY_PATH.read_text(encoding="utf-8")
    registry: dict[str, dict] = {}
    current_section = "Unknown"
    current_org = "3GPP"

    for line in text.split("\n"):
        # Track section headers
        sec_match = SECTION.match(line)
        if sec_match:
            section_name = sec_match.group(1).strip()
            current_section = section_name
            # Determine org from section context
            if "ETSI" in line and "3GPP" not in line:
                current_org = "ETSI"
            elif "GSMA" in line or "вне 3GPP" in line:
                current_org = "External"
            else:
                current_org = "3GPP"
            continue

        # Match 3GPP/ETSI spec rows
        m = SPEC_ROW.match(line)
        if not m:
            m = EXT_ROW.match(line)

        if m:
            spec_num = m.group(1).strip().replace(" ", "")
            # Extract name from the row (3rd column between pipes)
            parts = [p.strip() for p in line.split("|")]
            name = parts[2] if len(parts) > 2 and parts[2] else "(unnamed)"

            org = current_org
            if spec_num.startswith("TS 1") or spec_num.startswith("TR 1"):
                org = "ETSI"

            if org not in registry:
                registry[org] = {}

            registry[org][spec_num] = {
                "name": name.rstrip("*").strip(),
                "title": "",  # to be filled by WhatTheSpec
                "category": current_section,
            }

    return registry


def enrich_registry(dry_run: bool = True) -> list[dict]:
    """Fetch spec titles from WhatTheSpec API for all specs in registry.

    Args:
        dry_run: If True, show changes without writing.

    Returns:
        List of changes: {"spec": "31.102", "title": "...", "status": "new"/"updated"/"unchanged"}
    """
    registry = parse_registry()
    changes = []

    for org, specs in registry.items():
        if org == "External":
            continue  # GSMA/ISO/GP — not on WhatTheSpec

        for spec_num, info in specs.items():
            # Normalize spec number for API
            dotted = _normalize_spec(spec_num)
            if not dotted:
                continue

            try:
                meta = resolve_whatthespec(dotted)
                if meta and meta.title:
                    title = meta.title
                    if info["title"] != title:
                        old_title = info["title"]
                        changes.append({
                            "spec": dotted,
                            "org": org,
                            "title": title,
                            "status": "updated" if old_title else "new",
                            "old_title": old_title,
                        })
                        info["title"] = title
                else:
                    changes.append({
                        "spec": dotted,
                        "org": org,
                        "title": info.get("title", ""),
                        "status": "not_found",
                    })
            except Exception as e:
                changes.append({
                    "spec": dotted,
                    "org": org,
                    "title": str(e),
                    "status": "error",
                })

    if not dry_run and any(c["status"] in ("new", "updated") for c in changes):
        _write_registry(registry)

    return changes


def _normalize_spec(num: str) -> str | None:
    """Convert various spec formats to dotted notation for WhatTheSpec API.

    Handles: TS 31.102, TS31.102, 31.102, 31 102, GSM 11.11, TR 31.919
    Returns None for non-3GPP specs (SGP.02, ISO, GPC, TCA).
    """
    num = num.strip()

    # GSM 11.11 → "GSM 11.11" for API. Handle "GSM11.11" (space-less parse)
    if num.upper().startswith("GSM"):
        rest = num[3:].strip().replace(".", " ").replace("  ", " ").split()
        if len(rest) == 2:
            return f"GSM {rest[0]}.{rest[1]}"
        # "GSM1111" → "GSM 11.11"
        digits = num[3:].strip()
        if re.match(r'^\d{4}$', digits):
            return f"GSM {digits[:2]}.{digits[2:]}"
        return num

    # TS/TR prefix — strip it
    for prefix in ("TS", "TR"):
        upper = num.upper()
        if upper.startswith(prefix):
            # Could be "TS31.102", "TS 31.102", "TS 31 102"
            rest = num[len(prefix):].strip()
            num = rest
            break

    # Now num should be like "31.102", "31 102", "31102", "102221"
    # Remove spaces
    num = num.replace(" ", "")

    # If already dotted: "31.102" → keep
    if re.match(r'^\d+\.\d+(\.\d+)?$', num):
        return num

    # "31102" (5-6 digits, undotted) → "31.102"
    if re.match(r'^\d{5,6}$', num):
        if len(num) == 5:
            return f"{num[:2]}.{num[2:]}"
        elif len(num) == 6:
            return f"{num[:3]}.{num[3:]}"

    # ETSI 1xx.xxx format: "102221" → "102.221"
    if re.match(r'^\d{6}$', num) and num.startswith(('1', '2')):
        return f"{num[:3]}.{num[3:]}"

    return None


def _write_registry(enriched: dict[str, dict[str, str]]):
    """Write enriched registry — replace name column with WhatTheSpec titles, line by line."""
    if not REGISTRY_PATH.exists():
        print("[registry] ERROR: .spec-registry.md not found", file=sys.stderr)
        return

    lines = REGISTRY_PATH.read_text(encoding="utf-8").split("\n")
    replaced = 0

    for i, line in enumerate(lines):
        # Only process table rows: | **TS 31.102** | Name | ... |
        if not line.startswith("|"):
            continue

        parts = line.split("|")
        if len(parts) < 3:
            continue

        spec_cell = parts[1].strip()  # e.g. **TS 31.102**
        name_cell = parts[2].strip()  # e.g. USIM Application

        # Extract spec number from the cell (strip bold markers and spaces)
        spec_raw = spec_cell.replace("*", "").replace(" ", "").replace(" ", "")
        if not spec_raw:
            continue

        # Search enriched data for matching spec
        for org, specs in enriched.items():
            for spec_num, info in specs.items():
                title = info.get("title", "")
                if not title:
                    continue

                # Strip spaces for comparison
                sn_clean = spec_num.replace(" ", "")
                if len(sn_clean) < 3:
                    continue

                # Match: spec cell contains our number
                if sn_clean in spec_raw or spec_raw in sn_clean:
                    if name_cell != title and len(title) > len(name_cell):
                        # Replace the name column
                        parts[2] = f" {title} "
                        lines[i] = "|".join(parts)
                        replaced += 1
                        break

    if replaced > 0:
        REGISTRY_PATH.write_text("\n".join(lines), encoding="utf-8")
        print(f"[registry] Written: {replaced} titles updated in {REGISTRY_PATH}")
    else:
        print("[registry] No titles changed (all already up to date or no matches)")


# Remove old _spec_variants and regex-based write (no longer needed)


# ---------------------------------------------------------------------------
# Suggest: find relevant specs by topic keywords
# ---------------------------------------------------------------------------

def suggest_specs(topic: str) -> list[tuple[str, str, str, str]]:
    """Find specs relevant to a given topic.

    Searches .spec-registry.md by keyword matching against:
    - category headers
    - spec titles
    - key themes

    Args:
        topic: Natural language topic string.

    Returns:
        List of (spec_number, title, category, relevance) tuples.
    """
    registry = parse_registry()
    keywords = topic.lower().split()

    def _cat_match(cat_name: str, cat_kw: dict) -> str | None:
        """Fuzzy match a parsed section name to the keyword dictionary key.

        Handles multiple naming conventions:
        - "UICC / SIM / USIM (31-я серия)" — series ref stripped
        - "Non-Access Stratum (NAS) — 24-я серия" — domain label (NAS) kept, series ref stripped
        - "UE Capability (38.306 + 36.306 + cross-series)" — long spec list stripped
        """
        # 1) Strip trailing metadata after " — " (Russian dash convention)
        core = cat_name.split(' — ')[0].strip()
        # 2) Strip parenthetical series references (contain digits) but NOT domain labels
        #    Domain labels: (NAS), (LCS), (Location Services) — no digits
        #    Series refs: (31-я серия), (38.306 + 36.306 + ...) — contain digits
        core = re.sub(r'\s*\([^)]*\d[^)]*\)$', '', core).strip()
        core_lower = core.lower()

        for key in cat_kw:
            key_core = key.split(' — ')[0].strip().lower()
            if core_lower and key_core and (
                core_lower in key_core
                or key_core in core_lower
                or core_lower == key_core
            ):
                return key
        return None

    # Build category keyword map from section headers
    category_keywords = {
        "UICC / SIM / USIM": ["uicc", "sim", "usim", "card", "file", "ef_"],
        "UICC Platform / CAT / OTA": ["uicc", "cat", "stk", "ota", "over-the-air", "toolkit", "proactive"],
        "Security / Authentication": ["security", "auth", "aka", "milenage", "tuak", "key", "encrypt", "cipher", "suci", "supi"],
        "5G Core Architecture": ["5g", "core", "sba", "amf", "smf", "upf", "network function", "pcf", "nrf", "nwdaf", "5gc"],
        "Non-Access Stratum (NAS)": ["nas", "registration", "attach", "mobility", "emm", "esm", "5mm", "5gsm", "5gmm", "tau", "pdu session"],
        "NR / 5G RAN": ["nr", "ran", "rrc", "gnb", "radio", "beam", "phy", "mac", "pdcp", "rlc", "pdcp", "sdap", "coreset", "dc_", "ssb"],
        "Multi-RAT / NSA / EN-DC / Positioning": ["nsa", "en-dc", "ne-dc", "dual connectivity", "scg", "mcg", "sgnb", "lpp", "positioning protocol"],
        "LTE / E-UTRAN": ["lte", "4g", "e-utran", "enb", "s1", "x2", "epc"],
        "UE Capability": ["ue capability", "capability", "featureset", "featuregroup", "bandcombination", "band combination", "ue-capability", "ue radio access", "supportedband"],
        "V2X / Sidelink": ["v2x", "sidelink", "pc5", "vehicle", "c-v2x", "its", "prose"],
        "Positioning / LCS": ["positioning", "location", "lcs", "gmlc", "lmf", "nrppa", "otdoa", "gnss", "e-cid", "tdoa", "multi-rtt"],
        "NTN / Satellite": ["ntn", "satellite", "leo", "geo", "haps", "non-terrestrial", "space", "ephemeris"],
        "IoT / CIoT / RedCap": ["iot", "ciot", "redcap", "nb-iot", "emtc", "lte-m", "mtc", "constrained", "nidd", "early data"],
        "Service Aspects": ["service", "requirement", "plmn", "barring", "roaming", "vocabulary", "terminology", "glossary", "specification list", "henb", "hnb", "femtocell", "home node"],
        "Legacy GSM / 3G": ["gsm", "3g", "2g", "umts", "gprs", "sim"],
        "ETSI": ["etsi", "numbering", "aid", "ssp", "smart secure platform"],
        "Codecs / Media": ["codec", "voice", "media", "evs", "amr", "ims media", "voip", "rtp", "amr-wb"],
        "Core Network Protocols": ["diameter", "s6a", "rest", "nf", "nrf", "sba service", "gtp", "sbi", "nudm", "namf"],
        "OAM / Charging": ["charging", "cdr", "oam", "management", "trace", "mdt"],
        "Interworking / Migration": ["interworking", "migration", "epc", "n26", "handover", "eps fallback", "rat fallback"],
        "Conformance Testing": ["conformance", "test", "pct", "rf test", "rrm test", "ue test", "ota", "antenna", "emc", "electromagnetic", "a-gps", "protocol conformance", "ims conformance"],
    }

    # Score each category
    cat_scores = {}
    for cat, cat_kw in category_keywords.items():
        score = sum(1 for kw in keywords for ck in cat_kw if kw in ck or ck in kw)
        if score > 0:
            cat_scores[cat] = score

    # External sources keyword map
    external_prefixes = {
        "SGP": ["esim", "euicc", "rsp", "gsma", "profile", "subscription", "lpa", "lpad", "isd-r"],
        "ISO": ["iso", "apdu", "atr", "contact", "transport", "t=0", "t=1", "select", "fci", "smart card"],
        "GPC": ["globalplatform", "card spec", "isd", "ssd", "scp", "security domain", "gp"],
        "TCA": ["javacard", "stepping", "tca", "applet"],
    }

    results: list[tuple[str, str, str, str]] = []

    # Also add external specs based on keyword matching
    for org, specs in registry.items():
        if org == "External":
            for spec_num, info in specs.items():
                spec_text = f"{spec_num} {info.get('name', '')} {info.get('category', '')}".lower()
                for prefix, xkws in external_prefixes.items():
                    if spec_num.upper().startswith(prefix.upper()):
                        # This spec belongs to prefix group — check if query keywords match
                        kw_match = any(
                            any(ek in kw or kw in ek for ek in xkws)
                            for kw in keywords
                        )
                        if kw_match:
                            results.append((
                                spec_num,
                                info.get("name", info.get("title", "")),
                                info.get("category", "External"),
                                "P1 — внешний источник (не 3GPP, требуется ручная загрузка)"
                            ))
                        break
    for org, specs in registry.items():
        if org == "External":
            continue  # handled in the block above
        for spec_num, info in specs.items():
            cat = info.get("category", "")
            matched_key = _cat_match(cat, cat_scores)
            if matched_key:
                score = cat_scores[matched_key]
                relevance = _relevance_label(score)
                results.append((spec_num, info.get("name", info.get("title", "")), cat, relevance))

    # Sort: score by matched category, then by keyword density in spec name
    def _result_score(r: tuple) -> int:
        spec_num, name, cat, rel = r
        matched = _cat_match(cat, cat_scores)
        if not matched:
            return 0
        score = cat_scores[matched]
        # Bonus for keyword in spec name
        spec_text = f"{spec_num} {name}".lower()
        score += sum(1 for kw in keywords if kw in spec_text)
        return score

    results.sort(key=_result_score, reverse=True)

    # Deduplicate: keep highest-scoring entry per spec number
    seen: set[str] = set()
    deduped: list[tuple[str, str, str, str]] = []
    for r in results:
        spec_num = r[0]
        if spec_num not in seen:
            seen.add(spec_num)
            deduped.append(r)
    return deduped


def _relevance_label(score: int) -> str:
    if score >= 5:
        return "P0 — ядро темы"
    elif score >= 3:
        return "P1 — непосредственно связано"
    elif score >= 2:
        return "P2 — контекст"
    else:
        return "P3 — косвенно"


def print_suggestions(results: list[tuple[str, str, str, str]]):
    """Print spec suggestions in a formatted table."""
    if not results:
        print("[registry] No specs found for this topic.")
        print("  Try different keywords or search the web for non-3GPP sources.")
        return

    print(f"[registry] Found {len(results)} relevant specs:\n")
    for spec_num, name, cat, relevance in results[:20]:
        print(f"  {spec_num:16s} {relevance:28s} {cat}")
        if name:
            print(f"  {'':16s} {name}")
        print()
