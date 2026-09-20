#!/usr/bin/env python3
# /// script
# requires-python = ">=3.11"
# dependencies = ["beautifulsoup4", "requests", "pyarrow"]
# ///
"""Checkpointed acquisition and parsing of UP's separate 2017 urban winner table."""

from __future__ import annotations

import argparse
import collections
import datetime as dt
import fcntl
import gzip
import hashlib
import json
import re
import time
import unicodedata
from pathlib import Path
from urllib.parse import urlparse

import pyarrow as pa
import pyarrow.parquet as pq
import requests
from bs4 import BeautifulSoup

URL = "https://sec.up.nic.in/eleclive/NewWinnerList.aspx"
PREFIX = "ctl00$ContentPlaceHolder1$"
POST = PREFIX + "DropDownList1"
DISTRICT = PREFIX + "ddlDistrict"
GRID = PREFIX + "winnerdetail"
TITLE = (
    "\u0928\u0917\u0930\u0940\u092f \u0928\u093f\u0915\u093e\u092f"
    " \u0938\u093e\u092e\u093e\u0928\u094d\u092f"
    " \u0928\u093f\u0930\u094d\u0935\u093e\u091a\u0928 2017 \u0915\u0947"
    " \u0918\u094b\u0937\u093f\u0924 \u092a\u0930\u093f\u0923\u093e\u092e \u0915\u093e"
    " \u0935\u093f\u0935\u0930\u0923"
)
HEADERS = [
    "\u091c\u0928\u092a\u0926",
    "\u0928\u093f\u0915\u093e\u092f \u0915\u093e \u0928\u093e\u092e",
    "\u0935\u093e\u0930\u094d\u0921 \u0915\u093e \u0928\u093e\u092e",
    "\u092a\u0926 \u0915\u093e \u0906\u0930\u0915\u094d\u0937\u0923",
    "\u0909\u092e\u094d\u092e\u0940\u0926\u0935\u093e\u0930",
    "\u092a\u093f\u0924\u093e/\u092a\u0924\u093f",
    (
        "\u092a\u094d\u0930\u0924\u094d\u092f\u093e\u0936\u0940 \u0915\u093e"
        " \u091c\u093e\u0924\u093f/\u0935\u0930\u094d\u0917"
    ),
    (
        "\u0936\u0948\u0915\u094d\u0937\u093f\u0915"
        " \u092f\u094b\u0917\u094d\u092f\u0924\u093e"
    ),
    "\u092a\u093e\u0930\u094d\u091f\u0940 \u0915\u093e \u0928\u093e\u092e",
    "\u0932\u093f\u0902\u0917",
    "\u0906\u092f\u0941",
    "\u092e\u094b\u092c\u093e\u0907\u0932 \u0928\u0902\u0966",
    "\u092a\u094d\u0930\u093e\u092a\u094d\u0924 \u0935\u0948\u0927 \u092e\u0924",
    "\u092a\u094d\u0930\u093e\u092a\u094d\u0924 \u092e\u0924 %",
    "\u092e\u0924\u0926\u093e\u0928 %",
    "\u092a\u0930\u093f\u0923\u093e\u092e",
]
POSTS = {
    "7": (
        (
            "\u0928\u0917\u0930 \u0928\u093f\u0917\u092e"
            " \u092e\u0939\u093e\u092a\u094c\u0930"
        ),
        "\u0928\u0917\u0930 \u0928\u093f\u0917\u092e",
        "ulb_head",
    ),
    "8": (
        (
            "\u0928\u0917\u0930 \u0928\u093f\u0917\u092e"
            " \u092a\u093e\u0930\u094d\u0937\u0926"
        ),
        "\u0928\u0917\u0930 \u0928\u093f\u0917\u092e",
        "ulb_ward",
    ),
    "9": (
        (
            "\u0928\u0917\u0930 \u092a\u093e\u0932\u093f\u0915\u093e"
            " \u092a\u0930\u093f\u0937\u0926 \u0905\u0927\u094d\u092f\u0915\u094d\u0937"
        ),
        (
            "\u0928\u0917\u0930 \u092a\u093e\u0932\u093f\u0915\u093e"
            " \u092a\u0930\u093f\u0937\u0926"
        ),
        "ulb_head",
    ),
    "10": (
        (
            "\u0928\u0917\u0930 \u092a\u093e\u0932\u093f\u0915\u093e"
            " \u092a\u0930\u093f\u0937\u0926 \u0938\u0926\u0938\u094d\u092f"
        ),
        (
            "\u0928\u0917\u0930 \u092a\u093e\u0932\u093f\u0915\u093e"
            " \u092a\u0930\u093f\u0937\u0926"
        ),
        "ulb_ward",
    ),
    "11": (
        (
            "\u0928\u0917\u0930 \u092a\u0902\u091a\u093e\u092f\u0924"
            " \u0905\u0927\u094d\u092f\u0915\u094d\u0937"
        ),
        "\u0928\u0917\u0930 \u092a\u0902\u091a\u093e\u092f\u0924",
        "ulb_head",
    ),
    "12": (
        (
            "\u0928\u0917\u0930 \u092a\u0902\u091a\u093e\u092f\u0924"
            " \u0938\u0926\u0938\u094d\u092f"
        ),
        "\u0928\u0917\u0930 \u092a\u0902\u091a\u093e\u092f\u0924",
        "ulb_ward",
    ),
}
RAW_COLUMNS = {
    0: "district_name_raw",
    1: "local_body_name_raw",
    2: "ward_name_raw",
    3: "seat_reservation_raw",
    4: "winner_name_raw",
    5: "relation_name_raw",
    6: "candidate_category_raw",
    7: "education_raw",
    8: "party_name_raw",
    9: "sex_raw",
    10: "age_raw",
    12: "valid_votes_raw",
    13: "vote_share_raw",
    14: "turnout_raw",
    15: "result_status_raw",
}


