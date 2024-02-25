################## MODULES ####################
import pygame
import random
import os
import sqlite3
import threading as th
import math

################## INITIALIZATION ####################
pygame.mixer.init()
pygame.init()

################## COLOURS ####################
white = (255, 255, 255)
yellow = (255, 225, 0)
red = (255, 0, 0)
black = (0, 0, 0)
green = (0, 255, 0)
grey = (150, 200, 180)
brown = (165, 42, 42)
blue = (0,0,255)

################## SCREEN GENERATION ####################

screen_width = 900
screen_height = 600
gw = pygame.display.set_mode((screen_width, screen_height))

################## IMAGE _ HOME-SCREEN ####################
bgimg = pygame.image.load("homescreen.jpg")
bgimg = pygame.transform.scale(bgimg, (screen_width, screen_height)).convert_alpha()

################## TITLE N CLOCK ####################
pygame.display.set_caption("SnakesWithHarry")
pygame.display.update()
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 45)

################## DATABASE ####################
player_name = ""

# Create a database connection
conn = sqlite3.connect("player_data.db")
cursor = conn.cursor()

# Create a table to store player data
cursor.execute('''
    CREATE TABLE IF NOT EXISTS player (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        highscore INTEGER DEFAULT 0
    )
''')
conn.commit()


###############VARIABLES#####################
leaderboard_button_rect = pygame.Rect(750, 15, 135, 40)
leaderboard_button_color = (50, 50, 50)
leaderboard_button_text_color = white
leaderboard_button_font = pygame.font.SysFont(None, 30)

name_entry_visible = False
return_button_rect = pygame.Rect(10, 10, 150, 40)
return_button_color = (50, 50, 50)
return_button_text_color = white
return_button_font = pygame.font.SysFont(None, 30)

existing_user_button_rect = pygame.Rect(300, 500, 155, 40)
new_user_button_rect = pygame.Rect(550, 500, 110, 40)
user_button_color = (50, 50, 50)
user_button_text_color = white
user_button_font = pygame.font.SysFont(None, 30)


name_entry_visible = False
text_box_rect = pygame.Rect(250, 550, 400, 40)
text_box_color = white
text_box_line_color = red


def insert_player_data(name, highscore):
    # Check if the player already exists
    cursor.execute('''
        SELECT * FROM player WHERE name=?
    ''', (name,))
    existing_player = cursor.fetchone()

    if existing_player:
        # Update the highscore if the new highscore is greater
        if highscore > existing_player[2]:
            cursor.execute('''
                UPDATE player SET highscore=? WHERE name=?
            ''', (highscore, name))
    else:
        # Insert the player with the initial highscore of 0
        cursor.execute('''
            INSERT INTO player (name, highscore) VALUES (?, ?)
        ''', (name, highscore))
    
    conn.commit()

def get_highscore(player_name):
    cursor.execute('''
        SELECT highscore FROM player WHERE name=?
        ''', (player_name,))
                
    result = cursor.fetchone()

    if result:
        return result[0]  # Returning the highscore
    else:
        return None  # Player not found in the database
def show_score(text, color, x, y):
    screen_text = font.render(text, True, color)
    gw.blit(screen_text, [x, y])
    

def plot_snakey(gameWindow,color, snk_list, snake_size, time_elapsed):
    for i, (x, y) in enumerate(snk_list):
        # Calculate wavy patterns for both x and y coordinates
        angle_x = math.sin(time_elapsed + i / 5) * 10  # Adjust the multiplier for the wavy pattern in the x direction
        angle_y = math.cos(time_elapsed + i / 5) * 10  # Adjust the multiplier for the wavy pattern in the y direction

        if i == len(snk_list) - 1:  # Check if it's the head of the snake
            pygame.draw.circle(gameWindow, red, (int(x + angle_x + snake_size / 2), int(y + angle_y + snake_size / 2)), int(snake_size / 2))

            # Calculate positions for eyes
            eye_size = int(snake_size / 4)
            eye_left = (x + int(snake_size / 3) - 10, y + int(snake_size / 4))
            eye_right = (x + int(snake_size * 2 / 3) - eye_size + 10, y + int(snake_size / 4))

            # Draw eyes
            pygame.draw.circle(gameWindow, white, (int(eye_left[0] + angle_x + eye_size), int(eye_left[1] + angle_y + eye_size)), eye_size)
            pygame.draw.circle(gameWindow, white, (int(eye_right[0] + angle_x + eye_size), int(eye_right[1] + angle_y + eye_size)), eye_size)

            # Calculate position for the black dot (pupil)
            pupil_size = int(eye_size / 2)
            pupil_left = (int(eye_left[0] + angle_x + int(eye_size / 2)), int(eye_left[1] + angle_y + int(eye_size / 2)))
            pupil_right = (int(eye_right[0] + angle_x + int(eye_size / 2)), int(eye_right[1] + angle_y + int(eye_size / 2)))

            # Draw black dot (pupil)
            pygame.draw.circle(gameWindow, black, (pupil_left[0] + pupil_size, pupil_left[1] + pupil_size), pupil_size)
            pygame.draw.circle(gameWindow, black, (pupil_right[0] + pupil_size, pupil_right[1] + pupil_size), pupil_size)

        else:
            # Draw continuous wavy pattern on the snake's body in both directions
            pygame.draw.circle(gameWindow, green, (int(x + angle_x + snake_size / 2), int(y + angle_y + snake_size / 2)), int(snake_size / 2))

            # Draw blue circle every i%15 steps
            if i % 15 == 0:
                pygame.draw.circle(gameWindow, blue, (int(x + angle_x + snake_size / 2), int(y + angle_y + snake_size / 2)), int(snake_size / 2))

