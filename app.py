import pygame

from attrib import Bird, Color, Game, Pipe


def main():
    screen, clock, bird, pipes = Game.initialize()      # initialize game screen
    Game.loop(screen, clock, bird, pipes)               # loops untill user quits or game ends

if __name__ == '__main__':
    main()                          # calling main function upon execution
    pygame.quit()                   # quits all modules initialized by pygame
