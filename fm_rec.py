from datetime import *
import subprocess
import os
import socket
import re
from time import sleep

############################################################
# SET BY USER ##############################################
# Only set this variable to change FM source location ######
############################################################
#RADIO_STATION='SAN DIEGO'
RADIO_STATION='BANGALORE'
############################################################
# DO NOT MODIFY ############################################
# RECORD COMMANDS ##########################################
############################################################
STEREO_RECORD_CMD = 'sudo arecord -c 2 -f S16_LE -V stereo -r 48000 -d '
MONO_RECORD_CMD   = 'sudo arecord -c 1 -f S16_LE -r 44100 --device=hw:1,0 -d '
############################################################
# SET BY USER ##############################################
# SOUNDCARD TYPE ###########################################
############################################################
#REC_CMD = MONO_RECORD_CMD
REC_CMD = STEREO_RECORD_CMD
############################################################
# DO NOT MODIFY ############################################
# COMMON SETTINGS ##########################################
############################################################
TUNER_PATH = '/home/pi/Downloads/radio_tea5767/radio_tea5767'
DROPBOX_DELETE_CMD = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh delete /'
DROPBOX_LIST_CMD = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh list /'
MUSIC_DB         = '/home/pi/Music/fm_db/'
MIN_RECORD_DURATION_MINS = 12
############################################################

DROPBOX_DOWNLOAD_SCRIPT = ''
DROPBOX_DOWNLOAD_CMD = ''
SCHED_PATH_F = ''
ROOT_PATH = ''
COVER_ROOT = ''
FM_stations = {}
CoverArt = {}



def load_config(config):
    global REC_CMD
    global DROPBOX_DOWNLOAD_SCRIPT
    global DROPBOX_DOWNLOAD_CMD
    global SCHED_PATH_F
    global FM_stations
    global ROOT_PATH
    global CoverArt
    global COVER_ROOT
    print ('Load ' + config + ' config')
    if (config == 'SAN DIEGO'):
        
        # SAN DIEGO ################################################
        print ( REC_CMD )
        DROPBOX_DOWNLOAD_SCRIPT = 'sudo -S /home/pi/fm/download_schedule.sh'
        DROPBOX_DOWNLOAD_CMD = 'sudo /home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh download schedule.txt '
        SCHED_PATH_F = '/home/pi/Music/schedule.txt'
        ROOT_PATH = MUSIC_DB + 'san/'
        COVER_ROOT  = '/home/pi/fm/coverart/san/'
        FM_stations = {88.3: 'San_Diegos_Jazz',
                       89.5: 'NPR', 
                       91.1: '91X_XETRA_FM', 
                       93.3: 'Channel93_3', 
                       94.1: 'Star94_1', 
                       94.9: 'San_Diegos_Alternative', 
                       95.7: 'KISSFM', 
                       96.5: 'KYXY', 
                       98.1: 'Sunny_98_1', 
                       101.5: '101KGB_Classic_Rock', 
                       102.9: 'Amor', 
                       105.3: 'ROCK1053', 
                       106.5: 'Que_Buena'}
        CoverArt    = {88.3: COVER_ROOT + 'Jazz.jpg',
                       89.5: COVER_ROOT + 'san_fm.jpg',
                       91.1: COVER_ROOT + 'san_fm.jpg',
                       93.3: COVER_ROOT + 'san_fm.jpg',
                       94.1: COVER_ROOT + 'Star.jpg',
                       94.9: COVER_ROOT + 'san_fm.jpg',
                       95.7: COVER_ROOT + 'KissFM.jpg',
                       96.5: COVER_ROOT + 'san_fm.jpg',
                       98.1: COVER_ROOT + 'Sunny.jpg',
                       101.5: COVER_ROOT + 'KGB.jpg',
                       102.9: COVER_ROOT + 'Amor.jpg',
                       105.3: COVER_ROOT + 'san_fm.jpg',
                       106.5: COVER_ROOT + 'san_fm.jpg'}
    elif (config == 'BANGALORE'):
        # BANGALORE ################################################
        DROPBOX_DOWNLOAD_SCRIPT = 'sudo -S /home/pi/fm/download_blr_schedule.sh'
        DROPBOX_DOWNLOAD_CMD = 'sudo /home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh download schedule_blr.txt '
        SCHED_PATH_F = '/home/pi/Music/schedule_blr.txt'
        ROOT_PATH   = MUSIC_DB + 'blr/'
        COVER_ROOT  = '/home/pi/fm/coverart/blr/'
        FM_stations = {91.1: 'Radio_City', 
                       98.3: 'Radio_Mirchi', 
                       94.3: 'Radio_One', 
                       93.5: 'Red_FM', 
                       91.9: 'Radio_Indigo', 
                       92.7: 'Big_FM',
                       97.0: 'Radio_Girmit',
                       104.0: 'Fever_FM', 
                       100.1: 'Amrutavarshini', 
                       101.3: 'Rainbow',
                       90.4: 'Radio_Active_Jain', 
                       102.9: 'Vividh_Bharati',
                       105.6: 'GyanVani'}
        CoverArt    = {91.1:  COVER_ROOT + 'RadioCity.png', 
                       98.3:  COVER_ROOT + 'RadioMirchi.jpg',
                       94.3:  COVER_ROOT + 'RadioOne.JPG', 
                       93.5:  COVER_ROOT + 'RedFM.png', 
                       91.9:  COVER_ROOT + 'Indigo.JPG', 
                       92.7:  COVER_ROOT + 'BigFM.JPG', 
                       97.0:  COVER_ROOT + 'RadioGirmit.PNG',
                       104.0: COVER_ROOT + 'Fever.png', 
                       100.1: COVER_ROOT + 'Amrutavarshini.JPG', 
                       101.3: COVER_ROOT + 'FMRainbow.JPG', 
                       90.4:  COVER_ROOT + 'RadioActive.png', 
                       102.9: COVER_ROOT + 'Aakashvani.png',
                       105.6: COVER_ROOT + 'GyanVani.JPG'}
    print ( 'Record command: ' + REC_CMD )
        
