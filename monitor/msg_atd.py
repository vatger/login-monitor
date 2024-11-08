import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd


def send_email_with_dataframe(
    sender_email,
    receiver_email,
    subject,
    body,
    dataframe,
    smtp_server,
    smtp_port,
    login,
    password,
):
    # Convert the DataFrame to an HTML table
    html_table = dataframe.to_html(index=False, escape=False)

    # Combine the body text and the HTML table
    html_content = f"""
    <html>
        <body>
            <p>{body}</p>
            {html_table}
        </body>
    </html>
    """

    # Set up the MIME
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach the HTML content
    message.attach(MIMEText(html_content, "html"))

    # Connect to the server and send the email
    try:
        with smtplib.SMTP_SSL(smtp_server, smtp_port, timeout=30) as server:
            server.login(login, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully.")
    except Exception as e:
        print(f"Error: {e}")


# Usage
def send_mail(df):
    send_email_with_dataframe(
        sender_email="",
        receiver_email="atd@vatger.de",
        subject="Test Email",
        body="This is a test email sent from Python!",
        dataframe=df,
        smtp_server="mail.vatger.de",
        smtp_port=465,  # SSL typically uses port 465
        login="",
        password="",  # Use app-specific password if 2FA is enabled
    )


if __name__ == "__main__":
    send_mail(pd.DataFrame({"a": [1, 2, 3], "b": [4, 5, 6]}))
