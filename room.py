from pygame.locals import *
import pygame
import time
import numpy as np
import random as rnd
from enum import Enum


class Action(Enum):
    Up = 0
    Down = 1
    Right = 2
    Left = 3

class Agent:
    def __init__(self):
        self.color = (0, 128, 255)
        self.x = 0
        self.y = 0
        self.size = 10



    def move(self, action, obstacles):
        old_x = self.x
        old_y = self.y

        if action == Action.Up:
            self.y -= 1
        elif action == Action.Down:
            self.y += 1
        elif action == Action.Right:
            self.x += 1
        elif action == Action.Left:
            self.x -= 1

        self.set_pos()
        if self.rect.collidelistall(obstacles):
            self.x = old_x
            self.y = old_y
            self.set_pos()

    def set_pos(self):
        self.rect = pygame.Rect(self.x, self.y,
                           self.size, self.size)

    def draw(self, surface):
        self.set_pos()
        pygame.draw.rect(surface, self.color, self.rect)

class Room:
    def __init__(self, size=(400, 400)):
        self.agent = Agent()
        self.to_go = (40, 300, 10)
        self.size = size

        self.obstacles = []
        for obs in np.random.randint(400, size=(4, 3)):
            rect = pygame.Rect(obs[0], obs[1], obs[2]/10, obs[2]/10)
            self.obstacles.append(rect)


        pygame.init()
        self._display_surf = pygame.display.set_mode(
            (self.size[0], self.size[1]), pygame.HWSURFACE)
        pygame.display.set_caption('The agents environment')
        self._running = True

    def render(self):
        self._display_surf.fill((0, 0, 0))
        color = (100, 128, 100)
        for obs in self.obstacles:
            pygame.draw.rect(self._display_surf, color, obs)

        color = (255, 255, 0)
        rect = pygame.Rect(self.to_go[0], self.to_go[1], self.to_go[2], self.to_go[2])
        pygame.draw.rect(self._display_surf, color, rect)


        self.agent.draw(self._display_surf)
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()

    def execute(self):
        while(self._running):
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.agent.move(Action.Right, self.obstacles)
                    if event.key == pygame.K_LEFT:
                        self.agent.move(Action.Left, self.obstacles)
                    if event.key == pygame.K_DOWN:
                        self.agent.move(Action.Down, self.obstacles)
                    if event.key == pygame.K_UP:
                        self.agent.move(Action.Up, self.obstacles)
                    if event.key == pygame.K_ESCAPE:
                        self._running = False

            self.render()

            time.sleep(50.0 / 1000.0)

        self.cleanup()


if __name__ == "__main__":
    room = Room()
    room.execute()