def setup():
    global ROOT_PATH
    global MUSIC_DB
    global SCHED_PATH_F

    if (not os.path.exists(ROOT_PATH)):
        if (not os.path.exists(MUSIC_DB)):
            os.mkdir(MUSIC_DB)
        os.mkdir(ROOT_PATH)
        os.mkdir(ROOT_PATH+'wav')
        os.mkdir(ROOT_PATH+'mp3')
    download_schedule ()
        

def get_cover_art_path (freq):
    global COVER_ROOT
    global CoverArt
    # Default empty name
    cover_art_path = COVER_ROOT + 'default.jpeg'
    if freq in CoverArt:
        cover_art_path = CoverArt[freq]
    return cover_art_path

def get_tune_freq ():

    global SCHED_PATH_F

    ret_val = 0 # Radio off
    timenow = datetime.now();

    if (not os.path.exists(SCHED_PATH_F)):
        download_schedule ()
    sched_fp = open(SCHED_PATH_F, 'r')
    sched_lines = sched_fp.read().split("\n")
    sched_fp.close()

    if (timenow.minute < 59):
        ret_val = 1

    print ( sched_lines[0:24] )
    print ( 'Recording hour: ' + str(timenow.hour) + ':00' )
        
    # Extract station frequency
    if ((sched_lines[timenow.hour] > 0) and ret_val == 1):
        temp = sched_lines[timenow.hour].split(',')

        ret_val = temp[1]
        print ('Read station: ' + ret_val + ' MHz')
    else:
        ret_val = 0;
    return float(ret_val)


