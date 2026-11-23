#!/usr/bin/env python3
"""Werner: E-Mail über einen frei einstellbaren SMTP-Dienst senden.
Aufruf durch shell_command.werner_mail_senden (Werte aus den Werner-Helfern)."""
import argparse
import base64
import json
import smtplib
import ssl
import sys
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid

p = argparse.ArgumentParser()
for name in ("server", "port", "user", "password", "mode", "to", "subject", "body"):
    p.add_argument("--" + name, default="")
a = p.parse_args()
# Alle Werte kommen base64-kodiert, damit Leer- und Sonderzeichen sicher ankommen
for name in ("server", "port", "user", "password", "mode", "to", "subject", "body"):
    v = getattr(a, name)
    try:
        setattr(a, name, base64.b64decode(v).decode("utf-8").strip() if v else "")
    except Exception:
        setattr(a, name, v)
a.body = a.body  # Text bleibt mehrzeilig


def fertig(ok, text):
    print(json.dumps({"ok": ok, "text": text}, ensure_ascii=False))
    sys.exit(0 if ok else 1)


if not a.server or not a.user or not a.password:
    fertig(False, "Mail-Dienst ist nicht vollständig eingestellt (Server, Benutzer, Passwort).")
if not a.to or "@" not in a.to:
    fertig(False, "Keine gültige Empfänger-Adresse.")
try:
    port = int(float(a.port or 587))
except ValueError:
    port = 587

msg = EmailMessage()
msg["From"] = formataddr(("Werner", a.user))
msg["To"] = a.to
msg["Subject"] = a.subject or "Werner"
msg["Date"] = formatdate(localtime=True)
msg["Message-ID"] = make_msgid(domain=a.user.split("@")[-1] if "@" in a.user else None)
msg.set_content(a.body or "")

ctx = ssl.create_default_context()
try:
    if a.mode == "SSL/TLS" or port == 465:
        with smtplib.SMTP_SSL(a.server, port, context=ctx, timeout=30) as s:
            s.login(a.user, a.password)
            s.send_message(msg)
    else:
        with smtplib.SMTP(a.server, port, timeout=30) as s:
            s.ehlo()
            s.starttls(context=ctx)
            s.ehlo()
            s.login(a.user, a.password)
            s.send_message(msg)
except smtplib.SMTPAuthenticationError:
    fertig(False, "Anmeldung abgelehnt – Benutzer oder Passwort falsch (bei GMX/Web.de: externen Zugriff per SMTP freischalten).")
except (OSError, smtplib.SMTPException) as e:
    fertig(False, "Versand fehlgeschlagen: " + str(e)[:200])
fertig(True, "E-Mail an " + a.to + " gesendet.")
