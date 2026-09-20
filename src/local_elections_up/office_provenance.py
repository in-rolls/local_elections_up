"""Resolve evidence paths, distinguishing intermediates from originals."""

from __future__ import annotations

import gzip
import hashlib
import json
import tarfile
from pathlib import Path

STRINGS = [
    "source_local_path_raw",
    "source_response_path_raw",
    "source_document_sha256_raw",
    "source_document_role",
    "source_document_hash_basis",
    "source_path_resolution_status",
]


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


class SourceProvenance:
    def __init__(self, root, source, artifact):
        self.root = root.resolve()
        self.adapter = source["adapter"]
        self.cache = {}
        self.receipt = None
        self.archive = None
        self.archive_path = None
        self.archive_prefix = None
        self.base = self.root
        if self.adapter == "csv":
            receipt_path = artifact.parent / "receipt.json"
            raw = receipt_path.read_bytes()
            self.base = Path(json.loads(raw)["source_root"]).resolve()
            self.receipt = {
                "path": receipt_path.relative_to(self.root).as_posix(),
                "sha256": hashlib.sha256(raw).hexdigest(),
            }
            archive = source.get("source_archive")
            if archive is not None:
                self.archive_path = (self.root / archive["path"]).resolve()
                if (
                    not self.archive_path.is_relative_to(self.root)
                    or digest(self.archive_path) != archive["sha256"]
                ):
                    raise ValueError("CSV source archive checksum changed")
                self.archive = tarfile.open(self.archive_path, "r:gz")
                self.archive_prefix = archive["member_prefix"].strip("/")
        elif self.adapter == "gp":
            self.base = artifact.parent
        elif self.adapter in {"portal", "urban"}:
            relative = artifact.relative_to(self.root).as_posix()
            if "/parsed/" in relative:
                self.base = self.root / relative.split("/parsed/", 1)[0]
            elif self.adapter == "portal":
                raise ValueError("Portal artifact has no acquisition-root boundary")
        elif self.adapter in {"zp_archive", "block_archive"}:
            self.base = artifact.parents[2]
        self.base = self.base.resolve()
        if not self.base.is_relative_to(self.root):
            raise ValueError("Source evidence root escapes the state repository")

    def checked(self, raw_path, expected):
        key = (raw_path, expected)
        if key in self.cache:
            return self.cache[key]
        candidates = []
        for base in (self.root, self.base):
            path = (base / raw_path).resolve()
            if not path.is_relative_to(self.root):
                raise ValueError("Source evidence path escapes the state repository")
            if path.is_file() and path not in candidates:
                candidates.append(path)
        matches = []
        for path in candidates:
            stored = digest(path)
            if expected is None or stored == expected:
                matches.append((path, stored, "stored_bytes"))
            elif path.suffix == ".gz":
                with gzip.open(path, "rb") as stream:
                    payload = hashlib.file_digest(stream, "sha256").hexdigest()
                if payload == expected:
                    matches.append((path, payload, "gzip_payload"))
        if not matches and self.archive is not None:
            member_name = f"{self.archive_prefix}/{raw_path}"
            try:
                member = self.archive.getmember(member_name)
            except KeyError:
                member = None
            if member is not None and member.isfile():
                stream = self.archive.extractfile(member)
                if stream is None:
                    raise ValueError(f"Cannot read source archive member {member_name}")
                with stream:
                    stored = hashlib.file_digest(stream, "sha256").hexdigest()
                if expected is None or stored == expected:
                    archive_path = self.archive_path.relative_to(self.root).as_posix()
                    matches.append(
                        (f"{archive_path}#{member_name}", stored, "tar_member")
                    )
        if len(matches) != 1:
            raise ValueError(
                f"Expected one hash-matched source for {raw_path}; found {len(matches)}"
            )
        path, sha, basis = matches[0]
        result = (
            path if isinstance(path, str) else path.relative_to(self.root).as_posix(),
            sha,
            basis,
        )
        self.cache[key] = result
        return result

    def apply(self, record):
        record["source_local_path_raw"] = record["source_local_path"]
        record["source_response_path_raw"] = record["source_response_path"]
        record["source_document_sha256_raw"] = record["source_document_sha256"]
        expected = record["source_document_sha256"]
        local = record["source_local_path"]
        if not local and self.adapter in {"zp_archive", "block_archive"}:
            if not expected:
                raise ValueError("Archived source lacks its PDF hash")
            local = f"raw/{expected}.body.gz"
        resolved = []
        for field, raw in (
            ("source_local_path", local),
            ("source_response_path", record["source_response_path"]),
        ):
            if raw:
                path, sha, basis = self.checked(raw, expected)
                record[field] = path
                resolved.append((sha, basis))
        if not resolved:
            raise ValueError("Observation has no resolvable source evidence path")
        if len({sha for sha, _ in resolved}) != 1:
            raise ValueError(
                "Document and response references identify different bytes"
            )
        record["source_document_sha256"] = resolved[0][0]
        record["source_document_hash_basis"] = resolved[0][1]
        record["source_path_resolution_status"] = "hash_verified"
        role = (
            "derived_intermediate"
            if self.adapter == "gp"
            else "local_csv_export"
            if self.adapter == "csv"
            else "source_document"
        )
        record["source_document_role"] = role
        if role in {"derived_intermediate", "local_csv_export"}:
            flag = "original_http_source_provenance_unresolved"
            if flag not in record["quality_flags"]:
                record["quality_flags"].append(flag)

    def manifest(self):
        return {
            "paths_relative_to": "state_repository",
            "source_base": self.base.relative_to(self.root).as_posix(),
            "source_root_receipt": self.receipt,
            "source_archive": (
                None
                if self.archive_path is None
                else {
                    "path": self.archive_path.relative_to(self.root).as_posix(),
                    "sha256": digest(self.archive_path),
                    "member_prefix": self.archive_prefix,
                }
            ),
            "resolver_sha256": digest(Path(__file__)),
            "policy": (
                "Resolve explicit source roots and verify file or gzip-payload hashes. "
                "Retain incoming paths and hashes in raw fields. Derived intermediates "
                "and local CSV exports do not establish original HTTP provenance."
            ),
        }