DISTRICT_LABEL_ALIASES = {
    ("74", "\u092e\u093f\u0930\u094d\u091c\u093e\u092a\u0941\u0930"): {
        "printed_label": "\u092e\u0940\u0930\u091c\u093e\u092a\u0941\u0930",
        "evidence_source_sha256": (
            "2e6ebb53fbafa99df6bf4078009fdf3b7eb98d584ca7aac35935972bfff10f5b"
        ),
    },
    ("2", "\u092e\u0941\u091c\u092b\u094d\u092b\u0930 \u0928\u0917\u0930"): {
        "printed_label": (
            "\u092e\u0941\u091c\u093c\u092b\u094d\u092b\u0930\u0928\u0917\u0930"
        ),
        "evidence_source_sha256": (
            "ed15f220f19d026eadd32398a37590a0eb561becaf803c4e2235a4975278bb09"
        ),
    },
    ("27", "\u092b\u0930\u0942\u0916\u093e\u092c\u093e\u0926"): {
        "printed_label": (
            "\u092b\u093c\u0930\u094d\u0930\u0941\u0916\u093e\u092c\u093e\u0926"
        ),
        "evidence_source_sha256": (
            "4bf83f73c97c8028f0c73e3e411b68dbedeae9140c9471216d0a2fac9f81a1df"
        ),
    },
    ("21", "\u0910\u091f\u093e"): {
        "printed_label": "\u090f\u091f\u093e",
        "evidence_source_sha256": (
            "afea1df0648c3c7b66068743ad2d515245ec66e1f826e79e10f531e2f7162b5e"
        ),
    },
}


def norm(value):
    return " ".join(unicodedata.normalize("NFC", value).split())


def digest(data):
    return hashlib.sha256(data).hexdigest()


def now():
    return dt.datetime.now(dt.UTC).isoformat()


def atomic_json(path, value):
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


def form(soup):
    values = {
        item["name"]: item.get("value", "")
        for item in soup.select("input[type=hidden][name]")
    }
    for select in soup.select("select[name]"):
        option = select.find("option", selected=True) or select.find("option")
        values[select["name"]] = option.get("value", "") if option else ""
    return values


