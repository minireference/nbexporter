#!/usr/bin/env python

import io
import os

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


# Info about which files to export (by file_id) and what filenames to use for exported files
EXPORT_MANIFEST = {
    "destdir": "/Users/ivan/Projects/Eductaion/mp-84-atelier",
    "files": [
        # {   "destname": "Notions-de-Python-1.0.ipynb",
        #     "file_id": "1K5OipjFBFBDowYqkMc3_1KMbQAcn7Wx0"  },
        # {   'destname': 'Exercices-1.0.ipynb',
        #     'file_id': '172UswosDujNdB8cXu2Rn16y-h4j2ygVs'  },
        {   'destname': 'Exercices-1.0-Solutions.ipynb',
            'file_id': '1pfVZvKdMUinwxvTNI-rh3JFk5jyl7J-P'  },
        # {   'destname': 'Murales-1.0.ipynb',
        #     'file_id': '1Nn8wQgTbdTVg7emoQXGKP6tgPnSjsQPm'  },
        # {   'destname': 'Arbres-1.0.ipynb',
        #     'file_id': '1buBiJ2qbSqrSBYyUlISEVhnbRPbWcjlP'  },
    ]
}


# GOOGLE OAUTH FOR GDRIVE SERVICE
################################################################################

CREDENTIALS_PATH = os.path.join("credentials", "gdrive_credentials.json")
TOKEN_PATH = os.path.join("credentials", "token.json")
SCOPES = [
    'https://www.googleapis.com/auth/drive.metadata.readonly',
    'https://www.googleapis.com/auth/drive.readonly'
]

creds = None
# The file token.json stores the user's access and refresh tokens, and is
# created automatically when the authorization flow completes for the first
# time.
if os.path.exists(TOKEN_PATH):
    creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open(TOKEN_PATH, 'w') as token:
        token.write(creds.to_json())

service = build('drive', 'v3', credentials=creds)



# # Example call the Drive v3 API
# results = service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
# items = results.get('files', [])




# UTILS
################################################################################


def list_folder(folder_id):
    """
    Non-recursive list of contents of `folder_id`.
    via https://stackoverflow.com/a/50707508/127114
    """
    results = []
    kwargs = {
      "q": "'{}' in parents".format(folder_id),
      # Specify what you want in the response as a best practice. This string
      # will only get the files' ids, names, and the ids of any folders that they are in
      "fields": "nextPageToken,incompleteSearch,files(id,mimeType,parents,name)",
    }
    request = service.files().list(**kwargs)
    while request is not None:
        response = request.execute()
        results.extend(response['files'])
        request = service.files().list_next(request, response)
    return results



def download_file(file_id, destpath):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while done is False:
        status, done = downloader.next_chunk()
        print("Download %d%%." % int(status.progress() * 100))
    with open(destpath, 'wb') as destfile:
        destfile.write(fh.getbuffer())
    print('Contents of file_id', file_id, 'saved to', destpath)



# EXPORT
################################################################################


def export_files_manifest(manifest):
    for file in manifest['files']:
        print('Exporting file', file, '...')
        destpath = os.path.join(manifest['destdir'], file['destname'])
        download_file(file['file_id'], destpath)


if __name__ == '__main__':
    export_files_manifest(EXPORT_MANIFEST)


