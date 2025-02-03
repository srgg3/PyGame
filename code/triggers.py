from graphics import Platform, platforms, vertical_platforms, trigger_blocks, character, screen, load_image, enemies, \
    Vengefly, main_character, background_image, N
from data import global_cords, respawn_cords
import pygame
from load_music import battle_music, first_loc_music


class Boss_Wall_Lock(pygame.sprite.Sprite): # класс-триггер, который при пересечении с главным героем закрывает проход к боссу и спавнит этого босса
    def __init__(self):
        super().__init__(trigger_blocks)
        self.rect = pygame.rect.Rect(1050 * N, 900 * N, 100 * N, 200 * N)
        self.image = pygame.surface.Surface((self.rect.w, self.rect.y))
        self.image.set_alpha(0)
        self.lock_wall = False
        self.boss = None
        self.block_wall_exist = False

    def update(self):
        if not self.block_wall_exist:
            self.block_wall = Platform(1050, 1200, 20, 100, platforms, vertical_platforms)
            platforms.draw(screen)
            self.block_wall_exist = True
        if pygame.sprite.spritecollideany(self, character) and not self.lock_wall:
            self.lock_wall = True
            x, y, a, b = -40, -100, 10, 200
            self.block_wall_boss = Platform(x, y, a, b, platforms, vertical_platforms)
            platforms.draw(screen)

            mouthwing_graphics = []
            mouthwing_images = [(load_image('mouthwing\\mouthwing_flying.png'), 4),
                                (load_image('mouthwing\\mouthwing_turning.png'), 2),
                                (load_image('mouthwing\\mouthwing_diying.png'), 2)]

            for image, row in mouthwing_images:
                k = 400 / image.get_height()
                scaled_image = pygame.transform.scale(image, (
                    image.get_width() * k, image.get_height() * k))
                mouthwing_graphics.append((scaled_image, row, 1))

            mouthwing = Vengefly(30, -30, mouthwing_graphics, enemies)
            mouthwing.rect.h = 400
            mouthwing.rect.w = 500
            mouthwing.agr_radius = 1000
            mouthwing.hp = 20
            mouthwing.dropping_money = 100
            mouthwing.speed = 1
            self.boss = mouthwing
            battle_music()
            pygame.mixer.music.play(-1, fade_ms=50)

        if self.boss is not None:
            if self.boss.hp == 0:
                self.boss.hp = 1
                first_loc_music()
                pygame.mixer.music.play(-1, fade_ms=50)

                trigger_blocks.remove(self)
                self.block_wall.kill()
                self.block_wall_boss.kill()
                platforms.draw(screen)


class WhiteLight(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__(trigger_blocks)
        self.image = load_image('effects\\white_light.png')
        self.image = pygame.transform.scale(self.image, (20 * N, 30 * N))
        self.image = pygame.transform.flip(self.image, True, False)
        self.rect = pygame.rect.Rect(1460 * N + screen.get_width() // 2, 650 * N + screen.get_height() // 2, 20 * N, 30 * N)
        self.intersect_with_knight = False

    def update(self):
        if pygame.sprite.spritecollideany(self, character):
            self.intersect_with_knight = True
        else:
            self.intersect_with_knight = False



