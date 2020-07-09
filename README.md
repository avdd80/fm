# fm

Setup Audio Injector:

  1. Connect audio injector to Raspberry pi header
  2. Remove line "dtparam=audio=on" from /boot/config.txt
  3. In the same section, add "dtoverlay=audioinjector-wm8731-audio"

Dependencies:

  1. Dropbox Uploader 
  https://github.com/andreafabrizi/Dropbox-Uploader
  
  Create a dropbox account, get access token from https://www.dropbox.com/developers/apps
  
  2. TEA5767 Driver
  https://github.com/kjnam100/radio_tea5767
  
  3. MP3 Tagging Software
  sudo apt-get install -y libid3-tools
  
  
  
