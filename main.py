import pygame
import random

# Инициализация Pygame
pygame.init()

# Константы
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
TILE_SIZE = 100
FPS = 60
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLACK = (0, 0, 0)

# Инициализация экрана
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Боевая игра")
clock = pygame.time.Clock()

# Загрузка изображений
background_img = pygame.image.load("background.png")
player_img = pygame.transform.scale(pygame.image.load("player.png"), (TILE_SIZE, TILE_SIZE))
enemy_img = pygame.transform.scale(pygame.image.load("enemy.png"), (TILE_SIZE, TILE_SIZE))
sword_icon = pygame.transform.scale(pygame.image.load("sword.png"), (50, 50))
bow_icon = pygame.transform.scale(pygame.image.load("bow.png"), (50, 50))
shield_icon = pygame.transform.scale(pygame.image.load("shield.png"), (50, 50))


class Hero:
    def __init__(self, name, x, y, health):
        self.name = name
        self.x = x
        self.y = y
        self.health = health
        self.max_health = health
        self.action_points = 3
        self.shield_active = False

    def move(self, dx, dy, other):
        if self.action_points > 0:
            new_x = max(0, min((SCREEN_WIDTH // TILE_SIZE) - 1, self.x + dx))
            new_y = max(0, min((SCREEN_HEIGHT // TILE_SIZE) - 1, self.y + dy))
            # Проверка, чтобы не пересекаться с другим героем
            if (new_x, new_y) != (other.x, other.y):
                self.x = new_x
                self.y = new_y
                self.action_points -= 1

    def attack(self, other, power):
        if self.action_points > 0:
            if abs(self.x - other.x) <= 1 and abs(self.y - other.y) <= 1:
                damage = power if not other.shield_active else 0
                other.health -= damage
                other.health = max(0, other.health)
                other.shield_active = False
                self.action_points -= 1
                return damage
        return 0

    def defend(self):
        if self.action_points > 0:
            self.shield_active = True
            self.action_points -= 1

    def reset_actions(self):
        self.action_points = 3
        self.shield_active = False

    def is_alive(self):
        return self.health > 0

    def draw(self, surface, image):
        surface.blit(image, (self.x * TILE_SIZE, self.y * TILE_SIZE))


class Game:
    def __init__(self):
        self.running = True
        self.player = Hero("Игрок", 0, 1, 100)
        self.enemy = Hero("Противник", 4, 1, 100)
        self.current_turn = "player"
        self.damage_text = ""
        self.damage_timer = 0

    def draw_health_bar(self, x, y, hero):
        pygame.draw.rect(screen, RED, (x, y, 200, 20))
        health_width = int(200 * (hero.health / hero.max_health))
        pygame.draw.rect(screen, GREEN, (x, y, health_width, 20))
        font = pygame.font.Font(None, 24)
        health_text = font.render(f"{hero.health}/{hero.max_health}", True, WHITE)
        screen.blit(health_text, (x + 100 - health_text.get_width() // 2, y))

    def handle_player_input(self, event):
        if event.type == pygame.KEYDOWN and self.current_turn == "player":
            dx, dy = 0, 0
            if event.key == pygame.K_UP:
                dy = -1
            elif event.key == pygame.K_DOWN:
                dy = 1
            elif event.key == pygame.K_LEFT:
                dx = -1
            elif event.key == pygame.K_RIGHT:
                dx = 1
            self.player.move(dx, dy, self.enemy)
        if event.type == pygame.MOUSEBUTTONDOWN and self.current_turn == "player":
            x, y = event.pos
            if 50 < x < 100 and SCREEN_HEIGHT - 100 < y < SCREEN_HEIGHT - 50:
                damage = self.player.attack(self.enemy, 20)
                self.damage_text = f"-{damage}"
                self.damage_timer = 60
            elif 150 < x < 200 and SCREEN_HEIGHT - 100 < y < SCREEN_HEIGHT - 50:
                damage = self.player.attack(self.enemy, 10)
                self.damage_text = f"-{damage}"
                self.damage_timer = 60
            elif 250 < x < 300 and SCREEN_HEIGHT - 100 < y < SCREEN_HEIGHT - 50:
                self.player.defend()
                self.damage_text = "Защита"
                self.damage_timer = 60

    def enemy_turn(self):
        for _ in range(3):  # 3 действия компьютера
            action = random.choice(["attack", "defend", "move"])
            if action == "attack":
                damage = self.enemy.attack(self.player, 20)
                self.damage_text = f"-{damage}"
                self.damage_timer = 60
            elif action == "defend":
                self.enemy.defend()
                self.damage_text = "Защита"
                self.damage_timer = 60
            elif action == "move":
                dx, dy = random.choice([(0, -1), (0, 1), (-1, 0), (1, 0)])
                self.enemy.move(dx, dy, self.player)
        self.current_turn = "player"
        self.player.reset_actions()
        self.enemy.reset_actions()

    def update(self):
        if self.damage_timer > 0:
            self.damage_timer -= 1
        if self.player.action_points == 0 and self.current_turn == "player":
            self.current_turn = "enemy"
            self.enemy_turn()
        if not self.player.is_alive():
            print("Вы проиграли!")
            self.running = False
        if not self.enemy.is_alive():
            print("Вы победили!")
            self.running = False

    def draw(self):
        screen.blit(background_img, (0, 0))
        self.player.draw(screen, player_img)
        self.enemy.draw(screen, enemy_img)
        screen.blit(sword_icon, (50, SCREEN_HEIGHT - 100))
        screen.blit(bow_icon, (150, SCREEN_HEIGHT - 100))
        screen.blit(shield_icon, (250, SCREEN_HEIGHT - 100))
        self.draw_health_bar(20, 20, self.player)
        self.draw_health_bar(SCREEN_WIDTH - 220, 20, self.enemy)
        if self.damage_timer > 0 and self.damage_text:
            font = pygame.font.Font(None, 36)
            damage_surface = font.render(self.damage_text, True, RED)
            screen.blit(damage_surface, (SCREEN_WIDTH // 2 - damage_surface.get_width() // 2, 20))

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.handle_player_input(event)
            self.update()
            self.draw()
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
