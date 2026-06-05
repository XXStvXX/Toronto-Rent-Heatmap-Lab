from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import requests


@dataclass(frozen=True)
class TorontoOpenDataResource:
    package_name: str
    resource_name: str
    format: str
    url: str


def ckan_package_search(base_url: str, query: str, rows: int = 10) -> list[dict[str, Any]]:
    endpoint = f"{base_url.rstrip('/')}/api/3/action/package_search"
    response = requests.get(endpoint, params={"q": query, "rows": rows}, timeout=30)
    response.raise_for_status()
    payload = response.json()
    if not payload.get("success"):
        raise RuntimeError(f"CKAN package_search failed for query {query!r}")
    return payload["result"]["results"]


def discover_toronto_boundary_resources(
    base_url: str = "https://ckan0.cf.opendata.inter.prod-toronto.ca",
    query: str = "neighbourhood boundary",
) -> list[TorontoOpenDataResource]:
    resources: list[TorontoOpenDataResource] = []
    for package in ckan_package_search(base_url, query=query, rows=20):
        for resource in package.get("resources", []):
            fmt = str(resource.get("format") or "").lower()
            url = resource.get("url")
            if url and fmt in {"geojson", "json", "shp", "zip", "csv"}:
                resources.append(
                    TorontoOpenDataResource(
                        package_name=package.get("name", ""),
                        resource_name=resource.get("name", ""),
                        format=fmt,
                        url=url,
                    )
                )
    return resources


def download_file(url: str, output_path: str | Path) -> Path:
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with requests.get(url, stream=True, timeout=60) as response:
        response.raise_for_status()
        with target.open("wb") as handle:
            for chunk in response.iter_content(chunk_size=1024 * 256):
                if chunk:
                    handle.write(chunk)
    return target
