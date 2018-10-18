import pygame

pygame.init()
screen = pygame.display.set_mode((600, 600))
done = False
is_blue = True
x = 0
y = 0

clock = pygame.time.Clock()

while not done:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True

    pressed = pygame.key.get_pressed()
    if pressed[pygame.K_UP]: y -= 60
    if pressed[pygame.K_DOWN]: y += 60
    if pressed[pygame.K_LEFT]: x -= 60
    if pressed[pygame.K_RIGHT]: x += 60

    screen.fill((0, 0, 0))
    color = (0, 128, 255)
    pygame.draw.rect(screen, color, pygame.Rect(x, y, 60, 60))

    pygame.display.flip()
    clock.tick(10)
    