# Fast Analysis and Important-Information Filtering Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or **superpowers:executing-plans** to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a fast stock-analysis mode, make it the default scheduled mode, and show detailed per-stock information only when a material risk or catalyst exists.

**Architecture:** Keep `full` and `summary-lite` available. Add a `fast` report type that selects shorter data windows and concise output through existing configuration and pipeline context. Apply deterministic importance filtering at report rendering time so low-signal stocks receive only a one-line status.

**Tech Stack:** Python, GitHub Actions YAML, pytest, existing Config, ReportType, pipeline, analyzer, and notification renderer.

## Global Constraints

- Do not expose API keys or change provider credentials.
- Preserve `full` and `summary-lite` as selectable modes.
- Default scheduled/manual workflow mode becomes `fast`.
- A failed stock must not suppress successful stocks.
- News outside the fast window and duplicated/low-signal items must not be presented as important information.

### Task 1: Mode and configuration contract

**Files:** `.github/workflows/00-daily-analysis.yml`, `src/enums.py`, `src/config.py`, `src/core/config_registry.py`, `tests/test_report_renderer.py`

- [ ] Write failing tests for `fast` parsing and workflow default mapping.
- [ ] Run the focused tests and confirm they fail because `fast` is unsupported.
- [ ] Add `ReportType.FAST`, parser support, registry metadata, and workflow mapping.
- [ ] Run the focused tests and confirm they pass.

### Task 2: Fast data-window policy

**Files:** `src/core/pipeline.py`, `src/analyzer.py`, `tests/test_pipeline_prefetch_dry_run.py`

- [ ] Write a failing test proving fast mode carries a 3-day news window and short context marker.
- [ ] Run the test and confirm the expected context fields are absent.
- [ ] Add a fast policy with short news/history limits while leaving full modes unchanged.
- [ ] Run the focused tests and confirm they pass.

### Task 3: Important-information filtering

**Files:** `src/notification.py`, `tests/test_report_renderer.py`

- [ ] Write failing tests for a low-signal stock being collapsed and a stock with a risk/catalyst retaining only material sections.
- [ ] Run the tests and confirm they fail.
- [ ] Implement deterministic filtering based on risk, catalyst, earnings, announcement, and meaningful latest-news fields, with duplicate/placeholder suppression.
- [ ] Run the focused tests and confirm they pass.

### Task 4: Verification and documentation

**Files:** `docs/full-guide.md`, `docs/full-guide_EN.md`, relevant focused tests

- [ ] Run all tests covering config, pipeline, notification, and report rendering.
- [ ] Verify the workflow YAML contains `fast` and defaults to it.
- [ ] Run `git diff --check` and review the final diff for accidental credential or unrelated changes.
- [ ] Commit only after all verification commands pass.

