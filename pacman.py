# Pacman in Python with PyGame
# This code was originally taken from https://github.com/hbokmann/Pacman and adapted according to
# the Electronic Arts Software Engineering Virtual Experience Program challenge (Task 1)

# The game consists of an adaptation of the PacMan game, called VaxMan, and has the following rules:
#
# 1) Vax-Man can kill a ghost if he comes into contact with it (vaccinates it).
# 2) Contact with a ghost does not kill Vax-Man.
# 3) Each ghost that has not yet been hit multiplies itself every 30 seconds (the infection grows).
# 4) The goal of the game is to collect all the dots before the number of ghosts grows to 32 times the original number.

import pygame

# The colors used in the game are defined here
black  = (0,0,0)
white  = (255,255,255)
red    = (255,0,0)
green  = (0,255,0)
blue   = (0,0,255)
yellow = (255,255,0)
purple = (255,0,255)

playerIcon = pygame.image.load('images/Player.png')
pygame.display.set_icon(playerIcon)

# Call this function so the Pygame library can initialize itself
pygame.init()

# Create an 606x606 sized screen
screen = pygame.display.set_mode([606, 606])

# Set the title of the window
pygame.display.set_caption('Pacman')

# Create a surface we can draw on
background = pygame.Surface(screen.get_size())
background = background.convert() # Used for converting color maps and such
background.fill(black) # Fill the screen with a black background

clock = pygame.time.Clock()

pygame.font.init()
font = pygame.font.Font("freesansbold.ttf", 24)


# This class represents the bar at the bottom that the player controls
class Wall(pygame.sprite.Sprite):
  # Constructor function
  def __init__(self, x, y, width, height, color):
    # Call the parent's constructor
    pygame.sprite.Sprite.__init__(self)

    # Make a blue wall, of the size specified in the parameters
    self.image = pygame.Surface([width, height])
    self.image.fill(color)

    # Make our top-left corner the passed-in location.
    self.rect = self.image.get_rect()
    self.rect.top = y
    self.rect.left = x


# This class represents the "coins"
# It derives from the "Sprite" class in Pygame
class Block(pygame.sprite.Sprite):

  # Constructor: Pass in the color of the block and its x and y position
  def __init__(self, color, width, height):
    # Call the parent class (Sprite) constructor
    pygame.sprite.Sprite.__init__(self)

    # Create an image of the block, and fill it with a color.
    # This could also be an image loaded from the disk.
    self.image = pygame.Surface([width, height])
    self.image.fill(white)
    self.image.set_colorkey(white)
    pygame.draw.ellipse(self.image, color, [0, 0, width, height])

    # Fetch the rectangle object that has the dimensions of the image image.
    # Update the position of this object by setting the values of rect.x and rect.y
    self.rect = self.image.get_rect()


# This class represents the bar at the bottom that the player controls
class Player(pygame.sprite.Sprite):
  # Constructor function
  def __init__(self, x, y, filename = '', change_x = 0, change_y = 0):
    # Call the parent's constructor
    pygame.sprite.Sprite.__init__(self)

    self.start_x = x
    self.start_y = y

    # Set filename
    self.filename = filename

    # Set speed vector
    self.change_x = change_x
    self.change_y = change_y

    # Set height, width
    self.image = pygame.image.load(self.filename).convert()

    # Make our top-left corner the passed-in location.
    self.rect = self.image.get_rect()
    self.rect.top = y
    self.rect.left = x
    self.prev_x = x
    self.prev_y = y

  # Clear the speed of the player
  def prevdirection(self):
    self.prev_x = self.change_x
    self.prev_y = self.change_y

  # Change the speed of the player
  def changespeed(self, x, y):
    self.change_x += x
    self.change_y += y

  # Find a new position for the player
  def update(self, walls, gate):
    # Get the old position, in case we need to go back to it
    old_x = self.rect.left
    old_y = self.rect.top

    new_x = old_x + self.change_x
    new_y = old_y + self.change_y

    self.rect.left = new_x
    # Did this update cause us to hit a wall?
    x_collide = pygame.sprite.spritecollide(self, walls, False)
    if x_collide:
        # Whoops, hit a wall. Go back to the old position
        self.rect.left = old_x
    else:
      self.rect.top = new_y
      # Did this update cause us to hit a wall?
      y_collide = pygame.sprite.spritecollide(self, walls, False)
      if y_collide:
        # Whoops, hit a wall. Go back to the old position
        self.rect.top = old_y


    if gate != False:
      gate_hit = pygame.sprite.spritecollide(self, gate, False)
      if gate_hit:
        self.rect.left = old_x
        self.rect.top = old_y


