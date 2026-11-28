"""/health names the commit, so a hosted server can be compared with its branch."""

from __future__ import annotations

import json
import subprocess

import main
from helpers import build_info

SHA = "0492f3dbf93594bc8384edd6a3505b48ba39af86"


def test_the_commit_comes_from_the_environment_when_set(monkeypatch):
    monkeypatch.setenv("ECUADOR_MCP_COMMIT", SHA.upper())

    assert build_info.get_commit() == SHA


def test_render_s_own_variable_is_read(monkeypatch):
    monkeypatch.delenv("ECUADOR_MCP_COMMIT", raising=False)
    monkeypatch.setenv("RENDER_GIT_COMMIT", SHA)

    assert build_info.get_commit() == SHA


def test_a_value_that_is_not_a_sha_is_ignored(monkeypatch, tmp_path):
    monkeypatch.setenv("ECUADOR_MCP_COMMIT", "main; rm -rf /")
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)
    monkeypatch.setattr(build_info, "__file__", str(tmp_path / "helpers" / "build_info.py"))

    assert build_info.get_commit() is None


def test_a_checkout_without_git_on_the_path_reports_none(monkeypatch):
    monkeypatch.delenv("ECUADOR_MCP_COMMIT", raising=False)
    monkeypatch.delenv("RENDER_GIT_COMMIT", raising=False)

    def no_git(*args, **kwargs):
        raise FileNotFoundError("git")

    monkeypatch.setattr(subprocess, "run", no_git)

    assert build_info.get_commit() is None


async def test_health_reports_the_commit(monkeypatch):
    monkeypatch.setattr(main, "COMMIT", SHA)
    sent: list[dict] = []

    async def inner(scope, receive, send):
        raise AssertionError("/health must be answered before the inner app")

    async def receive():
        return {"type": "http.request"}

    async def send(message):
        sent.append(message)

    await main.with_health_endpoint(inner)(
        {"type": "http", "path": "/health", "headers": []}, receive, send
    )

    assert json.loads(sent[1]["body"])["commit"] == SHA
