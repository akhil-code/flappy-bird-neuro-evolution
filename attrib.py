from math import floor

import pygame
from numpy import array, random, reshape

from genetic import Population


def do_overlap(rect1, rect2):
    """ utility function to check if two rectangles overlap"""
    l1, r1 = rect1.topleft, rect1.bottomright
    l2, r2 = rect2.topleft, rect2.bottomright
    # conditions for non overlapping
    if r1[0] < l2[0] or r2[0] < l1[0]:
        return False
    if r2[1] < l1[1] or r1[1] < l2[1]:
        return False

    return True

class Color:
    """ This class stores standard colors required for game """
    RED = (255,0,0)
    GREEN = (0,255,0)
    DARK_GREEN = (0,153,0)
    BLUE = (0,0,255)
    WHITE = (255,255,255)
    YELLOW = (255,255,0)
    BLACK = (0,0,0)


class Game:
    """ Class responsible for iterating the game via frames """
    WIDTH = 640                 # width of screen
    HEIGHT = 480                # height of screen
    FRAME_RATE = 1200           # FPS (240, 1200)
    FRAMES = 0                  # counts number of frames elapsed
    TITLE = 'Flappy bird'       # Window Title
    EXIT = False                # Flag to exit the game
    GAME_OVER = False           # Flag to denote if it's game over
    ICON_PATH = 'res/icon.jpg'
    MANUAL = False

    # initializes required objects required for game
    def initialize():
        # initializes modules required for pygame
        pygame.init()

        # screen parameters
        icon = pygame.image.load(Game.ICON_PATH)
        pygame.display.set_icon(icon)
        pygame.display.set_caption(Game.TITLE)
        screen = pygame.display.set_mode(Game.get_dimensions())

        # Feature limits for neural network's normalization
        feature_limits = array([Game.HEIGHT, 100, Game.HEIGHT, Game.HEIGHT, Game.WIDTH])
        Game.feature_limits = reshape(feature_limits, (1,-1))
        
        # reference clock
        clock = pygame.time.Clock()
        
        # initializing game objects
        population = Population(pop_size=30, feature_limits=Game.feature_limits)    # population of birds
        pipes = []                                                                  # pipes on screen

        # background image
        background_image = pygame.image.load('res/background.png').convert()

        return screen, clock, population, pipes, background_image

    def reset():
        """ resets the game i.e removes all pipes on the screen """
        Game.FRAMES = 0             # resets number of frames to zero
        pipes = []                  # removes all the pipes on the screen
        return pipes
    
    def check_for_collision(population, pipes):
        """ Checks if a bird hits the pipe or touches floor or roof """
        # checking if any bird hits pipes
        for pipe in pipes:
            upper_rect, lower_rect = pipe.get_pipe_rects()
            for individual in population.individuals:
                if not individual.bird.game_over:
                    bird_rect = individual.bird.get_rect()
                    touch_pipes = do_overlap(bird_rect, upper_rect) or do_overlap(bird_rect, lower_rect)
                    if touch_pipes:
                        individual.bird.game_over = True
        
        # checking if any bird hits floor or roof
        for individual in population.individuals:
            bird = individual.bird
            if not bird.game_over and (bird.posy < 0 or bird.posy+bird.height > Game.HEIGHT):
                bird.game_over = True


    def update_scores(population):
        """ updates the score of birds that are alive """
        for individual in population.individuals:
            bird = individual.bird
            if not bird.game_over:
                individual.bird.score = Game.FRAMES
        
    def update_objects(population, pipes):
        """ updates the logic for objects in the game (like movement) """
        # move pipes on the screen
        pipes = Pipe.move_pipes(pipes)

        # update bird objects
        for individual in population.individuals:
            if not individual.bird.game_over:
                individual.bird.update()
        
        # has to change
        # feed forward the population of neural network
        population.update(Pipe.get_nearest_pipe(population.individuals[0].bird, pipes))

        # check if the birds hit the pipes
        Game.check_for_collision(population, pipes)

        # update scores of birds
        Game.update_scores(population)


    def get_dimensions():
        """ return the dimensions of the screen """
        return (Game.WIDTH, Game.HEIGHT)
    
    def draw_screen(screen, population, pipes, background_image):
        """ draws images on the screen with respect to properties of objects using pygame functions """
        Game.FRAMES += 1        # has to change
        screen.blit(background_image, (0, 0))


        # draw birds
        for individual in population.individuals:
            bird = individual.bird
            if not bird.game_over:
                screen.blit(bird.image, (bird.posx, bird.posy))

        # draw pipes
        for pipe in pipes:
            upper_rect, lower_rect = pipe.get_pipe_rects()
            pygame.draw.rect(screen, Color.DARK_GREEN, upper_rect)
            pygame.draw.rect(screen, Color.DARK_GREEN, lower_rect)
        
        # update whole screen
        pygame.display.update()
    
    
    def loop(screen, clock, population, pipes, background_image):
        """ looper for pygame. Loops frames of the game """
        
        # loops untill game is not exited
        while not Game.EXIT:
            # objects updated for each frame
            Game.update_objects(population, pipes)

            # has to change
            # manual input by human
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Game.EXIT = True
                elif event.type == pygame.KEYDOWN and Game.MANUAL:
                    if event.key == pygame.K_UP:
                        population.individuals[0].bird.fly()
            
            # has to change
            # checks if any bird of the population is alive
            if Game.are_all_birds_dead(population):
                """ if population is dead then evolve them """
                population.evolve()
                population.reset_individuals_to_inital_state()
                pipes = Game.reset()

            # drawing objects on the screen
            Game.draw_screen(screen, population, pipes, background_image)
            # ticks the clock - used to control frame rate
            clock.tick(Game.FRAME_RATE)
    
    def are_all_birds_dead(population):
        for individual in population.individuals:
            if not individual.bird.game_over:
                return False
        return True
    