def delete_remote_file (search_str):
    global DROPBOX_LIST_CMD
    global DROPBOX_DELETE_CMD

    ps = subprocess.Popen(DROPBOX_LIST_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(output)

    # Check if a file with current hour is present.
    if (len (output) > 0):

        # Is hh00_ present on the remote dir?
        if (search_str in output):
            i = 0
            
            # Split the result of list cmd line-by-line and locate the matching file
            # listing:
            # > Listing "/"... DONE
            # [D]        #  du_tests
            # [F] 27840768 2200_ABC.mp3
            # [F] 36480768 2300_DEF.mp3
            # [F] 57600768 0000_XYZ.mp3
            
            remote_list_lines = output.split("\n")
            length = len (remote_list_lines)
            
            # Search for matching file names
            while (i < length and search_str not in remote_list_lines[i]):
                i += 1
            print ('Found file at index ' + str(i) + '\n')

            # The first line of the list command result does not contain filename. If
            # i has not incremented beyond 0, no file on remote dir is found. 
            if (i > 0 and i < length):
           
                remote_list_lines_split = remote_list_lines[i].split(' ')
                if (len(remote_list_lines_split) >= 3):
                    filename = remote_list_lines_split[3]

                print (' Found remote file: ' + filename + ' out of ' + remote_list_lines[i])
                    
                # If a matching file is found, delete it
                if ('mp3' in filename):
                    print ('Deleting remote file: ' + filename)
                    #subprocess.call (DROPBOX_DELETE_CMD + filename)
                    ps = subprocess.Popen(DROPBOX_DELETE_CMD + filename, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                    output = ps.communicate()[0]
                    print(output)
                else:
                    print ('Found garbage on remote:\nFile: ' + filename + '\nCannot delete remote file!\n')
            else:
                print ('No matching file on remote dir for ' + search_str + '\n')
    else:
        print ('Bad result from list cmd!')

def radio_off():
    global TUNER_PATH
    cmd = TUNER_PATH + ' off'
    print (cmd)
    subprocess.call (cmd, shell=True)


def tune_fm(freq):
    global TUNER_PATH

    cmd = TUNER_PATH + ' on'
    print (cmd)
    subprocess.call (cmd, shell=True)
    
    cmd = TUNER_PATH + ' ' + str(freq)
    print (cmd)
    subprocess.call (cmd, shell=True)
    
    cmd = TUNER_PATH + ' ' + 'stereo'
    print (cmd)
    subprocess.call (cmd, shell=True)
    #subprocess.call ('/home/pi/Music/radio_tea5767/radio_tea5767 105.3', '')


# Download schedule.txt file from Dropbox. The schedule file contains an array of size 24
# Each line is a csv of hour,FM frequency pair:
#
# 0,91.1   # Tune into 91.1 MHz at 12:00 midnight
# 1,88.6   # Tune into 88.6 MHz at 01:00 AM
# 2,0      # Skip tuning at 02:00 AM
# ....
# 23,102.9 # Tune into 102.9 MHz at 11:00 PM
def download_schedule ():
    global DROPBOX_DOWNLOAD_CMD
#    global DROPBOX_DOWNLOAD_SCRIPT
    global SCHED_PATH_F
    cmd = DROPBOX_DOWNLOAD_CMD + SCHED_PATH_F
    print ('Download schedule cmd:\n')
    print (cmd + '\n')

    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(output)
    sleep (10)

    

def record_fm_mins (target_wav_file, duration_mins):
    
    global REC_CMD

    if (os.path.exists(target_wav_file)):
        print ('Deleting existing wav file:')
        print (target_wav_file)
        os.remove (target_wav_file)

    print ('Will record for ' + str(duration_mins) + ' minutes.')
    duration_secs = duration_mins * 60
    subprocess.call (REC_CMD + str(duration_secs) + ' ' + target_wav_file, shell=True)
    #subprocess.call ('sudo arecord -c 2 -f S16_LE -V stereo -r 48000 -d ' + str(duration_secs) + ' ' + target_wav_file, shell=True)
    print ('Record done!')
    if (os.path.exists(target_wav_file)):
        print ('Target file ' + target_wav_file + ' exists.')
        return 1
    else:
        print ('FAILED: Target file ' + target_wav_file + ' does not exists.')
        return 0


def send_udp_message (MESSAGE):

    UDP_IP = "127.0.0.1"
    UDP_PORT = 30000

    print ("UDP target IP:", UDP_IP)
    print ("UDP target port:", UDP_PORT)
    print ("message: ", MESSAGE)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))

def get_station_name (freq):

    global FM_stations
    # Default name
    station_name = str(freq) + 'MHz'
    if freq in FM_stations:
        station_name = FM_stations[freq]
    return station_name

