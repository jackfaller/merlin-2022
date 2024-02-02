'''
Script to demonstrate Neurol in action using a Muse 1 or Muse 2 headset. 

REQUIRES A BLUETOOTH DONGLE - TESTED ON MAC IOS

====================================
RUN FROM THE 'merlin-2022' DIRECTORY                 ...please read...
-----------------------------------------------------------------------------------
Cell 1: Library imports - run once.
Cell 2: Connect to muse headset - run until muse is connected, then never again.
Cell 3: Create the BCI - run once. 
Cell 4: Plot either voltage vs time, a spectrogram, or an FFT of live EEG data.
Cell 5: Print to console the classifiers descion between concentrating and relaxed.
===================================================================================

@author: Merlin Neurotech at Queen's University
'''

#%% CELL 1 - LIBRARY IMPORTS

from neurol import BCI
from neurol.plot import plot, plot_fft, plot_spectrogram
from neurol.connect_device import connect_muse
from neurol import BCI_tools
from neurol.models import classification_tools
from neurol.connect_device import get_lsl_EEG_inlets
from neurol import streams

#%% CELL 2 - CONNECT MUSE

connect_muse()

#%% CELL 3 - CREATE BCI

# DEFINE CALIBRATOR

my_clb = lambda stream : BCI_tools.band_power_calibrator(stream, ['AF7', 'AF8'], 'muse', bands=['alpha_low', 'alpha_high'], 
                                        percentile=65, recording_length=10, epoch_len=1, inter_window_interval=0.25)
    # we defined a calibrator which returns the 65th percentile of alpha wave ,
    # power over the 'AF7' and 'AF8' channels of a muse headset after recording for 10 seconds,
    # and using epochs of 1 second seperated by 0.25 seconds.

# DEFINE TRANSFORMER

my_tfrm = lambda buffer, clb_info: BCI_tools.band_power_transformer(buffer, clb_info, ['AF7', 'AF8'], 'muse',
                                                    bands=['alpha_low', 'alpha_high'], epoch_len=1)
    # we defined a transformer that corresponds to the choices we made with the calibrator.

# DEFINE CLASSIFIER

def my_clf(clf_input, clb_info):
    
    # use threshold_clf to get a binary classification
    binary_label = classification_tools.threshold_clf(clf_input, clb_info, clf_consolidator='all')
    
    # decode the binary_label into something more inteligible for printing
    label = classification_tools.decode_prediction(binary_label, {True: 'Relaxed', False: 'Concentrated'})
    
    return label

    # Again, we define a classifier that matches the choices we made
    # we use a function definition instead of a lambda expression since we want to do slightly more with z

# DEFINE BCI

my_bci = BCI.generic_BCI(my_clf, transformer=my_tfrm, action=print, calibrator=my_clb)
inlet = get_lsl_EEG_inlets()[0] # gets first inlet, assuming only one EEG streaming device is connected
stream = streams.lsl_stream(inlet, buffer_length=1024) # we ask the stream object to manage a buffer of 1024 samples from the inlet
my_bci.calibrate(stream)
print(my_bci.calibration_info)

#%% CELL 4 - PLOT THE STREAM

user_input = int(input("\nWhat would you like to plot?.\n0 = Voltage vs. Time\n1 = Spectrogram\n2 = FFT\n"))

try: 
    if user_input == 0: plot(stream)   
    if user_input == 1: plot_spectrogram(stream)        
    if user_input == 2: plot_fft(stream)                
except KeyboardInterrupt:
    stream.close()
    print('\n')
    print('QUIT BCI')

#%% CELL 5 - DISPLAY CONCENTRAION VS RELAXED PREDICTIONS

try:
    my_bci.run(stream)
except KeyboardInterrupt:
    stream.close()
    print('\n')
    print('QUIT BCI')