# Inheritime Player class
class Ghost(Player):
  def __init__(self, x, y, movement_list, name, filename):
    super().__init__(x, y, filename)
    self.turn = 0
    self.steps = 0
    self.movement_list = movement_list
    self.name = name

  def duplicate(self):
    new_ghost = Ghost(self.start_x, self.start_y, self.movement_list, self.name, self.filename)
    monster_list.add(new_ghost)
    all_sprites_list.add(new_ghost)

  # Change the speed of the ghost
  def changespeed(self):
    try:
      max_steps = self.movement_list[self.turn][2]
      if self.steps < max_steps:
        self.change_x = self.movement_list[self.turn][0]
        self.change_y = self.movement_list[self.turn][1]
        self.steps += 1
      else:
        if self.turn < len(self.movement_list)-1:
          self.turn += 1
        elif self.name in ["Clyde", "Inky"]:
          self.turn = 2
        else:
          self.turn = 0
        self.change_x = self.movement_list[self.turn][0]
        self.change_y = self.movement_list[self.turn][1]
        self.steps = 0
    except IndexError:
      return [0,0]


# Default directions for the ghosts
Blinky_directions = [
  [0,-15,4],
  [15,0,9],
  [0,15,11],
  [15,0,3],
  [0,15,7],
  [-15,0,11],
  [0,15,3],
  [15,0,15],
  [0,-15,15],
  [15,0,3],
  [0,-15,11],
  [-15,0,3],
  [0,-15,11],
  [-15,0,3],
  [0,-15,3],
  [-15,0,7],
  [0,-15,3],
  [15,0,15],
  [0,15,15],
  [-15,0,3],
  [0,15,3],
  [-15,0,3],
  [0,-15,7],
  [-15,0,3],
  [0,15,7],
  [-15,0,11],
  [0,-15,7],
  [15,0,5]
]

Pinky_directions = [
  [0,-30,4],
  [15,0,9],
  [0,15,11],
  [-15,0,23],
  [0,15,7],
  [15,0,3],
  [0,-15,3],
  [15,0,19],
  [0,15,3],
  [15,0,3],
  [0,15,3],
  [15,0,3],
  [0,-15,15],
  [-15,0,7],
  [0,15,3],
  [-15,0,19],
  [0,-15,11],
  [15,0,9]
]

Inky_directions = [
  [15,0,2],
  [0,-30,4],
  [15,0,10],
  [0,15,7],
  [15,0,3],
  [0,-15,3],
  [15,0,3],
  [0,-15,15],
  [-15,0,15],
  [0,15,3],
  [15,0,15],
  [0,15,11],
  [-15,0,3],
  [0,-15,7],
  [-15,0,11],
  [0,15,3],
  [-15,0,11],
  [0,15,7],
  [-15,0,3],
  [0,-15,3],
  [-15,0,3],
  [0,-15,15],
  [15,0,15],
  [0,15,3],
  [-15,0,15],
  [0,15,11],
  [15,0,3],
  [0,-15,11],
  [15,0,11],
  [0,15,3],
  [15,0,1],
]

Clyde_directions = [
  [-15,0,2],
  [0,-30,4],
  [15,0,5],
  [0,15,7],
  [-15,0,11],
  [0,-15,7],
  [-15,0,3],
  [0,15,7],
  [-15,0,7],
  [0,15,15],
  [15,0,15],
  [0,-15,3],
  [-15,0,11],
  [0,-15,7],
  [15,0,3],
  [0,-15,11],
  [15,0,9],
]


# default locations for Pacman and monsters at the start of the game
pacman_start_x = 303-16
pacman_start_y = (7*60)+19

blink_start_x = 303-16
blink_start_y = (3*60)+19