def draw_leaderboard_button():
    pygame.draw.rect(gw, leaderboard_button_color, leaderboard_button_rect)
    leaderboard_button_text = leaderboard_button_font.render("Leaderboard", True, leaderboard_button_text_color)
    gw.blit(leaderboard_button_text, (leaderboard_button_rect.x + 5, leaderboard_button_rect.y + 10))
    
def show_leaderboard():
    global player_name
    exit_leaderboard = False

    while not exit_leaderboard:
        gw.fill(black)
        show_score("Leaderboard", white, 350, 20)

        # Fetch top 5 high-scored players from the database
        cursor.execute('''
            SELECT name, highscore FROM player
            ORDER BY highscore DESC
            LIMIT 10
        ''')
        top_players = cursor.fetchall()

        y_offset = 100
        for rank, (name, highscore) in enumerate(top_players, start=1):
            show_score(f"{rank}. {name}: {highscore}", white, 350, y_offset)
            y_offset += 50

        # Draw Close button (X sign) at top-right corner
        close_button_rect = pygame.Rect(860, 20, 30, 30)
        pygame.draw.line(gw, white, (close_button_rect.x, close_button_rect.y), (close_button_rect.x + close_button_rect.width, close_button_rect.y + close_button_rect.height), 2)
        pygame.draw.line(gw, white, (close_button_rect.x, close_button_rect.y + close_button_rect.height), (close_button_rect.x + close_button_rect.width, close_button_rect.y), 2)

        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_leaderboard = True

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    exit_leaderboard = True

            # Handle mouse click events
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                if close_button_rect.collidepoint(mouse_pos):
                    exit_leaderboard = True


def draw_user_buttons():
    # Draw Existing User button
    pygame.draw.rect(gw, user_button_color, existing_user_button_rect)
    existing_user_button_text = user_button_font.render("Existing User", True, user_button_text_color)
    gw.blit(existing_user_button_text, (existing_user_button_rect.x + 10, existing_user_button_rect.y + 10))

    # Draw New User button
    pygame.draw.rect(gw, user_button_color, new_user_button_rect)
    new_user_button_text = user_button_font.render("New User", True, user_button_text_color)
    gw.blit(new_user_button_text, (new_user_button_rect.x + 10, new_user_button_rect.y + 10))


def draw_text_box():
    # Draw text box
    pygame.draw.rect(gw, text_box_color, text_box_rect)
    pygame.draw.line(gw, text_box_line_color, (text_box_rect.x, text_box_rect.y + text_box_rect.height), (text_box_rect.x + text_box_rect.width, text_box_rect.y + text_box_rect.height), 2)

    # Display player_name inside the text area
    text_surface = font.render(player_name, True, black)
    gw.blit(text_surface, (260, 555))


def welcome():
    global player_name, name_entry_visible
    exit_game = False
    existing_user = False
    new_user = False

    while not exit_game:
        gw.fill(black)
        gw.blit(bgimg, (0, 0))
        show_score(" The Game... ", red, 350, 430)
        highscore = get_highscore(player_name)
        if highscore:
            show_score("  HighScore : " + str(highscore) + "      Player : " + str(player_name), white, 5, 5)

        # Draw Existing User and New User buttons
        draw_user_buttons()
        draw_leaderboard_button()

        # Draw text box only if needed
        if existing_user or new_user or name_entry_visible:
            draw_text_box()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit_game = True
                return

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                # Check if Existing User button is clicked
                if existing_user_button_rect.collidepoint(mouse_pos):
                    existing_user = True
                    new_user = False

                # Check if New User button is clicked
                elif new_user_button_rect.collidepoint(mouse_pos):
                    existing_user = False
                    new_user = True

                # Check if Leaderboard button is clicked
                elif leaderboard_button_rect.collidepoint(mouse_pos):
                    show_leaderboard()

            # Handle keyboard events outside of conditions
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if new_user:
                        # Check if the name already exists
                        cursor.execute('''
                            SELECT name FROM player WHERE name=?
                        ''', (player_name,))
                        existing_name = cursor.fetchone()

                        if existing_name:
                            print("Warning: Name already exists. Please choose a different name.")
                        else:
                            name_entry_visible = False
                            pygame.mixer.music.load('game_music.mp3')
                            pygame.mixer.music.play()
                            insert_player_data(player_name, 0)
                            gameloop()
                    else:
                        cursor.execute('''
                            SELECT name FROM player WHERE name=?
                        ''', (player_name,))
                        existing_name = cursor.fetchone()

                        if existing_name:
                            name_entry_visible = False
                            pygame.mixer.music.load('game_music.mp3')
                            pygame.mixer.music.play()
                            pygame.mixer.fadeout(10)
                            gameloop()
                        else:
                            print("Warning: Name does not exist. Please enter a valid name.")

                elif event.key == pygame.K_BACKSPACE:
                    player_name = player_name[:-1]

                else:
                    player_name += event.unicode

        pygame.display.update()
        clock.tick(60)
