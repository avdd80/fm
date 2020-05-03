import socket
import subprocess
import shlex
import os

UDP_IP = "127.0.0.1"

UDP_PORT_IN  = 30000
sock_in = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_in.bind((UDP_IP, UDP_PORT_IN))

# ./dropbox_uploader.sh upload testfile.jpg /dropbox/whatever/folder/you/want
DROPBOX_UPLOADER_CMD = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh upload '
DROPBOX_LIST_CMD     = '/home/pi/Downloads/Dropbox-Uploader/dropbox_uploader.sh list '


def wav2mp3 (src, dest):

    is_success = 0

    print 'WAV2MP3:'
    cmd = 'sudo lame ' +  src + ' ' + dest
    print cmd
    subprocess.call (cmd, shell=True)
    
    if (os.path.exists (dest)):
        # Remove Wav file
        #os.remove (src)

        is_success = 1

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


def main ():
    
    
    data, server = sock_in.recvfrom(4096)
    
    print 'Received UDP: ' + data
    
    
    split_data = data.split(',')
    
    src = split_data[0]
    dst = split_data[1]


    print 'Source: ' + src
    print 'Destination: ' + dst
    
    wav2mp3 (src, dst)



def get_remote_file_name (hour):

    ps = subprocess.Popen(DROPBOX_LIST_CMD, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    remote_list = ps.communicate()[0]
    print(remote_list)
    

while True:
    data, addr = sock_in.recvfrom(512)

    temp = data.split(',')

    wav_target_file = temp[0]
    mp3_target_file = temp[1]

    is_wav2mp3_success = wav2mp3 (wav_target_file, mp3_target_file)
    os.remove (wav_target_file)

    if (is_wav2mp3_success):

        is_upload_success = trigger_file_upload (mp3_target_file)

        os.remove (mp3_target_file)