def main ():

    global ROOT_PATH
    loop = 1
    
    f = open("/home/pi/fm/fm.log", "w")
    f.write("Log begin\n")
    
    setup()
    
    while loop:
        #loop = 0
        target_wav_file = ''
        is_record_success = 0

        tune_freq = get_tune_freq ()
        timenow = datetime.now()
        hour = timenow.hour
        minute = timenow.minute
        f = open("/home/pi/fm/fm.log", "a")
        f.write(str(hour) + ":" + str(minute) + " Tune freq = " + str(tune_freq) + "\n")
        f.close()

        if (tune_freq > 0):
            timenow = datetime.now()
            hour = timenow.hour
            minute = timenow.minute
            formatted_hour = str(hour*100)
            if (hour == 0):
                formatted_hour = '0000'
            elif (hour < 10):
                formatted_hour = '0' + formatted_hour
            target_wav_file = ROOT_PATH + 'wav/' + formatted_hour + '_' + get_station_name(tune_freq) + '.wav'
            target_mp3_file = ROOT_PATH + 'mp3/' + formatted_hour + '_' + get_station_name(tune_freq) + '.mp3'
            print ('Target wave file: ' + target_wav_file)
            print ('Target mp3 file:  ' + target_mp3_file)
            if os.path.exists(target_wav_file):
                os.remove(target_wav_file)
            if os.path.exists(target_mp3_file):
                os.remove(target_mp3_file)
            print ('Tuning FM...')
            tune_fm(tune_freq)
            print ('FM tuned to ' + str(tune_freq) + ' MHz\n')
            timenow = datetime.now()
            duration_mins = 60 - minute
            if (duration_mins > MIN_RECORD_DURATION_MINS):
            
                f = open("/home/pi/fm/fm.log", "a")
                f.write(str(hour) + ":" + str(minute) + "Record for " + str(duration_mins) + " minutes\n")
                f.close()
            
                print ('Record for ' + str(duration_mins) + ' minutes')
                is_record_success = record_fm_mins (target_wav_file, duration_mins)
                print ('Record done.\n')

                if (is_record_success):

                    delete_remote_file (formatted_hour + '_')

                    ############### MP3 metadata ###############
                    #[Arg 0]                          [Arg 1]
                    udp_msg = target_wav_file + ',' + target_mp3_file + ','
                    #[Arg 2]
                    album_value = get_station_name(tune_freq)
                    udp_msg = udp_msg + album_value + ','
                    #[Arg 3]
                    song_value = formatted_hour + '_' + get_station_name(tune_freq)
                    udp_msg = udp_msg + song_value + ','
                    #[Arg 4]
                    artist_value = 'Abhijeet_Deshpande'
                    udp_msg = udp_msg + artist_value + ','
                    #[Arg 5]
                    year_value = str(timenow.year)
                    udp_msg = udp_msg + year_value + ','
                    #[Arg 6]
                    genre_value  = 'Radio'
                    udp_msg = udp_msg + genre_value + ','
                    #[Arg 7]
                    cover_art_path_value  = get_cover_art_path(tune_freq)
                    udp_msg = udp_msg + cover_art_path_value
                    
                    print ('Sending UDP message for coversion:')
                    print (udp_msg)
                    send_udp_message (udp_msg)
                    print ('Record success')

                    # Download requested recording schedule
                    download_schedule ()
                else:
                    f = open("/home/pi/fm/fm.log", "a")
                    f.write(str(hour) + ":" + str(minute) + "Record failed. Wait 10 seconds...\n")
                    f.close()
                    print ('Record failed. Wait 10 seconds...')
                    sleep (10)
            else:

                f = open("/home/pi/fm/fm.log", "a")
                f.write(str(hour) + ":" + str(minute) + "Record duration too short (" + str(duration_mins) + " minutes). Skipping current record. Wait 60 seconds...\n")
                f.close()
                print ('Record duration too short (' + str(duration_mins) + ' minutes). Skipping current record. Wait 60 seconds...')
                sleep (60)
        else:
            print ('No recording. Wait 60 seconds...')
            f = open("/home/pi/fm/fm.log", "a")
            f.write(str(hour) + ":" + str(minute) + "No recording. Wait 60 seconds...\n")
            f.close()
            sleep (60)

    else:
            radio_off()
###############################################################
# Main Function Call
###############################################################
load_config(RADIO_STATION)

main()
