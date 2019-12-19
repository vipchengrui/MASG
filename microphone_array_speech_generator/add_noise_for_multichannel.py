#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2019-11-12 15:13:27
# @Author  : Cheng Rui (chengrui@emails.bjut.edu.cn)
# @Function : add noise to clean and reverberation speech for multichannel
# @Veision  : Release 0.2

import numpy as np
import numpy.matlib
import matplotlib.pyplot as plt
from scipy.io import wavfile
import wave
from scipy.signal import lfilter

# ============= #
#   Functions   #
# ============= #

# sub_function - bin_interp
def bin_interp(upcount, lwcount, upthr, lwthr, Margin, tol):
    '''
    This implements bin_interp. 

    Usage:  bin_interp(upcount, lwcount, upthr, lwthr, Margin, tol)

    Example call:
        asl_ms_log, cc = bin_interp(upcount, lwcount, upthr, lwthr, Margin, tol)

    Python implementation from MATLAB: Rui Cheng
    '''

    if tol < 0:
        tol = -tol

    # check if extreme counts are not already the true active value
    iterno = 1
    if abs(upcount - upthr - Margin) < tol:
        asl_ms_log = upcount
        cc = upthr
        return asl_ms_log, cc
    if abs(lwcount - lwthr - Margin) < tol:
        asl_ms_log = lwcount
        cc = lwthr
        return asl_ms_log, cc

    # Initialize first middle for given (initial) bounds 
    midcount = (upcount + lwcount) / 2.0
    midthr = (upthr + lwthr) / 2.0
    # Repeats loop until `diff' falls inside the tolerance (-tol<=diff<=tol)
    while 1:
        diff = midcount - midthr - Margin
        if abs(diff) <= tol:
            break
        # if tolerance is not met up to 20 iteractions, then relax the tolerance by 10%
        iterno = iterno + 1
        if iterno > 20:
            tol = tol * 1.1
        if diff > tol:  # then new bounds are ...  
            midcount = (upcount + midcount) / 2.0
            # upper and middle activities
            midthr = (upthr + midthr) / 2.0
            # ... and thresholds
        elif diff < -tol:   # then new bounds are ... 
            midcount = (midcount + lwcount) / 2.0
            # middle and lower activities
            midthr = (midthr + lwthr) / 2.0
            # ... and thresholds

    # Since the tolerance has been satisfied, midcount is selected 
    # as the interpolated value with a tol [dB] tolerance.
    asl_ms_log = midcount
    cc = midthr

    return asl_ms_log, cc

# sub_function - asl_P56
def asl_P56(x, fs, nbits):
    '''
    This implements ITU P.56 method B. 

    Usage:  asl_P56(x, fs, nbits)

        x             - the column vector of floating point speech data
        fs            - the sampling frequency
        nbits         - the number of bits
    
    Example call:
        asl_ms, asl, c0 = asl_P56(x, fs, nbits)

    References:
    [1] ITU-T (1993). Objective measurement of active speech level. ITU-T 
        Recommendation P. 56

    Python implementation from MATLAB: Rui Cheng
    '''

    T = 0.03                # time constant of smoothing, in seconds
    H = 0.2                 # hangover time in seconds
    M = 15.9                # margin in dB of the difference between threshold and active speech level
    thres_no = nbits - 1    # number of thresholds, for 16 bit, it's 15
    eps = 2.2204e-16

    I = int(np.ceil(fs*H))       # hangover in samples
    g = np.exp(-1/(fs*T))   # smoothing factor in enevlop detection
    c = [pow(2,i) for i in range(-15, thres_no-16+1)]   
    # vector with thresholds from one quantizing level up to half the maximum code, at a step of 2, in the case of 16bit samples, from 2^-15 to 0.5
    a = [0 for i in range(thres_no)]    # activity counter for each level threshold
    hang = [I for i in range(thres_no)]     # % hangover counter for each level threshold

    sq = sum(pow(x,2))  # long-term level square energy of x
    x_len = len(x)      # length of x

    # use a 2nd order IIR filter to detect the envelope q
    x_abs = abs(x)
    p = lfilter([1-g], [1,-g], x_abs)
    q = lfilter([1-g], [1,-g], p)

    for k in range(x_len):
        for j in range(thres_no):
            if q[k] >= c[j]:
                a[j] = a[j] + 1
                hang[j] = 0
            elif hang[j] < I:
                a[j] = a[j] + 1
                hang[j] = hang[j] + 1
            else:
                break

    asl = 0
    asl_rms = 0
    if a[0] == 0:
        print('! ! ! ERROR ! ! !')
    else:
        AdB1 = 10*np.log10(sq/a[0]+eps)
    
    CdB1 = 20*np.log10(c[0]+eps)
    if AdB1-CdB1 < M:
        print('! ! ! ERROR ! ! !')

    AdB = [0 for i in range(thres_no)]
    CdB = [0 for i in range(thres_no)]
    Delta = [0 for i in range(thres_no)]
    AdB[0] = AdB1
    CdB[0] = CdB1
    Delta[0] = AdB1 - CdB1

    for j in range(1, thres_no):
        AdB[j] = 10*np.log10(sq/(a[j]+eps)+eps)
        CdB[j] = 20*np.log10(c[j]+eps)

    for j in range(1, thres_no):
        if a[j] != 0:
            Delta[j] = AdB[j] - CdB[j]
            if Delta[j] <= M:   # M = 15.9
                # interpolate to find the asl
                asl_ms_log, cl0 = bin_interp(AdB[j], AdB[j-1], CdB[j], CdB[j-1], M, 0.5)
                asl_ms = pow(10, asl_ms_log/10)
                asl = (sq/x_len)/asl_ms
                c0 = pow(10, cl0/20)
                break

    return asl_ms, asl, c0

