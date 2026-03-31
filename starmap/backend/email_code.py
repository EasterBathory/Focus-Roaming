import random, time, os
from typing import Dict

_rate: Dict[str, float] = {}

def gen_code() -> str:
    return str(random.randint(100000, 999999))

def send_email_code(to_email: str, code: str) -> bool:
    now = time.time()
    if _rate.get(to_email, 0) + 60 > now:
        raise ValueError("Too frequent, please retry after 60 seconds")
    _rate[to_email] = now

    smtp_user = os.getenv("SMTP_USER", "")
    smtp_pass = os.getenv("SMTP_PASS", "")

    body = (
        '<div style="font-family:sans-serif;max-width:480px;margin:0 auto;padding:32px;'
        'background:#0d1117;color:#e6edf3;border-radius:12px">'
        '<h2 style="color:#58a6ff">焦点漫游</h2>'
        '<p style="color:#8b949e">您正在进行身份验证</p>'
        '<div style="background:#21262d;border-radius:8px;padding:20px;text-align:center;'
        f'letter-spacing:8px;font-size:32px;font-weight:800;color:#e6edf3">{code}</div>'
        '<p style="color:#8b949e;font-size:13px">验证码5分钟内有效，请勿泄露给他人。</p>'
        '</div>'
    )

    import yagmail
    yag = yagmail.SMTP(
        user=smtp_user,
        password=smtp_pass,
        host=os.getenv("SMTP_HOST", "smtp.qq.com"),
        port=int(os.getenv("SMTP_PORT", 465)),
        smtp_ssl=True,
    )
    yag.send(
        to=to_email,
        subject=f"焦点漫游验证码 {code}",
        contents=body,
    )
    return True
