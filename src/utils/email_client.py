import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage


sender_email = "nikita.vsav@gmail.com"
password = "cjui omfh rupq rcps"


def send_email_with_image(image_path, message_body, recipient_emails):
    """
    Отправляет электронное письмо с изображением и текстовым сообщением на несколько email-адресов.

    Параметры:
    image_path (str): Путь к изображению, которое будет вложено в письмо.
    message_body (str): Текстовое сообщение, которое будет отправлено в теле письма.
    recipient_emails (list): Список email-адресов получателей.
    """
    sender_email = "nikita.vsav@gmail.com"
    password = "cjui omfh rupq rcps"
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    message = MIMEMultipart()
    message["From"] = sender_email
    message["Subject"] = "Уведомление о прогнозе"

    message.attach(MIMEText(message_body, "plain"))

    try:
        with open(image_path, 'rb') as image_file:
            img = MIMEImage(image_file.read())
            message.attach(img)
    except Exception as e:
        print(f"Ошибка при добавлении изображения: {e}")
        return

    to_emails = ', '.join(recipient_emails)
    message["To"] = to_emails

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, password)

        server.sendmail(sender_email, recipient_emails, message.as_string())

        print("Письмо отправлено успешно!")

    except Exception as e:
        print(f"Произошла ошибка: {e}")
    finally:
        server.quit()


if __name__ == "__main__":
    image_path = "/Users/nikitasavvin/Desktop/PhD/alert_manager/src/utils/newplot (1).png"
    message_body = "Привет, это письмо с вложением изображения!\n--\nC уважением, Alert Manager"
    recipient_emails = ["savvin.nikit@yandex.ru", 'vasenindmitrij01@gmail.com']

    send_email_with_image(image_path, message_body, recipient_emails)

