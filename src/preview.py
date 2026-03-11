from pathlib import Path
import pygame
import numpy as np
from PyQt6 import QtWidgets

KRPATH = str(Path(__file__).resolve().parent.parent) + "/"
SCENE = None # PASOS scene
F_array = lambda: np.swapaxes(SCENE.renderer.get_frame()[:, :, :3], 0, 1)

class PreviewState:
    def __init__(self):
        self.running = True
        self.visible_window = True
        self.window_resolution = (853, 480) #manim_resolution = (128/9, 8)
        self.window = None
        self.surf = pygame.surfarray.make_surface(F_array())
        self.play_tick_start = 0 # pygame time when playing starts
        self.play_time_start = 0 # scene time when playing starts

def run_preview(scene):
    global SCENE
    SCENE = scene
    V = PreviewState()

    while V.running:
        pygame.init() 
        V.window = pygame.display.set_mode(V.window_resolution)
        pygame.display.set_caption("Preview")
        try:
            pygame.display.set_icon(pygame.image.load(KRPATH+"icon_light.png"))
        except:
            pass

        while V.running and V.visible_window:
            function_calls(V)
            pygame_loop(V)
        pygame.quit()
        while V.running and not V.visible_window:
            function_calls(V)

def function_calls(V):
    if SCENE.edtv["function_call"]: # shared functions
        if SCENE.edtv["function_call"][-1] == "set_preview_visibility":
            V.visible_window = SCENE.edtv["function_call"][-2]
            SCENE.edtv["function_call"].pop(-1)
            SCENE.edtv["function_call"].pop(-1)

        elif SCENE.edtv["function_call"][-1] == "quit":
            V.running = False
            SCENE.edtv["function_call"].pop(-1)

def pygame_loop(V):
    editor_window = SCENE.edtv["editor_window_object"]

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            V.visible_window = False
            editor_window.preview_menu_action.setChecked(False)
        #if event.type == pygame.MOUSEBUTTONDOWN:
        #    dragging = True
        #if event.type == pygame.MOUSEBUTTONUP:
        #    dragging = False

    if SCENE.edtv["function_call"] and SCENE.edtv["function_call"][-1] == "start_playing":
        V.play_tick_start = pygame.time.get_ticks()
        V.play_time_start = SCENE.edtv["time"]
        SCENE.edtv["function_call"].pop(-1)

    if SCENE.edtv["playing"]:
        editor_window.set_time_to(V.play_time_start + (pygame.time.get_ticks() - V.play_tick_start)/1000 * SCENE.edtv["playing_speed"])
        if SCENE.edtv["time"] > SCENE.duration:
            editor_window.set_time_to(SCENE.duration)
            editor_window.playing_toggle()

    SCENE.update_mobs()
    SCENE.renderer.update_frame(SCENE)
    pygame.surfarray.blit_array(V.surf, F_array())
    V.window.blit(pygame.transform.scale(V.surf, V.window_resolution), (0, 0))
    pygame.display.flip()
