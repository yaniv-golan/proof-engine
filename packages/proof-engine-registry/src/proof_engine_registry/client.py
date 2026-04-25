"""Registry client. Talks the Registry Protocol v0.1.

Respects configured registry order. Never performs implicit fallback — the
caller must set fallback=True on a registry to permit querying it after a
miss on the previous registry.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

import requests

from proof_engine_registry import __protocol_version__
from proof_engine_registry.config import Registry
from proof_engine_registry.hashing import hash_claim
from proof_engine_registry.schema import Discovery, IndexEntry, from_json


class ProtocolVersionMismatch(Exception):
    """Registry speaks a higher major protocol version than the client."""


@dataclass(frozen=True)
class LookupHit:
    registry_name: str
    entry: IndexEntry

    # Convenience accessors mirror IndexEntry fields.
    @property
    def slug(self) -> str: return self.entry.slug
    @property
    def claim(self) -> str: return self.entry.claim
    @property
    def verdict(self) -> str: return self.entry.verdict
    @property
    def confidence(self) -> float: return self.entry.confidence
    @property
    def doi(self) -> Optional[str]: return self.entry.doi
    @property
    def proof_url(self) -> str: return self.entry.proof_url
    @property
    def badge_url(self) -> str: return self.entry.badge_url


class RegistryClient:
    def __init__(self, registries: list[Registry], timeout: float = 10.0):
        self.registries = registries
        self.timeout = timeout
        self._client_major, self._client_minor = (
            int(x) for x in __protocol_version__.split(".")
        )

    def _headers(self, registry: Registry) -> dict:
        if registry.token:
            return {"Authorization": f"Bearer {registry.token}"}
        return {}

    def _get(self, registry: Registry, path: str) -> Optional[dict]:
        url = f"{registry.url}{path}"
        resp = requests.get(url, headers=self._headers(registry),
                            timeout=self.timeout)
        if resp.status_code == 404:
            return None
        resp.raise_for_status()
        return resp.json()

    def discovery(self, registry: Registry) -> Discovery:
        data = self._get(registry, "/.well-known/proof-registry.json")
        if data is None:
            raise RuntimeError(f"Registry {registry.name} has no discovery doc")
        disco = from_json(Discovery, data)
        major = int(disco.protocol_version.split(".")[0])
        if major > self._client_major:
            raise ProtocolVersionMismatch(
                f"Registry {registry.name} speaks v{disco.protocol_version}, "
                f"client supports v{__protocol_version__}"
            )
        return disco

    def lookup(self, claim: str) -> Optional[LookupHit]:
        """Return the first registry hit for the claim, or None.

        Walks registries in order. If a registry returns 404, continues
        only if the NEXT registry has fallback=True.
        """
        claim_hash_hex = hash_claim(claim)
        previous_was_miss = False
        for i, registry in enumerate(self.registries):
            if i > 0 and previous_was_miss and not registry.fallback:
                break  # explicit no-fallback boundary
            data = self._get(registry, f"/claims/{claim_hash_hex}.json")
            if data is not None:
                return LookupHit(
                    registry_name=registry.name,
                    entry=from_json(IndexEntry, data),
                )
            previous_was_miss = True
        return None
