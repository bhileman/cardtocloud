#!/usr/bin/python
'''
Created 1/11/17 by BrettBuilds
v1.3  Updated 2/16/17

'''
import sys
import smtplib
from datetime import datetime
import mraa
import os.path
import logging
import time
import httplib2
from apiclient import discovery
from oauth2client import client
from oauth2client.file import Storage
from googleapiclient.http import MediaFileUpload
import ConfigParser
import os
import socket
import os
from urllib2 import urlopen, URLError, HTTPError


#assign upload start button
button = mraa.Gpio(20)

#assign program LED
led = mraa.Gpio(21)

#set GPIO21 to output mode
led.dir(mraa.DIR_OUT)

#set GPIO 20 to input mode
button.dir(mraa.DIR_IN)

def CheckConnect():
    print 'checking connection'
    socket.setdefaulttimeout( 23 )
    url = 'http://google.com/'
    try :
        response = urlopen( url )
    except HTTPError:
        led.write(1)
        return 'Disconnected'
    except URLError:
        led.write(1)
        return 'Disconnected'
    else :
        html = response.read()
        responseurl = response.url
        if response.url.startswith('http://www.google'):
            return 'Connected'
        else:
            return 'Disconnected'

class FindPhotos:
    # Search SD Card and find all photos
    def _init_(self):
        self._Photo_search()

    def _Photo_search(self):
        photolist = []
        for dirpath, subdirs, files in os.walk('./mnt'):
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

        # Assign the location of the config file path
        self.oauth_folder = './root/config'

        # Options to potentially add
        #self.delete_after_upload = config.getboolean('options', 'delete-after-upload')

        # Run auth sequence before any other funtions
        self._create_drive()

    def _create_drive(self):
        auth_required = True
        #Search if a credentials file already exists
        storage = Storage('./root/config/uploader_credentials.txt')
        credentials = storage.get()
        try:
            if credentials:
                # Check if token is expired
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
                './root/config/client_secrets.json',
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
        # Get the folder ID for the google drive folder specified
        """Find and return the id of the folder given the title."""
        print 'getting folder ID'
        files = self.drive_service.files().list(q="title='%s' and mimeType contains 'application/vnd.google-apps.folder' and trashed=false" % folder_name).execute()
        if len(files['items']) == 1:
            folder_id = files['items'][0]['id']
            return folder_id
        else:
            raise Exception('Could not find the %s folder' % folder_name)

    def upload_photo(self, photo_file_path, folder_id):
        """Upload a photo to the specified folder"""
        # print 'performing upload'
        "folder_id = self._get_folder_id(self.folder)"
        media = MediaFileUpload(photo_file_path, mimetype='image/jpeg')
        response = self.drive_service.files().insert(media_body=media, body={'title':os.path.basename(photo_file_path), 'parents':[{u'id': folder_id}]}).execute()
        #print response
        photo_link = response['alternateLink']

if __name__ == '__main__':
    os.system("mount /dev/mmcblk0p1 /mnt")
    time.sleep(1)
    # Check for internet connection, auto switch to AP Mode if not connected
    if CheckConnect() == 'Connected':
        print "connected"
    else:
        os.system("uci set wireless.sta.disabled=1")
        time.sleep(1)
        os.system("uci commit")
        time.sleep(3)
        os.system("wifi")
        while True:
            led.write(0)
            time.sleep(.2)
            led.write(1)
            time.sleep(.2)
    # Begin Upload Sequence
    while True:
        if button.read() == True:
            print
            led.write(1) # make LED solid while uploading
            logging.basicConfig(level=logging.ERROR)
            total_file_list = FindPhotos()._Photo_search() #Create list of all photos on the SD Card
            folder_id = PhotoUploader()._get_folder_id('CardToCloud Photos') #Get Folder ID.... Specify your desired folder here
            for photo_path in total_file_list:
                PhotoUploader().upload_photo('%s' % photo_path , folder_id)
                print "Photo %s uploaded" % photo_path
            print "Upload Complete"
            led.write(0) # turn off LED once upload is complete
            break
        else:
            # Blink LED to indicate that the program is in standby ready to begin
            led.write(0)
            time.sleep(1)
            led.write(1)
            time.sleep(1)
