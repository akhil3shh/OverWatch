import pygame
# for using geometry (sort of!)
import math

# initialize
pygame.init()

# set-up variables
fps = 60
timer = pygame.time.Clock()
font = pygame.font.Font('assets/font/myFont.ttf', 32)
big_font = pygame.font.Font('assets/font/myFont.ttf', 60)

# screen constants
WIDTH = 900
HEIGHT = 800
screen = pygame.display.set_mode([WIDTH, HEIGHT])

# using materials
backgrounds = []
score = []
guns = []
target_images = [[], [], []]  # list of lists of images for each levels

# specify the no. & type of enemies to be given in each level of game:
targets = {1: [10, 5, 3],
           2: [12, 8, 5],
           3: [15, 12, 8, 3]}  # one extra to make this level more interesting :)
level = 0
points = 0  # score
total_shots = 0
mode = 0  # 0->freestyle    1->accuracy    2->timed
ammo = 0
time_passed = 0
time_remaining = 0
counter = 1
best_freeplay = 0
best_ammo = 0
best_timed = 0
shot = False
menu = True  # displays menu at the start of game
game_over = False
pause = False
clicked = False
write_values = False
new_coords = True
one_coords = [[], [], []]
two_coords = [[], [], []]
three_coords = [[], [], [], []]

# importing menu graphics
menu_img = pygame.image.load(f'assets/menus/mainMenu.png')
game_over_img = pygame.image.load(f'assets/menus/gameOver.png')
pause_img = pygame.image.load(f'assets/menus/pause.png')
for i in range(1, 4):
    # formatted strings for using "i"
    backgrounds.append(pygame.image.load(f'assets/backgrounds/{i}.png'))
    score.append(pygame.image.load(f'assets/score/{i}.png'))
    guns.append(pygame.transform.scale(pygame.image.load(f'assets/guns/{i}.png'), (300, 300)))
    #  adjust the size of gun acc. to window

    if i < 3:
        for j in range(1, 4):
            # i=which level to point at & j=which one to actually use!
            # To make it a bit complicated we resize (actually reduce) each target's size acc. to the level as well!
            target_images[i - 1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j * 18), 80 - (j * 12))))
    else:
        for j in range(1, 5):  # we added an extra target for last level, so it's 5!
            # i=which level to point at & j=which one to actually use!
            # To make it a bit complicated we resize (actually reduce) each target's size acc. to the level as well!
            target_images[i - 1].append(pygame.transform.scale(
                pygame.image.load(f'assets/targets/{i}/{j}.png'), (120 - (j * 18), 80 - (j * 12))))

# importing remaining graphics and sounds
file = open('high_scores.txt', 'r')
read_file = file.readlines()
file.close()
best_freeplay = int(read_file[0])
best_ammo = int(read_file[1])
best_timed = int(read_file[2])
pygame.mixer.init()
pygame.mixer.music.load('assets/sounds/bg_music.mp3')
shotgun_sound = pygame.mixer.Sound('assets/sounds/shotgun.mp3')
shotgun_sound.set_volume(.9)
guardian_sound = pygame.mixer.Sound('assets/sounds/guardian.mp3')
guardian_sound.set_volume(.9)
sheriff_sound = pygame.mixer.Sound('assets/sounds/sheriff.mp3')
sheriff_sound.set_volume(.9)
pygame.mixer.music.play()


# function for displaying score:
def draw_score():
    points_text = font.render(f'Points: {points}', True, 'white')
    screen.blit(points_text, (320, 660))
    shots_text = font.render(f'Total Shots: {total_shots}', True, 'white')
    screen.blit(shots_text, (320, 687))
    time_text = font.render(f'Time Elapsed: {time_passed}', True, 'white')
    screen.blit(time_text, (320, 714))
    if mode == 0:
        mode_text = font.render(f'Freeplay!', True, 'white')
    if mode == 1:
        mode_text = font.render(f'Ammo Remaining: {ammo}', True, 'white')
    if mode == 2:
        mode_text = font.render(f'Time Remaining {time_remaining}', True, 'white')
    screen.blit(mode_text, (320, 741))


