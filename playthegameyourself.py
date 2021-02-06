# This is to try the game yourself, it's not that easy!

import pygame
import sys
import os
import random

# Always must write pygame.init() to start
pygame.init()
screen_size = [500,250]
# This is to set up a window, our window size is (500,250), normally you would want to make the window size a variable so you can change it later if you have to or use the window size to position items such as win_size = (500,250). Then we can position something in the middle by doing 
# (win_size[0] // 2, win_size[0] // 2)
win = pygame.display.set_mode((500,250))
# Caption is what appears at the top of the window
pygame.display.set_caption("Box game")
# Clock tracks time and can control framerate
clock = pygame.time.Clock()
# This is how to set up a font in pygame, you can have multiple
font = pygame.font.SysFont('comicsans', 30, True)
# This is how to load in an image, notice how we have unnamed.png in the same folder as main.py
bg_surface = pygame.image.load('background.png').convert()
# .convert() resizes the image to match our display.set_mode size
trophy = pygame.image.load('trophy.png').convert() 
# remove bg.com is a website to make the background transparent

# pygame.transform.scale resizes an image
trophy = pygame.transform.scale(trophy, (30, 45))
# Get rectangle we can track that is the same size as our trophy image
trophy_rect = trophy.get_rect(center = (460, 125))

# REPL CANNOT PLAY MUSIC, download python and run on own computer
music = pygame.mixer.music.load(os.path.join('resources','Hall of the Mountain King.mp3'))
pygame.mixer.music.play(-1)

hit_sound = pygame.mixer.Sound(os.path.join('resources','hit.wav'))

box_colour = (255,0,0)
box_x = 0
box_y = 125
box_width = 40
box_height = 40
score = 0

# Create our character rectangle
box = pygame.Rect(box_x, box_y, box_width, box_height)

def win_collision():
  global box_x, box_y, score, circles
  # This is one way to detect if rectangles collided
  if box.colliderect(trophy_rect):
    # This is the code to put text on a screen, notice how it is font.render where font is the variable we created at the top with pygame.font.SysFont()
    text = font.render('You win!', 1, (255,0,0))
    # (250, 100) is the location of the text, we hard coded this value
    win.blit(text, (250, 100))
    print("You win!")
    score += 5
    redrawGameWindow()
    #Copy this code to delay the game
    i = 0
    while i < 200:
        pygame.time.delay(10)
        i += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                i = 201
                pygame.quit()
    # print resetting
    box_x = 0
    box_y = 125
    circles = generate_random_circles()
    redrawGameWindow()
    
class BadCircle:
  colour = (255,255,0)
  radius = 5
  x_distance_travelled = 0
  y_distance_travelled = 0
  move_dir = 0 # 0 is for down/right, 1 is for up/left
  
  def __init__(self, x, y, move_speed = 1, move_range = 200):
    # This is the starting x and y coordinates for the circle
    self.x = x
    self.y = y
    self.move_speed = move_speed
    self.move_range = move_range
    
  def draw(self):
    # circle(surface, color, center, radius)
    pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius)
  
  def move(self, up_down = False, left_right = False):
    if up_down:
      # Move down until
      if self.move_dir == 0:
        self.y += self.move_speed
        self.y_distance_travelled += self.move_speed
        # Once it has travelled to edge of move range, change directions
        if self.y_distance_travelled >= self.move_range:
            self.move_dir = 1
            
      else: # Move back up
        self.y -= self.move_speed
        self.y_distance_travelled -= self.move_speed
        if self.y_distance_travelled <= 0:
            self.move_dir = 0

    if left_right:
      # Move right
      if self.move_dir == 0:
        self.x += self.move_speed
        self.x_distance_travelled += self.move_speed
        if self.x_distance_travelled >= self.move_range:
            self.move_dir = 1

      else: # Move left
        self.x -= self.move_speed
        self.x_distance_travelled -= self.move_speed
        if self.x_distance_travelled <= 0:
            self.move_dir = 0
            
  def collision(self):
      global box_x, box_y, score
      if box_y <= self.y <= box_y + box_height and box_x <= self.x <= box_x + box_width:
          print("Collision")
          hit_sound.play()
          box_x = 0
          box_y = 125
          redrawGameWindow()
          score -= 1


def generate_random_circles():
  circles = [BadCircle(200, 0, move_speed=3, move_range=150), BadCircle(300, 0, move_speed = 3, move_range = 300),BadCircle(400, 0, move_speed=3, move_range=150)]
  num_circles = random.randint(3,9)
  for _ in range(num_circles):
    start_x = random.randint(100, screen_size[0] // 1.2)
    start_y = random.randint(0, screen_size[1] // 1.2)
    move_range = random.randint(100, 300)
    # up_down = bool(random.getrandbits(1))
    # left_right = bool(random.getrandbits(1))
    # if not up_down and not left_right:
        # up_down = True
    move_speed = random.randrange(1, 3)
    circles.append(BadCircle(start_x, start_y, move_speed, move_range))
    # print("Created circle:",start_x, start_x, move_speed, move_range, up_down, left_right)

  return circles

circles = generate_random_circles()


def redrawGameWindow():
  win.blit(bg_surface,(0,0))
  win.blit(trophy, trophy_rect)
  game_score = font.render(str(score), 1, (0,0,0))
  # (250 - (game_score.get_width()/2) helps us center the x position of the text as the text. try removing the subtraction part and change the game_score to a big number. It will hang off to the right
  win.blit(game_score, (250 - (game_score.get_width()/2), 5)) # this is to make sure text is always centered
  pygame.draw.rect(win, box_colour, box)
  for circle in circles:
      circle.draw()
  # you must always update the display or else your changes won't show
  pygame.display.update()

while True:
  # This just allows the player to quit pygame if they hit the red x at the top right, always include this code 
  for event in pygame.event.get():
    if event.type == pygame.QUIT:
      pygame.quit()
      sys.exit()

  # This stores every key press
  keys = pygame.key.get_pressed()
  if keys[pygame.K_w]:
    if box_y > 0:
      box_y -= 3
  if keys[pygame.K_s]:
    if box_y < 200:
      box_y += 3
  if keys[pygame.K_a]:
    if box_x > 0:
      box_x -= 3
  if keys[pygame.K_d]:
    if box_x < 440:
      box_x += 3
    
    
  box = pygame.Rect(box_x, box_y, box_width, box_height)
  for circle in circles:
      circle.move(up_down = True)
      if circle.collision():
        break
  win_collision()
  #update display
  redrawGameWindow()
  # Setting the framerate
  clock.tick(60)