pinky_start_x = 303-16
pinky_start_y = (4*60)+19

inky_start_x = 303-16-32
inky_start_y = (4*60)+19

clyde_start_x = 303+(32-16)
clyde_start_y = (4*60)+19


# This creates all the walls in room 1
def setupRoomOne(all_sprites_list):
  # Make the walls. (x_pos, y_pos, width, height)
  wall_list = pygame.sprite.RenderPlain()

  # This is a list of walls. Each is in the form [x, y, width, height]
  walls = [
    [0,0,6,600],
    [0,0,600,6],
    [0,600,606,6],
    [600,0,6,606],
    [300,0,6,66],
    [60,60,186,6],
    [360,60,186,6],
    [60,120,66,6],
    [60,120,6,126],
    [180,120,246,6],
    [300,120,6,66],
    [480,120,66,6],
    [540,120,6,126],
    [120,180,126,6],
    [120,180,6,126],
    [360,180,126,6],
    [480,180,6,126],
    [180,240,6,126],
    [180,360,246,6],
    [420,240,6,126],
    [240,240,42,6],
    [324,240,42,6],
    [240,240,6,66],
    [240,300,126,6],
    [360,240,6,66],
    [0,300,66,6],
    [540,300,66,6],
    [60,360,66,6],
    [60,360,6,186],
    [480,360,66,6],
    [540,360,6,186],
    [120,420,366,6],
    [120,420,6,66],
    [480,420,6,66],
    [180,480,246,6],
    [300,480,6,66],
    [120,540,126,6],
    [360,540,126,6]
  ]

  # Loop through the list. Create the wall, add it to the list
  for item in walls:
    wall = Wall(item[0], item[1], item[2], item[3], blue)
    wall_list.add(wall)
    all_sprites_list.add(wall)

  # return our new list
  return wall_list


def setupGate(all_sprites_list):
  gate = pygame.sprite.RenderPlain()
  gate.add(Wall(282, 242, 42, 2, white))
  all_sprites_list.add(gate)
  return gate


# Define all the lists used
all_sprites_list = []
block_list = []
monster_list = []
pacman_collide = []
wall_list = []
gate = []

def startLists():
  global all_sprites_list, block_list, monster_list, pacman_collide, wall_list, gate

  all_sprites_list = pygame.sprite.RenderPlain()
  block_list = pygame.sprite.RenderPlain()
  monster_list = pygame.sprite.RenderPlain()
  pacman_collide = pygame.sprite.RenderPlain()
  wall_list = setupRoomOne(all_sprites_list)
  gate = setupGate(all_sprites_list)


def clearLists(all_sprites_list, block_list, monster_list, pacman_collide, wall_list, gate):
  del all_sprites_list
  del block_list
  del monster_list
  del pacman_collide
  del wall_list
  del gate


def drawGrid():
  for row in range(19):
    for column in range(19):
      if (row == 7 or row == 8) and (column == 8 or column == 9 or column == 10):
        continue
      else:
        block = Block(yellow, 4, 4)

        # Set a random location for the block
        block.rect.x = (30*column+6)+26
        block.rect.y = (30*row+6)+26

        b_collide = pygame.sprite.spritecollide(block, wall_list, False)
        p_collide = pygame.sprite.spritecollide(block, pacman_collide, False)
        if b_collide or p_collide:
          continue
        else:
          # Add the block to the list of objects
          block_list.add(block)
          all_sprites_list.add(block)


