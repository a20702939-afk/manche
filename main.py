import os
os.environ["SDL_VIDEO_ORIENTATION"] = "Portrait"

import pygame
import random
import math
from array import array

pygame.init()

# =========================================================
# AUDIO
# =========================================================
AUDIO_OK = False

try:
    pygame.mixer.init(
        frequency=22050,
        size=-16,
        channels=1,
        buffer=512
    )
    AUDIO_OK = True
except Exception:
    AUDIO_OK = False


def make_roll_sound():
    if not AUDIO_OK:
        return None

    samples = array("h")
    sample_rate = 22050

    for i in range(int(sample_rate * 0.65)):
        t = i / sample_rate
        frequency = 180 + 900 * abs(math.sin(t * 35))
        envelope = max(0, 1 - t / 0.65)

        value = int(
            4500 * envelope *
            math.sin(2 * math.pi * frequency * t)
        )
        samples.append(value)

    try:
        return pygame.mixer.Sound(buffer=samples.tobytes())
    except Exception:
        return None


roll_sound = make_roll_sound()

# =========================================================
# DISPLAY
# =========================================================
info = pygame.display.Info()
WIDTH = info.current_w
HEIGHT = info.current_h

if WIDTH < 300 or HEIGHT < 300:
    WIDTH, HEIGHT = 670, 1500

screen = pygame.display.set_mode(
    (WIDTH, HEIGHT),
    pygame.FULLSCREEN
)

pygame.display.set_caption("MANCH")
clock = pygame.time.Clock()

# =========================================================
# COLORS
# =========================================================
WHITE = (255, 255, 255)
BLACK = (35, 35, 35)
BG = (245, 239, 218)
GRAY = (185, 185, 185)
DARK = (35, 40, 50)

RED = (220, 35, 40)
GREEN = (20, 165, 75)
BLUE = (25, 100, 220)
YELLOW = (245, 195, 20)

LIGHT_RED = (255, 185, 185)
LIGHT_GREEN = (175, 235, 185)
LIGHT_BLUE = (175, 210, 255)
LIGHT_YELLOW = (255, 235, 155)

# =========================================================
# BOARD
# =========================================================
BOARD_SIZE = min(WIDTH - 30, HEIGHT - 260)
BOARD_SIZE = max(300, BOARD_SIZE)

CELL = BOARD_SIZE / 15

