def send_verification_email(email: str, token: str):
    # тут може бути SMTP або mock
    print(f"Verify email: {email} token: {token}")
