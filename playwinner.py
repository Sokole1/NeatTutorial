# This file gives an example of running 1 box - the box with the highest genome. It loads in win.pkl to use its genome
# Note, it only runs once and quits when it dies, you can change the code so it keeps running
import pygame
import sys
import random
import math
import os
import neat
import pickle 
import time

pygame.init()

screen_size = (500,250)
win = pygame.display.set_mode(screen_size)
pygame.display.set_caption("Box game")
clock = pygame.time.Clock()

font = pygame.font.SysFont('comicsans', 30, True)

bg_surface = pygame.image.load('background.png').convert()
trophy = pygame.image.load('trophy.png').convert() 
trophy = pygame.transform.scale(trophy, (30, 45))
trophy_location = (460, 125)
trophy_rect = trophy.get_rect(center = trophy_location)

class BadCircle:
  colour = (255,255,0)
  radius = 5
  x_distance_travelled = 0
  y_distance_travelled = 0
  move_down = 0 # 0 is for down/right, 1 is for up/left
  move_right = 0
  
  def __init__(self, x, y, move_speed = 1, move_range = 200, up_down = True, left_right = False):
    # This is the starting x and y coordinates for the circle
    self.x = x
    self.y = y
    self.move_speed = move_speed
    self.move_range = move_range
    self.up_down = up_down
    self.left_right = left_right

  def draw(self):
    # circle(surface, color, center, radius)
    pygame.draw.circle(win, self.colour, (self.x, self.y), self.radius)
  
  def move(self):
    if self.up_down:
      # Move down until
      if self.move_down == 0:
        self.y += self.move_speed
        self.y_distance_travelled += self.move_speed
        # Once it has travelled to edge of move range, change directions
        if self.y_distance_travelled >= self.move_range or self.y > screen_size[1]:
            self.move_down = 1
            
      else: # Move back up
        self.y -= self.move_speed
        self.y_distance_travelled -= self.move_speed
        if self.y_distance_travelled <= 0 or self.y < 0:
            self.move_down = 0

    if self.left_right:
      # Move right
      if self.move_right == 0:
        self.x += self.move_speed
        self.x_distance_travelled += self.move_speed
        if self.x_distance_travelled >= self.move_range or self.x > screen_size[0]:
            self.move_right = 1

      else: # Move left
        self.x -= self.move_speed
        self.x_distance_travelled -= self.move_speed
        if self.x_distance_travelled <= 0 or self.x < 0:
            self.move_right = 0
  
class SearchRect:
    # Pass in the top_left corner of the box, where we want the rect to be in respect to it, and how big it is
    def __init__(self, box_x, box_y, x_disp, y_disp, width, height):
        self.start_x = box_x + x_disp
        self.start_y = box_y + y_disp
        self.x_disp = x_disp
        self.y_disp = y_disp
        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.start_x, self.start_y, self.width, self.height)
        self.colour = (255,255,255)
    
    def update(self, box_x, box_y):
        self.start_x = box_x + self.x_disp
        self.start_y = box_y + self.y_disp
        self.rect = pygame.Rect(self.start_x, self.start_y, self.width, self.height)
    
    def draw(self):
        pygame.draw.rect(win, self.colour, self.rect)

    def contains_circle(self, circle_x, circle_y):
        if self.rect.collidepoint(circle_x, circle_y):
            self.colour = (0,0,255)
            return True
        else:
            self.colour = (255,255,255)
            return False