def gameloop():

    exit_game = False
    game_over = False
    snake_x = 45
    snake_y = 55
    vx = 0
    vy = 0
    snk_list = []
    snk_length = 1

    food_x = random.randint(20, int(screen_width / 2))
    food_y = random.randint(20, int(screen_height / 2))
    score = 0
    speed = 5
    snake_size = 30
    fps = 70
    time_elapsed = 0
    
    
    if not os.path.exists("highscore.txt"):
        with open ("highscore.txt","w") as f:
                f.write("0")
                
    with open ("highscore.txt","r") as f:
        highscore = f.read()
    
    
    while not exit_game:
        if game_over:
            with open ("highscore.txt","w") as f:
                f.write(str(highscore))
            
            cursor.execute('''
                UPDATE player
                SET highscore = ?
                WHERE name = ?
            ''', (highscore, player_name))
            gw.fill(black)

            show_score("  Naagin Khatam, Kahaani Khatam   Press Enter To Continue  ", red, 5, 250)
            show_score("                                               Zeher : " + str(score) , yellow, 10, 290)
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    conn.close()
                    exit_game = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        welcome()

        else:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    conn.close()
                    exit_game = True

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        vx = speed
                        vy = 0

                    if event.key == pygame.K_LEFT:
                        vx = -speed
                        vy = 0

                    if event.key == pygame.K_UP:
                        vx = 0
                        vy = -speed

                    if event.key == pygame.K_DOWN:
                        vx = 0
                        vy = speed
                    if event.key == pygame.K_q:
                        score += 20

            snake_x = snake_x + vx
            snake_y = snake_y + vy

            if abs(snake_x - food_x)<20 and abs(snake_y - food_y)<20:
                score +=10
                food_x = random.randint(20, int(screen_width / 2))
                food_y = random.randint(20, int(screen_height / 2))
                if food_x<10 and food_y<10:
                    food_y += 15
                snk_length +=5
                if score > int(highscore):
                    highscore = score

            gw.fill(black)
            
            highscore = get_highscore(player_name)
            if highscore is None or score > int(highscore):
                highscore = score

            #show_score("Score : " + str(score) + "   HighScore : " + str(highscore), white, 5, 5)
            show_score("Score : " + str(score), white, 5, 5)
            pygame.draw.rect(gw, yellow, [food_x, food_y, snake_size, snake_size])

            head = []
            head.append(snake_x)
            head.append(snake_y)
            snk_list.append(head)

            if len(snk_list)>snk_length:
                del snk_list[0]

            if head in snk_list[:-1]:
                pygame.mixer.music.load('boom.mp3')
                pygame.mixer.music.play()
                pygame.mixer.fadeout(10)
                game_over = True
                if highscore is None or score > int(highscore):
                    highscore = score

            if snake_x<0 or snake_x>screen_width or snake_y<0 or snake_y>screen_height:
                    if snake_x < 0:
                        for i in range(len(snk_list)):
                            snk_list[i][0] += screen_width
                        snake_x += screen_width

                    if snake_x > screen_width:
                        for i in range(len(snk_list)):
                            snk_list[i][0] -= screen_width
                        snake_x -= screen_width

                    if snake_y < 0:
                        for i in range(len(snk_list)):
                            snk_list[i][1] += screen_height
                        snake_y += screen_height

                    if snake_y > screen_height:
                        for i in range(len(snk_list)):
                            snk_list[i][1] -= screen_height
                        snake_y -= screen_height
                
            #plot_snake(gw, red, snk_list, snake_size)
            plot_snakey(gw, red, snk_list, snake_size, time_elapsed)
            time_elapsed += 0.1  # Adjust the increment to control the speed of the wave
            
        pygame.display.update()
        clock.tick(fps)

    pygame.quit()
    quit()


if __name__=="__main__":
    pygame.mixer.music.load('home_music.mp3')
    pygame.mixer.music.play()
    pygame.mixer.fadeout(1000)
    welcome()
