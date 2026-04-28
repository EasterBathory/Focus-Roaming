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

    resend_key = os.getenv("RESEND_API_KEY", "")
    from_email = os.getenv("RESEND_FROM", "焦点漫游 <onboarding@resend.dev>")

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

    if resend_key:
        import resend
        resend.api_key = resend_key
        resend.Emails.send({
            "from": from_email,
            "to": [to_email],
            "subject": f"焦点漫游验证码 {code}",
            "html": body,
        })
    else:
        # 没有 Resend key 时降级：跳过发送，验证码打印到日志
        print(f"[DEV] 验证码: {to_email} -> {code}")

    return True
