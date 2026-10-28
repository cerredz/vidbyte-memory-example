---
title: Pointers
description: Where things live outside this repo: dashboards, trackers, documents, services. Load when the request needs an external system.
write: Any run that learns where something lives, through skills/update-memory. A pointer holds a location, never a credential.
---

# Pointers

Format: `<name>: <URL or path>` then one sentence on what it is for, then the metadata line. See `memory/MAP.md`.

### P-001: Vidbyte SDK pricebook
Vidbyte SDK pricebook: https://github.com/cerredz/Vidbyte-SDK/blob/main/vidbyte/lib/registries/pricing.py
It is the SDK price table the owner updates from prices.csv, and its price rows cite provider documentation links in code comments, as FB-001 asked.
-- added: 2026-10-28 | source: FB-001 | status: active | evidence: file and its documentation-link comments checked on origin/main of cerredz/Vidbyte-SDK on 2026-10-28
