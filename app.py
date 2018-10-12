import pygame

from attrib import Bird, Color, Pipe, Game


def main():
    # initialize game screen
    screen, clock, bird, pipes = Game.initialize()
    Game.loop(screen, clock, bird, pipes)

if __name__ == '__main__':
    main()
    pygame.quit()
