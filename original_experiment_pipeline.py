"""
# Author       : Paul Verhoeven
# Date         : 25-03-2022
This is the main pipeline of this test. This was unmodified and cannot be run as the DVS videos and SPV are missing.
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


def load_json(base: str, filename: str, data_type_is_subject: bool = False):
    """
    Loads JSON files.
    :param data_type_is_subject: if json contains subject data, do some extra steps.
    :param filename: Json filename to load in.
    :param base: base path to said filename.
    :return: Returns dictionary, example: {0: first name-last name-subject_id}
    """
    try:
        with open(base + filename, 'r') as file:
            dictionary = json.load(file)
            file.close()

        if data_type_is_subject:
            saved_subject = objects.Subject(
                subject_id=dictionary['subject_id'],
                order=dictionary['order'],
                answers=dictionary['answers'],
                actions=dictionary['actions']
            )

            return saved_subject
        else:
            return dictionary
    except json.decoder.JSONDecodeError:
        pass
    except FileNotFoundError:
        print(f"WARNING: no such file: \'{base}\' + \'{filename}\'")
        return None


def save_subject_data(base: str, filename: str):
    """
    Saves the active_subject dictionary to .\\results\\ExperimentOneSubjectData.json.
    :param filename: Json filename to load in.
    :param base: base path to said filename.
    :return: Returns dictionary, example: {0: first name-last name-subject_id}
    """
    with open(base + filename, 'w') as file:
        json.dump(subject.get_object_as_dict(), file)
        file.close()
    return


def preload_video(video):
    """
    Loads a video and splits it into frames_in_list.
    :param video: Path to a video file
    :return: A list of video split into frames_in_list in chronological order.
    """
    frames_in_list = []
    cap = cv2.VideoCapture(video)
    _, video_frame = cap.read()
    while video_frame is not None:
        frames_in_list.append(video_frame)
        _, video_frame = cap.read()
    cap.release()
    return frames_in_list


def videos_path():
    """
    Put videos in list and links it to mode names; {MODE}: [path/to/vid1.mp4, path/to/vid2.mp4]}
    :return: Two dictionaries, filenames_dict has videos used for the test, test_sample_videos_dict has test videos.
    """
    filenames_dict = dict()
    test_sample_videos_dict = dict()
    for i in range(len(SUBFOLDERS)):
        path = os.path.join(DATA_DIR, SUBFOLDERS[i])
        filenames_dict[MODE_NAME[i]] = [os.path.join(path, filename) for filename in sorted(os.listdir(path)) if
                                        'stim' in filename]

        # Retrieve sample videos for the test run
        if MODE_NAME[i] == 'edge-detection' or MODE_NAME[i] == 'DVS':
            test_sample_videos_dict[MODE_NAME[i]] = [os.path.join(path, filename) for filename in
                                                     sorted(os.listdir(path)) if
                                                     'sample' in filename]
    return filenames_dict, test_sample_videos_dict


def start_video_transition(screen):
    """
    :param screen: A Pygame.screen to draw this trantition to
    """
    # Set screen to entirely black.
    pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
    pygame.display.flip()
    text_font = pygame.font.Font('freesansbold.ttf', 32)
    countdown_font = pygame.font.Font('freesansbold.ttf', 64)
    for i in range(3):
        pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
        pygame.display.flip()
        string_text = text_font.render('Video starts in:', True, 'WHITE')
        screen.blit(string_text, string_text.get_rect(center=(width // 2, heigth // 2 - heigth * 0.1)))
        string_countdown = countdown_font.render(f'{3 - i}', True, 'WHITE')
        screen.blit(string_countdown, string_countdown.get_rect(center=(width // 2, heigth // 2)))
        pygame.display.flip()
        time.sleep(1)
    pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
    pygame.display.flip()
    return


def loop_transition(screen, start_fg, start_bg, loops: int, transition_time: int = 1,
                    transition_fps: int = 60, reverse: bool = False):
    """
    :param screen: A Pygame.screen to draw this trantition to
    :param start_fg: Starting color for the foreground
    :param start_bg: Starting color for the background
    :param loops: Amount of loops, which is used to cancer the animation if spacebar is hit
    :param transition_time: Time animation should take to complete
    :param transition_fps: The amount of frames per second the animation
    :param reverse: Boolean, to reverse this animation back to black.
    :return:
    """
    # Set screen to entirely black.
    pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
    pygame.display.flip()
    x = 0
    while x < width:
        start_frame = time.time()
        # Spacebar should still end video preemptively
        pygame.event.pump()
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            return LOOP_AMOUNT

        # check which colors to use
        if reverse:
            to_use_fg = start_bg
            to_use_bg = start_fg
        else:
            to_use_fg = start_fg
            to_use_bg = start_bg

        screen.fill(color=to_use_bg)
        pygame.draw.rect(screen, to_use_fg, rect=pygame.Rect(0, 0, x, heigth))
        font = pygame.font.Font('freesansbold.ttf', 64)
        text = font.render('Restarting video', True, 'BLACK')
        screen.blit(text, text.get_rect(center=(width // 2, heigth // 2)))
        x += (width / (transition_time / (1 / transition_fps)))  # Each frame should add X amount of colour.

        if x >= width and not reverse:  # Restart function with colors reversed.
            x = 0
            reverse = True
        pygame.display.flip()

        # custom fps timer. changing framerate with fps.clock, messes with the video framerate that comes after.
        if time.time() - start_frame < 1 / transition_fps:
            try:
                time.sleep(1 / transition_fps - (time.time() - start_frame))
            except ValueError:
                pass
    pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
    pygame.display.flip()
    time.sleep(0.5)
    return loops


def fixed_render(frames_in_list, subject: objects.Subject, dvs: bool = False):
    """
    This function handles the rendering of videos, tracking of user input and providing GUI's.
    :param subject: Subject object used to track user input.
    :param frames_in_list: List with video frames
    """

    # Initiate pygame stuff
    pygame.init()
    fps_clock = pygame.time.Clock()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.event.set_grab(True)  # Locks cursor within boundaries of window
    pygame.mouse.set_visible(False)  # Make cursor invisible
    start_video_transition(screen)  # Countdown timer to video start

    if dvs:
        # This video has more fps so only show every 4th frame, I have tested this and frames still align.
        iterative_steps = range(0, len(frames_in_list), 4)
        # These 3 params are not important if the video is DVS.
        threshold = None
        sigma = None
        error = None
    else:
        iterative_steps = range(0, len(frames_in_list))
        video_name = video_file.split('\\')[-1]
        try:
            assert fixed_canny_params.get(video_name) is not None
            threshold = fixed_canny_params.get(video_name)[0]
            sigma = fixed_canny_params.get(video_name)[1]
            error = False
        except AssertionError:
            print(f"WARNING: no data points available for {video_name}")
            threshold = 140
            sigma = 1.5
            error = True

    # This start timer is used for tracking the total time spent in the video.
    timer = time.time()
    tracked_data = dict()
    frame_counter = 0
    looped = 0

    tracked_data['pre-start'] = {'DVS': dvs, 'sigma': sigma, 'threshold': threshold, 'canny_params_error': error}

    while looped < LOOP_AMOUNT:  # Loop over video for 'LOOP_AMOUNT' times.
        for frame in iterative_steps:
            frame = frames_in_list[frame]

            # Once per frame, check if spacebar has been hit.
            pygame.event.pump()  # Allow pygame to handle internal actions.
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:  # Press 'spacebar' to exit the while loop and skip to submit GUI
                # Break out of this while loop by saying the video has looped the max. amount of times.
                # (I do it like this everywhere!)
                looped = LOOP_AMOUNT
                break

            if not dvs:
                frame = imgproc.cannyfilter(frame, sigma=sigma, high_threshold=threshold)
            else:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # phosphene simulation
            frame = cv2.resize(frame, phosphene_imsize)
            phosphenes = simulator(frame)
            frame = pygame.surfarray.make_surface(phosphenes)
            frame = pygame.transform.rotate(frame, -90)  # Rotation correction as np array of image is rotated 90.
            screen.blit(frame, frame.get_rect(center=(width // 2, heigth // 2)))  # Add frame to center of pygame Frame.

            pygame.display.flip()

            tracked_data[frame_counter] = {'time': time.time() - timer, 'framerate': fps_clock.get_fps(),
                                           'phosphenes': simulator.count_phosphenes(),
                                           }
            frame_counter += 1
            fps_clock.tick(FRAMERATE)  # Limits FRAMERATE to FRAMERATE index_variable

        looped += 1
        # Transition when video restarts
        if looped < LOOP_AMOUNT:
            # Do the transition.
            looped = loop_transition(screen, 'GRAY', 'BLACK', transition_time=1, loops=looped)
            # Once again I use the amount of loops to check if spacebar has been hit.
            if looped == LOOP_AMOUNT:  # Still check if spacebar has been hit.
                break

    pygame.quit()

    prompt.ExperimentForm(video_file, vid_nr + subject_progress + 1, subject)

    # update active_subject object
    subject.update_actions(video_file, tracked_data)


def adaptive_render(frames_in_list, subject: objects.Subject):
    """
    This function handles the rendering of videos, tracking of user input and providing GUI's.
    :param subject: Subject object used to track user input.
    :param frames_in_list: List with video frames
    """

    # Initiate pygame stuff
    pygame.init()
    fps_clock = pygame.time.Clock()
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.event.set_grab(True)  # Locks cursor within boundaries of window
    pygame.mouse.set_visible(False)  # Make cursor invisible
    start_video_transition(screen)  # Countdown timer to video start

    tracked_mouse_data = dict()
    frame_counter = 0
    looped = 0

    # This start timer is used for tracking the total time spent in the video as well as time spent at specific coords.
    timer = time.time()

    while looped < LOOP_AMOUNT:  # Loop over video for 'LOOP_AMOUNT' times.
        # Randomize mouse location at start of each loop;
        prev_x = random.randint(0, width)
        # for y (which controls sigma) range starts from 1px because sigma cannot be 0.
        prev_y = random.randint(1, heigth)
        pygame.mouse.set_pos(prev_x, prev_y)
        forced_move = True
        # formula for determining threshold and sigma.
        # Note that sigma is reversed so that the top of the screen equals to the max. sigma.
        threshold = threshold_per_pixel * prev_x
        sigma = 3 - sigma_per_pixel * prev_y

        for frame in frames_in_list:
            # Once per frame, check mouse location.
            # records if it has changed and updates threshold and sigma accordingly.
            x, y = pygame.mouse.get_pos()

            if not forced_move:
                tracked_mouse_data[frame_counter] = {'time': time.time() - timer, 'x': prev_x, 'y': prev_y,
                                                     'threshold': threshold, 'sigma': sigma,
                                                     'framerate': fps_clock.get_fps()}
                threshold = threshold_per_pixel * x
                sigma = 3 - sigma_per_pixel * y
                prev_x = x
                prev_y = y

            else:
                forced_move = False

            # Once per frame, check if spacebar has been hit.
            pygame.event.pump()  # Allow pygame to handle internal actions.
            key = pygame.key.get_pressed()
            if key[pygame.K_SPACE]:  # Press 'spacebar' to exit the while loop and skip to submit GUI
                # Break out of this while loop by saying the video has looped the max. amount of times.
                # (I do it like this everywhere!)
                looped = LOOP_AMOUNT
                break

            frame = imgproc.cannyfilter(frame, sigma=sigma, high_threshold=threshold)
            frame_counter += 1

            # phosphene simulation
            frame = cv2.resize(frame, phosphene_imsize)
            phosphenes = simulator(frame)
            frame = pygame.surfarray.make_surface(phosphenes)
            frame = pygame.transform.rotate(frame, -90)  # Rotation correction as np array of image is rotated 90.
            screen.blit(frame, frame.get_rect(center=(width // 2, heigth // 2)))  # Add frame to center of pygame Frame.

            pygame.display.flip()
            fps_clock.tick(FRAMERATE)  # Limits FRAMERATE to FRAMERATE index_variable

        looped += 1
        # Transition when video restarts
        if looped < LOOP_AMOUNT:
            # Do the transition.
            looped = loop_transition(screen, 'GRAY', 'BLACK', transition_time=2, loops=looped)
            # Once again I use the amount of loops to check if spacebar has been hit.
            if looped == LOOP_AMOUNT:  # Still check if spacebar has been hit.
                break

        if looped >= LOOP_AMOUNT:
            # Last recording is added to trace the last mouse position before ending video.
            # If recording was already made due to mouse movement it gets overwritten.
            tracked_mouse_data[frame_counter] = {'time': time.time() - timer, 'x': prev_x, 'y': prev_y,
                                                 'threshold': threshold, 'sigma': sigma,
                                                 'framerate': fps_clock.get_fps()}

    pygame.quit()

    prompt.ExperimentForm(video_file, vid_nr + subject_progress + 1, subject)

    # update active_subject object
    subject.update_actions(filenames[MODE][vid_nr], tracked_mouse_data)


if __name__ == '__main__':
    # -PARAMETERS- #
    CONTROL = 'fixed'  # choose from ['adaptive', 'fixed']
    MODE = 'edge-detection'  # choose from ['depth','segmentation','edge-detection']

    # General dataset location and structure settings.
    DATA_DIR = '.\\Dataset'  # Dataset downloadable at https://osf.io/s2udz (https://doi.org/10.1145/3458709.3458982)
    SUBFOLDERS = ['Original Videos', 'Depth_simplification',
                  'Segmentation_simplification', 'DVS']  # SUBFOLDERS of interest
    MODE_NAME = ['edge-detection', 'depth', 'segmentation',
                 'DVS']  # Apply custom name to SUBFOLDERS (just for clarity).

    # General video settings
    MAX_THRESHOLD = 300  # Maximum number the threshold can be, used for combining mouse position with threshold value.
    MAX_SIGMA = 3  # Maximum number sigma can be, used for combining mouse position with sigma value.
    FRAMERATE = 25  # Framerate video is played at.
    LOOP_AMOUNT = 10  # number of times a video should be replayed
    phosphene_imsize = (960, 960)  # Specify size of stimulus

    filenames, test_sample_videos = videos_path()  # List of videos and list of practise videos
    random.shuffle(filenames.get(MODE))  # Shuffle the list of videos randomly

    width, heigth = pyautogui.size()  # Fetch width and height of monitor in pixels
    threshold_per_pixel = MAX_THRESHOLD / width  # Increments/decreases threshold with this value per pixel.
    sigma_per_pixel = MAX_SIGMA / heigth  # Increments/decreases sigma with this value per pixel.

    # Dilation (to make edge detection thicker)
    simulator = imgproc.PhospheneSimulator(intensity=10, phosphene_resolution=(50, 50), size=phosphene_imsize)

    subject = objects.Subject(subject_id='',
                              order=[],
                              answers={}, actions={})

    prompt.NewUserGUI(subject)

    overwrite_subject = load_json(base=f".\\results\\subjectdata\\{CONTROL}\\",
                                  filename=f"subject_{subject.get_subject_id()}_{CONTROL}.json",
                                  data_type_is_subject=True)

    if overwrite_subject is not None:  # Check if subject ID already exists.
        if len(overwrite_subject.get_answers()) != 0:  # If subject ID already exists but is not used, restart.
            subject = overwrite_subject

    if CONTROL == 'adaptive':
        subject.set_order(filenames.get(MODE))
    elif CONTROL == 'fixed':
        fixed_canny_params = load_json(base=".\\resource\\", filename="fixed_canny_params.json")
        fixed_vid_order = load_json(base=".\\resource\\", filename="fixed_vid_order.json")
        subject.set_order(list(fixed_vid_order.get(subject.get_subject_id()).values()))

    if len(subject.get_answers()) != 0:
        if len(subject.get_answers()) == 16:
            prompt.StartExperiment(
                message=f"User {subject.get_subject_id()} has already completed {len(subject.get_answers())}/16 videos",
                button_str="Quit",
                window_str=f"No can do.")
            quit()
        else:
            prompt.StartExperiment(
                message=f"User {subject.get_subject_id()} has completed {len(subject.get_answers())}/16 videos\n",
                button_str="Resume experiment.",
                window_str=f"Resume subject {subject.get_subject_id()}")
    else:  # Subject is new and will first be shown 8 practise video's.

        prompt.StartExperiment(
            message=f"You will now get to see 8 videos to practise",
            button_str="Start practise session",
            window_str=f"Training subject {subject.get_subject_id()}")

        dummy_subject = objects.Subject(subject_id='', order=[], answers={}, actions={})
        subject_progress = len(dummy_subject.get_answers())

        sample = 0
        use_dvs = False
        for vid_nr in range(8):
            if not use_dvs:
                video_file = test_sample_videos.get('edge-detection')[sample]
            else:
                video_file = test_sample_videos.get('DVS')[sample]

            frames = preload_video(video_file)

            if vid_nr >= 3:
                for index in range(len(frames)):
                    frames[index] = cv2.flip(frames[index], 1)
            fixed_render(frames, dummy_subject, use_dvs)

            if not use_dvs:
                use_dvs = True
            else:
                use_dvs = False
            sample += 1
            if vid_nr == 3:
                sample = 0
                use_dvs = True
        prompt.StartExperiment(
            message=f"Practise is up!",
            button_str="Start experiment",
            window_str=f"Start subject {subject.get_subject_id()}")

    subject_progress = len(subject.get_answers())
    order = subject.get_vidorder()

    for vid_nr in range(subject_progress, 16):
        video_file = order[vid_nr]
        frames = preload_video(video_file)
        if CONTROL == 'adaptive':
            adaptive_render(frames, subject)
        elif CONTROL == 'fixed':
            fixed_render(frames, subject, order[vid_nr].__contains__('DVS'))

        # Save subject to JSON
        save_subject_data(base=f".\\results\\subjectdata\\{CONTROL}\\",
                          filename=f"subject_{subject.get_subject_id()}_{CONTROL}.json")

    pygame.quit()
