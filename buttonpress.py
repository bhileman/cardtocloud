import mraa
import time
import os

button = mraa.Gpio(20)

#set GPIO 20 to input mode
button.dir(mraa.DIR_IN)
while True:
	print "P8 state:", button.read()
	if (button.read() == 1):
		os.system("python root/uploadersd.py")
		break
	time.sleep(2)
