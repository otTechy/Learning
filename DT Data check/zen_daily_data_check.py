#!/usr/bin/env python3
"""Config-driven stale-data check for zen dailydata feeds. Sends email if stale items found."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pyodbc

from email_sender import EmailSender

CONFIG_FILE = Path(__file__).parent / "config.json"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class TickerStatus:
    source: str
    ticker_name: str
    last_update: dt.date
    days_since_update: int

    def is_stale(self, stale_days: int) -> bool:
        return self.days_since_update > stale_days


@dataclass
class CheckResult:
    check_name: str
    check_description: str
    total_tickers: int
    statuses: list[TickerStatus]
    stale_threshold_days: int

    def stale_items(self) -> list[TickerStatus]:
        return [s for s in self.statuses if s.is_stale(self.stale_threshold_days)]


@dataclass
class ConnectionOptions:
    driver: str
    encrypt: str
    trust_server_certificate: str
    login_timeout: int
    connect_timeout: int
    max_retries: int


# ============================================================================
# SQL CLIENT
# ============================================================================

class SqlServerClient:
    def __init__(self, options: ConnectionOptions) -> None:
        self.options = options

    def _build_connection_string(self, server: str, database: str) -> str:
        encrypt_value = "Yes" if self.options.encrypt.strip().lower() == "yes" else "No"
        trust_value = "Yes" if self.options.trust_server_certificate.strip().lower() == "yes" else "No"
        conn = (
            f"DRIVER={{{self.options.driver}}};"
            f"SERVER={server};"
            f"DATABASE={database};"
            "Trusted_Connection=Yes;"
            f"Connection Timeout={self.options.connect_timeout};"
        )
        if "ODBC Driver" in self.options.driver:
            conn += f"Encrypt={encrypt_value};TrustServerCertificate={trust_value};"
        return conn

    def fetch_last_updates(self, check_config: dict[str, Any]) -> list[TickerStatus]:
        sql = f"""
            SELECT
                source,
                tickername,
                CAST(MAX(observationdate) AS date) AS last_update
            FROM {check_config['schema']}.{check_config['table']}
            WHERE tickername LIKE ?
              AND observationdate IS NOT NULL
            GROUP BY source, tickername
            ORDER BY source, tickername;
        """
        conn_str = self._build_connection_string(check_config["server"], check_config["database"])

        rows = None
        for attempt in range(1, self.options.max_retries + 1):
            try:
                with pyodbc.connect(conn_str, timeout=self.options.login_timeout) as conn:
                    rows = conn.cursor().execute(sql, check_config["ticker_like"]).fetchall()
                break
            except pyodbc.Error:
                if attempt == self.options.max_retries:
                    raise
                print(f"[WARN] Connection attempt {attempt}/{self.options.max_retries} failed; retrying in {attempt}s...")
                time.sleep(attempt)

        if rows is None:
            raise RuntimeError("Failed to retrieve rows from SQL Server.")

        today = dt.date.today()
        statuses: list[TickerStatus] = []
        for row in rows:
            source = str(row.source) if row.source is not None else "UNKNOWN"
            last_update = row.last_update
            if isinstance(last_update, dt.datetime):
                last_date = last_update.date()
            elif isinstance(last_update, dt.date):
                last_date = last_update
            else:
                last_date = dt.datetime.strptime(str(last_update), "%Y-%m-%d").date()
            statuses.append(TickerStatus(
                source=source,
                ticker_name=str(row.tickername),
                last_update=last_date,
                days_since_update=(today - last_date).days,
            ))
        return statuses


# ============================================================================
# CHECK SERVICE
# ============================================================================

class StaleDataCheckService:
    def __init__(self, sql_client: SqlServerClient) -> None:
        self.sql_client = sql_client

    def run_check(self, check_name: str, check_config: dict[str, Any]) -> CheckResult:
        print(f"Running check: {check_name}")
        statuses = self.sql_client.fetch_last_updates(check_config)
        statuses.sort(key=lambda x: x.last_update)
        result = CheckResult(
            check_name=check_name,
            check_description=check_config["description"],
            total_tickers=len(statuses),
            statuses=statuses,
            stale_threshold_days=int(check_config["stale_days"]),
        )
        print(f"  -> {result.total_tickers} tickers, {len(result.stale_items())} stale (> {result.stale_threshold_days} days)")
        return result


# ============================================================================
# CONSOLE REPORTER
# ============================================================================

class ConsoleReporter:
    @staticmethod
    def _ticker_sort_key(key: str) -> tuple:
        """M tenors first (3M, 6M...), then Y tenors (1Y, 2Y...), then alphabetical."""
        last = key.strip().upper().split("_")[-1]
        if last.endswith("M") or last.endswith("Y"):
            suffix_order = 0 if last.endswith("M") else 1
            try:
                return (suffix_order, int(last[:-1]), key)
            except (ValueError, IndexError):
                pass
        return (2, 0, key)

    @staticmethod
    def format_report(result: CheckResult) -> str:
        stale = result.stale_items()
        lines = []

        lines.append(f"[{'WARN' if stale else 'OK'}] {result.check_description}")
        lines.append(f"  Total tickers: {result.total_tickers}  |  Stale (> {result.stale_threshold_days} days): {len(stale)}")
        lines.append("")

        # Consolidated summary (most recent per ticker)
        lines.append("  ===== CONSOLIDATED SUMMARY (Most Recent per Ticker) =====")
        lines.append(f"  {'Ticker':<35} | {'CP':<12} | {'Last Update':<12} | {'Days Stale':>10} | {'Status':<10}")
        lines.append(f"  {'-'*35}-+-{'-'*12}-+-{'-'*12}-+-{'-'*10}-+{'-'*10}")

        ticker_map: dict[str, TickerStatus] = {}
        for status in result.statuses:
            key = status.ticker_name.strip().upper()
            if key not in ticker_map or status.last_update > ticker_map[key].last_update:
                ticker_map[key] = status

        for key in sorted(ticker_map.keys(), key=ConsoleReporter._ticker_sort_key):
            s = ticker_map[key]
            label = "STALE" if s.is_stale(result.stale_threshold_days) else "CURRENT"
            lines.append(f"  {s.ticker_name:<35} | {s.source:<12} | {s.last_update.isoformat():<12} | {s.days_since_update:>10} | {label:<10}")

        lines.append("")
        lines.append("  ===== DETAIL BY SOURCE (CP) =====")

        # Per-source detail tables
        sources: dict[str, list[TickerStatus]] = {}
        for status in result.statuses:
            sources.setdefault(status.source, []).append(status)

        for source in sorted(sources.keys()):
            tickers = sources[source]
            stale_count = sum(1 for t in tickers if t.is_stale(result.stale_threshold_days))
            lines.append(f"\n  SOURCE: {source} ({stale_count} stale of {len(tickers)} tickers)")
            lines.append(f"  {'-'*100}")
            lines.append(f"  {'Ticker':<45} | {'Last Update':<12} | {'Days Stale':>10} | {'Status':<10}")
            lines.append(f"  {'-'*100}")
            for s in sorted(tickers, key=lambda x: ConsoleReporter._ticker_sort_key(x.ticker_name.strip().upper())):
                label = "STALE" if s.is_stale(result.stale_threshold_days) else "CURRENT"
                lines.append(f"  {s.ticker_name:<45} | {s.last_update.isoformat():<12} | {s.days_since_update:>10} | {label:<10}")

        return "\n".join(lines)


# ============================================================================
# MAIN
# ============================================================================

def load_config() -> dict[str, Any]:
    if not CONFIG_FILE.exists():
        raise FileNotFoundError(f"Config file not found: {CONFIG_FILE}")
    with CONFIG_FILE.open() as f:
        return json.load(f)


def parse_args(check_names: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Stale-data monitor for zen dailydata feeds.")
    parser.add_argument("--check", choices=check_names, help="Run only a specific check (default: all)")
    parser.add_argument("--no-email", action="store_true", help="Print report only, do not send email")
    return parser.parse_args()


def main() -> int:
    cfg = load_config()
    sql_cfg = cfg["sql"]
    email_cfg = cfg["email"]
    checks_cfg = cfg["checks"]

    args = parse_args(list(checks_cfg.keys()))

    print("=" * 80)
    print("Data Freshness Monitor Started")
    print("=" * 80)

    base = {k: sql_cfg[k] for k in ("server", "database", "schema", "table")}
    checks_to_run = {args.check: {**base, **checks_cfg[args.check]}} if args.check else {
        name: {**base, **c} for name, c in checks_cfg.items()
    }

    options = ConnectionOptions(
        driver=sql_cfg["driver"],
        encrypt=sql_cfg["encrypt"],
        trust_server_certificate=sql_cfg["trust_server_certificate"],
        login_timeout=sql_cfg["login_timeout"],
        connect_timeout=sql_cfg["connect_timeout"],
        max_retries=sql_cfg["max_retries"],
    )
    checker = StaleDataCheckService(SqlServerClient(options))
    reporter = ConsoleReporter()
    emailer = EmailSender(email_cfg)

    for check_name, check_config in checks_to_run.items():
        try:
            result = checker.run_check(check_name=check_name, check_config=check_config)
            report = reporter.format_report(result)
            print("\n" + report)

            if not args.no_email:
                emailer.send_stale_alert(
                    check_name=result.check_name,
                    check_description=result.check_description,
                    stale_count=len(result.stale_items()),
                    report=report,
                    recipient_group=check_config.get("email_recipient_group", ""),
                )

        except KeyError as exc:
            print(f"ERROR: Config error in check '{check_name}': {exc}", file=sys.stderr)
            return 1
        except pyodbc.Error as exc:
            print(f"ERROR: Database error in check '{check_name}': {exc}", file=sys.stderr)
            return 2
        except Exception as exc:
            print(f"ERROR: Unexpected error in check '{check_name}': {exc}", file=sys.stderr)
            return 3

    print("\n" + "=" * 80)
    print("Data Freshness Monitor Completed")
    print("=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
