# Author: Brandon Le
# Purpose: Simple desktop app to create a gesture gallery from a folder of images
# Modified from https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Img_Viewer.py
# Modified from https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Desktop_Widget_Timer.py

import PySimpleGUI as sg
import os
from PIL import Image, ImageTk
import io
import random
import time


def time_as_int():
    return int(round(time.time() * 100))


def get_img_data(f, maxsize=(1200, 850), first=False):
    """Generate image data using PIL
    """

    # TODO save thumbnails in temporary directory and delete this directory when program exits
    #   to avoid redoing image processing work

    img = Image.open(f)
    img_size = img.size
    img_width, img_height = img_size
    # if the original width is larger than the max width
    if img_width > maxsize[0]:
        scale_factor_width = maxsize[0] / img_width

        # if the original height is larger than the max height after scaling by the width,
        #   scale the image to this scale factor instead
        if (img_height * scale_factor_width) > maxsize[1]:
            scale_factor_height = maxsize[1] / img_height
            img.thumbnail((img_width * scale_factor_height, img_height * scale_factor_height))
        # else if the original height is less than the max height after scaling,
        #   scale by just the width
        else:
            img.thumbnail((img_width * scale_factor_width, img_height * scale_factor_width))
    # else if the original width is smaller
    else:
        # if the original height is larger, scale by just the height
        if img_height > maxsize[1]:
            scale_factor_height = maxsize[1] / img_height
            img.thumbnail((img_width * scale_factor_height, img_height * scale_factor_height))
        # else the original width and height are smaller so enlarge them by the smallest scale factor
        else:
            scale_factor_width = maxsize[0] / img_width
            scale_factor_height = maxsize[1] / img_height
            scale_factor = min(scale_factor_width, scale_factor_height)
            img.thumbnail((img_width * scale_factor, img_height* scale_factor))

    # img.thumbnail(maxsize)
    if first:                     # tkinter is inactive the first time
        bio = io.BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()
    return ImageTk.PhotoImage(img)


if __name__ == "__main__":
    current_time, paused_time, paused = 0, 0, False
    start_time = time_as_int()

    # Get the folder containing the images from the user
    folder = sg.popup_get_folder('Image folder to open', default_path='')
    if not folder:
        sg.popup_cancel('Cancelling')
        raise SystemExit()

    # PIL supported image types
    img_types = (".png", ".jpg", ".jpeg", ".tiff", ".bmp")

    # get list of files in folder
    flist0 = os.listdir(folder)

    # create sub list of image files (no sub folders, no wrong file types)
    fnames = [f for f in flist0 if os.path.isfile(
        os.path.join(folder, f)) and f.lower().endswith(img_types)]

    # Randomly shuffle the order of files
    random.shuffle(fnames)

    num_files = len(fnames)  # number of images found
    if num_files == 0:
        sg.popup('No files in folder')
        raise SystemExit()

    del flist0  # no longer needed

    # make these 2 elements outside the layout as we want to "update" them later
    # initialize to the first file in the list
    filename = os.path.join(folder, fnames[0])  # name of first file in list
    image_elem = sg.Image(data=get_img_data(filename, first=True))
    filename_display_elem = sg.Text(filename, size=(80, 3))
    file_num_display_elem = sg.Text('File 1 of {}'.format(num_files), size=(15, 1))

    # define layout, show and read the form
    # col = [[filename_display_elem],
    #        [image_elem]]
    col = [[image_elem]]

    col_files = [[filename_display_elem],
                [sg.Listbox(values=fnames, change_submits=True, size=(60, 30), key='listbox')],
                 [sg.Button('Prev', size=(8, 2)), sg.Button('Next', size=(8, 2)), file_num_display_elem],
                 [sg.Text('')],
                 [sg.Text('', size=(8, 2), font=('Helvetica', 20),
                          justification='center', key='text')],
                 [sg.Button('Pause', key='-RUN-PAUSE-', button_color=('white', '#001480')),
                  sg.Button('Reset', button_color=('white', '#007339'), key='-RESET-'),
                  sg.Exit(button_color=('white', 'firebrick4'), key='Exit')]
                 ]

    layout = [[sg.Column(vertical_alignment='top', layout=col_files), sg.Column(vertical_alignment='top', layout=col)]]

    window = sg.Window('Image Browser', layout, return_keyboard_events=True,
                       location=(0, 0), size=(1920, 1080), resizable=True, use_default_focus=False)

    # loop reading the user input and displaying image, filename
    NEXTIMGTIMEOUT = 1000
    i = 0
    while True:
        print(sg.Window.get_screen_size())
        # print(paused)
        if not paused:
            event, values = window.read(timeout=10)
            current_time = time_as_int() - start_time
        else:
            event, values = window.read()
        # print(f"Event: {event}, Values: {values}")
        # perform button and keyboard operations

        if event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif event == '-RESET-':
            paused_time = start_time = time_as_int()
            current_time = 0
        elif event == '-RUN-PAUSE-':
            paused = not paused
            if paused:
                paused_time = time_as_int()
            else:
                start_time = start_time + time_as_int() - paused_time
            # Change button's text
            window['-RUN-PAUSE-'].update('Run' if paused else 'Pause')
        elif event in ('Next', 'Down:40', 'Next:34'):
            i += 1
            if i >= num_files:
                i -= num_files
            filename = os.path.join(folder, fnames[i])
            current_time = 0
        elif event in ('Prev', 'Up:38', 'Prior:33'):
            i -= 1
            if i < 0:
                i = num_files + i
            filename = os.path.join(folder, fnames[i])
            current_time = 0
        elif event == 'listbox':            # something from the listbox
            f = values["listbox"][0]            # selected filename
            filename = os.path.join(folder, f)  # read this file
            i = fnames.index(f)                 # update running index
        else:
            filename = os.path.join(folder, fnames[i])

        # print(f"current time = {current_time}")
        if current_time > NEXTIMGTIMEOUT:
            print("\n\n\nRESET\n\n\n")
            paused_time = start_time = time_as_int()
            current_time = 0
            i += 1
            if i >= num_files:
                i %= num_files
            filename = os.path.join(folder, fnames[i])

        # --------- Display timer in window --------
        # window['text'].update('{:02d}:{:02d}.{:02d}'.format((current_time // 100) // 60,
        #                                                     (current_time // 100) % 60,
        #                                                     current_time % 100))
        window['text'].update('{:02d}:{:02d}'.format((current_time // 100) // 60,
                                                     (current_time // 100) % 60))

        # update window with new image
        image_elem.update(data=get_img_data(filename, first=True))
        # update window with filename
        filename_display_elem.update(filename)
        # update page display
        file_num_display_elem.update('File {} of {}'.format(i+1, num_files))
        window.Refresh()

    window.close()