class Bird:
    ANIMATION_RATE = 5                  # animates for every 5 elapsed frames

    def __init__(self):
        self.posx = 0                   # x cordinate
        self.posy = int(Game.HEIGHT/2)  # y cordinate

        filename = 'res/bird.png'
        self.image = pygame.image.load(filename).convert()
        self.image.set_colorkey(Color.BLACK)
        rect = self.image.get_rect()

        self.width, self.height = rect.width, rect.height

        # gravitation parameters
        self.velocity = 0               # velocity in y-direction
        self.gravity = 0.08             # gravity in y-direction

        # random color to each and every bird
        self.color = (                  
            random.randint(256),
            random.randint(256),
            random.randint(256),
        )

        self.score = 0                  # score of the bird
        self.game_over = False          # flag will be set if it hits any object
        self.last_update = 0            # timestamp used for controlling animation

    def get_center(self):
        """ finds center of the bird """
        x = self.posx + self.radius
        y = self.posy + self.radius
        return (x,y)
    
    def update(self):
        """ updates the attributes of bird """
        # finding the new position of bird after elapsing few frames
        t = Game.FRAMES - self.last_update
        if t > Bird.ANIMATION_RATE:
            u = self.velocity
            a = self.gravity
            s = self.posy
            # updating position and velocity based on equations of motion
            self.posy += floor((u*t) + (0.5*(a*t*t)))
            self.velocity = u + a*t
            # stores the instant, when updated
            self.last_update = Game.FRAMES
    
    def fly(self):
        """ sets the y-velocity of bird when user taps the screen / presses up arrow """
        self.velocity = -3      # impulsive velocity in upward direction
    
    def get_rect(self):
        """ return pygame rectangle object of the bird """
        return pygame.rect.Rect(self.posx, self.posy, self.width, self.height)


class Pipe:
    gap_width = 175                         # vertical gap between two pipes
    width = 40                              # width of each pipe
    space_between_pipes = 350               # space between two adjacent pipes
    stepx = 5                               # pipes move in x direction by 5px
    ANIMATION_RATE = 5                      # animates after every 5th frame

    def __init__(self):
        # space between two vertical pipes is denoted as gap
        self.gap_start = random.randint(0, high=Game.HEIGHT - Pipe.gap_width)
        self.gap_end = self.gap_start + Pipe.gap_width
        self.posx = Game.WIDTH
        # stores the latest instant when updated
        self.last_update = 0
    
    def update(self):
        # updates the position of pipes after elapsing few frames
        t = Game.FRAMES - self.last_update
        if t > Pipe.ANIMATION_RATE:
            self.posx -= Pipe.stepx
            self.last_update = Game.FRAMES
    
    def get_pipe_rects(self):
        """ returns pygame rect objects of vertical pipe pair """
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
        """ function used to remove pipes stripping away from screen and adding new pipes as well """
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
        """ return pipe nearest/ahead of the bird """
        for pipe in pipes:
            if bird.posx < pipe.posx + pipe.width:
                return pipe
