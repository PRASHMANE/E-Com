import resend

from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY


def send_verification_email(
    email: str,
    otp: str
):
    resend.Emails.send(
        {
            "from": settings.EMAIL_FROM,
            "to": email,
            "subject": "Verify your account",
            "html": f"""
                <h2>Email Verification</h2>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This code expires in 10 minutes.</p>
            """
        }
    )



def send_password_reset_email(
    email: str,
    otp: str
):
    resend.Emails.send(
        {
            "from": settings.EMAIL_FROM,
            "to": email,
            "subject": "Reset your password",
            "html": f"""
                <h2>Password Reset</h2>
                <p>Your OTP is:</p>
                <h1>{otp}</h1>
                <p>This code expires in 10 minutes.</p>
            """
        }
    )