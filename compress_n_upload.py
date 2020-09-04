import socket
import subprocess
import shlex
import os
from datetime import *
from time import sleep

UDP_IP = "127.0.0.1"

UDP_PORT_IN  = 30000
sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind((UDP_IP, UDP_PORT_IN))

# ./dropbox_uploader.sh upload testfile.jpg /dropbox/whatever/folder/you/want
DROPBOX_UPLOADER_CMD = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh upload '
DROPBOX_LIST_CMD     = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh list '

# #################################################################
def is_file_valid(filepath, extension): # input audio file path and extension (.xxx)
    if os.path.isfile(filepath) and filepath.endswith(extension):
        return 1
    else:
        print('Bad file path ' + filepath + ' or extension: ' + extension) # warning message
        return 0

def wav2mp3 (src, dest, alb, song, artist, year, genre, cover_art):

    is_success = 0

    print 'WAV2MP3:'
    cmd = 'sudo lame '
    cmd = cmd + ' ' + src
    cmd = cmd + ' ' + dest
    cmd = cmd + ' --add-id3v2 '
    cmd = cmd + ' --tl ' + alb
    cmd = cmd + ' --tt ' + song
    cmd = cmd + ' --ta ' + artist
    cmd = cmd + ' --ty ' + year
    cmd = cmd + ' --tg ' + genre
    if (cover_art != ''):
        cmd = cmd + ' --ti ' + cover_art
    print 'Wave -> MP3:'
    print cmd
    subprocess.call (cmd, shell=True)
    sleep(10)
    ################ HACK ####################
    #ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #output = ps.communicate()[0]
    #print(output)
    
    if (os.path.exists (dest)):
        # Remove Wav file
        print ('Success! dest file created. Deleting src file....')
        ################ HACK ####################
        #os.remove (src)

        is_success = 1
    else:
        print ('Error: dest file creation failed!')

    return is_success


def trigger_file_upload (filename):

    global DROPBOX_UPLOADER_CMD

    print 'Uploading file to Dropbox...'
    cmd = DROPBOX_UPLOADER_CMD + ' ' + filename + ' /.'

    ps = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = ps.communicate()[0]
    print(output)

    if (output.find('DONE') > 0 ):
        return 1
    else:
        return 0

def get_remote_file_name (hour):

    ps = subprocess.Popen(DROPBOX_LIST_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    remote_list = ps.communicate()[0]
    print(remote_list)


while True:
    print ('Waiting for FM recorder to finish...')
    data, addr = sock_in.recvfrom(512)

    temp = data.split(',')

    wav_target_file = temp[0]
    mp3_target_file = temp[1]

    ############### MP3 metadata ###############
    album_value     = temp[2]
    song_value      = temp[3]
    artist_value    = temp[4]
    year_value      = temp[5]
    genre_value     = temp[6]
    cover_art_value = temp[7]

    print ('Received UDP message with payload:')
    print ('Wav file:  ' + wav_target_file)
    print ('MP3 file:  ' + mp3_target_file)
    print ('Album:     ' + album_value)
    print ('Song:      ' + song_value)
    print ('Artist:    ' + artist_value)
    print ('Year:      ' + year_value)
    print ('Genre:     ' + genre_value)
    print ('Cover Art: ' + cover_art_value)

    is_wav2mp3_success = wav2mp3 (wav_target_file, mp3_target_file, album_value, song_value, artist_value, year_value, genre_value, cover_art_value)
    
    # Delete wave file
    print ('Deleting wav file...')
    ################ HACK ####################
    #ps = subprocess.Popen('sudo rm -f ' + wav_target_file , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    #output = ps.communicate()[0]
    #print(output)

    if (is_wav2mp3_success):

        #tag_mp3 (mp3_target_file, album_value, song_value, artist_value, year_value, genre_value, '/home/pi/fm/cover.jpg')

        is_upload_success = trigger_file_upload (mp3_target_file)
        
        if (is_upload_success):
            print 'Success: Dropbox upload success'
        else:
            print 'Error: Dropbox upload failed.'

        #os.remove (mp3_target_file)
        print ('Deleting mp3 file...')
        ps = subprocess.Popen('sudo rm -f ' + mp3_target_file , shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        print(output)
    else:
        print ('Error: mp3 conversion failed!')
