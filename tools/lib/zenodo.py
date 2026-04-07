"""Zenodo API client for DOI minting."""

import json
from pathlib import Path

import requests


class ZenodoError(Exception):
    """Raised when a Zenodo API call fails."""


class ZenodoClient:
    def __init__(self, token: str, sandbox: bool = False):
        self.token = token
        self.sandbox = sandbox
        if sandbox:
            self.base_url = "https://sandbox.zenodo.org/api"
        else:
            self.base_url = "https://zenodo.org/api"
        self.headers = {"Authorization": f"Bearer {token}"}

    def _check(self, resp: requests.Response, context: str) -> None:
        if resp.status_code >= 400:
            raise ZenodoError(f"{context}: HTTP {resp.status_code} — {resp.text}")

    def create_deposition(
        self,
        title: str,
        description: str,
        creators: list[dict],
        keywords: list[str],
        license: str,
        related_identifiers: list[dict],
    ) -> dict:
        metadata = {
            "upload_type": "dataset",
            "title": title,
            "description": description,
            "creators": creators,
            "keywords": keywords,
            "license": license,
            "related_identifiers": related_identifiers,
        }
        resp = requests.post(
            f"{self.base_url}/deposit/depositions",
            headers={**self.headers, "Content-Type": "application/json"},
            data=json.dumps({"metadata": metadata}),
        )
        self._check(resp, "create deposition")
        return resp.json()

    def upload_file(self, bucket_url: str, file_path: Path) -> dict:
        file_path = Path(file_path)
        with open(file_path, "rb") as f:
            resp = requests.put(
                f"{bucket_url}/{file_path.name}",
                headers=self.headers,
                data=f,
            )
        self._check(resp, f"upload {file_path.name}")
        return resp.json()

    def publish(self, deposition_id: int) -> dict:
        resp = requests.post(
            f"{self.base_url}/deposit/depositions/{deposition_id}/actions/publish",
            headers=self.headers,
        )
        self._check(resp, "publish")
        return resp.json()

    def new_version(self, deposition_id: int) -> dict:
        resp = requests.post(
            f"{self.base_url}/deposit/depositions/{deposition_id}/actions/newversion",
            headers=self.headers,
        )
        self._check(resp, "new version")
        return resp.json()

    def delete_all_files(self, deposition_id: int) -> None:
        resp = requests.get(
            f"{self.base_url}/deposit/depositions/{deposition_id}/files",
            headers=self.headers,
        )
        self._check(resp, "list files")
        for f in resp.json():
            del_resp = requests.delete(
                f"{self.base_url}/deposit/depositions/{deposition_id}/files/{f['id']}",
                headers=self.headers,
            )
            self._check(del_resp, f"delete file {f['filename']}")

    def update_metadata(self, deposition_id: int, metadata: dict) -> dict:
        resp = requests.put(
            f"{self.base_url}/deposit/depositions/{deposition_id}",
            headers={**self.headers, "Content-Type": "application/json"},
            data=json.dumps({"metadata": metadata}),
        )
        self._check(resp, "update metadata")
        return resp.json()
