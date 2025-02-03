import sys
import os

import pygame

# Импорт классов и функций из графического модуля
from graphics import (
    platforms, screen, fps, size, character, knight, enemies, 
    main_character, menu, money, load_image, initialization, saving_points, 
    damage_waves, update_map_after_save, Money, money_list, 
    new_game_confirmation, Crawlid, trigger_blocks, Sly, npcs, 
    sly_dialogue, sly_shop, background, Elderbug, elderbug_dialogue
)

# Импорт данных
from data import (
    move_speed, start_jump_from_wall_position, start_jump_altitude, 
    fall_speed, global_cords, respawn_cords, FONT
)

# Импорт дополнительных модулей
import triggers
from menu import InGameMenu, Button, New_game_confirmation
import load_music

# Импорт контроллера громкости
from music_volume_controller import (
    volume_controller_filler, volume_controller_slider, volume_controller_base, 
    Base, Filler, Slider
)

# Импорт NPC и диалогов
from npc import Sly_dialogue, Sly_shop, Elderbug_dialogue

# Импорт сценария для нового начала игры
from new_game_intro import new_game_intro

# Импорт конца игры
import end_game

# индексы анимаций гг
ATTACKING_SHEET = 5
SLIDING_SHEET = 4
JUMPING_SHEET = 3
FALLING_SHEET = 2
RUNNING_SHEET = 1
STANDING_SHEET = 0

# точки сохранения
SAVING_POINTS_CORDS = {'1': (-570, 7550), '2': (8780, 9220), '3': (9480, 7350), '4': (23000, 23050)}

# деньги, звук
main_character_money = 0
volume = 0
boss_killed = False

lock_script = triggers.Boss_Wall_Lock()  # дверь, запирающая комнаты с боссом
whitelight = triggers.WhiteLight() # конец игры


