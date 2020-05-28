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
SAN_FM_stations = {88.3: 'San_Diegos_Jazz', 89.5: 'NPR', 91.1: '91X_XETRA_FM', 93.3: 'Channel93_3', 94.1: 'Star94_1', 94.9: 'San_Diegos_Alternative', 95.7: 'KISSFM', 96.5: 'KYXY', 98.1: 'Sunny_98_1', 101.5: '101KGB_Classic_Rock', 102.9: 'Amor', 105.3: 'ROCK1053', 106.5: 'Que_Buena'}
#BLR_FM_stations = {91.1: 'Radio City'}

DROPBOX_DOWNLOAD_SCRIPT = 'sudo -S /home/pi/fm/download_schedule.sh'
DROPBOX_DOWNLOAD_CMD = 'sudo /home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh download '
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

    ps = subprocess.Popen(DROPBOX_LIST_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(output)

    

    # Check if a file with current hour is present.
    if (len (output) > 0):
        # Search for 'hh00_'
        if (hour > 0):
            search_str = (str(hour*100)+'_')
        elif (hour == 0):
            search_str = '0000_'

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
            print 'Found file at index ' + str(i) + '\n'

            # The first list of the list command result does not contain filename. If
            # i has not incremented beyond 0, no file on remote dir is found. 
            if (i > 0 and i < length):
            
                print ' Found remote file: ' + remote_list_lines[i]
            
                remote_list_lines_split = remote_list_lines[i].split(' ')
                if (len(remote_list_lines_split) >= 3):
                    filename = remote_list_lines_split[3]

                # If a matching file is found, delete it
                if ('mp3' in filename):
                    print 'Deleting remote file (cmd commented) ' + filename
    #                subprocess.call (DROPBOX_DELETE_CMD + filename)
                else:
                    print ('Found garbage on remote! Cannot delete remote file!\n')
            else:
                print ('No matching file on remote dir for ' + search_str + '\n')
    else:
        print 'Bad result from list cmd!'



def tune_fm(freq):
    global TUNER_PATH
    print TUNER_PATH + ' ' + str(freq)
    subprocess.call (TUNER_PATH + ' ' + str(freq), shell=True)
    #subprocess.call ('/home/pi/Music/radio_tea5767/radio_tea5767 105.3', '')


def download_schedule ():
    global DROPBOX_DOWNLOAD_CMD
#    global DROPBOX_DOWNLOAD_SCRIPT
    global SCHED_PATH_F
    cmd = DROPBOX_DOWNLOAD_CMD + 'schedule.txt ' + SCHED_PATH_F
    #cmd = DROPBOX_DOWNLOAD_SCRIPT
    print 'Download schedule cmd:\n'
    print cmd + '\n'
    #subprocess.call (cmd)

    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(output)
    sleep (10)

    

def record_fm_mins (target_wav_file, duration_mins):

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

def get_station_name (freq):

    global SAN_FM_stations
    # Default name
    station_name = str(freq) + ' MHz'
    if freq in SAN_FM_stations:
        station_name = SAN_FM_stations[freq]
    return station_name

def main ():

    global ROOT_PATH
    loop = 1
    
    while loop:
        #loop = 0
        target_wav_file = ''
        is_record_success = 0

        tune_freq = get_tune_freq ()

        if (tune_freq > 0):
            timenow = datetime.now()
            hour = timenow.hour
            minute = timenow.minute
            formatted_hour = str(hour*100)
            if (hour == 0):
                formatted_hour = '0000'
            target_wav_file = ROOT_PATH + 'wav/' + formatted_hour + '_' + get_station_name(tune_freq) + '.wav'
            target_mp3_file = ROOT_PATH + 'mp3/' + formatted_hour + '_' + get_station_name(tune_freq) + '.mp3'
            if os.path.exists(target_wav_file):
                os.remove(target_wav_file)
            print 'Tuning FM...'
            tune_fm(tune_freq)
            print 'FM tuned to ' + str(tune_freq) + ' MHz\n'
            timenow = datetime.now()
            #duration_mins = 60 - minute
            duration_mins = 5
            
            if (duration_mins > 4):
            
                print 'Record for ' + str(duration_mins) + ' minutes'
                is_record_success = record_fm_mins (target_wav_file, duration_mins)
                print 'Record done.\n'

                if (is_record_success):

                    delete_remote_file (hour)

                    ############### MP3 metadata ###############
                    udp_msg = target_wav_file + ',' + target_mp3_file + ','

                    album_value = get_station_name(tune_freq)
                    udp_msg = udp_msg + album_value + ','

                    song_value = formatted_hour + ':00 ' + get_station_name(tune_freq)
                    udp_msg = udp_msg + song_value + ','

                    artist_value = 'Abhijeet Deshpande'
                    udp_msg = udp_msg + artist_value + ','

                    year_value = str(timenow.year)
                    udp_msg = udp_msg + year_value + ','

                    genre_value  = 'Radio'
                    udp_msg = udp_msg + genre_value

                    send_udp_message (udp_msg)
                    print 'Record success'

                    # Download requested recording schedule
                    download_schedule ()
                else:
                    print 'Record failed. Wait 60 seconds...'
                    sleep (60)
            else:
                print 'Record duration too short (' + str(duration_mins) + ' minutes). Skipping current record. Wait 60 seconds...'
                sleep (60)
        else:
            print 'No recording. Wait 60 seconds...'
            sleep (60)

    #else:
            #radio_off()
###############################################################
# Main Function Call
###############################################################
main()
