import smtplib
import win32com.client
import time
import random
import string

email = 'gu3123yiotlab@outlook.com'
password = '12345678*P'
currTemp = 18.5
isFanOn = False

# Generate a string identifier for the email
def generate_identifier(length=8):
    return ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(length))

email_identifier = generate_identifier()

# Send the initial email
with smtplib.SMTP('outlook.office365.com', 587) as smtp:
    smtp.ehlo()
    smtp.starttls()
    smtp.ehlo()
    smtp.login(email, password)
    subject = f'turn on fan? [{email_identifier}]'
    body = f'the current temperature is {currTemp}. Would you like to turn on the fan?'
    msg = f'subject: {subject}\n\n{body}'
    smtp.sendmail(email, email, msg)
    print("Email sent with identifier:", email_identifier)
    print("is fan on:", isFanOn)

# Continuously check for replies
while True:
    try:
        # Initialize Outlook COM object
        outlook = win32com.client.Dispatch("Outlook.Application")

        # Access the inbox
        inbox = outlook.GetNamespace("MAPI").GetDefaultFolder(6)
        messages = inbox.Items

        # Loop through received emails
        for message in messages:
            subject = message.Subject

            # Check if the correct email reply exists
            if email_identifier in subject and 'Yes' in message.Body:
                isFanOn = True
                print("Received a 'Yes' reply to the email with identifier:", email_identifier)
                print("is fan on:", isFanOn)
                # Delete the email once processed to prevent further checks
                message.Delete()
    except Exception as e:
        print("An error occurred:", e)


