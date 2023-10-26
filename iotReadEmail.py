import imaplib
import email
from email.header import decode_header
import time
import smtplib
import random
import string

# Account credentials
username = "gu3123yiotlab@outlook.com"
password = "12345678*P"
currTemp = 25
isFanOn = False

def generate_identifier(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

def send_email(email_identifier):
    imap_server = "outlook.office365.com"
    with smtplib.SMTP(imap_server, 587) as smtp:
        smtp.ehlo()
        smtp.starttls()
        smtp.ehlo()
        smtp.login(username, password)
        subject = f're: turn on fan? [{email_identifier}]'
        body = f'The current temperature is {currTemp}. Would you like to turn on the fan?'
        msg = f'subject: {subject}\n\n{body}'
        smtp.sendmail(username, username, msg)
        print("Email sent")

def process_email(email_message, email_identifier):
    # This function processes the received email
    subject = email_message["Subject"]
    
    # Check if the email is multipart
    if email_message.is_multipart():
        body = ""
        for part in email_message.walk():
            content_type = part.get_content_type()
            if "text/plain" in content_type:
                body += part.get_payload(decode=True).decode()
    else:
        body = email_message.get_payload()
    
    if f"Re: turn on fan? [{email_identifier}]" in subject:
        if "Yes" in body:
            print("Received 'Yes' in the email body.")
            isFanOn = True

def main():
    email_identifier = generate_identifier()
    send_email(email_identifier)
    
    while not isFanOn:
        try:
            # Connect to the IMAP server
            imap_server = "outlook.office365.com"
            imap = imaplib.IMAP4_SSL(imap_server)
            imap.login(username, password)

            # Select the INBOX
            imap.select("INBOX")

            # Search for all unseen messages
            status, messages = imap.search(None, "UNSEEN")

            if status == "OK" and messages:
                message_ids = messages[0].split()
                for msg_id in message_ids:
                    status, msg_data = imap.fetch(msg_id, "(RFC822)")
                    if status == "OK":
                        email_message = email.message_from_bytes(msg_data[0][1])
                        process_email(email_message, email_identifier)

            imap.logout()

            # Pause for a few seconds before checking again
            time.sleep(2)

        except Exception as e:
            print("An error occurred:", str(e))

if __name__ == "__main__":
    main()
