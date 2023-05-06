from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials

# If modifying these scopes, delete the file token.json.
scopes = ['https://www.googleapis.com/auth/drive']

def upload_to_folder(folder_id):
    """
    https://developers.google.com/identity
    for guides on implementing OAuth2 for the application.
    """

    # creds, _ = google.auth.default()
    creds = Credentials.from_authorized_user_file('token.json', scopes)
    
    try:
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': 'greenhouse.csv',
            'parents': [folder_id]
        }

        with open("test.csv", "r") as file:
            media = MediaFileUpload(
                file,
                mimetype='text/csv',
                resumable=True
                )
            
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id, webViewLink'
                ).execute()
        
        permission = {
            'role': 'reader',
            'type': 'anyone'
        }
        service.permissions().create(
            fileId=file.get("id"),
            body=permission
        ).execute()

        print(file.get("webViewLink"))

    except HttpError as error:
        print(F'An error occurred: {error}')

if __name__ == '__main__':
    upload_to_folder(folder_id='15D5_93-iImEVtpFnXdQz0gGq9IAvDQxJ')