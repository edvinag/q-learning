from pygame.locals import *
import pygame
import time
import numpy as np
import random as rnd
from enum import Enum
import math

class Agent:
    def __init__(self):
        self.x = 200
        self.y = 200
        self.width = 10
        self.length = 20
        self.pop = Population("agent", (self.width, self.length), (self.x, self.y))

        # To be able to switch COG, use variables, now COG is in enter of Vehicle.
        self.length_rear = self.length/2
        self.length_front = self.length/2
        self.sampleTime = 0.1
        self.yaw = 0
        self.velocity = 0

    def move_bm(self, actions, obstacles, goal):
        # Bicycle model
        # Input to movement is steering wheel angle and the velocity of the vehicle.
        # yaw: Vehicle angle in global coordinate system.
        # velocity_angle: Angle between vehicle velocity and the longitudinal axle of the vehicle.
        # x and y: Position in global coordinate system
        # length_rear: length between COG and rear axle
        # length_front: length between COG and front axle

        # Populate angles
        steer_wheel_angle = actions[0]
        acceleration = actions[1]

        # Save old value with old_ prefix of state variable
        old_yaw = self.yaw
        old_x = self.x
        old_y = self.y
        old_velocity = self.velocity

        # Truncate steer wheel angle at a certain degree
        truncate_value = 30
        steer_wheel_angle = math.radians(max(-truncate_value, min(truncate_value, steer_wheel_angle)))

        # Update states
        velocity_angle = math.atan(self.length_rear * math.tan(steer_wheel_angle)/(self.length_rear + self.length_front))
        self.x = old_x + self.sampleTime * old_velocity * math.cos(velocity_angle + old_yaw)
        self.y = old_y + self.sampleTime * old_velocity * math.sin(velocity_angle + old_yaw)
        self.yaw = old_yaw + (self.sampleTime * old_velocity * math.sin(velocity_angle)/self.length_rear)
        self.velocity = old_velocity + self.sampleTime * acceleration

        # Truncate steer wheel angle at a certain degree
        truncate_value = 30
        self.velocity = max(-truncate_value, min(truncate_value, self.velocity))

        self.set_pos()
        # Move vehicle to new states and check for collision, if collision, then use old states.
        if self.is_colliding(obstacles):
            self.yaw = old_yaw
            self.x = old_x
            self.y = old_y
            self.set_pos()

        goal_reached = False
        if self.is_at_goal(goal):
            goal_reached = True

        return goal_reached

    def set_pos(self):
        self.pop.image = pygame.transform.rotate(self.pop.image_original, -math.degrees(self.yaw))
        self.pop.rect = self.pop.image.get_rect(center=(self.x, self.y))
        self.pop.mask = pygame.mask.from_surface(self.pop.image)

    def draw(self, surface):
        self.set_pos()
        pygame.draw.rect(surface, self.color, self.rect)

    def is_colliding(self, obstacles):
        if pygame.sprite.spritecollideany(self.pop, obstacles, collided=None):
            collision_occurred = True
        else:
            collision_occurred = False
        return collision_occurred

    def is_at_goal(self, goal):
        if pygame.sprite.spritecollideany(self.pop, goal, collided=None):
            goal_reached = True
        else:
            goal_reached = False
        return goal_reached


class Population(pygame.sprite.Sprite):

    def __init__(self, type="",  size=(0, 0), pos=(0, 0), picture="yellowCar.png", rotation_degree=-90):
        pygame.sprite.Sprite.__init__(self)
        if "agent" in type:
            self.image = pygame.image.load(picture)
            self.image = pygame.transform.scale(self.image, size)
            x_pos = pos[0] + size[0]/2
            y_pos = pos[1] + size[1]/2
            self.rect = self.image.get_rect(center=(x_pos, y_pos))
            self.image = pygame.transform.rotate(self.image, rotation_degree)
            self.image_original = self.image
        elif "goal" in type:
            self.image = pygame.Surface(size)
            self.rect = self.image.get_rect(center=pos)
            self.image.fill((255, 255, 0))
        elif "obstacle" in type:
            self.image = pygame.Surface(size)
            self.rect = self.image.get_rect(center=pos)
            self.image.fill((100, 128, 100))
        else:
            self.image = pygame.Surface(size)

        self.mask = pygame.mask.from_surface(self.image)


class ObservationSpace:
    def __init__(self):
        self.shape = [3]


