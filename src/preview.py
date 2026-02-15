import pygame
import numpy as np
from PyQt6 import QtWidgets

def run_preview_window(scene):
    pygame.init()
    #manim_resolution = (128/9, 8)
    window_resolution = (853, 480)
    window = pygame.display.set_mode(window_resolution)
    pygame.display.set_caption("Preview")
    try:
        pygame.display.set_icon(pygame.image.load("icon_light.png"))
    except:
        pass
    play_tick_start = 0 # pygame time when playing starts
    play_time_start = 0 # scene time when playing starts
    editor_window = None # the EditorWindow is stored in this variable
    F_array = lambda: np.swapaxes(scene.renderer.get_frame()[:, :, :3], 0, 1)
    surf = pygame.surfarray.make_surface(F_array())
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            #if event.type == pygame.MOUSEBUTTONDOWN:
            #    dragging = True
            #if event.type == pygame.MOUSEBUTTONUP:
            #    dragging = False

        if scene.edtv["function_call"]: # shared functions
            if scene.edtv["function_call"][-1] == "update_pygame_editor_window_variable":
                editor_window = scene.edtv["function_call"][-2]
                editor_window.raise_()
                scene.edtv["function_call"].pop(-1)
                scene.edtv["function_call"].pop(-1)

            elif scene.edtv["function_call"][-1] == "start_playing":
                play_tick_start = pygame.time.get_ticks()
                play_time_start = scene.edtv["time"]
                scene.edtv["function_call"].pop(-1)
            
            elif scene.edtv["function_call"][-1] == "quit":
                running = False
                break

        if scene.edtv["playing"]:
            editor_window.set_time_to(play_time_start + (pygame.time.get_ticks() - play_tick_start)/1000 * scene.edtv["playing_speed"])
            if scene.edtv["time"] > scene.duration:
                editor_window.set_time_to(scene.duration)
                editor_window.mbtn_play.setIcon(editor_window.style().standardIcon(QtWidgets.QStyle.StandardPixmap.SP_MediaPlay))
                scene.edtv["playing"] = False

        scene.update_mobs()
        scene.renderer.update_frame(scene)
        pygame.surfarray.blit_array(surf, F_array())
        window.blit(pygame.transform.scale(surf, window_resolution), (0, 0))
        pygame.display.flip()

    pygame.quit()
