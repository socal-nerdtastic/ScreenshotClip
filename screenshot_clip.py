#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#   Documentation is like sex.
#   When it's good, it's very good.
#   When it's bad, it's better than nothing.
#   When it lies to you, it may be a while before you realize something's wrong.

import sys
import subprocess
import time
import os

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

from PIL import Image, ImageTk
from pyscreeze import screenshot

IMAGE_H = 300 # display image height
TEMP_FILE = "~/Desktop/temp_screenshot.png" # place to save temporary screenshot
TEMP_FILE = os.path.expanduser(TEMP_FILE)

class GUI(tk.Frame):
    def __init__(self, master=None, image=None, **kwargs):
        super().__init__(master, **kwargs)
        self.b_box = None

        self.gin_image = image
        width, height = image.size
        self.scale = height / IMAGE_H
        image_w = int(width / self.scale)
        img = image.resize((image_w, IMAGE_H))
        self.pi = ImageTk.PhotoImage(img)

        self.c = BoxDrawCanvas(self, bg='white', height=IMAGE_H+30, width=image_w+30, command=self.on_call)
        self.c.create_image(0, 0, image=self.pi, anchor='nw')
        self.c.grid()

        btn = ttk.Button(self, text="Copy & Quit", command=self.cut)
        btn.grid(column=1, row=0)

    def on_call(self, *b_box):
        self.b_box = b_box

    def cut(self):
        if self.b_box:
            new_box = [x*self.scale for x in self.b_box]
            new_img = self.gin_image.crop(new_box)
            new_img.save(TEMP_FILE, format='PNG')
            subprocess.run('xclip -selection clipboard -target image/png -i'.split() + [TEMP_FILE])
        self.quit()

class BoxDrawCanvas(tk.Canvas):
    """A canvas that will let you draw a box on it by clicking and dragging the mouse."""
    def __init__(self, master=None, **kwargs):
        self.command = kwargs.pop('command')
        super().__init__(master, **kwargs)
        self.bind("<Button>", self.on_click)
        self.bind("<ButtonRelease>", self.on_release)
        self.bind("<Motion>", self.on_motion)
        self.start = None
        self.current = None
        self.refs = [] # list of screen objects

    def on_click(self, event):
        self.clear()
        self.start = event.x, event.y
        self.current = self.create_rectangle(*self.start, *self.start, outline='red', width=2)
        self.refs.append(self.current)

    def on_motion(self, event):
        if self.current:
            self.coords(self.current, *self.start, event.x, event.y)

    def on_release(self, event):
        self.on_motion(event)
        self.current = None
        if self.command:
            self.command(*self.start, event.x, event.y)

    def clear(self):
        while self.refs:
            self.delete(self.refs.pop())

def from_screen():
    from_img(screenshot())

def from_img(img):
    if isinstance(img, str):
        img = Image.open(img)
    root = tk.Tk()
    window = GUI(root, img)
    window.pack()
    root.geometry(f"600x{IMAGE_H+20}+300+300")
    root.mainloop()
    root.destroy()

def main():
    if len(sys.argv) > 1:
        from_img(sys.argv[1])
    else:
        from_screen()
    time.sleep(600) # sleep for 5 minutes to keep the clipboard active
    os.remove(TEMP_FILE)

if __name__ == '__main__':

    main()