# function for displaying a gun:
def draw_gun():
    # track mouse position & rotate the gun accordingly:
    mouse_pos = pygame.mouse.get_pos()
    gun_point = (WIDTH / 2, HEIGHT - 200)  # position = middle of screen & 200 pixels above
    lasers = ['red', 'purple', 'green']  # display a point size object whenever you click on screen
    clicks = pygame.mouse.get_pressed()  # count the clicks in a list
    if mouse_pos[0] != gun_point[0]:
        slope = (mouse_pos[1] - gun_point[1]) / (mouse_pos[0] - gun_point[0])
        # calculate the line from rotation of gun & actual position of mouse
    else:
        slope = -100000  # just to make it easy use a really big -ve integer!
    angle = math.atan(slope)  # use inverse tan to calculate angle
    rotation = math.degrees(angle)  # convert to degrees from radians

    # to flip the gun
    if mouse_pos[0] < WIDTH / 2:
        gun = pygame.transform.flip(guns[level - 1], True, False)
        # True to flip it left/right & False to not invert it upside/down
        # when in the below section we don't want to shoot! we want to choose options instead!
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 90 - rotation), (WIDTH / 2 - 90, HEIGHT - 250))
            # to avoid the whole gun in the menu section & at proper angle!
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
                # to detect that we have actually clicked on screen!
    else:
        gun = guns[level - 1]
        if mouse_pos[1] < 600:
            screen.blit(pygame.transform.rotate(gun, 270 - rotation), (WIDTH / 2 - 30, HEIGHT - 250))
            # it's 270 because we flipped the gun by 180 so to match it we just add another 180 in it
            if clicks[0]:
                pygame.draw.circle(screen, lasers[level - 1], mouse_pos, 5)
                # to detect that we have actually clicked on screen!


# function to animate the movement of targets:
def move_level(coords):
    if level == 1 or level == 2:
        max_val = 3  # 3 targets
    else:
        max_val = 4  # 4 targets
    for i in range(max_val):
        for j in range(len(coords[i])):
            my_coords = coords[i][j]
            if my_coords[0] < -150:  # worst case for fully off-screen to left
                coords[i][j] = (WIDTH, my_coords[1])
            else:
                coords[i][j] = (my_coords[0] - 2 ** i, my_coords[1])  # speed of moving enemies based on level
    return coords  # since we're over-writing them!


# function for displaying the targets in any level:
def draw_level(coords):  # specifying co-ordinates of the targets!
    if level == 1 or level == 2:
        target_rects = [[], [], []]  # create invisible rectangles to detect collisions/hitboxes
    else:
        target_rects = [[], [], [], []]  # (level 3!)
    for i in range(len(coords)):
        for j in range(len(coords[i])):
            # x & y co-ords for hitboxes. 20 pixels are added to cover deadspaces & make the targets look accurate.
            # Rest attributes are to make these targets look progressively look smaller
            target_rects[i].append(pygame.rect.Rect((coords[i][j][0] + 20, coords[i][j][1]),
                                                    (60 - i * 12, 60 - i * 12)))
            # the part where we actually draw the targets on screen:
            screen.blit(target_images[level - 1][i], coords[i][j])
    return target_rects  # return list of all rect hitboxes


# function for tracking the no. of targets hit
# if mouse position and target collides, delete the prev co-ords & return ,modified co-ords list
def check_shot(targets, coords):
    global points
    mouse_pos = pygame.mouse.get_pos()
    for i in range(len(targets)):
        for j in range(len(targets[i])):
            if targets[i][j].collidepoint(mouse_pos):
                coords[i].pop(j)
                points += 10 + 10 * (i ** 2)  # making it progressive acc. to target hit
                if level == 1:
                    shotgun_sound.play()
                elif level == 2:
                    guardian_sound.play()
                elif level == 3:
                    sheriff_sound.play()
    return coords


