import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from config import sender_email, password



def send_email_with_html_attachment(html_path, subject, recipient_emails, email_body):
    """
    Отправляет электронное письмо с HTML-файлом в качестве вложения.

    Параметры:
    html_path (str): Путь к HTML-файлу, который будет отправлен как вложение.
    subject (str): Тема письма.
    recipient_emails (list): Список email-адресов получателей.
    """

    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = ', '.join(recipient_emails)
    message["Subject"] = subject
    message.attach(MIMEText(email_body, "html"))

    print('===================================')
    print('send_email_with_html_attachment 1 IS WORKING')
    print('===================================')

    try:
        with open(html_path, 'rb') as file:
            part = MIMEApplication(file.read(), Name="graph.html")
            part['Content-Disposition'] = 'attachment; filename="graph.html"'
            message.attach(part)
    except Exception as e:
        print(f"Ошибка при добавлении вложения: {e}")
        return

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, recipient_emails, message.as_string())
        print("Письмо успешно отправлено с HTML-вложением!")
    except Exception as e:
        print(f"Произошла ошибка при отправке письма: {e}")
