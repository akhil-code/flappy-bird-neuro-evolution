from numpy import random, array, reshape
from math import floor
import pygame
from genetic import Population

def do_overlap(rect1, rect2):
    l1, r1 = rect1.topleft, rect1.bottomright
    l2, r2 = rect2.topleft, rect2.bottomright
    # condition to not overlap
    if r1[0] < l2[0] or r2[0] < l1[0]:
        return False
    if r2[1] < l1[1] or r1[1] < l2[1]:
        return False

    return True

class Color:
    RED = (255,0,0)
    GREEN = (0,255,0)
    BLUE = (0,0,255)
    WHITE = (255,255,255)
    YELLOW = (255,255,0)
    BLACK = (0,0,0)

    colors = array([RED, GREEN, BLUE, WHITE, YELLOW])

class Game:
    WIDTH = 640             # width of screen
    HEIGHT = 480            # height of screen
    FRAME_RATE = 1200        # FPS
    FRAMES = 0              # counts number of frames elapsed
    TITLE = 'Flappy bird'   # Window Title
    EXIT = False            # Flag to exit the game
    GAME_OVER = False       # Flag to denote if it's game over
    ICON_PATH = 'res/icon.jpg'
    MANUAL = False
    # MANUAL = True

    # initializes required objects required for game
    def initialize():
        pygame.init()

        # screen parameters
        icon = pygame.image.load(Game.ICON_PATH)
        pygame.display.set_icon(icon)
        pygame.display.set_caption(Game.TITLE)
        screen = pygame.display.set_mode(Game.get_dimensions())

        # Feature limits
        feature_limits = array([Game.HEIGHT, 100, Game.HEIGHT, Game.HEIGHT, Game.WIDTH])
        Game.feature_limits = reshape(feature_limits, (1,-1))
        
        # reference clock
        clock = pygame.time.Clock()
        
        # initializing game objects
        population = Population(pop_size=30, feature_limits=Game.feature_limits)
        pipes = []

        return screen, clock, population, pipes

    def reset():
        Game.FRAMES = 0
        pipes = []
        return pipes
    
    def check_for_collision(population, pipes):
        for pipe in pipes:
            upper_rect, lower_rect = pipe.get_pipe_rects()
            for individual in population.individuals:
                if not individual.bird.game_over:
                    bird_rect = individual.bird.get_rect()
                    touch_pipes = do_overlap(bird_rect, upper_rect) or do_overlap(bird_rect, lower_rect)
                    if touch_pipes:
                        individual.bird.game_over = True
        
        for individual in population.individuals:
            bird = individual.bird
            if not bird.game_over and (bird.posy < 0 or bird.posy+bird.height > Game.HEIGHT):
                bird.game_over = True


    
    def update_scores(population):
        for individual in population.individuals:
            bird = individual.bird
            if not bird.game_over:
                individual.bird.score = Game.FRAMES
        
    def update_objects(population, pipes):
        # move pipes on the screen
        pipes = Pipe.move_pipes(pipes)

        # update bird objects
        for individual in population.individuals:
            if not individual.bird.game_over:
                individual.bird.update()
        
        population.update(Pipe.get_nearest_pipe(population.individuals[0].bird, pipes))

        # check if the birds hit the pipes
        Game.check_for_collision(population, pipes)

        # update scores of birds
        Game.update_scores(population)


    def get_dimensions():
        return (Game.WIDTH, Game.HEIGHT)
    
    def draw_screen(screen, population, pipes):
        Game.FRAMES += 1
        screen.fill(Color.BLACK)

        # draw bird
        for individual in population.individuals:
            bird = individual.bird
            if not bird.game_over:
                pygame.draw.circle(screen, bird.color, bird.get_center(), bird.radius)


        for pipe in pipes:
            upper_rect, lower_rect = pipe.get_pipe_rects()
            pygame.draw.rect(screen, Color.WHITE, upper_rect)
            pygame.draw.rect(screen, Color.WHITE, lower_rect)
        
        # update whole screen
        pygame.display.update()
    
    
    def loop(screen, clock, population, pipes):
        while not Game.EXIT:
            # objects updated for each frame
            Game.update_objects(population, pipes)

            # manual input by human
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.EXIT = True
                elif event.type == pygame.KEYDOWN and Game.MANUAL:
                    if event.key == pygame.K_UP:
                        population.individuals[0].bird.fly()
            
            if Game.are_all_birds_dead(population):
                population.evolve()
                population.reset_individuals_to_inital_state()
                pipes = Game.reset()

            Game.draw_screen(screen, population, pipes)
            clock.tick(Game.FRAME_RATE)
    
    def are_all_birds_dead(population):
        for individual in population.individuals:
            if not individual.bird.game_over:
                return False
        return True
    

