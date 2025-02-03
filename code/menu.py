import pygame
from graphics import menu, screen, new_game_confirmation
from data import FONT

class InGameMenu(pygame.sprite.Sprite): # класс внутриигрового меню, чисто визуальная часть
    def __init__(self):
        super().__init__(menu)
        self.image = pygame.Surface((screen.get_width() // 8, screen.get_height() // 4), pygame.SRCALPHA, 32)
        x, y = screen.get_width() // 2 - screen.get_width() // 10, screen.get_height() // 2 - screen.get_height() // 6
        pygame.draw.rect(self.image, (0, 0, 0, 100), self.image.get_rect(), border_radius=50)
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        self.resume_button = Button(self.rect.width // 1.5, self.rect.height // 8,
                                    self.rect.x + self.rect.width // 2 - self.rect.w // 1.5 // 2,
                                    self.rect.y + self.rect.height // 4,
                                    (50, 50, 50), (255, 255, 255, 100))
        self.back_to_main_menu_button = Button(self.rect.width // 1.5, self.rect.height // 8,
                                               self.rect.x + self.rect.width // 2 - self.rect.w // 1.5 // 2,
                                               self.rect.y + self.rect.height - self.rect.height // 5 -
                                               self.rect.height // 8,
                                               (50, 50, 50), (255, 255, 255, 100))

    def draw_menu_buttons(self):
        self.resume_button.draw('Вернуться в игру', 20)
        self.back_to_main_menu_button.draw('Главное меню', 20)


class Button: # класс кнопок, используемых в игре
    def __init__(self, width, height, x, y, inactive_color, active_color, disabled_color = None):
        # при инициализации задаем размеры, координаты и цвета, когда на кнопку наведён и не наведён курсор
        self.width = width
        self.height = height
        self.inactive_color = inactive_color
        self.active_color = active_color
        self.disabled_color = disabled_color # цвет кнопки, если она неактивна, если этот цвет передать, то она не будет
                                             # менять цвет при наведении на неё и с ней нельзя будет взаимодействовать
                                             # если ничего не передавать, то всё будет окей
        self.x = x
        self.y = y
        self.c = 0


    def draw(self, message=None, font_size=None):  # отрисовка кнопок на экране, если передать текст и его размер, кнопка будет с текстом
        mouse = pygame.mouse.get_pos() # берём координаты мыши

        if not self.disabled_color:
            if self.x < mouse[0] < self.x + self.width and self.y < mouse[1] < self.y + self.height:
                # если мышь наведена на кнопку, рисуем её цветом active_color
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
                pygame.draw.rect(self.image, self.active_color, self.image.get_rect(), border_radius=10)
                screen.blit(self.image, (self.x, self.y))
            else:
                # в ином случае рисуем цветом inactive_color
                self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
                pygame.draw.rect(self.image, self.inactive_color, self.image.get_rect(), border_radius=10)
                screen.blit(self.image, (self.x, self.y))
        else: # отрисовка кнопки, если передали аргумент disabled_color
            self.image = pygame.Surface((self.width, self.height), pygame.SRCALPHA, 32)
            pygame.draw.rect(self.image, self.disabled_color, self.image.get_rect(), border_radius=10)
            screen.blit(self.image, (self.x, self.y))

        if message: # пишем на кнопочке текст, если он есть
            font = pygame.font.Font(FONT, font_size)
            text = font.render(message, True, pygame.Color('White'))
            screen.blit(text, (self.x + (self.width / 2 - text.get_width() / 2),
                                         self.y + (self.height / 2 - text.get_height() / 2)))

    def get_pressed(self): # если кнопка активна и нажали на кнопку мыши, пока она внутри кнопки, возвращаем True
        if not self.disabled_color:
            if self.x < pygame.mouse.get_pos()[0] < self.x + self.width and \
                    self.y < pygame.mouse.get_pos()[1] < self.y + self.height and pygame.mouse.get_pressed()[0]:
                return True
        return False


class New_game_confirmation(pygame.sprite.Sprite): # окошко с подтверждением новой игры(если имеется сохранение)
    def __init__(self):
        super().__init__(new_game_confirmation)
        self.image = pygame.Surface((screen.get_width() // 8, screen.get_height() // 6), pygame.SRCALPHA, 32)
        x, y = screen.get_width() // 2 - self.image.get_width() // 2, \
               screen.get_height() // 2 - self.image.get_height() // 2
        pygame.draw.rect(self.image, (0, 0, 0, 75), self.image.get_rect(), border_radius=50)
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        self.confirm_button = Button(self.rect.width // 3, self.rect.height // 6,
                                self.rect.x + self.rect.width // 8,
                                self.rect.y + self.rect.height // 3 * 2,
                                (50, 50, 50), (255, 255, 255, 100))
        self.reject_button = Button(self.rect.width // 3, self.rect.height // 6,
                                self.rect.x + self.rect.width // 2 + self.rect.width // 16,
                                self.rect.y + self.rect.height // 3 * 2,
                                (50, 50, 50), (255, 255, 255, 100))

    def update(self):
        font = pygame.font.Font(FONT, 22)
        text = font.render('При начале новой игры', 1, pygame.Color('White'))
        screen.blit(text, (self.rect.x + (self.rect.width / 2 - text.get_width() / 2), self.rect.y + self.rect.w // 8))

        text = font.render('текущее сохранение сотрётся.', 1, pygame.Color('White'))
        screen.blit(text, (self.rect.x + (self.rect.width / 2 - text.get_width() / 2),
                           self.rect.y + self.rect.w // 8 + text.get_height() * 1.5))

        text = font.render('Начать новую игру?', 1, pygame.Color('White'))
        screen.blit(text, (self.rect.x + (self.rect.width / 2 - text.get_width() / 2),
                           self.rect.y + self.rect.w // 2 - text.get_height()))

    def draw_buttons(self):
        self.confirm_button.draw('Да', 20)
        self.reject_button.draw('Нет', 20)