class ActionSpace:
    def __init__(self):
        self.n = 6


class Room:
    def __init__(self, size=(400, 400)):
        self.agent = None
        self.goal_pop = None
        self.goal = None
        self.action_space = ActionSpace()
        self.observation_space = ObservationSpace()
        self.observation_space.shape = [(400, 400, 1)]
        self.obstacles = None
        self.size = size

        self.action = [0, 0]

        pygame.init()
        self._display_surf = pygame.display.set_mode(
            (self.size[0], self.size[1]), pygame.HWSURFACE)
        pygame.display.set_caption('The agents environment')
        self._running = True

    def setup(self):
        size = self.size
        self.agent = Agent()
        self.goal_pop = None
        while self.goal_pop is None or self.agent.pop.rect.colliderect(self.goal_pop.rect) != 0:
            self.goal_pop = Population("goal", (10, 10), np.random.randint(size[0], size=(1, 2))[0])
        self.goal = pygame.sprite.Group()
        self.goal.add(self.goal_pop)
        self.obstacles = pygame.sprite.Group()
        for obs in np.random.randint(size[0], size=(20, 3)):
            obstacle = None
            while obstacle is None or \
                    (self.agent.pop.rect.colliderect(obstacle.rect) != 0 and
                     self.goal_pop.rect.colliderect(obstacle.rect) != 0):
                obstacle = Population("obstacle", (obs[2] / 10, obs[2] / 10), (obs[0], obs[1]))
            self.obstacles.add(obstacle)

        left_wall = Population("obstacle", (10, size[1]), (0, size[1] / 2))
        self.obstacles.add(left_wall)
        right_wall = Population("obstacle", (10, size[1]), (size[1], size[1] / 2))
        self.obstacles.add(right_wall)
        top_wall = Population("obstacle", (size[0], 10), (size[0] / 2, 0))
        self.obstacles.add(top_wall)
        bottom_wall = Population("obstacle", (size[0], 10), (size[0] / 2, size[0]))
        self.obstacles.add(bottom_wall)

    def reward(self):
        x1, y1 = self.agent.x, self.agent.y
        x2, y2 = self.goal_pop.rect.center[0], self.goal_pop.rect.center[1]
        return - math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2)

    def reset(self):
        #self.cleanup()
        self.setup()
        new_state, _, _, _ = self.step(0)
        return new_state

    def render(self):
        pass

    def step(self, action_index):
        pygame.event.pump()

        # Index 0-2 concerns steer wheel angle.
        # Index 3-5 concerns acceleration.
        if action_index == 0:
            self.action[0] = 0
        elif action_index == 1:
            self.action[0] = 45
        elif action_index == 2:
            self.action[0] = -45
        elif action_index == 3:
            self.action[1] = 0
        elif action_index == 4:
            self.action[1] = 1
        elif action_index == 5:
            self.action[1] = -1

        terminal = self.agent.move_bm(self.action, self.obstacles, self.goal)
        self._render()
        image_state = pygame.surfarray.array2d(self._display_surf).reshape((400,400,1))
        return image_state, self.reward(), terminal, None

    def _render(self):
        # Render background
        self._display_surf.fill((0, 0, 0))

        # Render obstacles
        self.obstacles.draw(self._display_surf)

        # Render Goal
        self.goal.draw(self._display_surf)

        # Render agent
        self._display_surf.blit(self.agent.pop.image, self.agent.pop.rect)
        pygame.display.flip()

    def cleanup(self):
        pygame.quit()

    def execute(self):
        steer_wheel_angle = 0
        acceleration = 0
        self.setup()
        while self._running:
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        self.action[0] = 45
                    if event.key == pygame.K_LEFT:
                        self.action[0] = -45
                    if event.key == pygame.K_f:
                        self.action[0] = 0
                    if event.key == pygame.K_DOWN:
                        self.action[1] = -1
                    if event.key == pygame.K_UP:
                        self.action[1] = 1
                    if event.key == pygame.K_n:
                        self.action[1] = 0
                    if event.key == pygame.K_ESCAPE:
                        self._running = False

            goal_reached = self.agent.move_bm(self.action, self.obstacles, self.goal)
            if goal_reached:
                print("Goal is reached!")

            self._render()

            time.sleep(50.0 / 1000.0)

        self.cleanup()


if __name__ == "__main__":
    room = Room()
    room.execute()

