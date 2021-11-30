#JarvisMusic.py
"""
This module contains code for the Jarvis Music Player Application
"""

import os
import pygame
import random
from tkinter import *
from tkinter.filedialog import askdirectory
from ttkthemes import ThemedStyle
import tkinter.ttk as ttk


# Creates a list of all the mp3 files
def select_directory():
    print("Select the folder which contains songs")
    directory = askdirectory()              # asks user to select the folder which contains songs
    os.chdir(directory)                     # Changes current working directory

    for files in os.listdir(directory):
        if files.endswith(".mp3"):
            list_of_songs.append(files)

    pygame.mixer.init()                        # Initialising mixer
    pygame.mixer.music.load(list_of_songs[0])  # Loading music onto the player
    pygame.mixer.music.play()                  # Playing music


def next_song(event):
    try:
        global index
        index += 1
        pygame.mixer.music.load(list_of_songs[index])
        pygame.mixer.music.play()
        song_label.config(text=list_of_songs[index])
    except Exception:
        index -= 1
        print("You have reached the end of your songs list "
              "click on previous to go back")


def prev_song(event):
    try:
        global index
        index -= 1
        pygame.mixer.music.load(list_of_songs[index])
        pygame.mixer.music.play()
        song_label.config(text=list_of_songs[index])
    except IndexError:
        index += 1
        print("You have reached the start click on next")


def pause_song(is_paused):
    global paused
    paused = is_paused
    if paused:
        pygame.mixer.music.unpause()
        paused = False
    else:
        pygame.mixer.music.pause()
        paused = True


def shuffle_music(event):
    global list_of_songs
    global index
    listbox.delete(0, END)
    random.shuffle(list_of_songs)
    song_label.config(text=list_of_songs[0])
    pygame.mixer.music.unload()
    pygame.mixer.music.load(list_of_songs[0])
    for items in list_of_songs:
        listbox.insert(END, items)
    pygame.mixer.music.play()
    index = 0


def EXIT_PLAYER():
    pygame.mixer.music.stop()
    root.destroy()
    pass


def main():
    global list_of_songs
    global index
    global paused
    global root

    root = Tk()                                                 # Root window is created
    root.minsize(700, 400)
    style = ThemedStyle(root)
    style.set_theme("clearlooks")
    root.configure()

    list_of_songs = []
    index = 0

    select_directory()           # Calls the fucntion for selecting directory
    paused = False
    global label1
    label1 = Label(root, text="Music Player", font="italic")      # Creating labels and listbox
    label1.pack()
    global song_label
    song_label = Label(root, text="Music Player", font="calibri")
    song_label.pack()
    global listbox
    listbox = Listbox(root)
    listbox = Listbox(fg="black", font="bold")
    listbox.pack()

    for items in list_of_songs:
        listbox.insert(END, items)

    next_button = Button(root, text="Next", fg="black", font="bold")     # Creating buttons
    next_button.pack()

    previous_button = Button(root, text="Previous", fg="black", font="bold")
    previous_button.pack()

    pause_button = Button(root, text="Pause/Unpause", fg="black", font="bold", command=lambda: pause_song(paused))
    pause_button.pack()

    shuffle_button = Button(root, text="Shuffle", fg="black", font="bold")
    shuffle_button.pack()

    Exit_button = Button(root, text="Quit", fg="black", font="bold", command=EXIT_PLAYER)
    Exit_button.pack()

    next_button.bind("<Button-1>", next_song)        # Binding buttons to their functions
    previous_button.bind("<Button-1>", prev_song)
    shuffle_button.bind("<Button-1>", shuffle_music)

    root.mainloop()
