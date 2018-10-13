import pygame

from attrib import Bird, Color, Game, Pipe


def main():
    # screen, clock, bird, pipes, background_image = Game.initialize()  # initialize game screen
    # Game.loop(screen, clock, bird, pipes, background_image)           # loops untill user quits or game ends
    attribs = Game.initialize()  # initialize game screen
    Game.loop(*(attribs))           # loops untill user quits or game ends

if __name__ == '__main__':
    main()                          # calling main function upon execution
    pygame.quit()                   # quits all modules initialized by pygame
