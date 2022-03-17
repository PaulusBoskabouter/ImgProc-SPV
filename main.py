"""
# Author       : Paul Verhoeven
# Version      : 1.0
# Date         : 17-03-2022
In this script 3 different objects are written used by both main.py and prompt.py
"""

import cv2
import objects
import imgproc
import json
import os
import prompt
import pygame
import pyautogui
import random
import time


def load_test_subjects(file_loc: str = ".\\results\\ExperimentOneSubjectData.json"):
    """
    Loads the patient dictionary from .\\results\\ExperimentOneSubjectData.json.
    :param file_loc: Location of ExperimentOneSubjectData.json file
    :return: Returns dictionary, example: {0: first name-last name-age}
    """
    dictionary = {}
    try:
        with open(file_loc, 'r') as file:
            dictionary = json.load(file)
            file.close()
    except json.decoder.JSONDecodeError:
        pass
    except FileNotFoundError:
        print("Error: check the existence of \'result\' directory and \'ExperimentOneSubjectData.json\'")
        quit()

    list_of_subject_objects = {}
    uncompleted_test_subjects = {}
    for data in dictionary.items():
        subject_index = data[0]
        info = data[1]

        list_of_subject_objects[subject_index] = objects.Subject(
            index=subject_index,
            fname=info['first_name'],
            lname=info['last_name'],
            age=info['age'],
            order=info['order'],
            answers=info['answers'],
            actions=info['actions']
        )

        # If the number of answers are unqual to the amount of videos, subject is unfinished
        if len(info['answers']) != len(filenames.get(MODE)):
            uncompleted_test_subjects[subject_index] = list_of_subject_objects[subject_index]
    return list_of_subject_objects, uncompleted_test_subjects


def save_subject_data(file_loc: str = ".\\results\\ExperimentOneSubjectData.json"):
    """
    Saves the subject dictionary to .\\results\\ExperimentOneSubjectData.json.
    :param file_loc: Location of ExperimentOneSubjectData.json file
    :return: Returns dictionary, example: {0: first name-last name-age}
    """
    dictionary = {}
    with open(file_loc, 'w') as file:
        for subject_index, subject_objects in stored_data.items():
            dictionary[subject_index] = subject_objects.get_object_as_dict()
        json.dump(dictionary, file)
        file.close()
    return


def preload_video(video_nr, mode):
    """
    Loads a video and splits it into frames_in_list.
    :param video_nr: Number of video in list
    :param mode: Image pre-processing mode (depth, segmentation, edge-detection)
    :return: A list of video split into frames_in_list in chronological order.
    """
    frames_in_list = []
    cap = cv2.VideoCapture(filenames[mode][video_nr])
    _, video_frame = cap.read()
    while video_frame is not None:
        frames_in_list.append(video_frame)
        _, video_frame = cap.read()
    cap.release()
    return frames_in_list