def load_data_from_save(): # загружаем из файла сохранения всю информацию в нужные нам переменные
    global respawn_cords, main_character_money, money_list, volume, main_character, global_cords, boss_killed
    with open('../save/save.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        try:
            respawn_cords[0] = int(lines[0].split(':')[1].strip())
            respawn_cords[1] = int(lines[1].split(':')[1].strip())
            global_cords[0], global_cords[1] = 0, 0
            main_character_money = int(lines[2].split(':')[1].strip())
            for line in lines[3:-8]:
                collected = line.split(':')[1].split(', ')[4].strip()
                if collected == 'False':
                     money_list[lines.index(line) - 3][4] = False
                elif collected == 'True':
                    money_list[lines.index(line) - 3][4] = True
            volume = float(lines[-8].split(':')[1].strip())
            main_character.attack_damage = int(lines[-7].split(':')[1].strip())
            main_character.maximum_health = int(lines[-6].split(':')[1].strip())
            main_character.maximum_healings = int(lines[-5].split(':')[1].strip())
            main_character.killed_enemies = int(lines[-4].split(':')[1].strip())
            main_character.total_damage = int(lines[-3].split(':')[1].strip())
            main_character.deaths = int(lines[-2].split(':')[1].strip())
            boss_killed = lines[-1].split(':')[1].strip()
            if boss_killed == 'False':
                boss_killed = False
            else:
                boss_killed = True
        except:
            print('Файл сохранения повреждён, начните новую игру.')
            write_data_to_save()


def write_data_to_save(): # записываем инфу из переменных в файл
    global money_list, main_character, volume
    with open('../save/save.txt', 'w', encoding='utf-8') as f:
        f.write(f'respawn_x: {str(respawn_cords[0])}\n')
        f.write(f'respawn_y: {str(respawn_cords[1])}\n')
        f.write(f'main_character_money: {str(main_character_money)}\n')
        for coin in money_list:
            f.write(f'money: {", ".join([str(el) for el in coin])}\n')

        f.write(f'volume: {str(volume)}\n')
        f.write(f'main_character_attack_damage: {str(main_character.attack_damage)}\n')
        f.write(f'main_character_maximum_health: {str(main_character.maximum_health)}\n')
        f.write(f'main_character_maximum_healings: {str(main_character.maximum_healings)}\n')
        f.write(f'main_character_killed_enemies: {str(main_character.killed_enemies)}\n')
        f.write(f'main_character_total_damage: {str(main_character.total_damage)}\n')
        f.write(f'main_character_deaths: {str(main_character.deaths)}\n')
        f.write(f'boss_killed: {str(boss_killed)}')

# класс камеры
class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.x = size[0] // 2
        self.y = size[1] // 2
        self.summary_d_x, self.summary_d_y = 0, 0

    # позиционировать камеру на объекте target
    def update(self):
        global start_jump_altitude, start_jump_from_wall_position, global_cords

        # разница кординат
        d_x = main_character.rect.x - self.x
        d_y = main_character.rect.y - self.y

        r = 15 * N
        k = 0

        if d_x > r:
            k = -1
        elif d_x < -r:
            k = 1
        if k:
            # передвижение всех спрайтов при движении главного героя
            main_character.rect.x -= d_x + r * k
            self.x = main_character.rect.x + r * k
            self.summary_d_x += (d_x + r * k)

            start_jump_from_wall_position -= (d_x + r * k)
            for group in [platforms, money, enemies, saving_points, trigger_blocks, npcs]:
                for sprite in group:
                    if type(sprite) == Crawlid:
                        sprite.start_x -= (d_x + r * k)
                    sprite.rect.x -= (d_x + r * k)
        k = 0
        if d_y > r:
            k = -1
        elif d_y < -r:
            k = 1

        if k:
            main_character.rect.y -= d_y + r * k
            self.y = main_character.rect.y + r * k
            self.summary_d_y += (d_y + r * k)
            start_jump_altitude -= (d_y + r * k)
            for group in [platforms, money, enemies, saving_points, trigger_blocks, npcs]:
                for sprite in group:
                    sprite.rect.y -= (d_y + r * k)


def main_menu(screen): # функция главного меню
    global respawn_cords, main_character_money, volume
    global start_jump_altitude, start_jump_from_wall_position, money_list
    global jump, jump_from_wall, speeds_before_jump, count_fall, counter_fall, game_paused, right, left

    load_music.main_menu_music() # включаем музыку для главного меню, устанавливаем громкость
    pygame.mixer.music.set_volume(volume)
    pygame.mixer.music.play(-1, fade_ms=50)

    # инициализируем некоторые элементы
    confirmation = New_game_confirmation()

    base = Base()
    slider = Slider()
    filler = Filler()

    # фон главного меню
    background = pygame.transform.scale(load_image('main_menu_background_2.png'),
                                        (screen.get_width(), screen.get_height()))
    current_bg = 1 # текущий задний фон(его можно менять)
    # кнопочки
    change_bg_button = Button(400, 50, screen.get_width() // 2 - 200, screen.get_height() - 75,
                              (0, 0, 0, 0), (255, 255, 255, 100))

    new_game_button = Button(300, 100, screen.get_width() // 2 - 150, 300, (50, 50, 50), (255, 255, 255, 100))
    continue_button = Button(300, 100, screen.get_width() // 2 - 150, 450,
                             (50, 50, 50), (255, 255, 255, 20), (0, 0, 0, 100))
    exit_game_button = Button(300, 100, screen.get_width() // 2 - 150, 600, (50, 50, 50), (255, 255, 255, 100))

    start_new_game = False # если True, начинается новая игра
    confirm_new_game = False # если True, отображается подтверждение начала новой игры

    how_to_play = False # если True, отображается гайд по игре
    how_to_play_button = Button(200, 50, screen.get_width() - 250, 25,
                                (0, 0, 0, 100), (255, 255, 255, 100))
    how_to_play_font_color = pygame.Color('white')
    back_button = Button(300, 50, screen.get_width() // 2 - 150, screen.get_height() - 75,
                         (0, 0, 0, 100), (255, 255, 255, 100))
    while True:
        screen.blit(background, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.MOUSEMOTION:
                pass
            if event.type == pygame.MOUSEBUTTONDOWN:
                if change_bg_button.get_pressed() and not confirm_new_game and not how_to_play: # смена фона
                    if current_bg == 1:
                        current_bg = 2
                        background = pygame.transform.scale(load_image('main_menu_background_1.jpg'),
                                                            (screen.get_width(), screen.get_height()))
                        how_to_play_font_color = (30, 30, 30)
                    elif current_bg == 2:
                        current_bg = 1
                        background = pygame.transform.scale(load_image('main_menu_background_2.png'),
                                                            (screen.get_width(), screen.get_height()))
                        how_to_play_font_color = pygame.Color('White')
                if how_to_play_button.get_pressed() and not confirm_new_game and not how_to_play: # как играть
                    how_to_play = True
                if back_button.get_pressed() and how_to_play: # закрыть гайд
                    how_to_play = False
                if new_game_button.get_pressed() and not confirm_new_game and not how_to_play: # новая игра
                    if respawn_cords[0] and respawn_cords[1]: # если есть корды для возрождения, открываем меню подтверждения новой игры
                        confirm_new_game = True
                    else: # если координат нет, сразу запускаем новую игру
                        start_new_game = True
                if continue_button.get_pressed() and not confirm_new_game and not how_to_play:
                    # продолжить игру, кнопка активна только если есть координаты респавна
                    data = upload_data()
                    start_jump_altitude, start_jump_from_wall_position, jump, jump_from_wall = data[:4]
                    speeds_before_jump, count_fall, counter_fall, game_paused, \
                        right, left, condition_damage_effects = data[4:]

                    load_music.first_loc_music()
                    pygame.mixer.music.play(-1, fade_ms=50)

                    slider.kill()
                    filler.kill()
                    return
                if exit_game_button.get_pressed() and not confirm_new_game and not how_to_play:
                    # выход из игры
                    write_data_to_save()
                    pygame.quit()
                    sys.exit()
            slider.update(event)
            filler.update()

        if respawn_cords[0] and respawn_cords[1]: # активность кнопки "продолжить"
            continue_button.disabled_color = None

        if how_to_play: # отрисовка гайда по игре
            back_button.draw('Назад', 30)
            font = pygame.font.Font(FONT, 35)
            texts = ['A, D - Передвижение', 'ПРОБЕЛ - Прыжок', 'Левая кнопка мыши - Атака', 'H - Лечение',
                     'E - Взаимодействие', 'Деньги остаются на месте смерти.',
                     'Враги возрождаются после смерти и после взаимодействия с точкой сохранения.',
                     'Хорошей игры!']
            for el in texts:
                text = font.render(el, 1, how_to_play_font_color)
                screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2,
                                   screen.get_height() // 4 + text.get_height() * 2 * texts.index(el)))

        if confirm_new_game: # подтверждение новой игры
            new_game_confirmation.draw(screen)
            confirmation.draw_buttons()
            new_game_confirmation.update()
        if confirmation.confirm_button.get_pressed() and confirm_new_game:
            start_new_game = True
            confirm_new_game = False
        if confirmation.reject_button.get_pressed() and confirm_new_game:
            confirm_new_game = False

        if start_new_game: # сбрасываем переменные к исходным значениям при новой игре
            respawn_cords[0] ,respawn_cords[1] = 0, 0
            main_character_money = 0
            main_character.attack_damage = 1
            main_character.maximum_health = 5
            main_character.maximum_healings = 6
            main_character.killed_enemies = 0
            main_character.total_damage = 0
            main_character.deaths = 0
            for coin in money_list:
                money_list[money_list.index(coin)][4] = False
            data = upload_data()

            start_jump_altitude, start_jump_from_wall_position, jump, jump_from_wall = data[:4]
            speeds_before_jump, count_fall, counter_fall, game_paused, \
            right, left, condition_damage_effects = data[4:]

            load_music.first_loc_music()
            pygame.mixer.music.play(-1, fade_ms=50)

            slider.kill()
            filler.kill()
            new_game_intro() # заставка начальная
            return

        if not confirm_new_game and not how_to_play: # отрисовка основного главного меню, если не открыты другие разделы
            new_game_button.draw('Новая игра', 40)
            continue_button.draw('Продолжить', 40)
            exit_game_button.draw('Выйти из игры', 40)
            how_to_play_button.draw('Как играть', 30)
            change_bg_button.draw('Сменить задний фон', 30)

            font = pygame.font.Font(FONT, 35)
            text = font.render('Громкость', True, pygame.Color('White'))
            screen.blit(text, (275, 50))

            volume_controller_base.draw(screen)
            pygame.draw.rect(screen, (255, 255, 255), filler.rect, border_radius=10)
            volume_controller_slider.draw(screen)
            volume = pygame.mixer.music.get_volume()

        pygame.display.flip()

# обновление данных при новой игре
def upload_data():
    global main_character, global_cords, money_list, whitelight, lock_script
    start_jump_altitude = -100000
    start_jump_from_wall_position = 0
    jump = False
    jump_from_wall = False
    speeds_before_jump = [0, 0]
    for sprite in trigger_blocks:
        sprite.kill()
    lock_script = triggers.Boss_Wall_Lock()
    lock_script.lock_wall = False
    whitelight = triggers.WhiteLight()

    count_fall = False
    counter_fall = 0
    game_paused = False
    # перемещение в стороны
    right = left = 0

    initialization(money_list, main_character_money)

    if respawn_cords[0] and respawn_cords[1]:
        if size[0] == 2560 and size[1] == 1440:
            main_character.rect.x = respawn_cords[0]
            main_character.rect.y = respawn_cords[1]
        else:
            main_character.rect.x = respawn_cords[0]
            main_character.rect.y = respawn_cords[1] - 300
        global_cords[0], global_cords[1] = 0, 0
    condition_damage_effects = False

    camera.summary_d_x, camera.summary_d_y = 0, 0

    return (start_jump_altitude, start_jump_from_wall_position, jump, jump_from_wall, speeds_before_jump, count_fall,
            counter_fall, game_paused, right, left, condition_damage_effects)


# при смерти обновление всех данных до нуля и перемещение на точку сохранения
def check_dead(camera):
    global start_jump_altitude, start_jump_from_wall_position, jump, jump_from_wall, money_list, global_y, global_x
    global speeds_before_jump, count_fall, counter_fall, game_paused, right, left, condition_damage_effects
    global respawn_cords, main_character_money, lock_script
    if not main_character.health:
        x, y = main_character.rect.x, main_character.rect.y
        lost_money_x, lost_money_y = x + camera.summary_d_x, y + camera.summary_d_y

        for sprite in damage_waves:
            sprite.kill()

        lost_money = main_character.money

        damage_waves.draw(screen)
        data = upload_data()

        start_jump_altitude, start_jump_from_wall_position, jump, jump_from_wall = data[:4]
        speeds_before_jump, count_fall, counter_fall, game_paused, right, left,\
        condition_damage_effects = data[4:]

        main_character.money = 0
        main_character_money = main_character.money
        main_character.healings = 2
        main_character.health = main_character.maximum_health

        main_character.update_heals()
        main_character.update_money()
        main_character.update_healthbar()

        main_character.deaths += 1

        lost_money_coin = Money(lost_money_x, lost_money_y, lost_money)

        load_music.first_loc_music()
        pygame.mixer.music.play(-1, fade_ms=50)

        write_data_to_save()


# главный цикл
if __name__ == '__main__':
    # Перемещаю экран на центр
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    camera = Camera()
    stop_screen = screen.copy()

    data = upload_data()
    load_data_from_save()

    start_jump_altitude, start_jump_from_wall_position, jump, jump_from_wall = data[:4]
    speeds_before_jump, count_fall, counter_fall, game_paused, right, left, condition_damage_effects = data[4:]

    # коэффциент увеличения
    N = 10

    # инициализация окна pygame
    pygame.init()
    pygame.display.set_mode(size)
    # таймер для обновления фпс - 60
    clock = pygame.time.Clock()

    # меню паузы и диалоги
    paused_menu = InGameMenu()
    dialogue_with_sly = False
    dialogue_with_sly_window = Sly_dialogue()
    shop = Sly_shop()

    dialogue_with_elderbug = False
    dialogue_with_elderbug_window = Elderbug_dialogue()

    smooth_surface = pygame.Surface(size)
    smooth_surface.set_alpha(60)

    running = True
    # главное меню
    main_menu(screen)

    # фон
    background_image = load_image('background.png')
    background_image = pygame.transform.scale(background_image, (screen.get_width(), screen.get_height()))

    mouse_clicked_for_dialogues = False  # без этой переменной фразы в диалоге проматываются слишком быстро

    while running:
        # события мыши и клавиатуры
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            # если нажаты клавиши
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                # перемещение
                if keys[pygame.K_d]:
                    if not jump_from_wall:
                        right = 1
                    else:
                        speeds_before_jump[0] = 1
                if keys[pygame.K_a]:
                    if not jump_from_wall:
                        left = -1
                    else:
                        speeds_before_jump[1] = -1
                if keys[pygame.K_h]:
                    main_character.heal()

                # внутриигровое меню
                if keys[pygame.K_ESCAPE]:
                    if not game_paused and not dialogue_with_sly and not dialogue_with_elderbug:
                        game_paused = True
                    elif dialogue_with_sly:
                        dialogue_with_sly = False
                        dialogue_with_sly_window.open_shop = False
                    elif dialogue_with_elderbug:
                        dialogue_with_elderbug = False
                    elif game_paused:
                        game_paused = False
                    write_data_to_save()

                # взаимодействие
                if keys[pygame.K_e]:
                    for sprite in saving_points:
                        if sprite.can_save:
                            respawn_cords[0], respawn_cords[1] = SAVING_POINTS_CORDS[sprite.point_id]
                            global_cords[0], global_cords[1] = 0, 0
                            update_map_after_save(camera)
                            write_data_to_save()
                    for sprite in npcs:
                        if sprite.can_talk and type(sprite) == Sly:
                            dialogue_with_sly = True
                        if sprite.can_talk and type(sprite) == Elderbug:
                            dialogue_with_elderbug = True

                # при нажатии на пробел - прыжок
                if event.key == pygame.K_SPACE and (main_character.get_hor() or main_character.get_ver()):
                    start_jump_altitude = main_character.rect.y + 1
                    # проверка на зацепление за текстуры(был баг без этого)
                    main_character.rect.y -= 2
                    if main_character.get_ver() and main_character.get_hor():
                        main_character.rect.x += 1
                        if main_character.get_ver():
                            main_character.rect.x -= 2
                    # объявляю прыжок
                    jump = True
                    if main_character.get_ver():  # если есть касани вертикально стены, то объявляю прыжок от стены
                        jump_from_wall = True
                        speeds_before_jump = [0, 0]
                        main_character.rect.x -= 1
                        # запоминаю скорости
                        if main_character.get_ver():
                            right = 1
                            left = 0
                        else:
                            right = 0
                            left = -1

                        main_character.rect.x += 1
                        start_jump_from_wall_position = main_character.rect.x
                    else:
                        jump_from_wall = False

            # если отпускается какая-либо клавиша
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_d:
                    right = 0
                if event.key == pygame.K_a:
                    left = 0

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not main_character.attack:
                    main_character.start_attacking()
                mouse_clicked_for_dialogues = True
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_clicked_for_dialogues = False


        # перемещение в стороны
        move_hor = right + left
        if main_character.get_hor() or main_character.get_ver():
            count_fall = False

        if not main_character.get_hor() and not jump and not count_fall:
            count_fall = True
            counter_fall = 0

        # определение скорости падения
        if main_character.get_ver() and not jump:

            fall_speed = 15 * N + counter_fall
            count_fall = False
            counter_fall = 0
            main_character.cur_sheet = SLIDING_SHEET

        elif not jump:
            fall_speed = 45 * N + counter_fall
        if jump:
            # при прыжке, на самой верхней точке скорость меньше
            fall_speed = -(25 * N - start_jump_altitude + main_character.rect.y) * 7
            if fall_speed > -20:
                counter_fall = 0
                count_fall = True
                jump = False
                fall_speed = 45 * N
        # если совершается прыжок от стены
        if jump_from_wall:
            # если уже далеко от стены
            if abs(main_character.rect.x - start_jump_from_wall_position) > 2 * N:
                jump_from_wall = False
                right, left = speeds_before_jump
                speeds_before_jump = [0, 0]

        camera.update()
        # отрисовываю все группы спрайтов
        background.draw(screen)
        platforms.draw(screen)
        platforms.update()
        money.draw(screen)
        money.update()
        character.draw(screen)
        enemies.update()
        enemies.draw(screen)

        npcs.update()
        npcs.draw(screen)

        saving_points.update()
        saving_points.draw(screen)

        trigger_blocks.update()
        trigger_blocks.draw(screen)

        knight.draw(screen)

        # пауза
        if game_paused:
            screen.blit(smooth_surface, (0, 0))
            menu.draw(screen)
            InGameMenu.draw_menu_buttons(paused_menu)

            font = pygame.font.Font(FONT, 35)
            text = font.render(f'Урон от атаки: {main_character.attack_damage}', 1, pygame.Color('white'))
            screen.blit(text, (40, screen.get_height() - 200))

            text = font.render(f'Максимальное здоровье: {main_character.maximum_health}', 1, pygame.Color('white'))
            screen.blit(text, (40, screen.get_height() - 150))

            text = font.render(f'Максимум лечений: {main_character.maximum_healings}', 1, pygame.Color('white'))
            screen.blit(text, (40, screen.get_height() - 100))

            if paused_menu.resume_button.get_pressed():
                game_paused = False
            if paused_menu.back_to_main_menu_button.get_pressed():
                game_paused = False
                dialogue_with_sly = False
                main_character_money = main_character.money
                write_data_to_save()
                main_menu(screen)

        # диалог с торговцем
        if dialogue_with_sly:
            screen.blit(smooth_surface, (0, 0))

            # сам диалог
            if not dialogue_with_sly_window.open_shop:
                sly_dialogue.draw(screen)
                dialogue_with_sly_window.draw_buttons()

                if mouse_clicked_for_dialogues:
                    if dialogue_with_sly_window.close_dialogue_button.get_pressed():
                        dialogue_with_sly = False
                    if dialogue_with_sly_window.next_phrase_button and dialogue_with_sly_window.next_phrase_button.get_pressed():
                        dialogue_with_sly_window.current_phrase += 1
                    if dialogue_with_sly_window.shop_button and dialogue_with_sly_window.shop_button.get_pressed():
                        dialogue_with_sly_window.open_shop = True

                    mouse_clicked_for_dialogues = False
            else:
                # магазин
                sly_shop.draw(screen)
                shop.draw_buttons()

                font = pygame.font.Font(FONT, 30)
                text = font.render(f'Ваши деньги: {main_character.money}', 1, pygame.Color('white'))
                screen.blit(text, (screen.get_width() // 2 - text.get_width() // 2, 40))
                if shop.close_button.get_pressed():
                    dialogue_with_sly_window.open_shop = False

                if mouse_clicked_for_dialogues:
                    if shop.buy_attack_improvement.get_pressed():
                        if main_character.money >= shop.damage_improvement_price:
                            main_character.money -= shop.damage_improvement_price
                            main_character.attack_damage += 1
                    if shop.buy_maximum_health_improvement.get_pressed():
                        if main_character.money >= shop.maximum_health_improvement_price:
                            main_character.money -= shop.maximum_health_improvement_price
                            main_character.maximum_health += 1
                    if shop.buy_maximum_healings_improvement.get_pressed():
                        if main_character.money >= shop.maximum_healings_improvement_price:
                            main_character.money -= shop.maximum_healings_improvement_price
                            main_character.maximum_healings += 1

                    mouse_clicked_for_dialogues = False

                sly_shop.update()

            sly_dialogue.update()

        # диалог со старцем
        if dialogue_with_elderbug:
            screen.blit(smooth_surface, (0, 0))

            elderbug_dialogue.draw(screen)
            dialogue_with_elderbug_window.draw_buttons()

            if mouse_clicked_for_dialogues:
                if dialogue_with_elderbug_window.close_dialogue_button.get_pressed():
                     dialogue_with_elderbug = False
                if dialogue_with_elderbug_window.next_phrase_button and \
                        dialogue_with_elderbug_window.next_phrase_button.get_pressed():
                    dialogue_with_elderbug_window.current_phrase += 1

                mouse_clicked_for_dialogues = False
            elderbug_dialogue.update()

        # конец игры
        if whitelight.intersect_with_knight:
            respawn_cords[0], respawn_cords[1] = 0, 0
            end_game.end_game(main_character.killed_enemies, main_character.total_damage, main_character.deaths)
            main_menu(screen)
        # эффекты урона
        elif not condition_damage_effects:
            jump = main_character.update(move_hor, jump, move_speed, fall_speed)
            enemies.update()
        else:
            main_character.update_damage_resistant()

        # ускорение при падении
        if count_fall:
            counter_fall += 6
            if counter_fall == 6:
                main_character.cur_sheet = FALLING_SHEET
                main_character.cur_frame = 0
        elif not move_hor and main_character.get_hor():
            main_character.cur_sheet = STANDING_SHEET
            counter_fall = 0
            count_fall = False
        else:
            main_character.cur_sheet = RUNNING_SHEET

        # при прыжке
        if jump:
            main_character.cur_sheet = JUMPING_SHEET

        # при атаке
        if main_character.attack:
            main_character.cur_sheet = ATTACKING_SHEET

        # остановка экрана на полсекунды при получении урона
        if main_character.stop_screen and not condition_damage_effects:
            stop_screen = screen.copy()
            condition_damage_effects = True
        if not main_character.stop_screen:
            condition_damage_effects = False

        # проверка смерти
        check_dead(camera)

        if main_character.stop_screen:
            counter_fall = 0
            screen.blit(stop_screen, (0, 0))

        pygame.display.flip()
        clock.tick(fps)
    # выход программы
    write_data_to_save()
    pygame.quit()
