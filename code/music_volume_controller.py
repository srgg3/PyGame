import pygame
from graphics import screen

# ползунок изменения громкости звука, который находится в главном меню

class Base(pygame.sprite.Sprite): # основа, на которой рисуется сам ползунок
    def __init__(self):
        super().__init__(volume_controller_base)
        self.image = pygame.Surface((500, 30), pygame.SRCALPHA, 32)
        self.rect = pygame.Rect(100, 100, self.image.get_width(), self.image.get_height())
        pygame.draw.rect(self.image, (150, 150, 150), self.image.get_rect(), border_radius=10)


class Slider(pygame.sprite.Sprite): # ползунок(кружочек, который мы двигаем и меняем громкость)
    def __init__(self):
        super().__init__(volume_controller_slider)
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA, 32)
        self.rect = pygame.Rect(100 + 5 * pygame.mixer.music.get_volume() * 100, 100,
                                self.image.get_width(), self.image.get_height())
        pygame.draw.circle(self.image, (0, 0, 0), (15, 15), 15)

        self.mouse_x_on_slider = 0
        self.moving = False

    def update(self, *args):  # движение ползунка по основе, обновление громкости в зависимости от координаты ползунка
        if args:
            event = args[0]
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.rect.collidepoint(event.pos):
                    self.moving = True
                    self.mouse_x_on_slider = event.pos[0] - self.rect.x
            if event.type == pygame.MOUSEBUTTONUP:
                self.moving = False
            if event.type == pygame.MOUSEMOTION:
                if self.moving:
                    if 85 <= event.pos[0] - self.mouse_x_on_slider <= 585:
                        self.rect.x = event.pos[0] - self.mouse_x_on_slider
                        pygame.mixer.music.set_volume((self.rect.x - 100) / 5 / 100)


class Filler(pygame.sprite.Sprite): # штука которая заполняет пространство от левого края основы до ползунка
    def __init__(self):
        super().__init__(volume_controller_filler)
        w = 0
        for sprite in volume_controller_slider:
            w = sprite.rect.x - 100 + 20
        self.image = pygame.Surface((500, 30), pygame.SRCALPHA, 32)
        self.rect = pygame.Rect(100, 100, w, self.image.get_height())

    def update(self):
        w = 0
        for sprite in volume_controller_slider: # ширина штуки зависит от координаты ползунка
            w = sprite.rect.x - 100 + 20
        self.rect.width = w


# группы спрайтов, отдельная для каждого элемента регулятора громкости
volume_controller_base = pygame.sprite.Group()
volume_controller_slider = pygame.sprite.Group()
volume_controller_filler = pygame.sprite.Group()