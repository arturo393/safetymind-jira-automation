import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/documents', 'https://www.googleapis.com/auth/drive']

class GoogleDocsClient:
    def __init__(self, credentials_path='credentials.json', token_path='token.json'):
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.creds = None
        self.service = None

    def authenticate(self):
        """Authenticates with Google Docs API."""
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(f"Credentials file not found at {self.credentials_path}")
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            with open(self.token_path, 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('docs', 'v1', credentials=self.creds)
        print("Successfully authenticated with Google Docs API.")

    def create_document(self, title):
        """Creates a new Google Doc and returns its ID."""
        if not self.service:
            self.authenticate()
        
        body = {
            'title': title
        }
        doc = self.service.documents().create(body=body).execute()
        print(f"Created document: {doc.get('title')} (ID: {doc.get('documentId')})")
        return doc.get('documentId')

    def append_text(self, document_id, text):
        """Appends text to the end of the document."""
        if not self.service:
            self.authenticate()

        requests = [
            {
                'insertText': {
                    'location': {
                        'index': 1, # Start of doc, simplified for now. Real logic needs end index.
                    },
                    'text': text + "\n"
                }
            }
        ]
        
        # Real logic needs to find the end of the document to append properly.
        # For skeleton, we just notify this is a placeholder.
        print(f"Appending text to {document_id}: {text}")
        # self.service.documents().batchUpdate(documentId=document_id, body={'requests': requests}).execute()
