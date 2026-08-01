import json
import urllib.request
import urllib.error
from app.config import get_settings

settings = get_settings()


OTP_EMAIL_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin:0;padding:0;background-color:#030712;font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background-color:#030712;padding:40px 20px;">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0" style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.08);border-radius:16px;padding:40px;">
          <tr>
            <td align="center" style="padding-bottom:24px;">
              <div style="display:inline-block;width:56px;height:56px;border-radius:12px;background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.3);line-height:56px;text-align:center;">
                <span style="font-size:28px;color:#06b6d4;">&#x1f6e1;</span>
              </div>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom:8px;">
              <h1 style="color:#ffffff;font-size:22px;font-weight:700;margin:0;">DeepShield AI</h1>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom:32px;">
              <p style="color:rgba(255,255,255,0.5);font-size:14px;margin:0;">Security Verification</p>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom:24px;">
              <table cellpadding="0" cellspacing="0">
                <tr>
                  <td style="background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.3);border-radius:12px;padding:16px 32px;">
                    <span style="font-size:32px;font-weight:700;color:#06b6d4;letter-spacing:12px;font-family:monospace;">{OTP}</span>
                  </td>
                </tr>
              </table>
            </td>
          </tr>
          <tr>
            <td align="center" style="padding-bottom:24px;">
              <p style="color:rgba(255,255,255,0.6);font-size:14px;line-height:1.6;margin:0;">
                Your verification code is <strong style="color:#ffffff;">{OTP}</strong>.
              </p>
              <p style="color:rgba(255,255,255,0.6);font-size:14px;line-height:1.6;margin:8px 0 0 0;">
                This code expires in <strong style="color:#f59e0b;">5 minutes</strong>.
              </p>
            </td>
          </tr>
          <tr>
            <td style="padding-bottom:24px;">
              <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
            </td>
          </tr>
          <tr>
            <td align="center">
              <p style="color:rgba(255,255,255,0.3);font-size:12px;line-height:1.5;margin:0;">
                If you did not request this verification, please ignore this email.<br>
                Do not share this code with anyone.
              </p>
            </td>
          </tr>
        </table>
        <table width="480" cellpadding="0" cellspacing="0">
          <tr>
            <td align="center" style="padding-top:24px;">
              <p style="color:rgba(255,255,255,0.2);font-size:11px;margin:0;">
                DeepShield AI Security Team &bull; Automated message
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""


def send_otp_email(to_email: str, otp_code: str, purpose: str) -> dict:
    """Send OTP email via Resend HTTP API."""
    api_key = settings.RESEND_API_KEY
    if not api_key:
        return {"success": False, "error": "Email not configured. Set RESEND_API_KEY in environment variables."}

    html_body = OTP_EMAIL_TEMPLATE.replace("{OTP}", otp_code)
    text_body = f"DeepShield AI - Security Verification\n\nYour verification code is: {otp_code}\n\nThis code expires in 5 minutes.\n\nIf you did not request this verification, please ignore this email.\n\nDeepShield AI Security Team"

    payload = json.dumps({
        "from": "DeepShield AI <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "DeepShield AI - Security Verification",
        "html": html_body,
        "text": text_body,
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.resend.com/emails",
        data=payload,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            if resp.status in (200, 201):
                return {"success": True, "error": None}
            body = resp.read().decode()
            return {"success": False, "error": f"Resend API error: {resp.status} {body}"}
    except urllib.error.HTTPError as e:
        body = e.read().decode() if e.fp else str(e)
        return {"success": False, "error": f"Resend API error: {e.code} {body}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to send email: {str(e)}"}