def table(data, post, district):
    soup = BeautifulSoup(data, "html.parser")
    if TITLE not in [norm(h.get_text(" ", strip=True)) for h in soup.find_all("h3")]:
        raise ValueError("The explicit 2017 results heading is missing")
    values = form(soup)
    if values.get(POST) != post or values.get(DISTRICT) != district:
        raise ValueError("The response changed the requested post/district scope")
    grid = soup.find("table", id="ContentPlaceHolder1_winnerdetail")
    if grid is None:
        raise ValueError("The 2017 winner table is missing")
    if norm(grid.get_text(" ", strip=True)) == "No records" and not grid.find("th"):
        return soup, [], False
    headers = [norm(h.get_text(" ", strip=True)) for h in grid.find_all("th")]
    expected_headers = (
        HEADERS if POSTS[post][2] == "ulb_ward" else HEADERS[:2] + HEADERS[3:]
    )
    if headers != [norm(h) for h in expected_headers]:
        raise ValueError("The 2017 winner table header schema changed")
    rows = []
    for tr in grid.find_all("tr"):
        if tr.find_parent("table") is not grid:
            continue
        cells = tr.find_all("td", recursive=False)
        if not cells or (len(cells) == 1 and cells[0].get("colspan")):
            continue
        if len(cells) != len(expected_headers):
            raise ValueError("Unexpected number of cells in a winner row")
        values = [norm(c.get_text(" ", strip=True)) for c in cells]
        if len(expected_headers) == 15:
            values.insert(2, "")
        rows.append(values)
    if not rows:
        raise ValueError("No winner rows; an empty response is not completion")
    option = soup.find("select", attrs={"name": DISTRICT}).find(
        "option", attrs={"value": district}
    )
    if option is None:
        raise ValueError("Requested district is absent from response controls")

    def district_key(text):
        return norm(text).replace("\u093c", "")

    selected_label = norm(option.get_text(" ", strip=True))
    allowed_labels = {district_key(selected_label)}
    alias = DISTRICT_LABEL_ALIASES.get((district, selected_label))
    if alias is not None:
        allowed_labels.add(district_key(alias["printed_label"]))
    if district != "0" and any(
        district_key(row[0]) not in allowed_labels for row in rows
    ):
        raise ValueError("Printed row district differs from the selected district")
    next_links = {
        a.get("href", "")
        for a in grid.find_all("a")
        if norm(a.get_text(" ", strip=True)) == "Next" and a.get("href")
    }
    expected = "javascript:__doPostBack('" + GRID + "','Page$Next')"
    if next_links and next_links != {expected}:
        raise ValueError("Unexpected winner-table pagination target")
    return soup, rows, bool(next_links)


class RequestLimit(Exception):
    pass


class Client:
    def __init__(self, root, maximum, interval, cookies):
        self.root = root
        self.maximum = maximum
        self.interval = interval
        self.requests = 0
        self.last_started = 0.0
        self.session = requests.Session()
        self.session.cookies.update(cookies)
        for name in ("raw", "forms"):
            (root / name).mkdir(parents=True, exist_ok=True)

    def archive(self, folder, data, suffix):
        sha = digest(data)
        path = self.root / folder / (sha + suffix + ".gz")
        if not path.exists():
            path.write_bytes(gzip.compress(data, mtime=0))
        return sha

    def request(self, values=None):
        form_sha = None
        if values is not None:
            form_sha = self.archive(
                "forms", json.dumps(values, sort_keys=True).encode(), ".json"
            )
        for attempt in range(5):
            if self.requests >= self.maximum:
                raise RequestLimit
            time.sleep(max(0, self.interval - (time.monotonic() - self.last_started)))
            self.last_started = time.monotonic()
            self.requests += 1
            receipt = {
                "retrieved_utc": now(),
                "url": URL,
                "method": "POST" if values else "GET",
                "form_sha256": form_sha,
                "attempt": attempt + 1,
            }
            try:
                response = self.session.request(
                    receipt["method"], URL, data=values, timeout=(15, 60)
                )
            except requests.RequestException as exc:
                receipt["error_type"] = type(exc).__name__
                self.log(receipt)
                if attempt == 4:
                    raise
                time.sleep(min(30, 2 ** (attempt + 1)))
                continue
            sha = self.archive("raw", response.content, ".html")
            receipt.update(
                http_status=response.status_code,
                final_url=response.url,
                source_sha256=sha,
                bytes=len(response.content),
                content_type=response.headers.get("content-type"),
            )
            self.log(receipt)
            if response.status_code in (429, 500, 502, 503, 504) and attempt < 4:
                retry_after = response.headers.get("retry-after", "")
                delay = (
                    float(retry_after) if retry_after.isdigit() else 2 ** (attempt + 1)
                )
                time.sleep(min(120, delay))
                continue
            response.raise_for_status()
            if urlparse(response.url).hostname != urlparse(URL).hostname:
                raise ValueError("Unexpected result-host redirect")
            return response.content, sha
        raise RuntimeError("Retry loop exhausted")

    def log(self, receipt):
        with (self.root / "requests.jsonl").open("a") as stream:
            stream.write(json.dumps(receipt) + "\n")


