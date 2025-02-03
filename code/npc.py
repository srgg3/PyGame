import pygame
from graphics import screen, sly_dialogue, sly_shop, elderbug_dialogue
from menu import Button
from data import FONT


# файл с классами, реализующими отображение диалогов с нпс и в случае с жуком-торгашом отображение магазина
# так же частично реализованы некоторые функции взаимодействия с диалоговыми окнами

class Sly_dialogue(pygame.sprite.Sprite): # диалог со Слаем(торговцем)
    def __init__(self):
        super().__init__(sly_dialogue)
        self.image = pygame.Surface((screen.get_width() // 3, screen.get_height() // 8), pygame.SRCALPHA, 32)
        x, y = screen.get_width() // 2 - self.image.get_width() // 2, screen.get_height() // 3
        pygame.draw.rect(self.image, (150, 150, 150, 120), self.image.get_rect(), border_radius=50)
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        self.current_phrase = 0
        self.phrase_is_typing = True
        self.phrases = [['Здравствуй, отважный воин. Я не думал, что кто-то найдёт меня здесь.'],
                        ['Это место действительно пугает,',
                        'а чудовище, таящееся в комнате на востоке, лишило меня постоянных клиентов.'],
                        ['Я готов помочь тебе в борьбе с древним монстром.',
                        'Ты можешь купить у меня пару улучшений для своего оружия и брони.']]

        self.next_phrase_button = Button(50, 50, self.rect.x + self.rect.w - 10,
                                    self.rect.y + self.rect.h - 10, (50, 50, 50), (255, 255, 255, 100))
        self.close_dialogue_button = Button(50, 50, self.rect.x + self.rect.w - 10,
                                    self.rect.y - 50, (50, 50, 50), (255, 255, 255, 100))

        self.shop_button = None
        self.open_shop = False

    def update(self):
        if not self.open_shop:
            font = pygame.font.Font(FONT, 20)
            for phrase in self.phrases[self.current_phrase]:
                text = font.render(phrase, 1, pygame.Color('white'))
                screen.blit(text, (self.rect.x + 20,
                                    self.rect.y + 50 + text.get_height() * 1.5 *
                                    self.phrases[self.current_phrase].index(phrase)))

        if self.current_phrase == 2:
            self.next_phrase_button = None
            if not self.shop_button:
                self.shop_button = Button(self.rect.w // 3, self.rect.h // 5,
                                          self.rect.x + self.rect.w // 2 - self.rect.w // 6,
                                          self.rect.y + self.rect.h - self.rect.h // 10,
                                          (50, 50, 50), (255, 255, 255, 100))


    def draw_buttons(self):
        if self.next_phrase_button:
            self.next_phrase_button.draw('>>', 25)
        self.close_dialogue_button.draw('X', 25)
        if self.shop_button:
            self.shop_button.draw('Магазин', 25)


class Sly_shop(pygame.sprite.Sprite): # магазин Слая(для удобства сделан отдельным классом)
    def __init__(self):
        super().__init__(sly_shop)
        self.image = pygame.Surface((screen.get_width() // 6, screen.get_height() // 3), pygame.SRCALPHA, 32)
        x, y = screen.get_width() // 2 - self.image.get_width() // 2, screen.get_height() // 3
        pygame.draw.rect(self.image, (150, 150, 150, 120), self.image.get_rect(), border_radius=50)
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        self.close_button = Button(50, 50, self.rect.x + self.rect.w - 10,
                                        self.rect.y - 50, (50, 50, 50), (255, 255, 255, 100))
        self.buy_attack_improvement = Button(self.rect.w // 3, 30,
                                             self.rect.x + self.rect.w // 2 + self.rect.w // 8,
                                             self.rect.y + self.rect.h // 10, (50, 50, 50), (255, 255, 255, 100))
        self.buy_maximum_health_improvement = Button(self.rect.w // 3, 30,
                                             self.rect.x + self.rect.w // 2 + self.rect.w // 8,
                                             self.rect.y + self.rect.h // 10 + 45, (50, 50, 50), (255, 255, 255, 100))
        self.buy_maximum_healings_improvement = Button(self.rect.w // 3, 30,
                                             self.rect.x + self.rect.w // 2 + self.rect.w // 8,
                                             self.rect.y + self.rect.h // 10 + 90, (50, 50, 50), (255, 255, 255, 100))

        self.damage_improvement_price = 175
        self.maximum_health_improvement_price = 125
        self.maximum_healings_improvement_price = 125

    def update(self):
        font = pygame.font.Font(FONT, 17)
        text = font.render('Урон от атаки +1', 1, pygame.Color('white'))
        screen.blit(text, (self.rect.x + self.rect.w // 14, self.rect.y + self.rect.h // 10))

        text = font.render('Максимальное здоровье +1', 1, pygame.Color('white'))
        screen.blit(text, (self.rect.x + self.rect.w // 14, self.rect.y + self.rect.h // 10 + 45))

        text = font.render('Максимум лечений +1', 1, pygame.Color('white'))
        screen.blit(text, (self.rect.x + self.rect.w // 14, self.rect.y + self.rect.h // 10 + 90))

    def draw_buttons(self):
        self.close_button.draw('X', 25)
        self.buy_attack_improvement.draw(str(self.damage_improvement_price), 25)
        self.buy_maximum_health_improvement.draw(str(self.maximum_health_improvement_price), 25)
        self.buy_maximum_healings_improvement.draw(str(self.maximum_healings_improvement_price), 25)


class Elderbug_dialogue(pygame.sprite.Sprite): # диалог со стариком, который рассказывает историю
    def __init__(self):
        super().__init__(elderbug_dialogue)
        self.image = pygame.Surface((screen.get_width() // 3, screen.get_height() // 8), pygame.SRCALPHA, 32)
        x, y = screen.get_width() // 2 - self.image.get_width() // 2, screen.get_height() // 3
        pygame.draw.rect(self.image, (150, 150, 150, 120), self.image.get_rect(), border_radius=50)
        self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

        self.current_phrase = 0
        self.phrase_is_typing = True
        self.phrases = [['Ох, неужели ещё один смелый странник?'],
                        ['Ты, как все остальные, хочешь освободить нас от чумы?'],
                        ['Я видел множество таких же как и ты. Все они погибли страшной смертью...'],
                        ['Надеюсь хоть ты сможешь избавить нас от проклятия.'],
                        ['Источник чумы - огромная муха. Она находится в глубинах подземелья']]

        self.next_phrase_button = Button(50, 50, self.rect.x + self.rect.w - 10,
                                    self.rect.y + self.rect.h - 10, (50, 50, 50), (255, 255, 255, 100))
        self.close_dialogue_button = Button(50, 50, self.rect.x + self.rect.w - 10,
                                    self.rect.y - 50, (50, 50, 50), (255, 255, 255, 100))

    def update(self):
        font = pygame.font.Font(FONT, 20)
        for phrase in self.phrases[self.current_phrase]:
            text = font.render(phrase, 1, pygame.Color('white'))
            screen.blit(text, (self.rect.x + 20,
                                self.rect.y + 50 + text.get_height() * 1.5 *
                                self.phrases[self.current_phrase].index(phrase)))

        if self.current_phrase + 1 == len(self.phrases):
            self.next_phrase_button = None

    def draw_buttons(self):
        if self.next_phrase_button:
            self.next_phrase_button.draw('>>', 25)
        self.close_dialogue_button.draw('X', 25)