# main_function  - addnoise
def addnoise(clean_data, clean_rever_data, noise_data, snr, fs):
    '''
    This function is used to add noise to clean speech and reverberation speech.
    It uses the active speech level to compute the speech energy. 
    The active speech level is computed as per ITU-T P.56 standard [1].
    
    Usage:  addnoise(clean_data, clean_rever_data, noise_data, snr, fs)
               
        clean_data  				- clean speech data in each channel [nchannel x points]
        clean_rever_data 			- reverberation data in each channel [nchannel x points]
        noise_data  				- noise data, the length of noise has to be greater than speech length [1 x points]
        snr           				- desired snr in dB
        fs                          - sampling frequency
    
    Note that if the variable IRS below (line 38) is set to 1, then it applies the IRS filter to bandlimit the signal to 300 Hz - 3.2 kHz.
    The default IRS value is 0, ie, no IRS filtering is applied.
    
    Example call:
        out_clean_rever_noise, out_clean_noise, out_noise = addnoise_asl(clean_data, clean_rever_data, noise_data, snr, fs)
    
    References:
    [1] ITU-T (1993). Objective measurement of active speech level. ITU-T 
        Recommendation P. 56
    
    Author: Yi Hu and Philipos C. Loizou 
    
    Copyright (c) 2006 by Philipos C. Loizou

    Python implementation from MATLAB: Rui Cheng
    '''

    nbits = 16
    
    # wavread gives floating point column data
    # norm by 32768, and change data type to np.double
    clean = (clean_data/32768).astype(np.double)
    clean_rever = (clean_rever_data/32768).astype(np.double)
    noise = (noise_data/32768).astype(np.double)
    
    # create the output matrix
    out_noise = np.zeros((clean.shape[0],clean.shape[1]), dtype=np.double)
    out_clean_rever_noise = np.zeros((clean.shape[0],clean.shape[1]), dtype=np.double)
    out_clean_noise = np.zeros((clean.shape[0],clean.shape[1]), dtype=np.double)

    # add noise in each channel
    for i in range(clean.shape[0]):

        # asl_P56
        Px, asl, c0 = asl_P56(clean[i,:], fs, nbits)
        # Px is the active speech level ms energy
        # asl is the active factor
        # c0 is the active speech level threshold
        
        # get the length of speech and noise
        x = clean[i,:]
        x_len = len(x)
        noise_len = len(noise)
        
        # adjust the length of the noise
        rand_start_limit = noise_len - x_len
        # the start of the noise segment can vary between [0, rand_start_limit]
        rand_start = int(round(rand_start_limit * np.matlib.rand(1)[0,0] + 1))
        # random start of the noise segment
        rand_start = 10
        noise_segment = noise[rand_start:rand_start+x_len]

        # the randomly selected noise segment will be added to the clean and reverberation speech
        # clean speech x
        Pn = sum(pow(noise_segment,2))/x_len
        # we need to scale the noise segment samples to obtain the desired snr = 10*log10[Px/(sf^2 * Pn)]
        sf = np.sqrt(Px/Pn/(pow(10,(snr/10))))   # scale factor for noise segment data

        # out_noise
        out_noise[i,:] = noise_segment * sf
        # out_clean_rever_noise
        out_clean_rever_noise[i,:] = clean_rever[i,:] + out_noise[i,:]
        # out_clean_noise
        out_clean_noise[i,:] = clean[i,:] + out_noise[i,:]

    # anti-norm for wave write
    out_noise = (out_noise*32768).astype("int16")
    out_clean_rever_noise = (out_clean_rever_noise*32768).astype("int16")
    out_clean_noise = (out_clean_noise*32768).astype("int16")

    return out_clean_rever_noise, out_clean_noise, out_noise