def cached(root, sha):
    data = gzip.decompress((root / "raw" / (sha + ".html.gz")).read_bytes())
    if digest(data) != sha:
        raise ValueError("Cached response hash mismatch")
    return data


def fetch(root, posts, maximum, interval):
    checkpoint = root / "checkpoint.json"
    state = (
        json.loads(checkpoint.read_text())
        if checkpoint.exists()
        else {
            "version": 2,
            "url": URL,
            "election_year": 2017,
            "requested_posts": posts,
            "districts": [],
            "units": {},
        }
    )
    if (
        state.get("version") != 2
        or state.get("url") != URL
        or state.get("election_year") != 2017
        or state.get("requested_posts") != posts
    ):
        raise ValueError(
            "Use a separate version-2 district-query root; query scope must match"
        )
    client = Client(root, maximum, interval, state.get("cookies", {}))
    data = None
    sha = None

    def save():
        state["updated_utc"] = now()
        state["cookies"] = requests.utils.dict_from_cookiejar(client.session.cookies)
        atomic_json(checkpoint, state)

    try:
        if not state["districts"]:
            data, sha = client.request()
            soup, _, _ = table(data, "8", "0")
            state["districts"] = [
                {"code": o["value"], "label": norm(o.get_text(" ", strip=True))}
                for o in soup.find("select", attrs={"name": DISTRICT}).find_all(
                    "option"
                )
                if o.get("value") not in (None, "", "0")
            ]
            codes = [d["code"] for d in state["districts"]]
            if not codes or len(codes) != len(set(codes)):
                raise ValueError("Empty or ambiguous source district frame")
            available = {
                o.get("value")
                for o in soup.find("select", attrs={"name": POST}).find_all("option")
            }
            if not set(posts).issubset(available):
                raise ValueError("Requested post is absent from the source")
            state["frame_source_sha256"] = sha
            save()
        for district in state["districts"]:
            district_code = district["code"]
            for post in posts:
                unit_key = post + ":" + district_code
                unit = state["units"].setdefault(
                    unit_key,
                    {
                        "post": post,
                        "district_code": district_code,
                        "district_label": district["label"],
                        "pages": [],
                        "complete": False,
                    },
                )
                if unit["complete"]:
                    continue
                seen = {p["rows_sha256"] for p in unit["pages"]}
                if unit["pages"]:
                    data = cached(root, unit["pages"][-1]["source_sha256"])
                    soup, _, has_next = table(data, post, district_code)
                    if not has_next:
                        raise ValueError("Incomplete checkpoint has no next page")
                    values = form(soup)
                    values.update(__EVENTTARGET=GRID, __EVENTARGUMENT="Page$Next")
                    data, sha = client.request(values)
                else:
                    if data is None:
                        data, sha = client.request()
                    soup = BeautifulSoup(data, "html.parser")
                    for control, target in ((POST, post), (DISTRICT, district_code)):
                        values = form(soup)
                        if values.get(control) != target:
                            values[control] = target
                            values.update(__EVENTTARGET=control, __EVENTARGUMENT="")
                            data, sha = client.request(values)
                            soup = BeautifulSoup(data, "html.parser")
                    grid = soup.find("table", id="ContentPlaceHolder1_winnerdetail")
                    first_links = (
                        {
                            a.get("href", "")
                            for a in grid.find_all("a")
                            if norm(a.get_text(" ", strip=True)) == "First"
                            and a.get("href")
                        }
                        if grid
                        else set()
                    )
                    if first_links:
                        expected = (
                            "javascript:__doPostBack('" + GRID + "','Page$First')"
                        )
                        if first_links != {expected}:
                            raise ValueError("Unexpected first-page reset target")
                        values = form(soup)
                        values.update(__EVENTTARGET=GRID, __EVENTARGUMENT="Page$First")
                        data, sha = client.request(values)
                while True:
                    soup, rows, has_next = table(data, post, district_code)
                    fingerprint = digest(json.dumps(rows, ensure_ascii=False).encode())
                    if fingerprint in seen:
                        raise ValueError(
                            "Repeated winner page; refusing pagination loop"
                        )
                    seen.add(fingerprint)
                    unit["pages"].append(
                        {
                            "page": len(unit["pages"]) + 1,
                            "source_sha256": sha,
                            "row_count": len(rows),
                            "rows_sha256": fingerprint,
                            "has_next": has_next,
                        }
                    )
                    unit["complete"] = not has_next
                    unit["row_count"] = sum(p["row_count"] for p in unit["pages"])
                    unit["source_cap_suspected"] = unit["row_count"] >= 1000
                    unit["status"] = (
                        "source_empty"
                        if not rows
                        else "pager_exhausted"
                        if not has_next
                        else "in_progress"
                    )
                    save()
                    print(
                        json.dumps(
                            {
                                "event": "page_saved",
                                "post": post,
                                "district": district_code,
                                "page": len(unit["pages"]),
                                "rows": len(rows),
                                "requests": client.requests,
                                "complete": unit["complete"],
                                "source_cap_suspected": unit["source_cap_suspected"],
                            }
                        ),
                        flush=True,
                    )
                    if not has_next:
                        break
                    values = form(soup)
                    values.update(__EVENTTARGET=GRID, __EVENTARGUMENT="Page$Next")
                    data, sha = client.request(values)
    except RequestLimit:
        save()
        print(
            json.dumps({"event": "paused_request_limit", "requests": client.requests}),
            flush=True,
        )
        return False
    finally:
        client.session.close()
    return all(
        state["units"].get(post + ":" + d["code"], {}).get("complete", False)
        for d in state["districts"]
        for post in posts
    )


