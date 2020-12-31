# -*- coding: utf-8 -*-
"""
Created on Sat Dec 26 16:31:17 2020

@author: ellio
"""

import time
import tkinter as tk
import multiprocessing




def process1(): #Creating an interface to start and stop another process
    root = tk.Tk()
    
    HEIGHT = 600
    WIDTH = 900
    
    canvas = tk.Canvas(root,height = HEIGHT, width = WIDTH)
    canvas.pack
    
    frame = tk.Frame(root,bg = 'grey')
    frame.place(relwidth = 1 , relheight = 1)

    script_launch_button = tk.Button(text = 'Launch script', command = script_launch)
    script_launch_button.pack()
    
    script_stop_button = tk.Button(text = 'Stop script', command = script_stop)
    script_stop_button.pack()
    
    root.mainloop()
    
    
    
def script_launch(): #Launch other process
    p2 = multiprocessing.Process(target = process2)
    p2.start()
    
    
def script_stop(): #Stop other process
    p2.terminate()
    
    
    

def process2():
    _ = True
    counter = 0
    while _:
        print(f"Going to sleep for 5 seconds. So far, I've slept for 5 seconds {counter} times")
        time.sleep(5)
        
        counter = counter + 1
        
            
p1 = multiprocessing.Process(target = process1)
p2 = multiprocessing.Process(target = process2)

    
    
if __name__ == '__main__':   
    
    
    p1.start()
    
   






















