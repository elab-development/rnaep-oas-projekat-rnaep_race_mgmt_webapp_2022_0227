import mailtrap as mt
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path
from app.config import settings

# Jinja2 environment – ucitva template iz template dir-a
_templates_dir = Path(__file__).parent.parent / "templates"
_jinja_env = Environment(
    loader=FileSystemLoader(str(_templates_dir)),
    autoescape=select_autoescape(["html"]),
)


def _render(template_name: str, **context) -> str:
    context.setdefault("support_email", settings.email_support)
    return _jinja_env.get_template(template_name).render(**context)


def _mailtrap_client() -> mt.MailtrapClient:
    return mt.MailtrapClient(
        token=settings.mailtrap_api_token.get_secret_value(),
        sandbox=settings.mailtrap_sandbox,
        inbox_id=settings.mailtrap_inbox_id if settings.mailtrap_sandbox else None,
    )


async def _send_email(to_email: str, subject: str, html_body: str) -> bool:
    try:
        client = _mailtrap_client()
        mail = mt.Mail(
            sender=mt.Address(email=settings.email_from, name=settings.email_from_name),
            to=[mt.Address(email=to_email)],
            subject=subject,
            html=html_body,
        )
        client.send(mail)
        print(f"[Email] Successfully sent to {to_email} | {subject}")
        return True
    except Exception as e:
        print(f"[Email] Mailtrap error: {e}")
        return False


async def send_registration_pending_email(
    to_email: str,
    participant_name: str,
    race_name: str,
    race_date: str,
    race_location: str,
    registration_id: int,
) -> bool:
    html = _render(
        "registration_pending.html",
        participant_name=participant_name,
        race_name=race_name,
        race_date=race_date,
        race_location=race_location,
        registration_id=registration_id,
    )
    return await _send_email(
        to_email=to_email,
        subject=f"Registracion recieved – {race_name}",
        html_body=html,
    )


async def send_registration_confirmed_email(
    to_email: str,
    participant_name: str,
    race_name: str,
    race_date: str,
    race_location: str,
    registration_id: int,
    bib_number: str,
) -> bool:
    html = _render(
        "registration_confirmed.html",
        participant_name=participant_name,
        race_name=race_name,
        race_date=race_date,
        race_location=race_location,
        registration_id=registration_id,
        bib_number=bib_number,
    )
    return await _send_email(
        to_email=to_email,
        subject=f"Registration confirmed – {race_name} | Bib #{bib_number}",
        html_body=html,
    )


async def send_registration_failed_email(
    to_email: str,
    participant_name: str,
    race_name: str,
    race_location: str,
    race_date: str,
    registration_id: int,
) -> bool:
    html = _render(
        "registration_failed.html",
        participant_name=participant_name,
        race_name=race_name,
        race_date=race_date,
        race_location=race_location,
        registration_id=registration_id,
    )
    return await _send_email(
        to_email=to_email,
        subject=f"Problem with transaction – {race_name}",
        html_body=html,
    )