import pygame
import os
import sys
from screeninfo import get_monitors
from data import cords, global_cords, FONT


def load_image(name, colorkey=None):
    # путь до изображения
    fullname = os.path.join('..\data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()
    image = pygame.image.load(fullname)
    # создание прозрачности изображению
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


# эффект после получения урона
class DamageWaves(pygame.sprite.Sprite):
    def __init__(self, direction_x, direction_y):
        super().__init__(damage_waves)

        # направление движения эффектов относительно главного героя
        self.direction_x = direction_x
        self.direction_y = direction_y

        # картинка
        self.image = pygame.transform.flip(load_image('effects\damage_waves_1.png'), direction_x, direction_y)
        self.image = pygame.transform.scale(self.image, (300, 300))
        self.rect = self.image.get_rect()

        # координаты относительно главного героя
        x = main_character.rect.x + main_character.rect.w // 2 - self.rect.w * ((direction_x + 1) % 2)
        y = main_character.rect.y + main_character.rect.h // 2 - self.rect.h * direction_y

        self.rect.x = x
        self.rect.y = y

    # перемещение
    def update(self):
        # пока действует невосприятие урона у главного героя перемещение в сторону от гг
        if main_character.resist_count:
            if main_character.resist_count > 25:
                self.rect.x += 2400 / fps if self.direction_x else -2400 / fps
                self.rect.y -= 2400 / fps if self.direction_y else -2400 / fps
                self.image.set_alpha(80 - main_character.resist_count, False)


# базовый класс для перемещающихся объектов
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, graphics, *groups):
        # всякие кординаты
        super().__init__(character, *groups)
        # размеры спрайта
        w, h = screen.get_size()
        x *= N
        y *= N

        # кадры для анимации
        self.frames = []
        # графика
        for i in range(len(graphics)):
            sheet, columns, rows = graphics[i]
            self.cut_sheet(sheet, columns, rows, x, y)

        # размеры объекта и неободимые для работы атрибуты
        self.cur_frame = 0
        self.cur_sheet = 0
        self.image = self.frames[self.cur_sheet][self.cur_frame]
        self.rect = pygame.rect.Rect(x, y, 78, 130)
        self.rect = self.rect.move(x + w // 2 + 20, y + h // 2)
        self.count_flip = 0

    # создание анимации
    def cut_sheet(self, sheet, columns, rows, x, y):
        # при некоторых условиях количество кадров в короткой анимации увеличивается
        res = []
        if len(self.frames) == 1 and type(self) == Knight:
            count = 2
        elif len(self.frames) == 1 and type(self) == Crawlid:
            count = 4
        elif len(self.frames) == 5 and type(self) == Knight:
            count = 2
        elif type(self) == Sly:
            count = 6
        elif type(self) == Elderbug:
            count = 6
        else:
            count = 1

        # квадрат по картинке
        self.rect = pygame.Rect(x, y, sheet.get_width() // columns,
                                sheet.get_height() // rows)
        # у класса рыцаря обрезается картинка
        if type(self) == Knight:
            if len(self.frames) == 4:
                z = 1.6
            else:
                z = 1
            x = 1
        else:
            z = 0
            x = 0
        # обрезка кадров
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i + 20 * x, self.rect.h * j)
                image = sheet.subsurface(pygame.Rect(
                    frame_location, (self.rect.w - 40 * z, self.rect.h)))
                for _ in range(count):
                    res.append(image)

        self.frames.append(res)

    # возвращает истину, если объект пересекается с горизонтальными платформами
    def get_hor(self):
        return pygame.sprite.spritecollideany(self, horizontal_platforms)

    # возвращает истину, если объект пересекается с вертикальными платформами
    def get_ver(self):
        return pygame.sprite.spritecollideany(self, vertical_platforms)


# спрайт главного героя
class Knight(Character):
    def __init__(self, x, y, graphics, *groups):
        super().__init__(x, y, graphics, *groups)
        # здоровье и лечилки, деньги и хэпулина
        self.health = 5
        self.maximum_health = 5
        self.healings = 6
        self.maximum_healings = 6
        self.money = 0

        # картинки монет, сердечек и денег
        heart_image = load_image('heart.png')
        heal_image = load_image('heal.png')
        money_image = load_image('money.png')
        self.heart_image = pygame.transform.scale(heart_image, (100, 60))
        self.heal_image = pygame.transform.scale(heal_image, (60, 60))
        self.money_image = pygame.transform.scale(money_image, (60, 60))

        # необходимые переменные
        self.non_damage_count = 0
        self.damage = False
        self.old_move_hor = 0

        self.attack_radius = 100
        self.attack_damage = 1
        self.can_damage = False
        self.view_direcion = 0

        self.resist = False
        self.resist_count = 0
        self.stop_screen = False

        self.drop_direction = 1

        self.attack_count = 0
        self.attack = False

        self.killed_enemies = 0
        self.total_damage = 0
        self.deaths = 0

    # рисование
    def update(self, *args):
        move_hor, jump, move_speed, fall_speed = args
        x, y = self.rect.x, self.rect.y
        if move_hor:
            self.view_direcion = move_hor // abs(move_hor)

        if move_hor < 0:
            # если движение влево, то изначально значение отрицательно
            r = range(-(move_hor * move_speed) // fps)
        else:
            r = range((move_hor * move_speed) // fps)
        for _ in r:
            # начально условие
            condition = self.get_ver()
            # потом двигаю персонажа
            self.rect.x += move_hor
            # если условие не поменялось, то возвращаю обратно, и в любом случаю прекращаю движение
            if self.get_ver():
                if condition:
                    self.rect.x -= move_hor
                jump = False
                break

        if fall_speed:
            # падение и скольжение
            if fall_speed < 0:
                # отрицательно при прыжке
                r = range(-(fall_speed // fps))
            else:
                r = range(fall_speed // fps)
            for _ in r:
                condition = self.get_hor()
                self.rect.y += fall_speed // abs(fall_speed)
                if self.get_ver():
                    if jump:
                        self.rect.y += 3
                        jump = False
                        break
                    if condition:
                        self.rect.y -= fall_speed // abs(fall_speed)
                    break

        # обновление всех условий
        self.update_healthbar()
        self.update_heals()
        self.update_money()
        self.update_damage_resistant()
        self.update_effects()
        self.update_attack_condition()

        # счётки кадров и обновление
        if self.count_flip == 3:
            # счётчик при атаке
            if self.attack:
                self.attack_count += 1
            self.count_flip = 0
            # смена картинки
            if move_hor == 0 and self.cur_sheet == 0:
                self.cur_frame = 0
            else:
                self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.cur_sheet])
            self.image = self.frames[self.cur_sheet][self.cur_frame]
            # разворот картинки взависимости от направления движения гг
            if move_hor == -1 or self.old_move_hor == -1:
                self.image = pygame.transform.flip(self.image, True, False)

            self.mask = pygame.mask.from_surface(self.image)

        self.count_flip += 1
        if move_hor:
            self.old_move_hor = move_hor

        # изменение отслеживания координат персонажа
        global_cords[0] += (self.rect.x - x)
        global_cords[1] += (self.rect.y - y)

        # изменения координат фона
        if self.rect.x > x:
            background_image.rect.x -= 0.5
        elif self.rect.x < x:
            background_image.rect.x += 0.5

        return jump

    # обновление эффектов
    def update_effects(self):
        if self.resist:
            # обновление эффектов
            damage_waves.update()
            damage_waves.draw(screen)
        else:
            # если вышло время, то удаляю эффекты
            for sprite in damage_waves:
                sprite.kill()
            damage_waves.draw(screen)

    # обновление шкалы здоровья
    def update_healthbar(self):
        for i in range(self.health):
            x = 50 + i * 30
            y = 20
            screen.blit(self.heart_image, (x, y))
        if self.damage:
            self.non_damage_count += 2 / fps
        if self.non_damage_count > 2:
            self.damage = False
            self.non_damage_count = 0

    # лечение главного героя
    def heal(self):
        if self.healings > 0 and self.health < self.maximum_health:
            self.health += 1
            self.healings -= 1

    # обновление количества здоровья и отрисовка
    def update_heals(self):
        screen.blit(self.heal_image, (60, 80))
        font = pygame.font.Font(FONT, 40)
        text = font.render(str(self.healings), True, pygame.Color('White'))
        screen.blit(text, (130, 80))

    # получение монет
    def add_money(self, amount):
        self.money += amount

    # обновление отображения денег
    def update_money(self):
        screen.blit(self.money_image, (60, 140))
        font = pygame.font.Font(FONT, 40)
        text = font.render(str(self.money), True, pygame.Color('White'))
        screen.blit(text, (130, 140))

    # атака
    def attacking(self):
        # в зависимости от направления движения персонажа
        if self.view_direcion == 1:
            attacking_rect = pygame.Rect(self.rect.topright[0], self.rect.y, self.attack_radius, self.rect.width)
        else:
            attacking_rect = pygame.Rect(self.rect.x - self.attack_radius, self.rect.y,
                                         self.attack_radius, self.rect.height)

        # всем, кто находится в радиусе атаки наносится урон
        for sprite in enemies:
            if attacking_rect.colliderect(sprite.rect):
                self.total_damage += self.attack_damage
                sprite.get_damage(self.attack_damage)

    # создание условий для начала атаки
    def start_attacking(self):
        self.cur_frame = 0
        self.cur_sheet = 5

        self.attack_count = 0
        self.attack = True

    # обновление условий для атаки
    def update_attack_condition(self):
        if self.attack and self.attack_count == 5 and self.count_flip == 1:
            self.attacking()
        if self.attack and self.attack_count == 10:
            self.cur_sheet = 0
            self.cur_frame = 0
            self.attack_count = 0
            self.attack = False

    # получение урона
    def get_damage(self, damage, enemy):
        if not self.resist:
            # нужные переменные
            self.health -= damage
            self.resist = True
            self.stop_screen = True

            # эффекты получения урона
            DamageWaves(0, 0)
            DamageWaves(0, 1)
            DamageWaves(1, 0)
            DamageWaves(1, 1)

            # направление отбрасывания
            damage_waves.draw(screen)
            if enemy.rect.x < self.rect.x:
                self.drop_direction = -1
            else:
                self.drop_direction = 1

    # обновление защиты от урона
    def update_damage_resistant(self):
        if self.resist:
            self.resist_count += 1

            # при некоторых значения счётчика происходят нужные события:
            if self.resist_count == 100:  # завершение защиты
                self.resist = False
                self.resist_count = 0
            if self.resist_count == 25:  # завершение стоп-экрана
                self.stop_screen = False
            if 50 > self.resist_count > 25:  # отбрасывание
                self.rect.y -= 800 / fps
                if self.get_ver():
                    self.rect.y += 800 / fps
                self.rect.x -= (300 / fps) * self.drop_direction
                if self.get_hor():
                    self.rect.x += (300 / fps) * self.drop_direction


# класс врага
class Enemy(Character):
    def __init__(self, x, y, graphics, *groups):
        super().__init__(x, y, graphics, *groups)
        # здоровье, деньги и системная переменная
        self.hp = 3
        self.dropping_money = 10
        self.reverse_count = 0

    # получение урона
    def get_damage(self, damage):
        self.hp -= damage

    # выпадение денег
    def drop_money(self):
        Money(self.rect.x, self.rect.y, self.dropping_money)

    # возвращает истину, если маски гг и врага пересекаются
    def intersect_with_knight(self):
        return pygame.sprite.collide_mask(self, main_character)


# муха
class Vengefly(Enemy):
    def __init__(self, x, y, graphics, *groups):
        super().__init__(x, y, graphics, *groups)
        # здоровье, деньги, направление
        self.hp = 1
        self.dropping_money = 4
        self.direction = -1

        # всякие штуки для работы
        self.count_reverse = 0
        self.rect = pygame.rect.Rect(self.rect.x, self.rect.y, 120, 120)
        self.cur_sheet = self.cur_frame = 0
        self.start_x = self.rect.x
        # скорость
        self.speed = 2

        # преследование и радиус атаки
        self.chase = False
        self.agr_radius = 650

    # обновление
    def update(self):
        # нужда разворота
        need_reverse = False
        if self.direction == 1 and self.rect.x > main_character.rect.x or \
                self.direction == -1 and self.rect.x < main_character.rect.x:
            need_reverse = True

        # при нужде разворота
        if need_reverse:
            self.direction *= -1
            self.cur_sheet = 1
            self.count_reverse = 1
            self.cur_frame = 0

        # завершение разворота
        if self.cur_sheet == 1 and self.count_reverse == 3:
            self.count_reverse = 0
            self.count_flip = 0
            self.cur_sheet = self.cur_frame = 0

        # счётчик смены кадров
        if self.count_flip == 10:
            self.count_flip = 0
            # смена картинки
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.cur_sheet])
            self.image = self.frames[self.cur_sheet][self.cur_frame]
            # при смене направления
            if self.direction == 1:
                self.image = pygame.transform.flip(self.image, True, False)

            self.mask = pygame.mask.from_surface(self.image)

            if self.count_reverse:
                self.count_reverse += 1

        # преследование
        if ((self.rect.x - main_character.rect.x) ** 2 + (self.rect.y - main_character.rect.y) ** 2) ** 0.5 <= self.agr_radius:
            self.chase = True

        # преследование
        if self.chase:
            if self.rect.x < main_character.rect.x:
                self.rect.x += self.speed
                if self.get_ver():
                    self.rect.x -= self.speed * 2
            else:
                self.rect.x -= self.speed
                if self.get_ver():
                    self.rect.x += self.speed * 2

            if self.rect.y < main_character.rect.y:
                self.rect.y += self.speed / 2
                if self.get_hor():
                    self.rect.y -= self.speed
            else:
                self.rect.y -= self.speed / 2
                if self.get_hor():
                    self.rect.y += self.speed

        self.count_flip += 1

        self.check_needs_of_damage()

        # умертвление :(
        if self.hp <= 0:
            main_character.killed_enemies += 1
            self.kill()
            self.drop_money()

    # при соприкоснавении с гг он получает урон
    def check_needs_of_damage(self):
        if self.intersect_with_knight():
            main_character.get_damage(1, self)


# ползучий
class Crawlid(Enemy):
    def __init__(self, x, y, distance, direction, graphics, *groups):
        super().__init__(x, y, graphics, *groups)

        # урон, здоровье и деньги
        self.hp = 2
        self.dropping_money = 3
        self.direction = direction
        self.count_reverse = 0

        # нужные переменные
        self.rect = pygame.rect.Rect(self.rect.x, self.rect.y, 100, 85)
        self.cur_sheet = self.cur_frame = 0
        self.first_update = True
        self.start_x = self.rect.x
        self.distance = distance * N

    # обновление
    def update(self):
        # нужда разворота
        need_reverse = False
        if abs(self.rect.x - self.start_x) >= self.distance:
            if self.rect.x < self.start_x:
                self.rect.x += 2
            else:
                self.rect.x -= 2
            need_reverse = True

        # при нужде разворота
        if need_reverse:
            self.direction *= -1
            self.cur_sheet = 1
            self.count_reverse = 1
            self.cur_frame = 0

        # завершение разворота
        if self.cur_sheet == 1 and self.count_reverse == 3:
            self.count_reverse = 0
            self.count_flip = 0
            self.cur_sheet = self.cur_frame = 0

        # счётчик кадров
        if self.count_flip == 10:
            self.count_flip = 0
            # смена картинки
            self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.cur_sheet])
            self.image = self.frames[self.cur_sheet][self.cur_frame]
            # разворот
            if self.direction == 1:
                self.image = pygame.transform.flip(self.image, True, False)

            self.mask = pygame.mask.from_surface(self.image)

            if self.count_reverse:
                self.count_reverse += 1

        if self.cur_sheet == 0:
            self.rect.x += self.direction

        self.count_flip += 1

        self.check_needs_of_damage()

        # умертвление
        if self.hp <= 0:
            main_character.killed_enemies += 1
            self.kill()
            self.drop_money()

    # при взаимодействии с гг он получает урон
    def check_needs_of_damage(self):
        if self.intersect_with_knight():
            main_character.get_damage(1, self)


