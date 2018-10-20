from pygame.locals import *
import pygame
import time
import numpy as np
import random as rnd

class Agent:
    def __init__(self, x_position=0, y_position=0, size=20):
        self.x_position = x_position
        self.y_position = y_position
        self.size = size
        self.active_room = 1

    def move_x(self, direction):
        if direction == 1:
            self.x_position += self.size
            if self._detect_collision():
                self.x_position -= self.size

        if direction == -1:
            self.x_position -= self.size
            if self._detect_collision():
                self.x_position += self.size

        # Update active room based on the x position
        if self.x_position < 200:
            self.active_room = 1
        elif self.x_position >= 400:
            self.active_room = 3
        else:
            self.active_room = 2

    def move_y(self, direction):
        if direction == -1:
            self.y_position -= self.size
            if self._detect_collision():
                self.y_position += self.size

        if direction == 1:
            self.y_position += self.size
            if self._detect_collision():
                self.y_position -= self.size

    def _detect_collision(self):
        # Room 1 left and top
        if self.x_position < 0 or self.y_position < 0:
            return True

        # Room 1 bottom
        if (self.y_position + self.size) > 200 and \
           (self.x_position) < 200:
            return True

        # Room 1 right
        if (self.x_position + self.size) > 200 and \
           self.y_position < 160 and \
           self.x_position < 400:
            return True

        # Room 2 bottom
        if (self.y_position + self.size) > 360:
            return True

        # Room 2 right
        if (self.x_position + self.size) > 400 and \
           self.y_position + self.size > 240:
            return True

        # Room 3 top
        if self.x_position >= 400 and self.y_position < 40:
            return True

        # Room 3 right
        if self.x_position + self.size > 600:
            return True

        # No collision
        return False

    def draw(self, surface):
        color = (0, 128, 255)
        rect = pygame.Rect(self.x_position, self.y_position,
                           self.size, self.size)
        pygame.draw.rect(surface, color, rect)


class Action_Space:
    def __init__(self):
        self.n = 4


class Observation_Space:
    def __init__(self):
        self.shape = [4]

class Environment:


    def __init__(self, size=20, width=800, height=600):
        self._running = True
        self.size = size
        self.agent = Agent(0, 0, self.size)
        self._display_surf = None
        self.window_width = width
        self.window_height = height
        self.desired_room = 2
        self.action_space = Action_Space()
        self.observation_space = Observation_Space()
        self.steps = 0

    def init(self):
        pygame.init()
        self._display_surf = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.HWSURFACE)

        pygame.display.set_caption('The agents environment')
        self._running = True

    def update(self, action):
        # This function should move the agent one step in one direction
        # based on the input action, i.e. call move_x or move_y
        #
        # The function should return x and y of the agent
        if action == 0:
            self.agent.move_y(1)
        elif action == 1:
            self.agent.move_y(-1)
        elif action == 2:
            self.agent.move_x(1)
        elif action == 3:
            self.agent.move_x(-1)

        return self.agent.x_position, self.agent.y_position

    def render(self):
        self._display_surf.fill((0, 0, 0))

        room_color = (255, 255, 255)
        room1 = pygame.Rect(0, 0, 200, 200)
        pygame.draw.rect(self._display_surf, room_color, room1)
        room2 = pygame.Rect(200, 200 - 2 * self.size, 200, 200)
        pygame.draw.rect(self._display_surf, room_color, room2)
        room3 = pygame.Rect(400, 2 * self.size, 200, 200)
        pygame.draw.rect(self._display_surf, room_color, room3)

        self.agent.draw(self._display_surf)

        font = pygame.font.SysFont(None, 28)
        msg = 'R%d, (%d, %d)' % (self.agent.active_room,
                                 self.agent.x_position,
                                 self.agent.y_position)
        text = font.render(msg, True, (255, 0, 0), (0, 0, 0))
        self._display_surf.blit(text, (450, 300))
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()

    def make(self):
        if self.init() == False:
            self._running = False

    def reset(self):
        self.init()
        self.steps = 0
        x, y = self.update(-1)
        return np.array([x, y, self.agent.active_room, self.desired_room])

    def step(self, action):
        self.steps = self.steps + 1
        new_x, new_y = self.update(action)
        new_state = np.array([new_x, new_y, self.agent.active_room, self.desired_room])
        if self.desired_room == self.agent.active_room:
            reward = 1
            if rnd.random() > 0.98:
                self.desired_room = rnd.randint(1, 3)
                print('New room!!!')
        else:
            reward = -1

        return new_state, reward, (self.steps==200), None


    def execute(self):
        if self.init() == False:
            self._running = False

        while(self._running):
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.update(2)
                    if event.key == pygame.K_LEFT:
                        self.update(3)
                    if event.key == pygame.K_DOWN:
                        self.update(0)
                    if event.key == pygame.K_UP:
                        self.update(1)
                    if event.key == pygame.K_ESCAPE:
                        self._running = False

            new_x, new_y = self.update(-1)
            self.render()

            time.sleep(50.0 / 1000.0)

        self.cleanup()


if __name__ == "__main__":
    env = Environment(20, 600, 360)
    env.execute()
