# MASG
microphone array speech generator (MASG) in room acoustic.

## Abstract
It is used to simulate the speech data received by microphone array of various shapes in room acoustic environment, including clean speech (clean), reverberation speech (clean rever), noisy speech (clean noise), noisy and reverberation speech (clean rever niose) and corresponding noise signal (noise).

## Method

The MASG is implemented based on two tools, namely, Pyroomacoustic [1] and an improved version add_noise_for_multichannel with add noise [2]. The schematic diagram of MASG is shown in Fig. 1.

![image_method](https://github.com/vipchengrui/MASG/blob/master/img/method.png)
Fig. 1 The schematic diagram of MASG.

Based on Pyroomacoustic, the microphone array clean speech is obtained by setting the absorption to 1.0, and the microphone array reverberation speech is obtained by setting the absorption to less than 1.0. With the microphone array clean speech, combined with the noise signal and the expected signal-to-noise ratio (SNR), we can get the corresponding microphone array noise signal, and combine them with the microphone array clean speech and the microphone array reverberation speech to get the microphone array noisy speech and the microphone array noisy reverberation speech.

From this, we can get the simulation data of all microphone arrays used in indoor acoustic environment







