# cardtocloud
Quick upload device from SD card to cloud storage. 

Description: 
  - Hardware - Linkit Smart 7688
Firmware - 0.9.3
  - Supported Cloud Storage - Google Drive
  - File Support - jpg (JPG)
  
Installation:
  1. Follow steps here to get device connected to wifi: https://docs.labs.mediatek.com/resource/linkit-smart-7688/en/get-started/get-started-with-the-linkit-smart-7688-development-board
  2. Copy files to root directory on device using scp client
  3. SSH into device ,I use Putty, for Linkit device ip mylinkit.local port 22
  4. Install google drive api ```pip install --upgrade google-api-python-client```
  5. Create google app, active google drive and plus api, create credentials oauth client(other), download json, insert into config folder
  

Usage: 
  1. If using a different device you will need to update the directory for the os.walk piece of code. The Linkit mounts the SD card in this tmp folder location. This varies with your device. 
  2. connect device to wifi
  3. Insert SD card
  4. Go to top level cd / working on trying to figure out how to eliminate this step)
  5. run program ```python root/uploadersd.py```
  6. if first time using copy url from command 
  7. Go to link in browser, authorize the app, code code
  8. Manually enter code into command enter certificate will save to config folder
  9. Upload will gather all photos on sd card and will upload all photos to the folder specified in the config file


Planned Updates:

Software:
  - Add duplicate protection  PENDING
  - Main folder, year and month sub-dir when uploading  PENDING
  - Run on button press  PENDING

Credits:
Thanks Jeremy for the google flow code. Helped a ton! (https://github.com/jerbly/tutorials)
