#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 20 22:51:00 2023

@author: alossius
"""

#%% IMPORT LIBRARIES AND PARSE INPUT

from neurol.BCI import automl_BCI
from neurol.plot import plot, plot_fft, plot_spectrogram
from neurol import BCI_tools
from neurol import streams

from sklearn import svm

import argparse

from neurol.connect_device import get_lsl_EEG_inlets, connect_muse
import neurol.streams

def parse_input():
    """Parse user arguments.

    Returns
    -------
    args : argparse.Namespace
        Object that contains arguments.
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--skip_connect', action='store_true', help='Skip re-connecting muse')
    parser.add_argument('--skip_buildModel', action='store_true', help='Skip re-building a model')
    args=parser.parse_args()

    return args

args = parse_input()

#%% CONFIGURE BASIC PARAMS

epoch_len = 50
recording_length = 3
n_states = 5

model = svm.SVC()

my_tfrm = lambda buffer : BCI_tools.band_power_transformer(buffer, None, ['AF7', 'AF8'], 'muse', bands=['beta'], epoch_len=50)

#%%

import curses
import time

def display_arrow(stdscr, key):
    # define arrow characters
    up_arrow = u"\u2191"
    down_arrow = u"\u2193"
    right_arrow = u"\u2192"
    left_arrow = u"\u2190"
    star = "*"

    # clear the screen before displaying the arrow
    stdscr.clear()

    # check the input and display the appropriate arrow
    if key == 0:
        stdscr.addstr(0, 0, up_arrow)
    elif key == 1:
        stdscr.addstr(0, 0, down_arrow)
    elif key == 2:
        stdscr.addstr(0, 0, right_arrow)
    elif key == 3:
        stdscr.addstr(0, 0, left_arrow)
    elif key == 4:
        stdscr.addstr(0, 0, star)

    # refresh the screen to display the arrow
    stdscr.refresh()


def action(key):

    # initialize curses
    stdscr = curses.initscr()
    curses.cbreak()
    curses.noecho()
    
    display_arrow(stdscr, key)
    
    # try:
    #     # loop to continuously update arrow based on input integer
    #     while True:    
    #         # check that input is valid
    #         if key < 0 or key > 4:
    #             print("Invalid input, please enter an integer between 0 and 4.")
    #             continue
    
    #         # display the arrow for the current input integer
    #         display_arrow(stdscr, key)
                
    # finally:
    #     # restore terminal settings and end curses session
    #     curses.nocbreak()
    #     curses.echo()
    #     curses.endwin()



#%%

bci = automl_BCI(model, epoch_len, n_states, transformer=my_tfrm, action=action)

#%%

if args.skip_connect != True:
    connect_muse()

inlet = get_lsl_EEG_inlets()[0] 
stream = streams.lsl_stream(inlet, buffer_length=1024)

#%% Plot stream

# try: 
#     plot(stream)                    # voltage against time
#     #plot_spectrogram(stream)        # frequency spectrogram
#     #plot_fft(stream)                # fft 
# except KeyboardInterrupt:
#     stream.close()

#%%

if args.skip_buildModel != True:
    bci.build_model(stream, recording_length)

#%%

try:
    bci.run(stream)
except KeyboardInterrupt:
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    print('\n')
    print('QUIT BCI')