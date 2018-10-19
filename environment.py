from pygame.locals import *
import pygame
import time


class Agent:
    def __init__(self, x_position=0, y_position=0, size=20):
        self.x_position = x_position
        self.y_position = y_position
        self.size = size

    def move_x(self, direction):
        if direction == 1:
            self.x_position += self.size
            if self._detect_collision():
                self.x_position -= self.size

        if direction == -1:
            self.x_position -= self.size
            if self._detect_collision():
                self.x_position += self.size

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


class Environment:
    def __init__(self, size=20, width=800, height=600):
        self._running = True
        self.size = size
        self.agent = Agent(0, 0, self.size)
        self._display_surf = None
        self.window_width = width
        self.window_height = height

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
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()

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
                        self.agent.move_x(1)
                    if event.key == pygame.K_LEFT:
                        self.agent.move_x(-1)
                    if event.key == pygame.K_DOWN:
                        self.agent.move_y(1)
                    if event.key == pygame.K_UP:
                        self.agent.move_y(-1)
                    if event.key == pygame.K_ESCAPE:
                        self._running = False

            new_x, new_y = self.update(1)
            self.render()

            time.sleep(50.0 / 1000.0)

        self.cleanup()


if __name__ == "__main__":
    env = Environment(20, 600, 360)
    env.execute()