def render(frames_in_list):
    """
    This function is the mainloop of the program
    :param frames_in_list: List with video frames
    """

    # Initiate pygame stuff
    pygame.init()
    fps_clock = pygame.time.Clock()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.event.set_grab(True)  # Locks cursor within boundaries of window
    pygame.mouse.set_visible(False)  # Make cursor invisible

    # Randomize mouse start location;
    prev_x = random.randint(0, width)
    # for y (which controls sigma) range starts from 1px because sigma cannot be 0.
    prev_y = random.randint(1, heigth)
    pygame.mouse.set_pos(prev_x, prev_y)

    # formula for determining threshold and sigma.
    # Note that sigma is reversed so that the top of the screen equals to the max. sigma.
    threshold = threshold_per_pixel * prev_x
    sigma = 3 - sigma_per_pixel * prev_y

    # This start timer is used for tracking the total time spent in the video as well as time spent at specific coords.
    timer = time.time()

    # Hardcodingly put the starting
    tracked_mouse_data = {
        0: {'time': time.time() - timer, 'threshold': threshold, 'sigma': sigma, 'fps': fps_clock.get_fps()}
    }
    frame_counter = 1
    temp = []
    while True:  # Infinitely loop over video
        for frame in frames_in_list:

            # Once per frame, check mouse location.
            # records if it has changed and updates threshold and sigma accordingly
            x, y = pygame.mouse.get_pos()
            if (x, y) != (prev_x, prev_y):
                tracked_mouse_data[frame_counter] = {'time': time.time() - timer, 'threshold': threshold,
                                                     'sigma': sigma, 'fps': fps_clock.get_fps()}
                threshold = threshold_per_pixel * x
                sigma = 3 - sigma_per_pixel * y
                prev_x = x
                prev_y = y

            # Once per frame, check if spacebar has been hit.
            pygame.event.pump()  # Allow pygame to handle internal actions.
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:  # Press 'spacebar' to exit the program
                pygame.quit()
                prompt.E1(filenames[MODE][vid_nr], vid_nr + append_vid_nr + 1, subject)

                # Last recording is added to trace the last mouse position before ending video.
                # If recording was already made due to mouse movement it gets overwritten.
                tracked_mouse_data[frame_counter] = {'time': time.time() - timer, 'threshold': threshold,
                                                     'sigma': sigma, 'fps': fps_clock.get_fps()}

                # update subject object
                subject.update_actions(filenames[MODE][vid_nr], tracked_mouse_data)
                return temp

            # for event in pygame.event.get():  # look at all events
            #     # Track mouse motion; Change sigma & threshold values with coords.
            #
            #     if event.type == pygame.KEYDOWN:
            #         if event.key == pygame.K_SPACE:
            #             pygame.quit()
            #             prompt.E1(filenames[MODE][vid_nr], vid_nr + append_vid_nr + 1, subject)
            #
            #             # in the pygame.event.get() list keydown event make come before mousevent.
            #             # so one last recording is added to trace the last mouse position before ending video.
            #             tracked_mouse_data[frame_counter] = {'time': time.time() - timer, 'threshold': threshold,
            #                                                  'sigma': sigma, 'fps': fps_clock.get_fps()}
            #
            #             # update subject object
            #             subject.update_actions(filenames[MODE][vid_nr], tracked_mouse_data)
            #             return temp
            #
            #         # TODO: Temp, weghalen
            #         elif event.key == pygame.K_ESCAPE:
            #             quit()

            if MODE == 'edge-detection':
                frame = imgproc.cannyfilter(frame, sigma=sigma, high_threshold=threshold)
                frame = cv2.dilate(frame, dilation_kernel, iterations=1)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # phosphene simulation
            frame = cv2.resize(frame, phosphene_imsize)
            phosphenes = simulator(frame)
            frame = pygame.surfarray.make_surface(phosphenes)
            frame = pygame.transform.rotate(frame, -90)  # Rotation correction as np array of image is rotated 90.
            screen.blit(frame, frame.get_rect(center=(width // 2, heigth // 2)))  # Add frame to center of pygame Frame.
            pygame.display.update()
            frame_counter += 1
            fps_clock.tick(fps)  # Limits fps to fps names_variable


DATA_DIR = '.\\Dataset'

# Generate Dictionary with the filenames
filenames = dict()
subfolders = ['Original Videos', 'Depth_simplification', 'Segmentation_simplification']  # subfolders of interest
mode_name = ['edge-detection', 'depth', 'segmentation']

for i in range(len(subfolders)):
    path = os.path.join(DATA_DIR, subfolders[i])
    filenames[mode_name[i]] = [os.path.join(path, filename) for filename in sorted(os.listdir(path)) if
                               'stim' in filename]

# Specify size of stimulus
phosphene_imsize = (960, 960)  # TODO: determine appropriate sizing

mode_cases = ['depth', 'segmentation', 'edge-detection']
MODE = 'edge-detection'  # choose from ['depth','segmentation','edge-detection']

fps = 25

# Dilation (to make edge detection thicker)
DILATION_STRENGTH = 5
dilation_kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (DILATION_STRENGTH, DILATION_STRENGTH))
simulator = imgproc.PhospheneSimulator(intensity=10, phosphene_resolution=(50, 50), size=phosphene_imsize)
# length = len(videos[MODE])

# Data dicts using a data object

start_new_check = objects.BooleanCheck(True)

stored_data, uncompleted_subjects = load_test_subjects()

# print(collected_data.get_test_subjects())

# Shuffle the list of videos randomly

filenames.get(MODE)
index = len(stored_data)

# Check for resuming an incomplete save or start a new user.
prompt.StartGUI(start_new_check, len(uncompleted_subjects) != 0)
if start_new_check.get_value():
    subject = stored_data[index] = objects.Subject(index=len(stored_data), fname='', lname='', age='',
                                                   order=filenames.get(MODE),
                                                   answers={}, actions={})
    prompt.NewUserGUI(subject)
    range_of_vids = len(filenames[MODE])
    random.shuffle(filenames.get(MODE))

else:
    selected_user_index = objects.ContinuationIndex()
    prompt.ResumeGUI(uncompleted_subjects, selected_user_index)
    subject = stored_data.get(selected_user_index.get_index())
    filenames[MODE] = subject.get_vidorder()[len(subject.get_answers()):]

# Pipeline starts, user is presented with an infinite loop of each video until the 'spacebar' is hit.

# Rules of determining threshold and sigma
width, heigth = pyautogui.size()
max_sigma = 3
sigma_per_pixel = max_sigma / heigth
max_threshold = 300
threshold_per_pixel = max_threshold / width
append_vid_nr = len(subject.get_answers())
for vid_nr in range(len(filenames[MODE])):
    frames = preload_video(vid_nr, MODE)  # list of preloaded frames_in_list of  current video.
    tracked_data = render(frames)
    totaal = 0
    fps_ding = 0
    for i in tracked_data:
        if i != 0:
            totaal += 1
            fps_ding += i
    print(
        f"FPS voor:\t{filenames[MODE][vid_nr]}\nMeting over:\t{totaal / fps} sec\nGemiddelde fps:\t{fps_ding / totaal}\n")

    save_subject_data()

pygame.quit()