BOARD_X = (WIDTH - BOARD_SIZE) // 2
BOARD_Y = max(80, (HEIGHT - BOARD_SIZE - 180) // 2)

# =========================================================
# FONTS
# =========================================================
font = pygame.font.Font(None, max(22, int(WIDTH * 0.045)))
font_small = pygame.font.Font(None, max(18, int(WIDTH * 0.035)))
font_big = pygame.font.Font(None, max(40, int(WIDTH * 0.09)))

# =========================================================
# PLAYERS
# =========================================================
players = [
    {"name": "RED", "color": RED, "light": LIGHT_RED, "start": 0},
    {"name": "GREEN", "color": GREEN, "light": LIGHT_GREEN, "start": 13},
    {"name": "BLUE", "color": BLUE, "light": LIGHT_BLUE, "start": 26},
    {"name": "YELLOW", "color": YELLOW, "light": LIGHT_YELLOW, "start": 39}
]

pieces = [[-1, -1, -1, -1] for _ in range(4)]

active_players = []
player_count = 4
current_player = 0
dice_value = 0
dice_rolled = False
winner = None

message = "ROLL THE DICE!"
game_state = "menu"

# =========================================================
# SAFE START CELLS
# =========================================================
# هر خانه شروع بازیکن، خانه امن است.
SAFE_PATH_INDICES = {
    player["start"] for player in players
}

# =========================================================
# MOVEMENT ANIMATION
# =========================================================
bounce_height = 0
MOVE_FRAME_DELAY = 0.012

# =========================================================
# MAIN PATH - 52 CELLS
# =========================================================
path_cells = [
    (6, 1), (6, 0), (7, 0), (8, 0),
    (8, 1), (8, 2), (8, 3), (8, 4),
    (8, 5), (9, 6), (10, 6), (11, 6),
    (12, 6), (13, 6), (14, 6), (14, 7),
    (14, 8), (13, 8), (12, 8), (11, 8),
    (10, 8), (9, 8), (8, 9), (8, 10),
    (8, 11), (8, 12), (8, 13), (8, 14),
    (7, 14), (6, 14), (6, 13), (6, 12),
    (6, 11), (6, 10), (6, 9), (5, 8),
    (4, 8), (3, 8), (2, 8), (1, 8),
    (0, 8), (0, 7), (0, 6), (1, 6),
    (2, 6), (3, 6), (4, 6), (5, 6),
    (6, 5), (6, 4), (6, 3), (6, 2)
]

# =========================================================
# FINAL LANES
# =========================================================
final_lanes = [
    [(7, 1), (7, 2), (7, 3), (7, 4), (7, 5), (7, 6)],
    [(13, 7), (12, 7), (11, 7), (10, 7), (9, 7), (8, 7)],
    [(7, 13), (7, 12), (7, 11), (7, 10), (7, 9), (7, 8)],
    [(1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7)]
]

# =========================================================
# HOME POSITIONS
# =========================================================
homes = [
    [(1.5, 1.5), (4.5, 1.5), (1.5, 4.5), (4.5, 4.5)],
    [(10.5, 1.5), (13.5, 1.5), (10.5, 4.5), (13.5, 4.5)],
    [(10.5, 10.5), (13.5, 10.5), (10.5, 13.5), (13.5, 13.5)],
    [(1.5, 10.5), (4.5, 10.5), (1.5, 13.5), (4.5, 13.5)]
]

# =========================================================
# CELL HELPERS
# =========================================================
def cell_pos(col, row):
    return (
        int(BOARD_X + col * CELL + CELL / 2),
        int(BOARD_Y + row * CELL + CELL / 2)
    )


def cell_rect(col, row):
    margin = max(1, int(CELL * 0.025))
    return pygame.Rect(
        int(BOARD_X + col * CELL + margin),
        int(BOARD_Y + row * CELL + margin),
        int(CELL - margin * 2),
        int(CELL - margin * 2)
    )


def draw_cell(col, row, color):
    rect = cell_rect(col, row)
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(
        screen, BLACK, rect,
        max(1, int(CELL * 0.035))
    )


# =========================================================
# MENU BUTTONS
# =========================================================
menu_buttons = {}


def make_menu_buttons():
    global menu_buttons

    button_w = min(WIDTH - 80, 440)
    button_h = max(65, int(HEIGHT * 0.065))
    gap = 22

    center_x = WIDTH // 2
    start_y = HEIGHT // 2 - button_h

    menu_buttons = {
        "PLAY": pygame.Rect(
            center_x - button_w // 2,
            start_y, button_w, button_h
        ),
        "2": pygame.Rect(
            center_x - button_w // 2,
            start_y, button_w, button_h
        ),
        "3": pygame.Rect(
            center_x - button_w // 2,
            start_y + button_h + gap,
            button_w, button_h
        ),
        "4": pygame.Rect(
            center_x - button_w // 2,
            start_y + 2 * (button_h + gap),
            button_w, button_h
        )
    }


make_menu_buttons()

# =========================================================
# MENU DRAWING
# =========================================================
def draw_button(rect, text, color):
    pygame.draw.rect(
        screen, (15, 20, 30),
        rect.move(0, 6), border_radius=18
    )
    pygame.draw.rect(
        screen, color, rect,
        border_radius=18
    )
    pygame.draw.rect(
        screen, WHITE, rect, 3,
        border_radius=18
    )

    label = font_big.render(text, True, WHITE)
    screen.blit(label, (
        rect.centerx - label.get_width() // 2,
        rect.centery - label.get_height() // 2
    ))


def draw_menu():
    screen.fill(DARK)

    title_font = pygame.font.Font(
        None, max(60, int(WIDTH * 0.13))
    )

    title = title_font.render("MANCH", True, WHITE)
    screen.blit(title, (
        WIDTH // 2 - title.get_width() // 2,
        HEIGHT // 4 - title.get_height() // 2
    ))

    subtitle = font.render(
        "LUDO BOARD GAME", True, (210, 215, 230)
    )
    screen.blit(subtitle, (
        WIDTH // 2 - subtitle.get_width() // 2,
        HEIGHT // 4 + 65
    ))

    if game_state == "menu":
        draw_button(menu_buttons["PLAY"], "PLAY", GREEN)

    elif game_state == "players":
        label = font_big.render(
            "SELECT PLAYERS", True, WHITE
        )
        screen.blit(label, (
            WIDTH // 2 - label.get_width() // 2,
            HEIGHT // 2 - 210
        ))

        draw_button(menu_buttons["2"], "2 PLAYERS", RED)
        draw_button(menu_buttons["3"], "3 PLAYERS", BLUE)
        draw_button(menu_buttons["4"], "4 PLAYERS", GREEN)


# =========================================================
# START GAME
# =========================================================
def start_game(count):
    global active_players, player_count
    global current_player, dice_value, dice_rolled
    global winner, message, pieces, game_state

    player_count = count

    if count == 2:
        active_players = [0, 2]
    elif count == 3:
        active_players = [0, 1, 2]
    else:
        active_players = [0, 1, 2, 3]

    pieces = [[-1, -1, -1, -1] for _ in range(4)]

    current_player = active_players[0]
    dice_value = 0
    dice_rolled = False
    winner = None

    message = players[current_player]["name"] + ": ROLL!"
    game_state = "game"


# =========================================================
# 3D HOMES
# =========================================================
def draw_homes():
    home_data = [
        (0, 0, RED, LIGHT_RED),
        (9, 0, GREEN, LIGHT_GREEN),
        (9, 9, BLUE, LIGHT_BLUE),
        (0, 9, YELLOW, LIGHT_YELLOW)
    ]

    depth = max(4, int(CELL * 0.18))

    for index, (hx, hy, color, light_color) in enumerate(home_data):
        rect = pygame.Rect(
            int(BOARD_X + hx * CELL),
            int(BOARD_Y + hy * CELL),
            int(CELL * 6),
            int(CELL * 6)
        )

        if index not in active_players:
            pygame.draw.rect(screen, BG, rect)
            continue

        pygame.draw.rect(
            screen, (65, 65, 65),
            rect.move(0, depth),
            border_radius=int(CELL * 0.2)
        )

        pygame.draw.rect(
            screen, color, rect,
            border_radius=int(CELL * 0.2)
        )

        edge = max(3, int(CELL * 0.13))

        pygame.draw.line(
            screen, light_color,
            rect.topleft, rect.topright, edge
        )
        pygame.draw.line(
            screen, light_color,
            rect.topleft, rect.bottomleft, edge
        )

        dark_color = (
            max(0, color[0] - 65),
            max(0, color[1] - 65),
            max(0, color[2] - 65)
        )

        pygame.draw.line(
            screen, dark_color,
            rect.bottomleft, rect.bottomright, edge
        )

        pygame.draw.rect(
            screen, BLACK, rect,
            max(2, int(CELL * 0.07)),
            border_radius=int(CELL * 0.2)
        )

        inner = pygame.Rect(
            int(BOARD_X + (hx + 1) * CELL),
            int(BOARD_Y + (hy + 1) * CELL),
            int(CELL * 4),
            int(CELL * 4)
        )

        pygame.draw.rect(
            screen, (90, 90, 90),
            inner.move(0, max(3, int(CELL * 0.12))),
            border_radius=int(CELL * 0.3)
        )

        pygame.draw.rect(
            screen, (250, 250, 245),
            inner,
            border_radius=int(CELL * 0.3)
        )

        pygame.draw.rect(
            screen, light_color,
            inner,
            max(3, int(CELL * 0.1)),
            border_radius=int(CELL * 0.3)
        )

        pygame.draw.line(
            screen, WHITE,
            (inner.left + 8, inner.top + 5),
            (inner.right - 8, inner.top + 5),
            max(2, int(CELL * 0.06))
        )

        pygame.draw.rect(
            screen, BLACK, inner,
            max(1, int(CELL * 0.04)),
            border_radius=int(CELL * 0.3)
        )


# =========================================================
# DRAW BOARD
# =========================================================
def draw_board():
    screen.fill(BG)

    outer = pygame.Rect(
        int(BOARD_X - CELL * 0.35),
        int(BOARD_Y - CELL * 0.35),
        int(BOARD_SIZE + CELL * 0.7),
        int(BOARD_SIZE + CELL * 0.7)
    )

    pygame.draw.rect(
        screen, (225, 213, 180),
        outer, border_radius=12
    )
    pygame.draw.rect(
        screen, BLACK, outer, 3,
        border_radius=12
    )

    pygame.draw.rect(
        screen, WHITE,
        (BOARD_X, BOARD_Y, BOARD_SIZE, BOARD_SIZE)
    )

    draw_homes()

    for i, (col, row) in enumerate(path_cells):
        color = WHITE

        for p in active_players:
            if i == players[p]["start"]:
                color = players[p]["light"]

        draw_cell(col, row, color)

    for p in active_players:
        for col, row in final_lanes[p]:
            draw_cell(col, row, players[p]["light"])

    left = BOARD_X + 6 * CELL
    top = BOARD_Y + 6 * CELL
    right = BOARD_X + 9 * CELL
    bottom = BOARD_Y + 9 * CELL

    center = (
        BOARD_X + 7.5 * CELL,
        BOARD_Y + 7.5 * CELL
    )

    pygame.draw.polygon(
        screen, RED,
        [(left, top), (right, top), center]
    )
    pygame.draw.polygon(
        screen, GREEN,
        [(right, top), (right, bottom), center]
    )
    pygame.draw.polygon(
        screen, BLUE,
        [(right, bottom), (left, bottom), center]
    )
    pygame.draw.polygon(
        screen, YELLOW,
        [(left, bottom), (left, top), center]
    )

    pygame.draw.rect(
        screen, BLACK,
        (int(left), int(top), int(3 * CELL), int(3 * CELL)),
        2
    )

    for p in active_players:
        for piece in range(4):
            if pieces[p][piece] != -1:
                continue

            hx, hy = homes[p][piece]
            x = int(BOARD_X + hx * CELL)
            y = int(BOARD_Y + hy * CELL)

            pygame.draw.circle(
                screen, (190, 190, 190),
                (x + 2, y + 4), int(CELL * 0.75)
            )
            pygame.draw.circle(
                screen, WHITE,
                (x, y), int(CELL * 0.72)
            )
            pygame.draw.circle(
                screen, players[p]["color"],
                (x, y), int(CELL * 0.58)
            )
            pygame.draw.circle(
                screen, players[p]["light"],
                (x - int(CELL * 0.15), y - int(CELL * 0.15)),
                int(CELL * 0.20)
            )
            pygame.draw.circle(
                screen, BLACK,
                (x, y), int(CELL * 0.58), 2
            )


# =========================================================
# PIECE POSITION
# =========================================================
def get_piece_position(player, piece):
    state = pieces[player][piece]

    if state == -1:
        hx, hy = homes[player][piece]
        return (
            int(BOARD_X + hx * CELL),
            int(BOARD_Y + hy * CELL)
        )

    if state == 57:
        return cell_pos(7, 7)

    if 0 <= state <= 51:
        index = (
            players[player]["start"] + state
        ) % len(path_cells)

        col, row = path_cells[index]
        return cell_pos(col, row)

    final_index = max(0, min(5, state - 52))
    col, row = final_lanes[player][final_index]
    return cell_pos(col, row)


# =========================================================
# 3D PIECES WITH BOUNCE PHYSICS
# =========================================================
def draw_pieces():
    for player in active_players:
        for piece in range(4):
            if pieces[player][piece] == -1:
                continue

            x, y = get_piece_position(player, piece)
            y -= int(bounce_height)

            radius = int(CELL * 0.38)

            # Shadow
            shadow_radius = max(
                4,
                radius + 4 - int(bounce_height * 0.12)
            )

            pygame.draw.ellipse(
                screen,
                (130, 130, 130),
                (
                    x - shadow_radius,
                    y + radius + 3 + int(bounce_height * 0.5),
                    shadow_radius * 2,
                    max(3, int(radius * 0.45))
                )
            )

            # Base shadow
            pygame.draw.ellipse(
                screen,
                (70, 70, 70),
                (
                    x - radius,
                    y - radius // 2,
                    radius * 2,
                    radius * 2
                )
            )

            # Main body
            pygame.draw.circle(
                screen, players[player]["color"],
                (x, y), radius
            )

            # Light highlight
            pygame.draw.circle(
                screen, players[player]["light"],
                (
                    x - radius // 3,
                    y - radius // 3
                ),
                max(2, radius // 3)
            )

            pygame.draw.circle(
                screen, WHITE,
                (
                    x - radius // 3,
                    y - radius // 2
                ),
                max(2, radius // 7)
            )

            # Dark outline
            pygame.draw.circle(
                screen, BLACK,
                (x, y), radius, 2
            )


# =========================================================
# DICE
# =========================================================
DICE_SIZE = max(70, min(int(CELL * 2.0), 110))

dice_rect = pygame.Rect(0, 0, DICE_SIZE, DICE_SIZE)
dice_rect.center = (
    BOARD_X + BOARD_SIZE // 2,
    BOARD_Y + BOARD_SIZE // 2
)


def create_dice_surface(value):
    surface = pygame.Surface(
        (DICE_SIZE, DICE_SIZE),
        pygame.SRCALPHA
    )

    pygame.draw.rect(
        surface, GRAY,
        (3, 4, DICE_SIZE - 6, DICE_SIZE - 6),
        border_radius=15
    )

    pygame.draw.rect(
        surface, WHITE,
        (0, 0, DICE_SIZE - 6, DICE_SIZE - 6),
        border_radius=15
    )

    pygame.draw.rect(
        surface, BLACK,
        (0, 0, DICE_SIZE - 6, DICE_SIZE - 6),
        3, border_radius=15
    )

    positions = {
        1: [(0, 0)],
        2: [(-1, -1), (1, 1)],
        3: [(-1, -1), (0, 0), (1, 1)],
        4: [(-1, -1), (1, -1), (-1, 1), (1, 1)],
        5: [(-1, -1), (1, -1), (0, 0), (-1, 1), (1, 1)],
        6: [(-1, -1), (-1, 0), (-1, 1), (1, -1), (1, 0), (1, 1)]
    }

    if value == 0:
        text = font_small.render("ROLL", True, BLACK)
        surface.blit(text, (
            (DICE_SIZE - text.get_width()) // 2,
            (DICE_SIZE - text.get_height()) // 2
        ))
        return surface

    cx = (DICE_SIZE - 6) // 2
    cy = (DICE_SIZE - 6) // 2
    offset = DICE_SIZE * 0.22

    for px, py in positions[value]:
        pygame.draw.circle(
            surface, BLACK,
            (
                int(cx + px * offset),
                int(cy + py * offset)
            ),
            max(4, int(DICE_SIZE * 0.06))
        )

    return surface


def draw_dice(angle=0, value=None):
    if value is None:
        value = dice_value

    dice_surface = create_dice_surface(value)

    if angle != 0:
        dice_surface = pygame.transform.rotate(
            dice_surface, angle
        )

    rect = dice_surface.get_rect(center=dice_rect.center)
    screen.blit(dice_surface, rect)


# =========================================================
# DRAW GAME
# =========================================================
def draw_game():
    draw_board()
    draw_pieces()
    draw_dice()
    draw_ui()
    draw_winner()


# =========================================================
# DICE ROLL ANIMATION
# =========================================================
def animate_dice_roll():
    global dice_value

    if winner is not None:
        return

    if roll_sound is not None:
        try:
            roll_sound.play()
        except Exception:
            pass

    start_time = pygame.time.get_ticks()
    duration = 850

    while True:
        elapsed = pygame.time.get_ticks() - start_time

        if elapsed >= duration:
            break

        progress = elapsed / duration
        temporary_value = random.randint(1, 6)

        angle = (
            math.sin(elapsed * 0.035) *
            30 * (1 - progress)
        )

        draw_board()
        draw_pieces()
        draw_dice(angle, temporary_value)
        draw_ui()

        pygame.display.flip()
        clock.tick(30)

    dice_value = random.randint(1, 6)
    draw_game()
    pygame.display.flip()


# =========================================================
# MOVEMENT RULES
# =========================================================
def can_move(player, piece, dice):
    state = pieces[player][piece]

    # ورود از خانه فقط با 6
    if state == -1:
        return dice == 6

    # مسیر اصلی و مسیر پایانی
    if 0 <= state <= 56:
        return state + dice <= 57

    return False


# =========================================================
# ANIMATED MOVEMENT
# =========================================================
def animate_piece_move(player, piece, target_state):
    global bounce_height

    start_state = pieces[player][piece]

    # ورود از خانه به خانه شروع مسیر
    if start_state == -1:
        pieces[player][piece] = 0

        for frame in range(18):
            progress = frame / 18
            bounce_height = (
                math.sin(progress * math.pi) * CELL * 0.85
            )

            draw_game()
            pygame.display.flip()
            clock.tick(60)

        bounce_height = 0
        start_state = 0

    # حرکت مرحله‌ای
    if target_state > start_state:
        for step in range(start_state + 1, target_state + 1):
            pieces[player][piece] = step

            for frame in range(8):
                progress = frame / 8
                bounce_height = (
                    math.sin(progress * math.pi) * CELL * 0.35
                )

                draw_game()
                pygame.display.flip()
                clock.tick(60)

            bounce_height = 0

    # فرود فنری
    for frame in range(12):
        progress = frame / 12
        bounce_height = (
            math.sin(progress * math.pi) * CELL * 0.2
        )

        draw_game()
        pygame.display.flip()
        clock.tick(60)

    bounce_height = 0
    pieces[player][piece] = target_state

    draw_game()
    pygame.display.flip()


# =========================================================
# MOVE PIECE
# =========================================================
def move_piece(player, piece):
    global message, winner

    dice = dice_value
    state = pieces[player][piece]

    if state == -1:
        # ورود به خانه شروع مسیر
        target_state = 0
    else:
        target_state = min(state + dice, 57)

    animate_piece_move(
        player,
        piece,
        target_state
    )

    new_state = pieces[player][piece]

    # =====================================================
    # CAPTURE - SAFE START CELLS
    # =====================================================
    if 0 <= new_state <= 51:
        my_index = (
            players[player]["start"] + new_state
        ) % len(path_cells)

        # خانه شروع بازیکنان امن است
        if my_index not in SAFE_PATH_INDICES:
            for enemy in active_players:
                if enemy == player:
                    continue

                for enemy_piece in range(4):
                    enemy_state = pieces[enemy][enemy_piece]

                    if 0 <= enemy_state <= 51:
                        enemy_index = (
                            players[enemy]["start"] + enemy_state
                        ) % len(path_cells)

                        if (
                            my_index == enemy_index
                            and enemy_index not in SAFE_PATH_INDICES
                        ):
                            pieces[enemy][enemy_piece] = -1
                            message = "CAPTURE!"

    if all(
        pieces[player][i] == 57
        for i in range(4)
    ):
        winner = player
        message = players[player]["name"] + " WINS!"
    else:
        message = players[player]["name"] + " MOVED!"


# =========================================================
# NEXT TURN
# =========================================================
def next_turn():
    global current_player
    global dice_value, dice_rolled, message

    if not active_players:
        return

    current_index = active_players.index(current_player)

    current_player = active_players[
        (current_index + 1) % len(active_players)
    ]

    dice_value = 0
    dice_rolled = False
    message = players[current_player]["name"] + ": ROLL!"


# =========================================================
# ROLL DICE
# =========================================================
def roll_dice():
    global dice_value, dice_rolled, message

    if winner is not None or dice_rolled:
        return

    animate_dice_roll()
    dice_rolled = True

    possible = any(
        can_move(current_player, piece, dice_value)
        for piece in range(4)
    )

    if not possible:
        message = "NO MOVES!"

        if dice_value != 6:
            next_turn()
        else:
            dice_rolled = False
            message = "ROLL AGAIN!"


# =========================================================
# SELECT PIECE
# =========================================================
def select_piece(pos):
    global dice_rolled, message

    if not dice_rolled or winner is not None:
        return

    for piece in range(4):
        px, py = get_piece_position(current_player, piece)

        if math.hypot(
            pos[0] - px,
            pos[1] - py
        ) <= CELL * 0.75:

            if can_move(
                current_player,
                piece,
                dice_value
            ):
                move_piece(current_player, piece)

                if dice_value == 6:
                    dice_rolled = False
                    message = "ROLL AGAIN!"
                else:
                    next_turn()

                return


# =========================================================
# UI
# =========================================================
def draw_ui():
    title = font.render(
        "TURN: " + players[current_player]["name"],
        True, players[current_player]["color"]
    )

    screen.blit(title, (
        (WIDTH - title.get_width()) // 2,
        25
    ))

    msg = font_small.render(message, True, BLACK)

    screen.blit(msg, (
        (WIDTH - msg.get_width()) // 2,
        BOARD_Y + BOARD_SIZE + 20
    ))

    exit_rect = pygame.Rect(15, 20, 100, 45)

    pygame.draw.rect(
        screen, WHITE, exit_rect,
        border_radius=10
    )
    pygame.draw.rect(
        screen, BLACK, exit_rect, 2,
        border_radius=10
    )

    text = font_small.render("EXIT", True, BLACK)

    screen.blit(text, (
        exit_rect.centerx - text.get_width() // 2,
        exit_rect.centery - text.get_height() // 2
    ))

    home_rect = pygame.Rect(WIDTH - 115, 20, 100, 45)

    pygame.draw.rect(
        screen, WHITE, home_rect,
        border_radius=10
    )
    pygame.draw.rect(
        screen, BLACK, home_rect, 2,
        border_radius=10
    )

    home_text = font_small.render("MENU", True, BLACK)

    screen.blit(home_text, (
        home_rect.centerx - home_text.get_width() // 2,
        home_rect.centery - home_text.get_height() // 2
    ))


# =========================================================
# WINNER
# =========================================================
def draw_winner():
    if winner is None:
        return

    overlay = pygame.Surface(
        (WIDTH, HEIGHT),
        pygame.SRCALPHA
    )

    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))

    text = font_big.render(
        players[winner]["name"] + " WINS!",
        True, WHITE
    )

    screen.blit(text, (
        WIDTH // 2 - text.get_width() // 2,
        HEIGHT // 2 - text.get_height() // 2
    ))


# =========================================================
# MAIN LOOP
# =========================================================
running = True

while running:
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                if game_state == "game":
                    game_state = "menu"
                else:
                    running = False

            elif (
                event.key == pygame.K_SPACE
                and game_state == "game"
            ):
                roll_dice()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos

            if game_state == "menu":
                if menu_buttons["PLAY"].collidepoint(pos):
                    game_state = "players"

            elif game_state == "players":
                if menu_buttons["2"].collidepoint(pos):
                    start_game(2)
                elif menu_buttons["3"].collidepoint(pos):
                    start_game(3)
                elif menu_buttons["4"].collidepoint(pos):
                    start_game(4)

            elif game_state == "game":
                exit_rect = pygame.Rect(15, 20, 100, 45)
                home_rect = pygame.Rect(
                    WIDTH - 115, 20, 100, 45
                )

                if exit_rect.collidepoint(pos):
                    running = False

                elif home_rect.collidepoint(pos):
                    game_state = "menu"

                elif dice_rect.collidepoint(pos):
                    roll_dice()

                else:
                    select_piece(pos)

    if game_state in ("menu", "players"):
        draw_menu()

    elif game_state == "game":
        draw_game()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
