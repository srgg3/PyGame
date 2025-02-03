import pygame
import os

# функции для смены музыки в игре
def main_menu_music():
    pygame.mixer.music.load(os.path.join("..\data\music", "main_menu.mp3"))

def first_loc_music():
    pygame.mixer.music.load(os.path.join("..\data\music", "first_loc.mp3"))

def battle_music():
    pygame.mixer.music.load(os.path.join("..\data\music", "battle_music.mp3"))