def category(value):
    text = norm(value).replace("\u093c", "")
    woman = "\u092e\u0939\u093f\u0932\u093e" in text
    if text in (
        "\u0905\u0928\u093e\u0930\u0915\u094d\u0937\u093f\u0924",
        "\u092e\u0939\u093f\u0932\u093e",
        (
            "\u0905\u0928\u093e\u0930\u0915\u094d\u0937\u093f\u0924"
            " \u092e\u0939\u093f\u0932\u093e"
        ),
    ):
        return "NONE", woman
    for label, code in (
        (
            (
                "\u0905\u0928\u0941\u0938\u0942\u091a\u093f\u0924"
                " \u091c\u0928\u091c\u093e\u0924\u093f"
            ),
            "ST",
        ),
        (
            "\u0905\u0928\u0941\u0938\u0942\u091a\u093f\u0924 \u091c\u093e\u0924\u093f",
            "SC",
        ),
        (
            (
                "\u0905\u0928\u094d\u092f \u092a\u093f\u091b\u0921\u093e"
                " \u0935\u0930\u094d\u0917"
            ),
            "BC",
        ),
    ):
        if text in (label, label + " \u092e\u0939\u093f\u0932\u093e"):
            return code, woman
    return None, None


def number(value, integer, flag, flags):
    clean = value.replace(",", "").strip()
    if clean in ("", "-", "--"):
        return None
    try:
        result = int(clean) if integer else float(clean)
    except ValueError:
        flags.append(flag)
        return None
    if result < 0 or (not integer and not 0 <= result <= 100):
        flags.append(flag)
        return None
    return result