class Bird:
    ANIMATION_RATE = 5      # animates for every 5 elapsed frames
    def __init__(self):
        self.radius = 15
        self.width = self.radius*2
        self.height = self.radius*2
        self.posx = 0
        self.posy = int(Game.HEIGHT/2)
        # gravitation parameters
        self.velocity = 0
        self.gravity = 0.08

        self.color = (
            random.randint(256),
            random.randint(256),
            random.randint(256),
        )

        self.score = 0
        self.game_over = False
        self.last_update = 0

    def get_center(self):
        x = self.posx + self.radius
        y = self.posy + self.radius
        return (x,y)
    
    def update(self):
        t = Game.FRAMES - self.last_update
        if t > Bird.ANIMATION_RATE:
            u = self.velocity
            a = self.gravity
            s = self.posy
            # updating position and velocity based on equations of motion
            self.posy += floor((u*t) + (0.5*(a*t*t)))
            self.velocity = u + a*t

            # if bird goes above the screen
            # if self.posy < 0:
                # self.posy = 0
            
            # if it goes below the screen
            # elif self.posy + self.height > Game.HEIGHT:
                # self.posy = Game.HEIGHT - self.height
            
            # stores the instant, when updated
            self.last_update = Game.FRAMES
    
    def fly(self):
        self.velocity = -3      # impulsive velocity in upward direction
    
    def get_rect(self):
        return pygame.rect.Rect(self.posx, self.posy, self.width, self.height)


class Pipe:
    gap_width = 175             # vertical gap between two pipes
    width = 30                  # width of each pipe
    space_between_pipes = 350   # space between two adjacent pipes
    stepx = 5                   # pipes move in x direction by 5px
    ANIMATION_RATE = 5          # animates after every 5th frame

    def __init__(self):
        # space between two vertical pipes is denoted as gap
        self.gap_start = random.randint(0, high=Game.HEIGHT - Pipe.gap_width)
        self.gap_end = self.gap_start + Pipe.gap_width
        self.posx = Game.WIDTH
        # stores the latest instant when updated
        self.last_update = 0
    
    def update(self):
        t = Game.FRAMES - self.last_update
        if t > Pipe.ANIMATION_RATE:
            self.posx -= Pipe.stepx
            self.last_update = Game.FRAMES
    
    def get_pipe_rects(self):
        # upper pipe
        pipe_position = (self.posx, 0)
        pipe_dimensions = (self.width, self.gap_start)
        upper_rect = pygame.Rect(pipe_position, pipe_dimensions)
        
        # lower pipe
        pipe_position = (self.posx, self.gap_end)
        pipe_dimensions = (self.width, Game.HEIGHT - self.gap_end)
        lower_rect = pygame.Rect(pipe_position, pipe_dimensions)

        return upper_rect, lower_rect

    def move_pipes(pipes):
        if len(pipes) > 0:
            # add new pipe if possible
            last_pipe = pipes[-1]
            if last_pipe.posx + Pipe.width + Pipe.space_between_pipes < Game.WIDTH:
                pipes.append(Pipe())
            
            # remove first pipe if it stripes away from screen
            first_pipe = pipes[0]
            if first_pipe.posx + Pipe.width < 0:
                del pipes[0]
        else:
            # add new pipe
            pipes.append(Pipe())
        
        # update each of pipe object
        for pipe in pipes:
            pipe.update()
        
        return pipes

    def get_nearest_pipe(bird, pipes):
        for pipe in pipes:
            if bird.posx < pipe.posx + pipe.width:
                return pipe


