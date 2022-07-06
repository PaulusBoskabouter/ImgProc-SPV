"""
# Author       : Paul Verhoeven
# Date         : 25-03-2022
This is script is made purely for demonstration purposes. It's mostly a copy-paste of experiment_pipeline.py
with some hard coded nonsense.
"""
import cv2
import objects
import imgproc
import prompt
import pygame
import pyautogui
import time


def transition(screen, fps_clock, start_fg, start_bg, transition_time: int = 1, transition_fps: int = 60,
               reverse: bool = False):
    pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
    pygame.display.flip()
    x = 0
    while x < width:
        pygame.event.pump()
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            return 1
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
        x += (width / (transition_time / (1 / transition_fps)))

        if x >= width and not reverse:
            x = 0
            reverse = True
        pygame.display.flip()
        fps_clock.tick(transition_fps)

    pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
    pygame.display.flip()
    time.sleep(0.5)
    return 1


# General video settings
MAX_THRESHOLD = 300
MAX_SIGMA = 3
FRAMERATE = 25

phosphene_imsize = (960, 960)

# -PARAMETERS- #
width, heigth = pyautogui.size()

simulator = imgproc.PhospheneSimulator(intensity=10, phosphene_resolution=(50, 50), size=phosphene_imsize)

frames_in_list = []
cap = cv2.VideoCapture(".\\dataset\\Original Videos\\sample3.mp4")
_, video_frame = cap.read()
while video_frame is not None:
    frames_in_list.append(video_frame)
    _, video_frame = cap.read()
cap.release()
pygame.init()
fps_clock = pygame.time.Clock()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
previous_key = {pygame.K_UP: False, pygame.K_DOWN: False}
display_mode = 0
frame_index = 0
pause = False
dummy_subject = objects.Subject(subject_id='', order="", answers={}, actions={})
width, heigth = pyautogui.size()  # Fetch width and height of monitor in pixels
threshold = 150
sigma = 1.5
pygame.event.set_grab(True)  # Locks cursor within boundaries of window
pygame.mouse.set_visible(False)  # Make cursor invisible
while True:
    max = len(frames_in_list)
    frame = frames_in_list[frame_index]
    pygame.event.pump()
    key = pygame.key.get_pressed()
    if key[pygame.K_UP] and not previous_key[pygame.K_UP]:
        display_mode += 1
    if key[pygame.K_DOWN] and not previous_key[pygame.K_DOWN]:
        display_mode -= 1
    if key[pygame.K_SPACE] and not previous_key[pygame.K_SPACE]:
        display_mode = 4
    if key[pygame.K_ESCAPE]:
        quit()

    previous_key = key

    if display_mode == 0:
        pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))

    if display_mode == 1:
        pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
        frame = frame[:, :, ::-1]
        frame = pygame.surfarray.make_surface(frame)
        frame = pygame.transform.rotate(frame, -90)
        screen.blit(frame, frame.get_rect(center=(width // 2, heigth // 2)))

    if display_mode == 2 or display_mode == 3:
        # for y (which controls sigma) range starts from 1px because sigma cannot be 0.
        pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
        original_frame = frame[:, :, ::-1]
        original_frame = pygame.surfarray.make_surface(original_frame)
        original_frame = pygame.transform.rotate(original_frame, -90)
        frame = imgproc.cannyfilter(frame, sigma=sigma, high_threshold=threshold)
        # phosphene simulation
        frame = cv2.resize(frame, phosphene_imsize)
        frame = simulator(frame)
        frame = pygame.surfarray.make_surface(frame)
        frame = pygame.transform.rotate(frame, -90)
        if display_mode == 2:
            screen.blit(original_frame, original_frame.get_rect(center=(width // 4, heigth // 2)))
            screen.blit(frame, frame.get_rect(center=(width * .75, heigth // 2)))
        else:
            pygame.draw.rect(screen, 'BLACK', rect=pygame.Rect(0, 0, width, heigth))
            screen.blit(frame, frame.get_rect(center=(width // 2, heigth // 2)))

    if display_mode == 4:
        prompt.ExperimentForm(vid_id='', title_bar=1, subject_data=dummy_subject)
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
        display_mode = 1

    if display_mode == 5 or display_mode < 0:
        display_mode = transition(screen, fps_clock, 'GRAY', 'BLACK', transition_time=2)

    if not pause:
        frame_index += 1
    if frame_index >= len(frames_in_list):
        frame_index = 0
    pygame.display.flip()
    fps_clock.tick(FRAMERATE)  # Limits FRAMERATE to FRAMERATE index_variable
