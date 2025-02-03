import pygame
from graphics import screen
from data import FONT

# функция, которая запускается при начале новой игры, вводит в суть повествования

def new_game_intro():
    phrases = ['Чума...', 'Чума поработила нашу деревню.', 'Столько людей погибло в подземелье, пытаясь нас спасти...',
               'Отважный воин, помоги нам!', 'Отыщи источник.'] # список фраз
    c = 0 # переменная-таймер
    cur_phrase = 0
    num_of_showed_letters = 1
    font = pygame.font.Font(FONT, 40)
    while True: # в цикле реализовано постепенное появление текста
        screen.fill(pygame.Color('black'))
        showed_text = phrases[cur_phrase][:num_of_showed_letters]
        c += 1
        if c % 40 == 0:
            if num_of_showed_letters - 1 <= len(phrases[cur_phrase]):
                num_of_showed_letters += 1
        text = font.render(showed_text, 1, pygame.Color('white'))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2,
                            screen.get_height() // 2 - text.get_height() // 2))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN: # если нажимаем кнопку мыши:
                if num_of_showed_letters < len(phrases[cur_phrase]): # если выведена ещё не вся фраза, выводим её полностью
                    num_of_showed_letters = len(phrases[cur_phrase])
                elif cur_phrase + 1 < len(phrases): # если фраза выведена полностью, меняем её на следующую
                    cur_phrase += 1
                    num_of_showed_letters = 1
                    c = 0
                else: # если вывелись все фразы, выходим из функции и идём в главный цикл игры
                    return
        pygame.display.flip()
