import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

def send_email(sender_email, sender_password, recipient_email, subject, body):
    # メールの作成
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject

    # メール本文を追加
    msg.attach(MIMEText(body, 'plain'))

    try:
        # GmailのSMTPサーバーに接続
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # セキュリティを強化
        server.login(sender_email, sender_password)  # ログイン

        # メールを送信
        server.send_message(msg)

        # 終了処理
        server.quit()

        print("メールが送信されました！")

    except Exception as e:
        print(f"メールの送信に失敗しました: {e}")

'''使用例
send_email(
    sender_email="your_email@gmail.com",
    sender_password="your_password",
    recipient_email="recipient_email@example.com",
    subject="テストメール",
    body="これはPythonから送信されたメールです"
)
'''