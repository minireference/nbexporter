#!/usr/bin/env python
import argparse
import io
import os
import re
from urllib.parse import quote

from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from nbconvert import NotebookExporter
import yaml


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


def parse_git_url(repo_url):
    """
    Parse `repo_url` to extract `org` and repo `name` (for creating links).
    """
    git_url_pat = re.compile("(?P<host>(git@|https://)([\w\.@]+)(/|:))(?P<org>[\w,\-,\_]+)/(?P<name>[\w,\-,\_]+)(.git){0,1}((/){0,1})")
    m = git_url_pat.match(repo_url)
    org = m.groupdict()["org"]
    name = m.groupdict()["name"]
    return org, name



# NOTEBOOK FILE EXPORT
################################################################################

def export_files_manifest(manifest, readme=False):
    """
    Export the notebooks listed in the manifest to the destination directory.
    """
    destdir = manifest['destdir']
    for file in manifest['notebooks']:
        print('Exporting file', file, '...')
        destpath = os.path.join(destdir, file['file_name'])
        download_file(file['file_id'], destpath)

        # reformat notebook JSON to avoid diffs bâtard
        # equivalent to command `jupyter-nbconvert --to notebook  --inplace`
        nbsrc, _resources = NotebookExporter().from_filename(filename=destpath)
        with open(destpath, "w") as nbfile:
            nbfile.write(nbsrc)



# NOTEBOOKS README WRITER
################################################################################

IMG_LINK_TEMPLATE = "[![{badge_alt}]({badge_url})]({link_url})"

badge_urls = {
    "binder": "https://mybinder.org/badge_logo.svg",
    "colab": "https://colab.research.google.com/assets/colab-badge.svg",
}

MYBINDER_URL_TEMPLATE = "https://mybinder.org/v2/gh/{org}/{name}/{branch}"
MYBINDER_PATH_SUFFIX = "?labpath={urlquoted_path}"

COLAB_URL_TEMPLATE = "https://colab.research.google.com/github/{org}/{name}/blob/{branch}/{path}"
COLAB_URL_TEMPLATE_NO_PATH = "https://colab.research.google.com/github/{org}/{name}/blob/{branch}"


def get_binder_link(org, name, branch="main", path=None):
    """
    Create a link that opens notebook in mybinder.org/v2/.
    """
    binder_link_url = MYBINDER_URL_TEMPLATE.format(
        org=org,
        name=name,
        branch=branch,
    )
    if path:
        urlquoted_path = quote(path, safe='')
        binder_link_url += MYBINDER_PATH_SUFFIX.format(urlquoted_path=urlquoted_path)
    binder_link = IMG_LINK_TEMPLATE.format(
        badge_alt="Binder",
        badge_url=badge_urls['binder'],
        link_url=binder_link_url
    )
    return binder_link


def get_colab_link(org, name, branch="main", path=None):
    """
    Create a link that opens notebook in Google Colab.
    """
    if not path:
        raise ValueError("Colab links require a path to a notebook")
    colab_link_url = COLAB_URL_TEMPLATE.format(
        org=org,
        name=name,
        branch=branch,
        path=path,
    )
    colab_link = IMG_LINK_TEMPLATE.format(
        badge_alt="Colab",
        badge_url=badge_urls['colab'],
        link_url=colab_link_url
    )
    return colab_link


def write_readme(manifest, branch="main", subdir="notebooks", binder=True, colab=True):
    """
    Create a README.md file in the destination directory with mybinder and colab
    links to all the notebooks in the export manifest.
    """
    org, name = parse_git_url(manifest["repo_url"])
    README = "# Notebooks\n\n"
    for file in manifest['notebooks']:
        file_name = file['file_name']
        path = os.path.join(subdir, file_name)
        binder_link = get_binder_link(org, name, branch="main", path=path)
        colab_link = get_colab_link(org, name, branch="main", path=path)
        README += f"- {file_name}"
        if binder:
            README += f" {binder_link}"
        if colab:
            README += f" {colab_link}"
        README += "\n"

    destdir = manifest['destdir']
    readme_path = os.path.join(destdir, "README.md")
    with open(readme_path, "w") as readme_file:
        readme_file.write(README)



# CLI
################################################################################

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Notebook exporter')
    parser.add_argument('--manifest', required=True, help="YAML manifest file")
    parser.add_argument('--readme', action='store_true', help="Write README.md")
    args = parser.parse_args()

    manifest = yaml.safe_load(open(args.manifest))
    # Check manifest file format
    assert manifest["destdir"], "Manifest file is missing destdir key"
    assert manifest["notebooks"], "Manifest file is missing notebooks list"
    
    export_files_manifest(manifest)

    if args.readme:
        # Write the notebooks/READEME.md file
        assert manifest["repo_url"], "Manifest file is missing repo_url key"
        write_readme(manifest, branch="main", subdir="notebooks", binder=True, colab=True)
