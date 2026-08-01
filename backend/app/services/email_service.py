import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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
          <!-- Logo -->
          <tr>
            <td align="center" style="padding-bottom:24px;">
              <div style="display:inline-block;width:56px;height:56px;border-radius:12px;background:rgba(6,182,212,0.1);border:1px solid rgba(6,182,212,0.3);line-height:56px;text-align:center;">
                <span style="font-size:28px;color:#06b6d4;">&#x1f6e1;</span>
              </div>
            </td>
          </tr>
          <!-- Title -->
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
          <!-- OTP Box -->
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
          <!-- Message -->
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
          <!-- Divider -->
          <tr>
            <td style="padding-bottom:24px;">
              <div style="height:1px;background:linear-gradient(90deg,transparent,rgba(255,255,255,0.1),transparent);"></div>
            </td>
          </tr>
          <!-- Warning -->
          <tr>
            <td align="center">
              <p style="color:rgba(255,255,255,0.3);font-size:12px;line-height:1.5;margin:0;">
                If you did not request this verification, please ignore this email.<br>
                Do not share this code with anyone.
              </p>
            </td>
          </tr>
        </table>
        <!-- Footer -->
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
    """
    Send OTP email via Gmail SMTP.
    Returns dict with success status and any error message.
    """
    if not settings.EMAIL_ADDRESS or not settings.EMAIL_APP_PASSWORD:
        return {"success": False, "error": "Email not configured. Set EMAIL_ADDRESS and EMAIL_APP_PASSWORD in .env"}

    subject = "DeepShield AI - Security Verification"

    html_body = OTP_EMAIL_TEMPLATE.replace("{OTP}", otp_code)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"DeepShield AI <{settings.EMAIL_ADDRESS}>"
    msg["To"] = to_email

    # Plain text fallback
    text_part = MIMEText(
        f"DeepShield AI - Security Verification\n\n"
        f"Your verification code is: {otp_code}\n\n"
        f"This code expires in 5 minutes.\n\n"
        f"If you did not request this verification, please ignore this email.\n\n"
        f"DeepShield AI Security Team",
        "plain"
    )
    html_part = MIMEText(html_body, "html")

    msg.attach(text_part)
    msg.attach(html_part)

    try:
        import ssl
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context, timeout=15) as server:
            server.login(settings.EMAIL_ADDRESS, settings.EMAIL_APP_PASSWORD)
            server.sendmail(settings.EMAIL_ADDRESS, to_email, msg.as_string())
        return {"success": True, "error": None}
    except smtplib.SMTPAuthenticationError:
        return {"success": False, "error": "SMTP authentication failed. Check EMAIL_APP_PASSWORD in .env"}
    except smtplib.SMTPException as e:
        return {"success": False, "error": f"SMTP error: {str(e)}"}
    except Exception as e:
        return {"success": False, "error": f"Failed to send email: {str(e)}"}