# торговец
class Sly(Character):
    def __init__(self, x, y, graphics):
        super().__init__(x, y, graphics, npcs)
        self.cur_sheet = self.cur_frame = 0
        self.can_talk = False

    # обновление
    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.cur_sheet])
        self.image = self.frames[self.cur_sheet][self.cur_frame]
        if pygame.sprite.spritecollideany(self, knight):
            self.can_talk = True
            font = pygame.font.Font(FONT, 30)
            text = font.render('Поговорить(E)', 1, pygame.Color('white'))
            screen.blit(text, (self.rect.x + self.rect.w // 2 - text.get_width() // 2, self.rect.y - text.get_height()))
        else:
            self.can_talk = False


# старец, повествующий легенду
class Elderbug(Character):
    def __init__(self, x, y, graphics):
        super().__init__(x, y, graphics, npcs)
        self.cur_sheet = self.cur_frame = 0
        self.can_talk = False

    # обновление
    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames[self.cur_sheet])
        self.image = self.frames[self.cur_sheet][self.cur_frame]
        if pygame.sprite.spritecollideany(self, knight):
            self.can_talk = True
            font = pygame.font.Font(FONT, 30)
            text = font.render('Поговорить(E)', 1, pygame.Color('white'))
            screen.blit(text, (self.rect.x + self.rect.w // 2 - text.get_width() // 2, self.rect.y - text.get_height()))
        else:
            self.can_talk = False


# деньги
class Money(pygame.sprite.Sprite):
    def __init__(self, x, y, amount, id=None):
        super().__init__(money)
        self.amount = amount
        image = load_image('money.png')
        self.image = pygame.transform.scale(image, (40, 40))
        self.id = id
        if self.id:
            self.rect = pygame.Rect(x * N + screen.get_width() // 2, y * N + screen.get_height() // 2,
                                    self.image.get_width(), self.image.get_height())
        else:
            self.rect = pygame.Rect(x, y, self.image.get_width(), self.image.get_height())

    def update(self):
        if pygame.sprite.spritecollideany(self, knight):
            main_character.add_money(self.amount)
            if self.id:
                money_list[self.id - 1][4] = True
            self.kill()


# класс стен
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, a, b, *groups):
        w, h = screen.get_size()  # ширина и высота окна
        self.a, self.b = a * N, b * N
        x *= N
        y *= N
        super().__init__(*groups)
        # кординаты и картинка. Картинка для последующей обработки столкновений
        self.cords = (w // 2 + x, h // 2 + y, self.a, self.b)
        self.image = pygame.Surface((self.a, self.b))

        # начальное положение. Чтобы поменять self.rect.x = 100 или self.rect.y = 200
        self.rect = pygame.Rect(w // 2 + x, h // 2 + y, self.a, self.b)
        pygame.draw.rect(self.image, 'black', self.rect)


# точка сохранения
class Saving_point(pygame.sprite.Sprite):
    def __init__(self, x, y, point_id):
        super().__init__(saving_points)
        image = load_image('saving_point.png', -1)
        self.image = pygame.transform.scale(image, (50, 50))
        self.rect = pygame.Rect(x * N + screen.get_width() // 2, y * N + screen.get_height() // 2,
                                self.image.get_width(), self.image.get_height())
        # возможность сохранения и ай ди точки
        self.can_save = False
        self.point_id = point_id

    # обновление
    def update(self):
        if self.rect.colliderect(main_character):
            font = pygame.font.Font(FONT, 30)
            text = font.render('Установить точку возрождения(E)', 0, pygame.Color('white'))
            screen.blit(text, (self.rect.x + self.rect.w // 2 - text.get_width() // 2, self.rect.y - text.get_height()))
            self.can_save = True
        else:
            self.can_save = False


# задний фон
class Background(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(background)
        background_image = load_image('background.png')
        self.image = pygame.transform.scale(background_image, (screen.get_width() * 5, screen.get_height()))
        self.rect = self.image.get_rect()
        self.rect.x = -screen.get_width() * 2.5


# инициализация всего
def initialization(money_list, main_character_money):
    global main_character, platforms, money, vertical_platforms, horizontal_platforms, enemies, saving_points, mouthwing
    background = pygame.Surface(size)
    for group in [platforms, money, vertical_platforms, horizontal_platforms, enemies, saving_points, npcs]:
        for sprite in group:
            sprite.kill()
            group.clear(screen, background)
            group.draw(screen)

    # главный герой
    images = [(load_image('knight\knight_standing.png'), 1), (load_image('knight\knight_running.png'), 6),
              (load_image('knight\knight_falling.png'), 7),
              (load_image('knight\knight_in_jump.png', 'white'), 1),
              (load_image('knight\knight_sliding.png'), 4), (load_image('knight\knight_attacking.png'), 5)]
    graphics_knight = []
    for image, row in images:
        k = 130 / image.get_height()
        scaled_image = pygame.transform.scale(image, (
            image.get_width() * k, image.get_height() * k))
        graphics_knight.append((scaled_image, row, 1))
    # главный герой
    if main_character is None:
        main_character = Knight(0, 0, graphics_knight, knight)
    else:
        main_character.rect.y -= 300
        main_character.rect.x += 50
        main_character.health = main_character.maximum_health
        main_character.healings = main_character.maximum_healings
        main_character.money = main_character_money

    # торговец
    sly_graphics = []
    sly_images = [(load_image('npcs\sly.png'), 6)]
    for image, row in sly_images:
        k = 120 / image.get_height()
        scaled_image = pygame.transform.scale(image, (
            image.get_width() * k, image.get_height() * k))
        sly_graphics.append((scaled_image, row, 1))
    Sly(300, 506.5, sly_graphics)

    # старец
    elderbug_graphics = []
    elderbug_images = [(load_image('npcs\elderbug.png', -1), 6)]
    for image, row in elderbug_images:
        k = 200 / image.get_height()
        scaled_image = pygame.transform.scale(image, (
            image.get_width() * k, image.get_height() * k))
        elderbug_graphics.append((scaled_image, row, 1))
    Elderbug(-50, 340, elderbug_graphics)

    # ползучий
    crawlids_graphics = []
    crawlids_images = [(load_image('crawlid\\crawlid_walking.png'), 4), (load_image('crawlid\\crawlid_reversing.png'), 2),
                       (load_image('crawlid\\crawlid_diying.png'), 3)]
    for image, row in crawlids_images:
        k = 80 / image.get_height()
        scaled_image = pygame.transform.scale(image, (
            image.get_width() * k, image.get_height() * k))
        crawlids_graphics.append((scaled_image, row, 1))

    for x, y, d, direction in crawlid_cords:
        Crawlid(x, y, d, direction, crawlids_graphics, enemies)

    vengefly_graphics = []
    vengefly_images = [(load_image('vengefly\\vengefly_flying.png'), 5),
                       (load_image('vengefly\\vengefly_turning.png'), 2),
                       (load_image('vengefly\\vengefly_diying.png'), 3)]

    # муха
    for image, row in vengefly_images:
        k = 120 / image.get_height()
        scaled_image = pygame.transform.scale(image, (
            image.get_width() * k, image.get_height() * k))
        vengefly_graphics.append((scaled_image, row, 1))

    for x, y in vengefly_cords:
        Vengefly(x, y, vengefly_graphics, enemies)

    # точки сохранения
    points = [(-185, 685, '1'), (750, 850, '2'), (820, 670, '3'), (2300, 2305, '4')]
    for el in points:
        x, y, id = el
        Saving_point(x, y, id)

    # монеты
    list_of_money = money_list
    for coin in list_of_money:
        x, y, value, id, collected = coin
        if not collected:
            Money(x, y, value, id)

    # платформы
    for cord in cords:
        x, y, a, b = cord
        Platform(x + 1 / N, y, a - 2 / N, b, platforms, horizontal_platforms)
        Platform(x, y + 1 / N, a, b - 2 / N, platforms, vertical_platforms)


def update_map_after_save(camera):
    global main_character, enemies

    for sprite in enemies:
        sprite.kill()

    crawlids_graphics = []
    crawlids_images = [(load_image('crawlid\crawlid_walking.png'), 4), (load_image('crawlid\crawlid_reversing.png'), 2),
                       (load_image('crawlid\crawlid_diying.png'), 3)]
    for image, row in crawlids_images:
        k = 80 / image.get_height()
        scaled_image = pygame.transform.scale(image, (
            image.get_width() * k, image.get_height() * k))
        crawlids_graphics.append((scaled_image, row, 1))

    for x, y, d, direction in crawlid_cords:
        Crawlid(x, y, d, direction, crawlids_graphics, enemies)

    vengefly_graphics = []
    vengefly_images = [(load_image('vengefly\\vengefly_flying.png'), 5),
                       (load_image('vengefly\\vengefly_turning.png'), 2),
                       (load_image('vengefly\\vengefly_diying.png'), 3)]

    for image, row in vengefly_images:
        k = 120 / image.get_height()
        scaled_image = pygame.transform.scale(image, (
            image.get_width() * k, image.get_height() * k))
        vengefly_graphics.append((scaled_image, row, 1))

    for x, y in vengefly_cords:
        Vengefly(x, y, vengefly_graphics, enemies)

    for sprite in enemies:
        sprite.rect.x -= camera.summary_d_x
        sprite.rect.y -= camera.summary_d_y
        sprite.start_x = sprite.rect.x

    main_character.health = main_character.maximum_health
    main_character.healings = main_character.maximum_healings


# получаю параметры монитора, по ним делаю окно игры
monitor = get_monitors()[0]
size = monitor.width, monitor.height

# сам экран
screen = pygame.display.set_mode(size)
# частота обноления экрана
fps = 60

# группы спрайтов
platforms = pygame.sprite.Group()
character = pygame.sprite.Group()
knight = pygame.sprite.Group()
horizontal_platforms = pygame.sprite.Group()
vertical_platforms = pygame.sprite.Group()
enemies = pygame.sprite.Group()
npcs = pygame.sprite.Group()
sly_shop = pygame.sprite.Group()
sly_dialogue = pygame.sprite.Group()
elderbug_dialogue = pygame.sprite.Group()
menu = pygame.sprite.Group()
new_game_confirmation = pygame.sprite.Group()
money = pygame.sprite.Group()
saving_points = pygame.sprite.Group()
damage_waves = pygame.sprite.Group()
trigger_blocks = pygame.sprite.Group()
background = pygame.sprite.Group()
N = 10
main_character = None
mouthwing = None

# кординаты
money_list = [[-180, 120, 50, 1, False], [75, 350, 50, 2, False],  [720, 720, 50, 3, False]]
crawlid_cords = [(-10, 61, 45, -1), (25, 181, 45, -1), (25, 346, 45, -1), (100, 396, 100, -1),
                 (150, 396, 100, -1), (200, 396, 100, 1), (360, 386, 50, -1), (310, 428.5, 40, 1), (355, 306, 25, 1),
                 (355, 536, 25, 1), (300, 536, 50, -1), (5, 466, 50, 1)]
vengefly_cords = [(0, 20), (150, 320), (230, 330), (175, 370), (130, 360), (290, 365), (355, 350), (335, 290),
                  (-25, 420), (10, 450)]
initialization(money_list, 0)
background_image = Background()
