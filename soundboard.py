# -*- coding: utf-8 -*-
"""
Created on Thu Dec  7 18:15:39 2023

@author: Charly
"""

from functools import partial
import customtkinter as ct
import soundfile as sf
import sounddevice as sd
import threading
import keyboard as kb
import os
from configparser import ConfigParser
config=ConfigParser()

def _play(sound,device=5):
    global stop_event
    event =threading.Event()

    def callback(outdata, frames, time, status):
        if stop_event.is_set():  # Check if stop event is triggered
            raise sd.CallbackStop
        data = wf.buffer_read(frames, dtype='float32')
        if len(outdata) > len(data):
            outdata[:len(data)] = data
            outdata[len(data):] = b'\x00' * (len(outdata) - len(data))
            raise sd.CallbackStop
        else:
            outdata[:] = data

    with sf.SoundFile(sound) as wf:
        stream = sd.RawOutputStream(samplerate=wf.samplerate,
                                    device=device,
                                    channels=2,
                                    callback=callback,
                                    blocksize=1024,
                                    finished_callback=event.set)
        with stream:
            event.wait()

def stop_all_sounds():
    global stop_event
    stop_event.set()  # Trigger stop event to stop all sounds


def read_sound(path : str):
    global stop_event
    stop_event.clear()
    for i in (sd.default.device[1],'VoiceMeeter Input (VB-Audio VoiceMeeter VAIO), Windows DirectSound'):
        new_thread = threading.Thread(target=_play, args=(path,i,))
        new_thread.start()

def load_sounds_from_folder(folder,i):
    son = []
    for filename in os.listdir(folder):
        if filename[-3:]=='wav' : son.append((filename[:-4],f'sounds/page_{i}/'+filename))
    return son

song=load_sounds_from_folder('sounds/page_1',1)
voices=load_sounds_from_folder('sounds/page_2',2)
sounds=load_sounds_from_folder('sounds/page_3',3)    

def sortie():
    root.quit()
    root.destroy()
    
def set_shortcuts():

    global list_shortcuts
    kb.unhook_all()
    for i in list_shortcuts:
        kb.add_hotkey(f'ctrl+{list_shortcuts.index(i)}', partial( read_sound,i))


list_shortcuts = list()  # result list

def checkbox_command():
    global list_shortcuts
    list_shortcuts = []
    for key in sound_dict.keys():
        if vars[ key ].get() == 1:
            list_shortcuts.append( sound_dict[ key ] )

sound_dict={}
for x in song:
    sound_dict[x[0]]=x[1]
for x in voices:
    sound_dict[x[0]]=x[1]
for x in sounds:
    sound_dict[x[0]]=x[1]

vars = {} # checkboxes dict for variables

ct.set_appearance_mode("dark")
ct.set_default_color_theme("dark-blue")

config.read('config.ini')

root=ct.CTk()
root.title('soundboard')

#_______________________________window geometry________________________________
root.geometry(config.get('window parameters', 'main_size'))
root.rowconfigure(0,weight=3)
root.rowconfigure(1,weight=1)
root.rowconfigure(2,weight=1)


song_scr  =ct.CTkScrollableFrame(root,width=config.getint('table 1 parameters','width'), height=config.getint('table 1 parameters','height'))
voices_scr=ct.CTkScrollableFrame(root,width=config.getint('table 2 parameters','width'), height=config.getint('table 2 parameters','height'))
sounds_scr=ct.CTkScrollableFrame(root,width=config.getint('table 3 parameters','width'), height=config.getint('table 3 parameters','height'))

song_scr.grid(row=0,column=0,padx=8)
voices_scr.grid(row=0,column=1,padx=8)
sounds_scr.grid(row=0,column=2,padx=8)

c1=config.get('table 1 parameters','color');hc1=config.get('table 1 parameters','hover_color')
c2=config.get('table 2 parameters','color');hc2=config.get('table 2 parameters','hover_color')
c3=config.get('table 3 parameters','color');hc3=config.get('table 3 parameters','hover_color')

for x in range(len(song)):
    ct.CTkButton(song_scr, text="{}".format(song[x][0]),fg_color=c1,hover_color=hc1,text_color='black',command= partial(read_sound, song[x][1])).grid(row=x,column=0,pady=10,padx=5)
    vars[ song[x][0] ] = ct.IntVar( value = 0 )
    checkbutton =ct.CTkCheckBox( song_scr,text='', variable = vars[ song[x][0] ], 
        onvalue = 1, offvalue = 0, fg_color = 'white',
        command = checkbox_command )
    checkbutton.grid(row=x,column=1,pady=10)

for x in range(len(voices)):
    ct.CTkButton(voices_scr, text="{}".format(voices[x][0]),fg_color=c2,hover_color=hc2,text_color='black',command= partial(read_sound, voices[x][1])).grid(row=x,column=0,pady=10,padx=5)
    vars[ voices[x][0] ] = ct.IntVar( value = 0 )
    checkbutton =ct.CTkCheckBox( voices_scr,text='', variable = vars[ voices[x][0] ], 
        onvalue = 1, offvalue = 0, fg_color = 'white',
        command = checkbox_command )
    checkbutton.grid(row=x,column=1,pady=10)
    
for x in range(len(sounds)):
    ct.CTkButton(sounds_scr, text="{}".format(sounds[x][0]),fg_color=c3,hover_color=hc3,text_color='black',command= partial(read_sound, sounds[x][1])).grid(row=x,column=0,pady=10,padx=5)
    vars[ sounds[x][0] ] = ct.IntVar( value = 0 )
    checkbutton =ct.CTkCheckBox( sounds_scr,text='', variable = vars[ sounds[x][0] ], 
        onvalue = 1, offvalue = 0, fg_color = 'white',
        command = checkbox_command )
    checkbutton.grid(row=x,column=1,pady=10)

shrt_cut_button= ct.CTkButton(root, text='hot keys',command=set_shortcuts)
shrt_cut_button.grid(row=1,column=0,pady=5)
exit_button = ct.CTkButton(root, text="Exit", command=sortie)
exit_button.grid(row=1,column=1,pady=5)
exit_button = ct.CTkButton(root, text="Stop", command=stop_all_sounds)
exit_button.grid(row=1,column=2,pady=5)
root.mainloop()