class Box:
    move_speed = 3
    width = 30
    height = 30
    score = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.box = pygame.Rect(self.x, self.y, self.width, self.height)
        self.trophy_dist = math.sqrt(((self.x - trophy_location[0])**2)+((self.y - trophy_location[1])**2))
        self.colour = [255,0,0]
        self.no_move_timer = 0
        self.heighest = 0
        # All of this map is just to create 4 rectanges completely surround the box
        self.search_rects = [SearchRect(x, y, self.width // 1 * -1, self.height // 1 * -1, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, 0, self.height // 1 * -1, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width, self.height // 1 * -1, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width, 0, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width, self.height, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, 0, self.height, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width * -1, self.height, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width * -1, 0, self.width * 1.2, self.height * 1.2)]
        # self.search_rects = [SearchRect(x, y, self.width // 1 * -1, self.height // 1 * -1, self.width + self.width // 1, self.height // 1),
        #                     SearchRect(x, y, self.width, self.height // 1 * -1, self.width // 1, self.height + self.height // 1),
        #                     SearchRect(x, y, self.width // 1 * -1, 0, self.width // 1, self.height + self.height // 1),
        #                     SearchRect(x, y, 0, self.height, self.width + self.width // 1, self.height // 1)]
                        
    def draw(self):
        pygame.draw.rect(win, self.colour, self.box)

    def draw_rects(self):
        for rect in self.search_rects:
            rect.draw()
  
    def move(self, output): # Output [left, right, up, down]
        # Use these to detect if it has moved towards trophy
        initial_x = self.x
        moved = True

        if output[0] > 0.5 and self.x + self.width // 2 > 0:
            self.x -= 3
        if output[1] > 0.3 and self.x < screen_size[0] - self.width // 2:
            self.x += 3
        if output[2] > 0.5 and self.y + self.height // 2 > 0:
            self.y -= 3
        if output[3] > 0.5 and self.y < screen_size[1] - self.height // 2:
            self.y += 3

        if self.x <= self.heighest:
            self.no_move_timer += 0.1
            moved = False

        if self.x > self.heighest:
            self.no_move_timer = 0
            self.heighest = self.x

        self.box = pygame.Rect(self.x, self.y, self.width, self.height)
        for rect in self.search_rects:
            rect.update(self.x, self.y)
    
    # If Box collides with closest circle, return True
    def collision(self, circle_x, circle_y):
        if self.y - 3 <= circle_y <= self.y + self.height + 3 and self.x - 3 <= circle_x <= self.x + self.width + 3:
            self.score -= 1
            return True
        else:
            return False
    
    
    def has_won(self):
        if self.box.colliderect(trophy_rect):
            self.score += 5
            self.x = 0
            self.y = 125
            self.heighest = 0
            self.no_move_timer = 0

            return True
        else:
            return False
    
    def get_closest_circle(self, circles):
        closest_coordinates = (0,0)
        closest = 10000
        for circle in circles:
            distance = math.sqrt(((self.x - circle.x)**2)+((self.y - circle.y)**2))
            if distance < closest:
                closest = distance
                closest_coordinates = (circle.x, circle.y)
            
        dist_x = abs(self.x - closest_coordinates[0])
        dist_y = abs(self.y - closest_coordinates[1])
        return dist_x, dist_y, closest_coordinates[0], closest_coordinates[1]

    def distance_to_trophy(self):
        closer = False
        distance = math.sqrt(((self.x - trophy_location[0])**2)+((self.y - trophy_location[1])**2))
        if distance < self.trophy_dist:
            self.trophy_dist = distance
            closer = True
        return abs(self.x - trophy_location[0]), abs(self.y - trophy_location[1]), closer
        # return math.sqrt(((self.x - tropy_location[0])**2)+((self.y - tropy_location[1])**2))

    def check_rects(self, circles):
        contains_circle = []
        for rect in self.search_rects:
            for circle in circles:
                if rect.contains_circle(circle.x, circle.y):
                    contains_circle.append(50)
                    break
                elif rect.start_x < 0 or rect.start_x >= screen_size[0] - self.width // 2 or rect.start_y < 0 or rect.start_y >= screen_size[1] - self.height //2:
                    contains_circle.append(10)
                    break 
            else:
                contains_circle.append(0)
        return contains_circle



def redrawGameWindow(box, circles):
  win.blit(bg_surface,(0,0))
  win.blit(trophy, trophy_rect)
  box.draw()
  for circle in circles:
      circle.draw()
      
  pygame.display.update()


def generate_random_circles(range_x, range_y):
  circles = [BadCircle(200, 0, move_speed=3, move_range=150), BadCircle(300, 0, move_speed = 3, move_range = 300),BadCircle(400, 0, move_speed=3, move_range=150)]
  num_circles = random.randint(range_x, range_y)
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

def main(genomes, config):
  start_time = time.time()
  circles = generate_random_circles(3, 9)
  net = neat.nn.FeedForwardNetwork.create(genome, config)
  box = Box(0,125)
  run = True
  while run:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()


    for circle in circles:
        circle.move()

    dist_circle_x, dist_circle_y, circle_x, circle_y = box.get_closest_circle(circles)
    detector = box.check_rects(circles)
    trophy_x_dist, trophy_y_dist, moved_closer = box.distance_to_trophy()

    outputs = net.activate((*detector, trophy_x_dist, trophy_y_dist)) # Pass in x and y distance to closest circle and x,y to trophy

    box.move([outputs[0], outputs[1], outputs[2], outputs[3]])

    if box.collision(circle_x, circle_y): # or box.in_wall()
    # ge[index].fitness -= 5
        print("Dead")
        break

    if box.has_won():
        box.colour[1] = 30
        box.colour[0] = 0

        if int(time.time() - start_time) > 30:
            print("SHUFFLED")
            circles = generate_random_circles(6, 12)

    pygame.display.update()

    redrawGameWindow(box, circles)
    clock.tick(60)

if __name__ == '__main__':
  local_dir = os.path.dirname(__file__)
  config_path = os.path.join(local_dir, "config-feedforward.txt")
  with open("win.pkl", "rb") as f:
    genome = pickle.load(f)
  config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
  main(genome, config)
  time.sleep(2)