def observation(cells, post, page, row_number, sha, complete):
    label, body_type, tier = POSTS[post]
    flags = ["independent_review_pending", "geography_unvalidated"]
    row = {field: cells[index] for index, field in RAW_COLUMNS.items()}
    row.update(
        observation_id=digest(f"{sha}:{post}:{row_number}".encode()),
        source_url=URL,
        source_sha256=sha,
        source_response_path=f"raw/{sha}.html.gz",
        source_page=page,
        source_row_on_page=row_number,
        election_year=2017,
        post_code_raw=post,
        post_label_raw=label,
        local_body_type_raw=body_type,
        body_type_source="selected_post_control",
        tier=tier,
        source_query_complete=complete,
        assignment_usable=False,
        source_header_count=16 if tier == "ulb_ward" else 15,
        source_ward_column_present=tier == "ulb_ward",
    )
    caste, woman = category(row["seat_reservation_raw"])
    row.update(caste_reservation=caste, woman_reserved=woman)
    if caste is None:
        flags.append("seat_category_unresolved")
    candidate_caste, candidate_woman = category(row["candidate_category_raw"])
    row.update(
        candidate_caste_reported=candidate_caste,
        candidate_woman_label_reported=candidate_woman,
    )
    if candidate_caste is None:
        flags.append("candidate_category_unresolved")
    ward = None
    ward_label = None
    if tier == "ulb_ward":
        match = re.fullmatch(
            r"([0-9\u0966-\u096f]+)\s*[-\u2013]\s*(.+)", row["ward_name_raw"]
        )
        if match:
            ward = int("".join(str(unicodedata.digit(c)) for c in match.group(1)))
            ward_label = match.group(2).strip()
        if ward is None or ward < 1:
            ward = None
            flags.append("ward_unresolved")
    elif row["ward_name_raw"] not in ("", "-", "--"):
        flags.append("head_has_ward_text")
    row.update(ward=ward, ward_label_source_raw=ward_label)
    row["age"] = number(row["age_raw"], True, "age_unresolved", flags)
    row["valid_votes"] = number(row["valid_votes_raw"], True, "votes_unresolved", flags)
    row["vote_share"] = number(
        row["vote_share_raw"], False, "vote_share_unresolved", flags
    )
    row["turnout"] = number(row["turnout_raw"], False, "turnout_unresolved", flags)
    if not row["winner_name_raw"]:
        flags.append("winner_missing")
    if not row["district_name_raw"] or not row["local_body_name_raw"]:
        flags.append("body_context_missing")
    row["quality_flags"] = ";".join(sorted(flags))
    return row


