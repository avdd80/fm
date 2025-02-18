# FM over IP

Setup Audio Injector:

  1. Connect audio injector or HifiBerry DAC+ADC to Raspberry pi header
  2. Remove line "dtparam=audio=on" from /boot/config.txt
  3. In the same section, add "dtoverlay=audioinjector-wm8731-audio" for audio injector and "dtoverlay=hifiberry-dacplusadc" for HifiBerry DAC+ADC
  4. Reboot Raspberry Pi and check if the soundcard is detected using "arecord -l"

# Dependencies:

  1. Dropbox Uploader
    https://github.com/andreafabrizi/Dropbox-Uploader
    Install in /home/pi/Downloads
  
  2. Create a dropbox account, get access token from https://www.dropbox.com/developers/apps

  3. TEA5767 Driver
    https://github.com/kjnam100/radio_tea5767
    Install in /home/pi/Downloads
    Compile a binary using following command inside /home/pi/Downloads/radio_tea5767
```
      sudo g++ -Wall -lm  radio_tea5767.c -o radio_tea5767 -lwiringPi
```  
  4. LAME MP3 encoding software
  sudo apt-get install lame
  
  5. MP3 Tagging Software (optional)
  sudo apt-get install -y libid3-tools
  
  # Add FM scripts to startup: 

  1. Add following lines to /home/pi/fm/cron_launcher.sh
     ```
     #!/bin/sh
     sudo /usr/bin/python /home/pi/fm/compress_n_upload.py &
     sudo /usr/bin/python /home/pi/fm/fm_rec.py &
     ```
  2. Make the shell script executable
     ```
     chmod +x /home/pi/fm/cron_launcher.sh
     ```
  3. Add shell script to crontab:
     ```
     sudo nano /etc/crontab

     # Reboot everyday at midnight 12:00 AM
     0 0 * * * root reboot
     # Launch FM scripts at 12:02 AM everyday
     2 0 * * * root /home/pi/fm/cron_launcher.sh
     ```
   4. Reboot RPi to ensure crontab takes effect.
   5. Confirm that scripts have started by grepping running processes:
      ```
      ps axg | grep fm_rec
      ps axg | grep compress_n_upload
      ps axg | grep arecord
      ```
     
  
