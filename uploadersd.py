#!/usr/bin/python
'''
Created 1/11/16 by BrettBuilds
v1.0

'''
import sys

import smtplib
from datetime import datetime

import os.path
import logging

import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload

import ConfigParser
import os

class FindPhotos:
    def _init_(self):
        self._Photo_search()

    def _Photo_search(self):
	#Create list of all photos
        photolist = []
        for dirpath, subdirs, files in os.walk('/tmp/run/mountd/mmcblk0p1'):
            for file in files:
                if file.endswith(('.jpg', '.JPG')):
                    photolist.append(os.path.join(dirpath,file))
	return photolist


class PhotoUploader:
    def __init__(self):
        # Load config
        config_file_path = './root/config/uploader.cfg'
        config = ConfigParser.ConfigParser()
        config.read(config_file_path)

        # OAuth folder
        self.oauth_folder = config.get('oauth', 'folder')

        # Folder (or collection) in Drive where you want the photos to go
        self.folder = config.get('docs', 'folder')

        # Options
        self.delete_after_upload = config.getboolean('options', 'delete-after-upload')

        self._create_drive()

    def _create_drive(self):
        """Create a Drive service."""
        auth_required = True
        #Is there already a credentials file?
        storage = Storage(self.oauth_folder+'uploader_credentials.txt')
        credentials = storage.get()
        try:
            if credentials:
                # Check for expiry
                if credentials.access_token_expired:
                    if credentials.refresh_token is not None:
                        credentials.refresh(httplib2.Http())
                        auth_required = False
                else:
                    auth_required = False
        except:
            # Something went wrong - try manual auth
            pass

        if auth_required:
            flow = client.flow_from_clientsecrets(
                self.oauth_folder+'client_secrets.json',
                scope='https://www.googleapis.com/auth/drive',
                redirect_uri='urn:ietf:wg:oauth:2.0:oob')

            auth_uri = flow.step1_get_authorize_url()

            print 'Go to this link in your browser:'
            print auth_uri

            auth_code = raw_input('Enter the auth code: ')
            credentials = flow.step2_exchange(auth_code)
            storage.put(credentials)

        #Get the drive service
        http_auth = credentials.authorize(httplib2.Http())
        self.drive_service = discovery.build('drive', 'v2', http_auth)

    def _get_folder_id(self, folder_name):
        """Find and return the id of the folder given the title."""
        files = self.drive_service.files().list(q="title='%s' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false" % folder_name).execute()
        if len(files['items']) == 1:
            folder_id = files['items'][0]['id']
            return folder_id
        else:
            raise Exception('Could not find the %s folder' % folder_name)

    def upload_photo(self, photo_file_path):
        """Upload a photo to the specified folder. Then optionally send an email and optionally delete the local file."""
        folder_id = self._get_folder_id(self.folder)

        media = MediaFileUpload(photo_file_path, mimetype='image/jpeg')
        response = self.drive_service.files().insert(media_body=media, body={'title':os.path.basename(photo_file_path), 'parents':[{u'id': folder_id}]}).execute()
        #print response
        photo_link = response['alternateLink']

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.ERROR)
	#Run the find photos function
        FindPhotos()
        total_file_list = FindPhotos()._Photo_search()
        print total_file_list #just for reference
	#Upload photos
        for photo_path in total_file_list:
            PhotoUploader().upload_photo('%s' % photo_path)
            print "Photo %s uploaded" % photo_path
        print "Upload Complete"
    except Exception as e:
        exit('Error: [%s]' % e)
