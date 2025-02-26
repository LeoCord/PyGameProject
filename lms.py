import pygame
import random

WIDTH, HEIGHT = 300, 600
BLOCK_SIZE = 25
SCORE_PANEL_WIDTH = 100
RED = (255, 0, 0)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
COLORS = [
    (0, 255, 255),  # Циан
    (255, 165, 0),  # Оранжевый
    (0, 0, 255),  # Синий
    (255, 0, 0),  # Красный
    (128, 0, 128),  # Фиолетовый
    (0, 255, 0),  # Зеленый
    (255, 255, 0)  # Желтый
]
DROP_INTERVAL = 100

SHAPES = [
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],  # O
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]],  # J
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 1, 1, 1]]  # I
]


class Tetris:
    def __init__(self):
        self.board = [[0] * (WIDTH // BLOCK_SIZE) for _ in range(HEIGHT // BLOCK_SIZE)]
        self.current_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.next_piece = self.new_piece()
        self.level = 1
        self.score = 0
        self.start_time = pygame.time.get_ticks()

        self.line_sound = pygame.mixer.Sound('Line.wav')
        self.line_sound.set_volume(0.3)

        self.drop_sound = pygame.mixer.Sound('Drop.wav')
        self.drop_sound.set_volume(0.5)

        self.rotate_sound = pygame.mixer.Sound('Rotate.wav')
        self.rotate_sound.set_volume(0.2)

        self.move_sound = pygame.mixer.Sound('Move.wav')
        self.move_sound.set_volume(0.2)

    @staticmethod
    def new_piece():
        shape = random.choice(SHAPES)
        color = COLORS[SHAPES.index(shape)]
        return {'shape': shape, 'color': color, 'x': WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2, 'y': 0}

    def rotate_piece(self):
        self.current_piece['shape'] = [list(row) for row in zip(*self.current_piece['shape'][::-1])]
        self.rotate_sound.play()

    def valid_move(self):
        for y in range(len(self.current_piece['shape'])):
            for x in range(len(self.current_piece['shape'][y])):
                if self.current_piece['shape'][y][x]:
                    if (self.current_piece['x'] + x < 0 or
                            self.current_piece['x'] + x >= WIDTH // BLOCK_SIZE or
                            self.current_piece['y'] + y >= HEIGHT // BLOCK_SIZE or
                            self.board[self.current_piece['y'] + y][self.current_piece['x'] + x]):
                        return False
        return True

    def merge_piece(self):
        for y in range(len(self.current_piece['shape'])):
            for x in range(len(self.current_piece['shape'][y])):
                if self.current_piece['shape'][y][x]:
                    self.board[self.current_piece['y'] + y][self.current_piece['x'] + x] = self.current_piece['color']
        self.clear_lines()

    def clear_lines(self):
        lines_to_clear = []
        for i in range(len(self.board)):
            if all(self.board[i]):
                self.line_sound.play()
                lines_to_clear.append(i)
        for i in lines_to_clear:
            del self.board[i]
            self.board.insert(0, [0] * (WIDTH // BLOCK_SIZE))
            self.score += len(lines_to_clear)

    def drop(self):
        self.current_piece['y'] += 1
        if not self.valid_move():
            self.current_piece['y'] -= 1
            self.merge_piece()
            self.current_piece = self.next_piece
            self.next_piece = self.new_piece()
            self.drop_sound.play()
            if not self.valid_move():
                return False
        return True

    def level_up(self):
        global DROP_INTERVAL
        self.level += 1
        DROP_INTERVAL = int(DROP_INTERVAL * 0.7)


def draw_board(screen, board):
    for y in range(len(board)):
        for x in range(len(board[y])):
            color = board[y][x]
            if color:
                pygame.draw.rect(screen, color,
                                 (x * BLOCK_SIZE + SCORE_PANEL_WIDTH, y * BLOCK_SIZE,
                                  BLOCK_SIZE - 1, BLOCK_SIZE - 1))


def draw_score_panel(screen, score):
    pygame.draw.rect(screen, BLACK, (0, 0, SCORE_PANEL_WIDTH, HEIGHT))
    font = pygame.font.Font(None, 26)
    score_text = font.render(f'Score: {score}/10', True, WHITE)
    screen.blit(score_text, (0, 10))


def draw_dividing_line(screen):
    pygame.draw.line(screen, WHITE, (SCORE_PANEL_WIDTH, 0), (SCORE_PANEL_WIDTH, HEIGHT), 2)


def show_start_screen(screen):
    screen.fill(BLACK)
    font = pygame.font.Font(None, 74)
    title_text = font.render('Tetris', True, WHITE)
    screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2 + SCORE_PANEL_WIDTH // 2, HEIGHT // 4))

    font = pygame.font.Font(None, 36)
    instructions_text = font.render('Press any key to start', True, WHITE)
    screen.blit(instructions_text,
                (WIDTH // 2 - instructions_text.get_width() // 2 + SCORE_PANEL_WIDTH // 2, HEIGHT // 2))

    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                waiting = False


def show_win_screen(screen):
    font = pygame.font.Font(None, 74)
    text = font.render("You Win!", True, RED)
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    screen.fill(BLACK)
    screen.blit(text, text_rect)
    pygame.display.flip()

    pygame.mixer.music.stop()
    sound = pygame.mixer.Sound('Win.mp3')
    sound.set_volume(0.2)
    sound.play()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False


def show_game_over_screen(screen):
    font = pygame.font.Font(None, 74)
    text = font.render("Game Over", True, RED)
    text_rect = text.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

    screen.fill(BLACK)
    screen.blit(text, text_rect)
    pygame.display.flip()

    pygame.mixer.music.stop()
    sound = pygame.mixer.Sound('Game Over.mp3')
    sound.set_volume(0.2)
    sound.play()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    waiting = False


def draw_next_piece(screen, piece):
    piece_surface = pygame.Surface((BLOCK_SIZE * len(piece['shape'][0]), BLOCK_SIZE * len(piece['shape'])))
    piece_surface.fill(BLACK)

    for y in range(len(piece['shape'])):
        for x in range(len(piece['shape'][y])):
            if piece['shape'][y][x]:
                pygame.draw.rect(piece_surface,
                                 piece['color'],
                                 (x * BLOCK_SIZE,
                                  y * BLOCK_SIZE,
                                  BLOCK_SIZE - 1,
                                  BLOCK_SIZE - 1))
    font = pygame.font.Font(None, 26)
    label = font.render("Next piece:", True, WHITE)
    screen.blit(label, (0, BLOCK_SIZE * 4))
    screen.blit(piece_surface, (0, BLOCK_SIZE * 5))


def draw_timer(screen, remaining_time):
    font = pygame.font.Font(None, 26)
    minutes = int(remaining_time) // 60
    seconds = int(remaining_time) % 60
    timer_text = f"{minutes:02}:{seconds:02}"

    timer_surface = font.render(timer_text, True, WHITE)
    screen.blit(timer_surface, (0, HEIGHT // 2))

    label = font.render("Remaining", True, WHITE)
    screen.blit(label, (0, HEIGHT // 2 - 40))
    label = font.render("time:", True, WHITE)
    screen.blit(label, (0, HEIGHT // 2 - 20))


def shake_screen(screen):
    original_position = screen.get_rect().topleft
    shake_amount = 1

    offset_x = random.randint(-shake_amount, shake_amount)
    offset_y = random.randint(-shake_amount, shake_amount)
    screen.blit(screen, (offset_x + original_position[0], offset_y + original_position[1]))
    pygame.display.flip()


def main():
    pygame.init()
    pygame.display.set_caption('Tetris')

    pygame.mixer.music.load('Tetris.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.1)

    screen = pygame.display.set_mode((WIDTH + SCORE_PANEL_WIDTH, HEIGHT))
    clock = pygame.time.Clock()

    show_start_screen(screen)

    tetris = Tetris()
    tetris.score = 0
    last_drop_time = pygame.time.get_ticks()
    remaining_time = 150

    running = True
    while running:
        screen.fill(BLACK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
                tetris.rotate_piece()
                if not tetris.valid_move():
                    tetris.rotate_piece()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            tetris.current_piece['x'] -= 1
            if not tetris.valid_move():
                tetris.current_piece['x'] += 1
            else:
                tetris.move_sound.play()

        if keys[pygame.K_RIGHT]:
            tetris.current_piece['x'] += 1
            if not tetris.valid_move():
                tetris.current_piece['x'] -= 1
            else:
                tetris.move_sound.play()

        if keys[pygame.K_DOWN]:
            tetris.drop()

        draw_board(screen, tetris.board)

        for y in range(len(tetris.current_piece['shape'])):
            for x in range(len(tetris.current_piece['shape'][y])):
                if tetris.current_piece['shape'][y][x]:
                    pygame.draw.rect(screen,
                                     tetris.current_piece['color'],
                                     ((tetris.current_piece['x'] + x) * BLOCK_SIZE + SCORE_PANEL_WIDTH,
                                      (tetris.current_piece['y'] + y) * BLOCK_SIZE,
                                      BLOCK_SIZE - 1,
                                      BLOCK_SIZE - 1))

        draw_score_panel(screen, tetris.score)
        draw_dividing_line(screen)
        draw_next_piece(screen, tetris.next_piece)

        current_time = pygame.time.get_ticks()
        if current_time - last_drop_time > DROP_INTERVAL:
            if not tetris.drop():
                show_game_over_screen(screen)
                running = False

            if tetris.score == 10 and tetris.level == 1:
                tetris.level_up()
                pygame.mixer.music.stop()
                pygame.mixer.music.load('TetrisF.mp3')
                pygame.mixer.music.set_volume(0.3)
                pygame.mixer.music.play()

            if not remaining_time:
                show_win_screen(screen)
                running = False

            last_drop_time = current_time

        if tetris.level == 2:
            shake_screen(screen)
            remaining_time -= 0.1
            draw_timer(screen, remaining_time)

        pygame.display.flip()
        clock.tick(10)

    pygame.quit()


if __name__ == "__main__":
    main()
