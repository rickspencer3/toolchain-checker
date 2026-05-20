#!/usr/bin/env python3
"""Append-only event log for toolchain scanner runs.

Log file is RUN.log at the repo root. Call log() to append a timestamped
event line. All timestamps are UTC.

Event types used by scanners:
  RUN_START   - a scan run has begun
  ATTACK      - an attack being checked in this run (one line per attack)
  CLEAN       - scan completed, no compromised packages found
  COMPROMISED - scan completed, one or more compromised packages found
"""

from datetime import datetime, timezone

LOG_FILE = 'RUN.log'


def log(event: str, message: str) -> None:
    ts = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')
    line = f"[{ts}] {event:<12} {message}\n"
    with open(LOG_FILE, 'a') as f:
        f.write(line)


def attack_label(attack: dict) -> str:
    """Return a short human-readable label for an attack entry."""
    ecosystem = attack.get('ecosystem', '?')
    discovered = attack.get('discovered', '?')
    if 'package_name' in attack:
        name = attack['package_name']
        versions = attack.get('malicious_versions', [])
        ver_str = ', '.join(versions[:3])
        if len(versions) > 3:
            ver_str += f' (+{len(versions) - 3} more)'
        return f"{name} ({ecosystem}) malicious: {ver_str} | discovered {discovered}"
    else:
        scope = attack.get('package_scope', '(unknown)')
        count = attack.get('package_count', '?')
        return f"{scope} ({ecosystem}, {count} pkgs) | discovered {discovered}"
