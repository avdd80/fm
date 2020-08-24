# fm

Setup Audio Injector:

  1. Connect audio injector or HifiBerry DAC+ADC to Raspberry pi header
  2. Remove line "dtparam=audio=on" from /boot/config.txt
  3. In the same section, add "dtoverlay=audioinjector-wm8731-audio" for audio injector and "dtoverlay=hifiberry-dacplusadc" for HifiBerry DAC+ADC
  4. Reboot Raspberry Pi and check if the soundcard is detected using "arecord -l"

Dependencies:

  1. Dropbox Uploader 
  https://github.com/andreafabrizi/Dropbox-Uploader
  Install in /home/pi/Downloads
  
  Create a dropbox account, get access token from https://www.dropbox.com/developers/apps
  
  2. TEA5767 Driver
  https://github.com/kjnam100/radio_tea5767
  Install in /home/pi/Downloads
  Compile a binary using command "sudo make all" inside /home/pi/Downloads/radio_tea5767
  
  3. LAME MP3 encoding software
  sudo apt-get install lame
  
  4. MP3 Tagging Software (optional)
  sudo apt-get install -y libid3-tools
  
  
  
