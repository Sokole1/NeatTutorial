# This is to watch the AI train over the generations.
# If you have any code questions, ask on Teams and tell me the file and which lines
# https://neat-python.readthedocs.io/en/latest/config_file.html Here is a link to learn more about the config-feedforward.txt file

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
        # All of this math is just to create 8 rectanges completely surround the box
        self.search_rects = [SearchRect(x, y, self.width // 1 * -1, self.height // 1 * -1, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, 0, self.height // 1 * -1, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width, self.height // 1 * -1, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width, 0, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width, self.height, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, 0, self.height, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width * -1, self.height, self.width * 1.2, self.height * 1.2),
                            SearchRect(x, y, self.width * -1, 0, self.width * 1.2, self.height * 1.2)]
                        
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
        if output[1] > 0.5 and self.x < screen_size[0] - self.width // 2:
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

def redrawGameWindow(boxes, circles):
  win.blit(bg_surface,(0,0))
  win.blit(trophy, trophy_rect)
  for box in boxes:
    box.draw()
    box.draw_rects()
  for circle in circles:
      circle.draw()
      
  pygame.display.update()

def generate_random_circles(range_x, range_y):
    circles = [BadCircle(200, 0, move_speed=3, move_range=150), BadCircle(300, 0, move_speed = 3, move_range = 300),BadCircle(400, 0, move_speed=3, move_range=150),BadCircle(350, 0, move_speed=4, move_range=150),BadCircle(320, 0, move_speed=4, move_range=150)]
    num_circles = random.randint(range_x, range_y)
    for _ in range(num_circles):
        start_x = random.randint(100, screen_size[0] // 1.2)
        start_y = random.randint(0, screen_size[1] // 1.2)
        move_range = random.randint(100, 300)
        move_speed = random.randrange(1, 3)
        circles.append(BadCircle(start_x, start_y, move_speed, move_range))

    return circles

def main(genomes, config):
  start_time = time.time()
  nets = [] # Neural networks
  ge = [] # Genomes
  boxes = []
  circles = generate_random_circles(3, 5)
  for _, g in genomes: # Set up a neural network for our genome
    net = neat.nn.FeedForwardNetwork.create(g, config)
    nets.append(net)
    boxes.append(Box(0,125))
    g.fitness = 0
    ge.append(g)

  run = True
  while run:
    for event in pygame.event.get():
      if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()
    
    if len(boxes) == 0: # When all boxes dead
      run = False
      break

    for circle in circles:
        circle.move()

    for index, box in enumerate(boxes):
        dist_circle_x, dist_circle_y, circle_x, circle_y = box.get_closest_circle(circles)
        detector = box.check_rects(circles) # Returns a list of 8 numbers corresponding to 50, 10, or 10 if a circle is inside it, it's touching a wall, or nothing
      
        trophy_x_dist, trophy_y_dist, moved_closer = box.distance_to_trophy()

        if moved_closer: # We want to reward it whenever it moves forward
            ge[index].fitness += 0.01
    
        outputs = nets[index].activate((*detector, trophy_x_dist, trophy_y_dist)) # Pass in x and y distance to closest circle and x,y to trophy

        box.move([outputs[0], outputs[1], outputs[2], outputs[3]])

        if box.collision(circle_x, circle_y):
            boxes.pop(index)
            nets.pop(index)
            ge.pop(index)
                
        if box.no_move_timer >= 30:
            if box.x < 100 or box.x > 400: # Punish boxes that stop moving in the beginning or end
                ge[index].fitness -= 2

            boxes.pop(index)
            nets.pop(index)
            ge.pop(index)

        if box.has_won():
            ge[index].fitness += 50
            box.colour[1] = 30
            box.colour[0] = 0
            # This is to make the game harder each time they win if they have survived more than 30 seconds
            if int(time.time() - start_time) > 30:
                print("SHUFFLED")
                circles = generate_random_circles(6, 12)

    pygame.display.update()
    redrawGameWindow(boxes, circles)
    clock.tick(60)

def run(config_path):
    use_checkpoint = False # Set this to True if you want to load in a checkpoint, False to start from generation 1

    if use_checkpoint: # Checkout the 'Checkpoints' folder to see some checkpoints, I deleted most of them, but 339 is probably one of the best
        population = neat.Checkpointer.restore_checkpoint(os.path.join("Checkpoints", "box-checkpoint-339"))
    
    else:
        config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)
        population = neat.Population(config)

    # Just add these stat reporters so we can see what is happening
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.Checkpointer(generation_interval=10,
                                            time_interval_seconds=5000, filename_prefix=os.path.join("Checkpoints","box-checkpoint-")))

    winner = population.run(main,100) # Get the winner (highest fitness genome) out of 100 generations
    # Save the winner to win.pkl file
    with open("win.pkl", "wb") as f:
        pickle.dump(winner, f, 1)

# This just finds the configuration file and runs the "run" function
if __name__ == '__main__':
  local_dir = os.path.dirname(__file__)
  config_path = os.path.join(local_dir, "config-feedforward.txt")
  run(config_path)