def startGame():
  startLists()

  start_time = pygame.time.get_ticks()

  # Create the player paddle object and the initial monsters
  Pacman = Player(pacman_start_x, pacman_start_y, "images/Player.png")
  all_sprites_list.add(Pacman)
  pacman_collide.add(Pacman)

  Blinky = Ghost(blink_start_x, blink_start_y, Blinky_directions, "Blinky", "images/Blinky.png")
  monster_list.add(Blinky)
  all_sprites_list.add(Blinky)

  Pinky = Ghost(pinky_start_x, pinky_start_y, Pinky_directions, "Pinky", "images/Pinky.png")
  monster_list.add(Pinky)
  all_sprites_list.add(Pinky)

  Inky = Ghost(inky_start_x, inky_start_y, Inky_directions, "Inky", "images/Inky.png")
  monster_list.add(Inky)
  all_sprites_list.add(Inky)

  Clyde = Ghost(clyde_start_x, clyde_start_y, Clyde_directions, "Clyde", "images/Clyde.png")
  monster_list.add(Clyde)
  all_sprites_list.add(Clyde)

  drawGrid()

  bll = len(block_list)

  score = 0

  done = False

  while done == False:
    # Duplicate the monsters every 30 seconds and reset timer
    current_time = pygame.time.get_ticks()
    if (current_time - start_time > 30000):
      for monster in monster_list:
        monster.duplicate()

      start_time = current_time

    # End game condition
    if (len(monster_list) >= 128):
      done = True
      doNext("Oh no! The monsters won!", 145, all_sprites_list, block_list, monster_list, pacman_collide, wall_list, gate)


    # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        done=True

      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_LEFT:
          Pacman.changespeed(-30,0)
        if event.key == pygame.K_RIGHT:
          Pacman.changespeed(30,0)
        if event.key == pygame.K_UP:
          Pacman.changespeed(0,-30)
        if event.key == pygame.K_DOWN:
          Pacman.changespeed(0,30)

      if event.type == pygame.KEYUP:
        if event.key == pygame.K_LEFT:
          Pacman.changespeed(30,0)
        if event.key == pygame.K_RIGHT:
          Pacman.changespeed(-30,0)
        if event.key == pygame.K_UP:
          Pacman.changespeed(0,30)
        if event.key == pygame.K_DOWN:
          Pacman.changespeed(0,-30)
    # ALL EVENT PROCESSING SHOULD GO ABOVE THIS COMMENT



    # ALL GAME LOGIC SHOULD GO BELOW THIS COMMENT
    Pacman.update(wall_list, gate)

    for monster in monster_list:
      monster.changespeed()
      monster.update(wall_list, False)

    # See if the Pacman block has collided with anything.
    blocks_hit_list = pygame.sprite.spritecollide(Pacman, block_list, True)

    # Check the list of collisions.
    if len(blocks_hit_list) > 0:
      score +=len(blocks_hit_list)
    # ALL GAME LOGIC SHOULD GO ABOVE THIS COMMENT



    # ALL CODE TO DRAW SHOULD GO BELOW THIS COMMENT
    screen.fill(black)

    wall_list.draw(screen)
    gate.draw(screen)
    all_sprites_list.draw(screen)
    monster_list.draw(screen)

    text = font.render("Score: "+str(score)+"/"+str(bll), True, red)
    screen.blit(text, [10, 10])

    monster_count_text = font.render("Monsters: "+str(len(monster_list)), True, green)
    screen.blit(monster_count_text, [400, 10])

    if score == bll:
      doNext("Congratulations, you won!", 145, all_sprites_list, block_list, monster_list, pacman_collide, wall_list, gate)

    pygame.sprite.spritecollide(Pacman, monster_list, True)
    # ALL CODE TO DRAW SHOULD GO ABOVE THIS COMMENT

    pygame.display.flip()
    clock.tick(10)

def doNext(message, left, all_sprites_list, block_list, monster_list, pacman_collide, wall_list, gate):
  while True:
    # ALL EVENT PROCESSING SHOULD GO BELOW THIS COMMENT
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
          pygame.quit()
        if event.key == pygame.K_RETURN:
          clearLists(all_sprites_list, block_list, monster_list, pacman_collide, wall_list, gate)
          startGame()

    # Grey background
    w = pygame.Surface((400, 200)) # the size of your rect
    w.set_alpha(10)                # alpha level
    w.fill((128, 128, 128))        # this fills the entire surface
    screen.blit(w, (100, 200))     # (0,0) are the top-left coordinates

    # Won or lost
    text1 = font.render(message, True, white)
    screen.blit(text1, [left, 233])

    text2 = font.render("To play again, press ENTER.", True, white)
    screen.blit(text2, [135, 303])

    text3 = font.render("To quit, press ESCAPE.", True, white)
    screen.blit(text3, [165, 333])

    pygame.display.flip()
    clock.tick(10)

startGame()

pygame.quit()
