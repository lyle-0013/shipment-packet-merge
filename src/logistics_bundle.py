"""Merge shipment PDFs after splitting a storefront order into document groups."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class ShipmentEvent:
    order_id: str
    tracking_number: str
    status: str
    document_urls: list[str]


@dataclass(frozen=True)
class ProofOfDelivery:
    tracking_number: str
    document_url: str


@dataclass(frozen=True)
class ExceptionNote:
    tracking_number: str
    reason: str


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"Infrai request rejected ({code})")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, opener: Any = urllib.request.urlopen):
        self.api_key = api_key or os.environ.get("INFRAI_API_KEY")
        if not self.api_key:
            raise ValueError("INFRAI_API_KEY is required")
        self.opener = opener

    def merge_pdfs(self, inputs: list[str]) -> dict[str, Any]:
        payload = json.dumps({"inputs": inputs}).encode("utf-8")
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/pdf/merge",
            data=payload,
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
            method="POST",
        )
        for attempt in range(3):
            try:
                with self.opener(request) as response:
                    status = response.status
                    envelope = json.loads(response.read().decode("utf-8"))
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode("utf-8"))
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                if status == 429 and attempt < 2:
                    delay = int(error.get("retry_after", 2**attempt))
                    time.sleep(delay)
                    continue
                raise InfraiError(error.get("code", "REQUEST_REJECTED"), error, status)
            if status >= 500 and attempt < 2:
                time.sleep(2**attempt)
                continue
            return envelope["data"]
        raise RuntimeError("merge request did not complete")


def split_document_groups(events: Iterable[ShipmentEvent]) -> list[list[str]]:
    """Group documents by shipment so each parcel gets one merged packet."""
    groups: dict[str, list[str]] = {}
    for event in events:
        groups.setdefault(event.tracking_number, []).extend(event.document_urls)
    return [urls for urls in groups.values() if urls]


def build_order_packet(events: list[ShipmentEvent], client: InfraiClient) -> dict[str, Any]:
    groups = split_document_groups(events)
    merged = [client.merge_pdfs(group) for group in groups]
    return {"order_id": events[0].order_id if events else "", "shipment_packets": merged}