def parse(root):
    state = json.loads((root / "checkpoint.json").read_text())
    if (
        state.get("version") != 2
        or state.get("url") != URL
        or state.get("election_year") != 2017
    ):
        raise ValueError("Expected a version-2 district-query checkpoint")
    soup, _, _ = table(cached(root, state["frame_source_sha256"]), "8", "0")
    frame = [
        {"code": o["value"], "label": norm(o.get_text(" ", strip=True))}
        for o in soup.find("select", attrs={"name": DISTRICT}).find_all("option")
        if o.get("value") not in (None, "", "0")
    ]
    if frame != state["districts"]:
        raise ValueError("District frame differs from its pinned source")
    planned = {
        post + ":" + d["code"]: (post, d)
        for d in frame
        for post in state["requested_posts"]
    }
    if set(state["units"]) - set(planned) or set(state["requested_posts"]) - set(POSTS):
        raise ValueError("Unexpected district-query scope")
    records = []
    coverage = []
    for unit_key, (post, district) in planned.items():
        unit = state["units"].get(unit_key, {"pages": [], "complete": False})
        row_count = sum(p["row_count"] for p in unit["pages"])
        capped = row_count >= 1000
        if unit["pages"]:
            if unit["post"] != post or unit["district_code"] != district["code"]:
                raise ValueError("Query checkpoint identity mismatch")
            if [p["page"] for p in unit["pages"]] != list(
                range(1, len(unit["pages"]) + 1)
            ):
                raise ValueError("Noncontiguous query pages")
            if any(not p["has_next"] for p in unit["pages"][:-1]):
                raise ValueError("A terminal source page is followed by more pages")
            if unit["complete"] != (not unit["pages"][-1]["has_next"]):
                raise ValueError("Query completion differs from source pagination")
        coverage.append(
            {
                "post_code_raw": post,
                "query_district_code_raw": district["code"],
                "query_district_name_raw": district["label"],
                "pages": len(unit["pages"]),
                "rows": row_count,
                "pager_exhausted": unit["complete"],
                "source_empty": unit["complete"] and row_count == 0,
                "source_cap_suspected": capped,
            }
        )
        for page in unit["pages"]:
            sha = page["source_sha256"]
            _, cells, has_next = table(cached(root, sha), post, district["code"])
            if len(cells) != page["row_count"] or has_next != page["has_next"]:
                raise ValueError("Cached page differs from its acquisition receipt")
            if (
                digest(json.dumps(cells, ensure_ascii=False).encode())
                != page["rows_sha256"]
            ):
                raise ValueError("Cached row fingerprint mismatch")
            for index, values in enumerate(cells, 1):
                row = observation(
                    values, post, page["page"], index, sha, unit["complete"]
                )
                row.update(
                    query_district_code_raw=district["code"],
                    query_district_name_raw=district["label"],
                )
                alias = DISTRICT_LABEL_ALIASES.get(
                    (district["code"], district["label"])
                )
                uses_alias = alias is not None and norm(values[0]) == norm(
                    alias["printed_label"]
                )
                row["district_label_match_method"] = (
                    "explicit_source_label_alias"
                    if uses_alias
                    else "normalized_source_label"
                )
                row["district_label_alias_evidence_sha256"] = (
                    alias["evidence_source_sha256"] if uses_alias else None
                )
                if capped:
                    row["quality_flags"] += ";source_query_possibly_capped"
                records.append(row)
    if not records:
        raise ValueError("No acquired winner records")
    if len({r["observation_id"] for r in records}) != len(records):
        raise ValueError("Duplicate source-observation identity")
    seat_counts = collections.Counter(
        (
            r["post_code_raw"],
            r["district_name_raw"],
            r["local_body_name_raw"],
            r["ward"],
        )
        for r in records
        if r["tier"] == "ulb_head" or r["ward"] is not None
    )
    for row in records:
        key = (
            row["post_code_raw"],
            row["district_name_raw"],
            row["local_body_name_raw"],
            row["ward"],
        )
        if seat_counts[key] > 1:
            row["quality_flags"] += ";duplicate_source_seat_key_requires_review"
    output = root / "parsed" / dt.datetime.now(dt.UTC).strftime("%Y%m%dT%H%M%S%fZ")
    output.mkdir(parents=True, exist_ok=False)
    artifact = output / "winner_reservations.parquet"
    pq.write_table(pa.Table.from_pylist(records), artifact, compression="zstd")
    coverage_artifact = output / "query_coverage.parquet"
    pq.write_table(
        pa.Table.from_pylist(coverage), coverage_artifact, compression="zstd"
    )
    flags = collections.Counter(
        f for r in records for f in r["quality_flags"].split(";")
    )
    receipt = {
        "parsed_utc": now(),
        "source_url": URL,
        "election_year": 2017,
        "rows": len(records),
        "rows_by_post": dict(collections.Counter(r["post_code_raw"] for r in records)),
        "acquisition_scope": "district_partitioned_urban_winners",
        "requested_posts": state["requested_posts"],
        "source_districts": len(frame),
        "planned_queries": len(coverage),
        "completed_queries": sum(q["pager_exhausted"] for q in coverage),
        "empty_queries": sum(q["source_empty"] for q in coverage),
        "all_planned_queries_complete": all(q["pager_exhausted"] for q in coverage),
        "queries_at_source_cap": [q for q in coverage if q["source_cap_suspected"]],
        "query_coverage_sha256": digest(coverage_artifact.read_bytes()),
        "frame_source_sha256": state["frame_source_sha256"],
        "district_label_alias_rules": [
            {"district_code": code, "selector_label": label, **rule}
            for (code, label), rule in DISTRICT_LABEL_ALIASES.items()
        ],
        "district_label_alias_rows": sum(
            r["district_label_match_method"] == "explicit_source_label_alias"
            for r in records
        ),
        "quality_flags": dict(flags),
        "assignment_usable": False,
        "artifact_sha256": digest(artifact.read_bytes()),
        "script_sha256": digest(Path(__file__).read_bytes()),
        "checkpoint_sha256": digest((root / "checkpoint.json").read_bytes()),
        "source_headers_by_post": {
            post: HEADERS if POSTS[post][2] == "ulb_ward" else HEADERS[:2] + HEADERS[3:]
            for post in state["requested_posts"]
        },
        "excluded_derived_source_columns": [HEADERS[11]],
        "scope": (
            "Reported 2017 winners. Seat reservation and candidate category are"
            " distinct source fields; no administrative-code validation or independent"
            " source certification."
        ),
    }
    atomic_json(output / "parse_receipt.json", receipt)
    atomic_json(
        output / "dictionary.json",
        {
            "source_column_mapping": {
                HEADERS[i]: name for i, name in RAW_COLUMNS.items()
            },
            "raw_string_normalization": (
                "NFC and whitespace only; exact HTML retained by source hash."
            ),
            "ward": (
                "Leading printed ward number, only for member posts; not an"
                " administrative code."
            ),
            "source_header_count": (
                "15 for head tables and 16 for ward tables; these are distinct accepted"
                " source schemas."
            ),
            "source_ward_column_present": (
                "False for head tables, which omit the ward column. Their empty"
                " ward_name_raw is an internal schema placeholder, not a printed blank."
            ),
            "caste_reservation": (
                "Typed seat reservation, not candidate caste; null for unknown labels."
            ),
            "woman_reserved": (
                "Whether the printed seat reservation includes women; null if category"
                " unknown."
            ),
            "candidate_caste_reported": (
                "Candidate classification reported by the source, never used to fill"
                " seat reservation."
            ),
            "candidate_woman_label_reported": (
                "Whether the candidate-category label includes women; separate from"
                " reported sex."
            ),
            "source_page": (
                "One-based result-table page within the selected post and district."
            ),
            "query_district_code_raw": (
                "Portal control value, not a validated administrative or cross-year"
                " code."
            ),
            "query_district_name_raw": (
                "District label in the pinned source query frame."
            ),
            "district_label_match_method": (
                "Normalized exact source-label match or an explicit"
                " code-and-selector-scoped spelling alias; not administrative identity"
                " validation."
            ),
            "district_label_alias_evidence_sha256": (
                "Hash of the cached response documenting the explicit selector/table"
                " spelling variation; null when no alias was used."
            ),
            "query_coverage": (
                "Every planned district/post query, including explicit source-empty,"
                " incomplete and potentially capped queries."
            ),
            "source_row_on_page": (
                "One-based data-row ordinal excluding headers and pagination."
            ),
            "body_type_source": (
                "Body type comes from the selected post control, not an unprinted row"
                " column."
            ),
            "source_response_path": (
                "Relative to the acquisition root; gzip-compressed exact HTTP body."
            ),
            "source_query_complete": (
                "The selected post's Next pager was exhausted, not proof of universe"
                " completeness."
            ),
            "assignment_usable": (
                "Always false while independent review and geographic reconciliation"
                " remain pending."
            ),
            "phone_policy": (
                "Phone numbers excluded from derived records; restricted-use original"
                " HTML retains source fidelity."
            ),
            "numeric_fields": (
                "age and valid_votes are integers; vote_share and turnout are"
                " percentages on [0,100]. Original strings retained."
            ),
        },
    )
    print(
        json.dumps({"output": str(output), **receipt}, ensure_ascii=False), flush=True
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", choices=("fetch", "parse", "all"), default="all")
    parser.add_argument(
        "--source-root",
        type=Path,
        default=Path("data/recovery/sec_historical_results/ulb2017/district_queries"),
    )
    parser.add_argument(
        "--posts", nargs="+", choices=list(POSTS), default=["8", "10", "12"]
    )
    parser.add_argument("--max-requests", type=int, default=2000)
    parser.add_argument("--interval", type=float, default=1.0)
    args = parser.parse_args()
    if args.max_requests < 1 or args.interval < 0:
        parser.error("max-requests must be positive and interval nonnegative")
    args.source_root.mkdir(parents=True, exist_ok=True)
    with (args.source_root / ".harvest.lock").open("a") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        if args.stage in ("fetch", "all") and not fetch(
            args.source_root, args.posts, args.max_requests, args.interval
        ):
            raise SystemExit(2)
        if args.stage in ("parse", "all"):
            parse(args.source_root)


if __name__ == "__main__":
    main()
