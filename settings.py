import pygame

SCREEN_WIDTH = 800
SCREEN_HEIGHT = int(SCREEN_WIDTH * 0.8)

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Shooter')

#set framerate
clock = pygame.time.Clock()
FPS_OPTIONS = [30,60,100,144,165]
FPS = FPS_OPTIONS[0]

#define game variables
GRAVITY = 0.75
SCROLL_THRESH = 200
ROWS = 16
COLS = 150
TILE_SIZE = SCREEN_HEIGHT // ROWS
TILE_TYPES = 21
MAX_LEVELS = 2
screen_scroll = 0
bg_scroll = 0
level = 1
start_game = False
start_intro = False
achievementMenu = False
controlsMenu = False
gameCompleted = False
firingModesOn = False
firingModes = ['Semi', '3 Round Burst', 'Automatic']
firingModeCounter = 0
activeFiringMode = firingModes[firingModeCounter]
burstAmount = 3
automaticMode = False
timeCompleted = 0
timerStarted = False
startTime = 0
endTime = 0
score = 0
ammo = 20
grenades = 9


#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False



##Achievement Flags
armyspecialist = "Army Specialist"
pacifist = "Pacifist"
assassin = "Assassin"
immortal = "Immortal"
resourceful = "Resourceful"
triggerfinger = "Trigger Finger"
explosivesexpert = "Explosives Expert"
speedrunner = "Speedrunner"
sniper = "Sniper"
lastlegs = "Last Legs"
optionsoptionsoptions = "Options, Options, Options"
pathofdestruction = "Path of Destruction"
counter = 0

#Achievement variables - used to track player's progress
shotsFired = 0
grenadesThrown = 0
enemyCounter = 0
totalEnemyCounter = 0
damageTaken = 0
enemiesKilled = 0
itemBoxesGained = 0
shotsHit = 0
enemiesDamagedByGrenades = 0 #this should equal grenades thrown if every grenade successfully did damage to an enemy
roundsFinishedWithEmptyMagazine = 0