# function for displaying menu:
def draw_menu():
    global game_over, pause, mode, level, menu, time_passed, total_shots, points, ammo  # variables required
    global time_remaining, best_freeplay, best_ammo, best_timed, write_values, clicked, new_coords
    game_over = False
    pause = False
    screen.blit(menu_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    freeplay_button = pygame.rect.Rect((100, 400), (260, 150))  # display the freeplay option
    screen.blit(font.render(f'{best_freeplay}', True, 'black'), (250, 515))
    ammo_button = pygame.rect.Rect((520, 450), (330, 120))  # display the ammo option
    screen.blit(font.render(f'{best_ammo}', True, 'black'), (750, 515))
    timed_button = pygame.rect.Rect((60, 620), (310, 130))  # display the timed-mode option
    screen.blit(font.render(f'{best_timed}', True, 'black'), (275, 705))
    reset_button = pygame.rect.Rect((500, 630), (340, 130))  # display the reset option

    # interacting with the freeplay button
    if freeplay_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 0
        level = 1
        menu = False
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True

    # interacting with the ammo button
    if ammo_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 1
        level = 1
        menu = False
        time_passed = 0
        ammo = 81
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True

    # interacting with the timed button
    if timed_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        mode = 2
        level = 1
        menu = False
        time_remaining = 5
        time_passed = 0
        total_shots = 0
        points = 0
        clicked = True
        new_coords = True

    # interacting with the reset button
    if reset_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        best_freeplay = 0
        best_ammo = 0
        best_timed = 0
        clicked = True
        write_values = True


# function for gameOver:
def draw_game_over():
    global clicked, level, pause, game_over, menu, points, total_shots, time_passed, time_remaining  # variables
    if mode == 0:
        display_score = time_passed
    else:
        display_score = points
    screen.blit(game_over_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()  # examining the mouse click on targets
    exit_button = pygame.rect.Rect((70, 630), (130, 110))  # examining the exit option
    menu_button = pygame.rect.Rect((700, 620), (130, 120))  # examining the menu option
    screen.blit(big_font.render(f'{display_score}', True, 'white'), (580, 410))
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        clicked = True
        level = 0
        pause = False
        game_over = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
    if exit_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        global run
        run = False


# function for pausedGame:
def draw_pause():
    global level, pause, menu, points, total_shots, time_passed, time_remaining, clicked, new_coords
    screen.blit(pause_img, (0, 0))
    mouse_pos = pygame.mouse.get_pos()
    clicks = pygame.mouse.get_pressed()
    resume_button = pygame.rect.Rect((170, 661), (260, 100))
    menu_button = pygame.rect.Rect((475, 661), (260, 100))
    if resume_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        level = resume_level
        pause = False
        clicked = True
    if menu_button.collidepoint(mouse_pos) and clicks[0] and not clicked:
        pygame.mixer.music.play()
        level = 0
        pause = False
        menu = True
        points = 0
        total_shots = 0
        time_passed = 0
        time_remaining = 0
        clicked = True
        new_coords = True


# boolean for run var
run = True
while run:
    timer.tick(fps)
    if level != 0:
        if counter < 60:
            counter += 1
        else:
            counter = 1
            time_passed += 1
            if mode == 2:  # for time mode:
                time_remaining -= 1

    # initialize enemy co-ords
    if new_coords:
        one_coords = [[], [], []]
        two_coords = [[], [], []]
        three_coords = [[], [], [], []]

        for i in range(3):
            my_list = targets[1]  # referring to the 1st level target
            for j in range(my_list[i]):
                one_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))
                # draw targets in a procedural way with some distance b/w each

        for i in range(3):
            my_list = targets[2]  # referring to the 2nd level target
            for j in range(my_list[i]):
                two_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 150) + 30 * (j % 2)))

        for i in range(4):
            my_list = targets[3]  # referring to the 3rd level target
            for j in range(my_list[i]):
                three_coords[i].append((WIDTH // (my_list[i]) * j, 300 - (i * 100) + 30 * (j % 2)))
        new_coords = False

    screen.fill('white')  # populate the screen
    screen.blit(backgrounds[level - 1], (0, 0))  # use background acc. to level
    screen.blit(score[level - 1], (0, HEIGHT - 200))  # make menus 200 pixels high
    if menu:
        level = 0
        draw_menu()
    if game_over:
        level = 0
        draw_game_over()
    if pause:
        level = 0
        draw_pause()

    if level == 1:
        target_boxes = draw_level(one_coords)
        one_coords = move_level(one_coords)  # get them back!
        if shot:
            one_coords = check_shot(target_boxes, one_coords)
            shot = False  # just to run this thing only once!
    elif level == 2:
        target_boxes = draw_level(two_coords)
        two_coords = move_level(two_coords)
        if shot:
            two_coords = check_shot(target_boxes, two_coords)
            shot = False
    elif level == 3:
        target_boxes = draw_level(three_coords)
        three_coords = move_level(three_coords)
        if shot:
            three_coords = check_shot(target_boxes, three_coords)
            shot = False
    if level > 0:
        draw_gun()
        draw_score()

    # to avoid an infinite loop & possibly your device crash:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # close window option
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # only left click considered!
            mouse_position = pygame.mouse.get_pos()
            if (0 < mouse_position[0] < WIDTH) and (0 < mouse_position[1] < HEIGHT - 200):
                shot = True
                total_shots += 1  # to track the no. of shots
                if mode == 1:
                    ammo -= 1
            if (670 < mouse_position[0] < 860) and (600 < mouse_position[1] < 715):
                resume_level = level
                pause = True
                clicked = True
            if (670 < mouse_position[0] < 860) and (715 < mouse_position[1] < 760):
                menu = True
                pygame.mixer.music.play()
                clicked = True
                new_coords = True
        if event.type == pygame.MOUSEBUTTONUP and event.button == 1 and clicked:
            clicked = False

    if level > 0:
        if target_boxes == [[], [], []] and level < 3:
            level += 1
        if (level == 3 and target_boxes == [[], [], [], []]) or (mode == 1 and ammo == 0) or (
                mode == 2 and time_remaining == 0):
            new_coords = True
            pygame.mixer.music.play()
            if mode == 0:
                if time_passed < best_freeplay or best_freeplay == 0:
                    best_freeplay = time_passed
                    write_values = True
            if mode == 1:
                if points > best_ammo:
                    best_ammo = points
                    write_values = True
            if mode == 2:
                if points > best_timed:
                    best_timed = points
                    write_values = True
            game_over = True
    if write_values:
        file = open('high_scores.txt', 'w')
        file.write(f'{best_freeplay}\n{best_ammo}\n{best_timed}')
        file.close()
        write_values = False
        # when all targets have passed the screen or hit, change the level!

    pygame.display.flip()  # actually put all the instructions on the screen
pygame.quit()
