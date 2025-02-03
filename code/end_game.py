import pygame
from graphics import screen
from data import FONT
from menu import Button

# отрисовываем конечную заставку так же, как начальную
def end_game(killed_enemies, total_damage, deaths_amounts):
    killed_enemies, total_damage, deaths_amounts =  killed_enemies, total_damage, deaths_amounts
    phrases = ['Спасибо, храбрый рыцарь, ты спас нас!', 'Наша деревня навсегда запомнит тебя']
    c = 0
    cur_phrase = 0
    num_of_showed_letters = 1
    font = pygame.font.Font(FONT, 40)
    while True:
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
            if event.type == pygame.MOUSEBUTTONDOWN:
                if num_of_showed_letters < len(phrases[cur_phrase]):
                    num_of_showed_letters = len(phrases[cur_phrase])
                elif cur_phrase + 1 < len(phrases):
                    cur_phrase += 1
                    num_of_showed_letters = 1
                    c = 0
                else:
                    print(1)
                    draw_statistics(killed_enemies, total_damage, deaths_amounts)
                    return
        pygame.display.flip()


# отображаем статистику, которую собирали в игре
def draw_statistics(killed_enemies, total_damage, deaths_amounts):
    font = pygame.font.Font(FONT, 40)
    to_menu_button = Button(300, 40, screen.get_width() // 2 - 150, screen.get_height() - 60,
                            (50, 50, 50), (255, 255, 255, 100))
    while True:
        screen.fill((0, 0, 0))
        text = font.render(f'Убито врагов: {killed_enemies}', 1, pygame.Color('white'))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, screen.get_height() // 3))

        text = font.render(f'Урона нанесено: {total_damage}', 1, pygame.Color('white'))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2,
                           screen.get_height() // 3 + text.get_height() * 1.5))

        text = font.render(f'Смерти: {deaths_amounts}', 1, pygame.Color('white'))
        screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2,
                           screen.get_height() // 3 + text.get_height() * 3))

        to_menu_button.draw('Главное меню', 30)

        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if to_menu_button.get_pressed():
                    return

        pygame.display.flip()

