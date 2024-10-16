import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Step 1: Set up OAuth 2.0 Scopes and Token Storage
SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def get_credentials():
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no valid credentials, prompt the user to log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save the credentials for future use
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

# Step 2: Create the email message with attachments and a grey signature
def create_message_with_attachment(sender, to, subject, message_text, files):
    # Create the multipart message object
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    # Add a signature with smaller grey text and no bold
    signature = """
    <div style="font-family:Arial, sans-serif; font-size:11px; color:#6e6e6e; line-height:1.4;">
        <br><br>
        Best regards,<br>
        Mohammad Mashreghi<br>
        <span>B.Sc. Student in Electrical Engineering,<br>
        University of Tehran<br>
        Assistant researcher at Smart Network Lab</span><br>
        <span>WhatsApp: +98 9308810317 | 
    </div>
    """

    # Combine the message text with the signature and format it as HTML
    message_body = f"{message_text}<br><br>{signature}"
    message.attach(MIMEText(message_body, 'html'))

    # Attach the files
    for file in files:
        # Open the file in binary mode
        with open(file, "rb") as attachment:
            # Create a MIMEBase instance
            mime_base = MIMEBase('application', 'octet-stream')
            mime_base.set_payload(attachment.read())
            
            # Encode the payload with base64
            encoders.encode_base64(mime_base)

            # Add header with filename
            mime_base.add_header('Content-Disposition', f'attachment; filename={os.path.basename(file)}')

            # Attach the instance to the message
            message.attach(mime_base)

    # Return the encoded message as a dictionary
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

# Step 3: Send the email
def send_email(service, user_id, message):
    try:
        message = service.users().messages().send(userId=user_id, body=message).execute()
        print(f"Message Id: {message['id']}", message['threadId'])
        return message
    except Exception as error:
        print(f"An error occurred: {error}")
        return None

def main():
    # Get OAuth 2.0 credentials
    creds = get_credentials()

    # Step 4: Build the Gmail API service
    service = build('gmail', 'v1', credentials=creds)

    # Step 5: Create and send the email with attachments and grey signature
    sender_email = "------"
    receiver_email = "------"
    subject = "Test email with attachments a"
    message_text = "Hello, this is a test email with attachments and a grey signature sent using Gmail API with OAuth 2.0 in Python."

    # # Specify the file paths to attach
    # files = [
    #     r"D:\Sending email\resume end of 8 semester - Mashreghi.pdf",
    #     r"D:\Sending email\resume_Mashreghi_v2.pdf"
    # ]
    
    # Create the message with attachments and smaller grey signature
    message = create_message_with_attachment(sender_email, receiver_email, subject, message_text, files)
    
    # Send the email
    send_email(service, 'me', message)

if __name__ == '__main__':
    main()
