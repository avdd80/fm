from datetime import *
import subprocess
import os
import socket
import re
from time import sleep

MONO_USB_AUDIO_REC_CMD = ''
STEREO_AUDIO_INJECTOR_REC_CMD = 'sudo arecord -c 2 -f S16_LE -V stereo -r 48000 -d '
TUNER_PATH = '/home/pi/Music/radio_tea5767/radio_tea5767'
ROOT_PATH = '/home/pi/Music/fm_db/'
SCHED_PATH_F = '/home/pi/Music/schedule.txt'
#TEMP_FILE_F = '/home/pi/temp.txt'

DROPBOX_DOWNLOAD_CMD = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh download '
DROPBOX_DELETE_CMD = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh delete /'
DROPBOX_LIST_CMD = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh list /'

def get_tune_freq ():

    global SCHED_PATH_F

    ret_val = 0 # Radio off
    timenow = datetime.now();

    sched_fp = open(SCHED_PATH_F, 'r')
    log_lines = sched_fp.read().split("\n")
    sched_fp.close()

    if (timenow.minute < 59):
        ret_val = 1

    # Extract station frequency
    if ((log_lines[timenow.hour] > 0) and ret_val == 1):
        temp = log_lines[timenow.hour].split(',')

        ret_val = temp[1]
        print 'Read station: ' + ret_val
    else:
        ret_val = 0;

    return float(ret_val)


def delete_remote_file (hour):
    global DROPBOX_LIST_CMD
    global DROPBOX_DELETE_CMD
#    global TEMP_FILE_F

    # Get a list of all files on Dropbox
#    subprocess.call ('sudo ' + DROPBOX_LIST_CMD + ' | grep ' + str(hour*100) + ' > /home/pi/temp.txt' )
#    remote_list_fp = open(TEMP_FILE_F, 'r')
#    remote_list_lines = remote_list_fp.read().split("\n")
#    remote_list_fp.close()
#    os.remove (TEMP_FILE_F)

    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(output)

    remote_list_lines = output.split("\n")

    # Check if a file with current hour is present. 
    if (len (remote_list_lines) > 0):
        if (hour in remote_list_lines[0]):
            remote_list_lines_split = remote_list_lines[0].split(' ')
            filename = remote_list_lines_split[2]

            # If the file is found, delete it
            if ('mp3' in filename):
                print 'Deleting remote file (cmd commented) ' + filename
#                subprocess.call (DROPBOX_DELETE_CMD + filename)
            else:
                print ('Found garbage on remote! Cannot delete remote file!')



def tune_fm(freq):
    global TUNER_PATH
    print TUNER_PATH + ' ' + str(freq)
    subprocess.call (TUNER_PATH + ' ' + str(freq), shell=True)
    #subprocess.call ('/home/pi/Music/radio_tea5767/radio_tea5767 105.3', '')


def download_schedule ():
    global DROPBOX_DOWNLOAD_CMD
    global SCHED_PATH_F
    subprocess.call (DROPBOX_DOWNLOAD_CMD + 'schedule.txt ' + SCHED_PATH_F)


def record_fm_60_mins (target_wav_file, duration_mins):

    if (os.path.exists(target_wav_file)):
        print ('Deleting existing wav file:')
        os.remove (target_wav_file)
        print target_wav_file

    print 'Will record for ' + str(duration_mins) + ' minutes.'
    duration_secs = duration_mins * 60
    subprocess.call (STEREO_AUDIO_INJECTOR_REC_CMD + str(duration_secs) + ' ' + target_wav_file, shell=True)
    #subprocess.call ('sudo arecord -c 2 -f S16_LE -V stereo -r 48000 -d ' + str(duration_secs) + ' ' + target_wav_file, shell=True)
    print 'Record done!'
    if (os.path.exists(target_wav_file)):
        print ('Target file ' + target_wav_file + ' exists.')
        return 1
    else:
        print ('FAILED: Target file ' + target_wav_file + ' does not exists.')
        return 0


def send_udp_message (MESSAGE):

    UDP_IP = "127.0.0.1"
    UDP_PORT = 30000

    print "UDP target IP:", UDP_IP
    print "UDP target port:", UDP_PORT
    print "message: ", MESSAGE

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(MESSAGE, (UDP_IP, UDP_PORT))



FM_stations = {88.3: 'San_Diegos_Jazz', 89.5: 'NPR', 91.1: '91X_XETRA_FM', 93.3: 'Channel93_3', 94.1: 'Star94_1', 94.9: 'San_Diegos_Alternative', 95.7: 'KISSFM', 96.5: 'KYXY', 98.1: 'Sunny_98_1', 101.5: '101KGB_Classic_Rock', 102.9: 'Amor', 105.3: 'ROCK1053', 106.5: 'Que_Buena'}

def get_station_name (freq):
    station_name = ''
    if freq in FM_stations:
        station_name = FM_stations[freq]
    return station_name

def main ():

    global ROOT_PATH
    loop = 1
    
    ########################## HACK ##########################
    delete_remote_file (9)
    exit()
    while loop:
        #loop = 0
        target_wav_file = ''
        is_record_success = 0

        tune_freq = get_tune_freq ()

        if (tune_freq > 0):
            timenow = datetime.now()
            hour = timenow.hour
            minute = timenow.minute
            print timenow
            formatted_hour = str(hour*100)
            if (len(formatted_hour) < 4):
                formatted_hour = '0' + formatted_hour
            target_wav_file = ROOT_PATH + 'wav/' + formatted_hour + '_' + get_station_name(tune_freq) + '.wav'
            target_mp3_file = ROOT_PATH + 'mp3/' + formatted_hour + '_' + get_station_name(tune_freq) + '.mp3'
            if os.path.exists(target_wav_file):
                os.remove(target_wav_file)
            print 'Tuning FM...'
            tune_fm(tune_freq)
            print 'FM tuned to ' + str(tune_freq) + ' MHz'
            timenow = datetime.now()
            duration_mins = 60 - minute
            
            print 'Record for ' + str(duration_mins) + ' mins'
            is_record_success = record_fm_60_mins (target_wav_file, duration_mins)

            if (is_record_success):
                
                #delete_remote_file (hour)

                send_udp_message (target_wav_file + ',' + target_mp3_file)
                print 'Record success'
                
                # Download requested recording schedule
                download_schedule ()
            else:
                print 'Record failed'
                sleep (60)
        else:
            print 'No recording'
            sleep (60)

    #else:
            #radio_off()

main()
