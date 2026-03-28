from datetime import timezone, datetime
from urllib.parse import urlencode, urljoin
from app.config import settings
from app.utils.plugins import templates


def today_datetime(tz=timezone.utc)-> datetime:
    if not tz:
        tz = timezone.utc
    return datetime.now(tz=tz)

def reset_password_mail_content(user_name: str,reset_token: str) -> str:
    query_string = urlencode({"token": reset_token})
    reset_link = urljoin(settings.FRONTEND_DOMAIN, '/reset-password') + "?" + query_string
    template_content = templates.get_template("reset_password.html")
    html_content = template_content.render(user_name=user_name, reset_link=reset_link,
                                           expiry=settings.RESET_TOKEN_EXPIRE_MINUTES)
    return html_content