"""Email alerting for the zen daily data freshness monitor (via dt_utilities)."""

from __future__ import annotations

import datetime as dt
from typing import Any

from dt_utilities.email.emailutility import EmailUtility


class EmailSender:
    def __init__(self, email_config: dict[str, Any]) -> None:
        self.sender = email_config["sender"]
        self.recipient_groups = email_config["recipient_groups"]

    def send(self, recipients: list[str], subject: str, body: str) -> None:
        """Send a plain-text report email via dt_utilities EmailUtility (internal relay)."""
        html_body = f"<pre style='font-family:monospace;font-size:13px'>{body}</pre>"
        eu = EmailUtility(
            app_name="zen_daily_data_check",
            _from=self.sender,
            _to=recipients,
        )
        # Override Security Benefit branding with Eldridge branding
        eu.config.LOGO_IMAGE = ""
        eu.config.HEADER = "Eldridge - Derivatives Technology"
        eu.config.FOOTER = "For questions or concerns: <a href='mailto:shujing.purcell@eldridge.com'>Derivatives Technology</a>"
        # Use subject_prefix to fully control the subject (suppresses SUCCESS:/ERROR: prefix)
        eu.send_email(
            data=html_body,
            subject=subject,
            data_date=dt.date.today(),
            subject_prefix="",
        )
        print(f"  -> Email sent to: {', '.join(recipients)}")

    def send_stale_alert(self, check_name: str, check_description: str,
                        stale_count: int, report: str, recipient_group) -> None:
        groups = recipient_group if isinstance(recipient_group, list) else [recipient_group]

        recipients: list[str] = []
        for g in groups:
            group_recipients = self.recipient_groups.get(g)
            if not group_recipients:
                print(f"  [WARN] No recipients configured for group '{g}', skipping.")
                continue
            recipients.extend(group_recipients)

        recipients = list(dict.fromkeys(recipients))  # dedupe, preserve order

        if not recipients:
            print(f"  [WARN] No recipients resolved for groups {groups}, skipping email.")
            return

        today = dt.date.today().isoformat()
        if stale_count == 0:
            subject = f"[DATA OK] {check_description} -- All tickers current as of {today}"
        else:
            subject = f"[DATA ALERT] {check_description} -- {stale_count} stale tickers as of {today}"
        self.send(recipients, subject, report)