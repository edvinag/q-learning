from pygame.locals import *
import pygame
import time
import numpy as np
import random as rnd
from enum import Enum
import math

class Action(Enum):
    Up = 0
    Down = 1
    Right = 2
    Left = 3


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

    def move_bm(self, steer_wheel_angle, velocity, obstacles, goal):
        # Bicycle model
        # Input to movement is steering wheel angle and the velocity of the vehicle.
        # yaw: Vehicle angle in global coordinate system.
        # velocity_angle: Angle between vehicle velocity and the longitudinal axle of the vehicle.
        # x and y: Position in global coordinate system
        # length_rear: length between COG and rear axle
        # length_front: length between COG and front axle

        # Save old value with old_ prefix of state variable
        old_yaw = self.yaw
        old_x = self.x
        old_y = self.y

        # Update states
        velocity_angle = math.atan(self.length_rear * math.tan(steer_wheel_angle)/(self.length_rear + self.length_front))
        self.x = old_x + self.sampleTime * velocity * math.cos(velocity_angle + old_yaw)
        self.y = old_y + self.sampleTime * velocity * math.sin(velocity_angle + old_yaw)
        self.yaw = old_yaw + (self.sampleTime * velocity * math.sin(velocity_angle)/self.length_rear)

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


class Room:
    def __init__(self, size=(400, 400)):
        self.agent = Agent()
        goal = Population("goal", (10, 10), (40, 300))
        self.goal = pygame.sprite.Group()
        self.goal.add(goal)

        self.size = size
        self.obstacles = pygame.sprite.Group()
        for obs in np.random.randint(400, size=(4, 3)):
            obstacle = Population("obstacle", (obs[2]/10, obs[2]/10), (obs[0], obs[1]))
            self.obstacles.add(obstacle)

        leftWall = Population("obstacle", (10, size[1]), (0, size[1]/2))
        self.obstacles.add(leftWall)
        rightWall = Population("obstacle", (10, size[1]), (size[1], size[1] / 2))
        self.obstacles.add(rightWall)
        topWall = Population("obstacle", (size[0], 10), (size[0] / 2, 0))
        self.obstacles.add(topWall)
        bottomWall = Population("obstacle", (size[0], 10), (size[0] / 2, size[0]))
        self.obstacles.add(bottomWall)


        pygame.init()
        self._display_surf = pygame.display.set_mode(
            (self.size[0], self.size[1]), pygame.HWSURFACE)
        pygame.display.set_caption('The agents environment')
        self._running = True

    def render(self):
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
        velocity = 0
        while(self._running):
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RIGHT:
                        steer_wheel_angle += 10
                    if event.key == pygame.K_LEFT:
                        steer_wheel_angle -= 10
                    if event.key == pygame.K_DOWN:
                        velocity -= 30
                    if event.key == pygame.K_UP:
                        velocity += 30
                    if event.key == pygame.K_ESCAPE:
                        self._running = False

                # Truncate angle at a certain degree
                truncate_value = 60
                steer_wheel_angle = max(-truncate_value, min(truncate_value, steer_wheel_angle))
            goal_reached = self.agent.move_bm(math.radians(steer_wheel_angle), velocity, self.obstacles, self.goal)
            if goal_reached:
                print("Goal is reached!")

            self.render()

            time.sleep(50.0 / 1000.0)

        self.cleanup()


if __name__ == "__main__":
    room = Room()
    room.execute()

