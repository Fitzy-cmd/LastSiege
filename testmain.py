from settings import *
from main import *
import pygame



run = True
setup = False
while run:

    clock.tick(FPS)

    if start_game == False:
        #draw menu
        screen.fill(BG)
        screen.blit(logo, (100, 15))
        draw_text("Controls", font2, WHITE, 20, 450)
        draw_text("Movement: Arrow Keys or WASD", font3, WHITE, 20, 470)
        draw_text("Fire Gun: F Key", font3, WHITE, 20, 490)
        draw_text("Throw Grenade: Q Key", font3, WHITE, 20, 510)
        #add buttons
        a.optionsAchievementCheck()
        if achievementMenu == False:
            if start_button.draw(screen):
                start_game = True
                start_intro = True
            if exit_button.draw(screen):
                run = False
            if achievements_button.draw(screen):
                achievementMenu = True
                
        else:
            a.draw()
            for event in pygame.event.get():
                #quit game
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
            if start_button2.draw(screen):
                start_game = True
                start_intro = True
            if exit_button2.draw(screen):
                run = False

    else:
        if not settings.timerStarted and settings.startTime == 0:
            settings.startTime = time.time()
            settings.timerStarted = True
        #update background
        draw_bg()
        #draw world map
        world.draw()
        #show player health
        health_bar.draw(player.health)
        #show ammo
        draw_text('AMMO: ', font2, WHITE, 10, 35)
        for x in range(player.ammo):
            screen.blit(bullet_img, (90 + (x * 10), 40))
        #show grenades
        draw_text('GRENADES: ', font2, WHITE, 10, 60)
        for x in range(player.grenades):
            screen.blit(grenade_img, (135 + (x * 15), 60))


        player.update()
        player.draw()

        for enemy in enemy_group:
            enemy.ai()
            enemy.update()
            enemy.draw()

        #update and draw groups
        bullet_group.update()
        grenade_group.update()
        explosion_group.update()
        item_box_group.update()
        decoration_group.update()
        water_group.update()
        exit_group.update()
        bullet_group.draw(screen)
        grenade_group.draw(screen)
        explosion_group.draw(screen)
        item_box_group.draw(screen)
        decoration_group.draw(screen)
        water_group.draw(screen)
        exit_group.draw(screen)

        if settings.firingModesOn:
            draw_text(settings.activeFiringMode, font2, WHITE, 625, 10)

        if not setup: ##level-specific one-time events
            settings.enemyCounter = len(enemy_group)
            settings.totalEnemyCounter += len(enemy_group)
            setup = True
        #show intro
        if start_intro == True:
            if intro_fade.fade():
                start_intro = False
                intro_fade.fade_counter = 0


        #update player actions
        if player.alive:
            #shoot bullets
            if shoot:
                player.shoot(settings.activeFiringMode)
            #throw grenades
            elif grenade and grenade_thrown == False and player.grenades > 0:
                grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),\
                             player.rect.top, player.direction)
                grenade_group.add(grenade)
                #reduce grenades
                player.grenades -= 1
                grenade_thrown = True
            if player.in_air:
                player.update_action(2)#2: jump
            elif moving_left or moving_right:
                player.update_action(1)#1: run
            else:
                player.update_action(0)#0: idle
            screen_scroll, level_complete = player.move(moving_left, moving_right)
            bg_scroll -= screen_scroll

            #check if player has completed the level
            if level_complete:
                if MAX_LEVELS == level:
                    settings.gameCompleted = True
                if not settings.gameCompleted:
                    a.endLevelAchievementCheck()
                    start_intro = True
                    setup = False
                    level += 1
                    bg_scroll = 0
                    world_data = reset_level()
                    if level <= settings.MAX_LEVELS:
                        #load in level data and create world
                        with open(f'level{level}_data.csv', newline='') as csvfile:
                            reader = csv.reader(csvfile, delimiter=',')
                            for x, row in enumerate(reader):
                                for y, tile in enumerate(row):
                                    world_data[x][y] = int(tile)
                        world = World()
                        player, health_bar = world.process_data(world_data)
                else:
                    a.endGameAchievementCheck()
                    a.endLevelAchievementCheck()

                    screen.blit(endimg, (0,0))
                    draw_text("Congratulations!", font4, WHITE, 235, 50)

                    if settings.timerStarted and settings.endTime == 0:
                        settings.timerStarted = False
                        settings.endTime = time.time()
                        unalteredScore = settings.score
                        settings.score += player.health * 5
                        settings.score += player.ammo * 2
                        settings.score += player.grenades * 30
                    
                    settings.timeCompleted = settings.endTime - settings.startTime
                    draw_text("You completed the game in", font, WHITE, 240, 120)
                    draw_text(str(round(settings.timeCompleted, 2)) + " seconds", font4, WHITE, 275, 160)
                    draw_text("with a total score of", font, WHITE, 290, 250)
                    draw_text(str(settings.score) + " points", font4, WHITE, 300, 290)
                    score_text = f"+{unalteredScore} normal points scored"
                    score_text1 = f"+{player.health * 5}pts bonus from your leftover health"
                    score_text2 = f"+{player.ammo * 2}pts bonus from your leftover ammo"
                    score_text3 = f"+{player.grenades * 30}pts bonus from your leftover grenades"
                    draw_text(score_text, font2, WHITE, 280, 360)
                    draw_text(score_text1, font2, WHITE, 280, 380)
                    draw_text(score_text2, font2, WHITE, 280, 400)
                    draw_text(score_text3, font2, WHITE, 280, 420)
                    print(level_complete, start_intro)
                    if restart_button_endscreen.draw(screen):
                        level_complete = False
                        print("heaps pranked gottem yeet")
                        start_intro = False
                        start_game = False
        
        
        
        else:
            screen_scroll = 0
            if death_fade.fade():

                if restart_button.draw(screen):
                    death_fade.fade_counter = 0
                    start_intro = True
                    bg_scroll = 0
                    world_data = reset_level()
                    #load in level data and create world
                    with open(f'level{level}_data.csv', newline='') as csvfile:
                        reader = csv.reader(csvfile, delimiter=',')
                        for x, row in enumerate(reader):
                            for y, tile in enumerate(row):
                                world_data[x][y] = int(tile)
                    world = World()
                    player, health_bar = world.process_data(world_data)


    for event in pygame.event.get():
        #quit game
        if event.type == pygame.QUIT:
            run = False
        #keyboard presses
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = True
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = True
            if event.key == pygame.K_f:
                if start_game == True: #done to make sure that no keys pressed before game starts account towards firing shots, as well as preventing shots fired from enemies counting towards this variable
                    settings.shotsFired += 1
                    if settings.activeFiringMode == "Automatic":
                        settings.automaticMode = True
                shoot = True
            if event.key == pygame.K_q:
                if start_game == True:
                    settings.grenadesThrown += 1
                grenade = True
            if event.key == pygame.K_w and player.alive or event.key == pygame.K_UP:
                player.jump = True
                jump_fx.play()
            if event.key == pygame.K_ESCAPE:
                run = False
            if event.key == pygame.K_v and settings.firingModesOn:
                changeFiringModes.getCurrentFiringMode()


        #keyboard button released
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_a or event.key == pygame.K_LEFT:
                moving_left = False
            if event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                moving_right = False
            if event.key == pygame.K_f:
                shoot = False
                settings.automaticMode = False
            if event.key == pygame.K_q:
                grenade = False
                grenade_thrown = False


    pygame.display.update()






pygame.quit()
exit()
