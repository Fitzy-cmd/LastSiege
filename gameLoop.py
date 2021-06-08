from main import *
from settings import *
import settings
import pygame


while settings.run:

    clock.tick(FPS)
    if settings.start_game == False:
        mainGame.mainMenu()

    else:
        mainGame.gameRun()
        

pygame.quit()
exit()