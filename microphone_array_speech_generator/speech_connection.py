#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date     : 2019-11-27 09:33:27
# @Author   : Cheng Rui (chengrui@emails.bjut.edu.cn)
# @Function : speech connection
# @Veision  : Release 0.1

import numpy as np
from scipy.io import wavfile
import glob

# speech connection
def speech_connection(root_path, mic, channels, SNRs, RTs):
    '''
    This function is used to implement speech connection.
    
    Usage:  speech_connection(root_path, mic, channels, SNRs, RTs)

        root_path      - address of independent speech and noise
        mic            - the index of speech and noise
        channels       - the index of channel
        SNRs           - the index of SNR
        RTs            - the index of RT60
    
    Example call:
        speech_connection(root_path, mic, channels, SNRs, RTs)
    
    Author: Rui Cheng
    '''

    fileNamesTrain = np.array([])

    for s in mic:
        for ch in channels:
            for snr in SNRs:
                for rt in RTs:
                    for file in glob.glob(root_path+s+'\\'+ch+'\\'+snr+'\\'+rt+'\\'+'*.wav'):
                        fileNamesTrain = np.append(fileNamesTrain, file)

            print(s, ch, 'have been obtained. There are', fileNamesTrain.shape[0], 'segments in total. Speech connection...')
			
            trimmed_output_train = np.array([])
            for fileName in fileNamesTrain:
                Fs, newFile = wavfile.read(fileName)
                trimmed_output_train = np.append(trimmed_output_train, newFile)

            # define output as int16 in order to avoid clipping using wavfile.write
            int_array = trimmed_output_train.astype("int16")
            print(int_array, int_array.shape)
			
            wavfile.write(root_path+s+'\\'+s+'_'+ch+'_4snr_7rt.wav', 16000, int_array)         #TIMIT_577(3)_TRAIN  TIMIT_288(32)_TRAIN
            print ("Connected and output.")

print('\n')
print('Speech Connection')
print('==========================================================================================================')
print('\n')

# address and index
train_root_path = 'C:\\Projects\\chengrui\\Multi_Data\\MASG_mic_speech_train\\'
test_root_path = 'C:\\Projects\\chengrui\\Multi_Data\\MASG_mic_speech_test\\'
mic = ['mic_clean', 'mic_clean_noise', 'mic_clean_rever', 'mic_clean_rever_noise', 'mic_noise']
channels = ['ch0', 'ch1', 'ch2', 'ch3', 'ch4', 'ch5', 'ch6', 'ch7', 'ch8', 'ch9']
SNRs = ['-5dB', '0dB', '5dB', '10dB']
RTs = ['200ms', '300ms', '400ms', '500ms', '600ms', '700ms', '800ms']

'''# speech connection for test dataset
print('[test dataset]')
speech_connection(test_root_path, mic, channels, SNRs, RTs)
print('test dataset has been connection.')
print('\n')'''

# speech connection for train dataset
print('[train dataset]')
speech_connection(train_root_path, mic, channels, SNRs, RTs)
print('train dataset has been connection.')
print('\n')
