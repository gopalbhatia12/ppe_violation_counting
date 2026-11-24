import smtplib
import ssl
import os
from email.message import EmailMessage
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
load_dotenv(PROJECT_DIR / ".env")


def _get_setting(name, default=None):
    value = os.getenv(name)
    if value:
        return value

    secrets_file = PROJECT_DIR / ".streamlit" / "secrets.toml"
    if secrets_file.is_file():
        return st.secrets.get(name, default)
    return default


def send_report_email(receiver_email, video_name, report_df):
    sender_email = _get_setting("SMTP_EMAIL")
    sender_password = _get_setting("SMTP_PASSWORD")
    smtp_host = _get_setting("SMTP_HOST", "smtp.gmail.com")
    smtp_port = int(_get_setting("SMTP_PORT", "587"))

    if not sender_email or not sender_password:
        raise ValueError(
            "SMTP credentials are missing. Set SMTP_EMAIL and SMTP_PASSWORD "
            "in .env or .streamlit/secrets.toml."
        )

    email = EmailMessage()
    email["Subject"] = f"PPE detection and violation - {video_name}"
    email["From"] = sender_email
    email["To"] = receiver_email

    email.set_content(
        f"""
        Hello,

Your PPE Detection and People Counting report is ready.

Video processed: {video_name}

The detailed CSV report is attached.

Regards,
PPE Detection System

        """
    )
    csv_data = report_df.to_csv(index=False).encode("utf-8")
    email.add_attachment(
        csv_data,
        maintype="text",
        subtype="csv",
        filename="PPE_Report.csv"
    )
    context = ssl.create_default_context()

    with smtplib.SMTP(smtp_host, smtp_port, timeout=30) as server:
        server.ehlo()
        server.starttls(context=context)
        server.ehlo()
        server.login(sender_email, sender_password)
        server.send_message(email)
    return True