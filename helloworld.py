#! /usr/bin/python3

# Docs: https://www.pygame.org/docs/

import pygame

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
FPS_LIMIT = 60

pygame.init()
screen = pygame.display.set_mode([WINDOW_WIDTH, WINDOW_HEIGHT])
pygame.display.set_caption("Hello world!")
clock = pygame.time.Clock()
dt = 1 / FPS_LIMIT

isDragging = 0
dragDelta = pygame.Vector2(0, 0)

circle1Pos = pygame.Vector2(screen.get_width() / 2 - 128, screen.get_height() / 2)
circle1Radius = 150

circle2Pos = pygame.Vector2(screen.get_width() / 2 + 128, screen.get_height() / 2)
circle2Radius = 100

# Program loop
halt = False
while not halt:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            halt = True
        # Start dragging the circle
        elif event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]:
            if (pygame.mouse.get_pos() - circle1Pos).length() < circle1Radius:
                isDragging = 1
                dragDelta = pygame.mouse.get_pos() - circle1Pos
            elif (pygame.mouse.get_pos() - circle2Pos).length() < circle2Radius:
                isDragging = 2
                dragDelta = pygame.mouse.get_pos() - circle2Pos
        # Stop dragging
        elif event.type == pygame.MOUSEBUTTONUP and isDragging > 0 and not pygame.mouse.get_pressed()[0]:
            isDragging = 0

    if isDragging == 1:
        circle1Pos = pygame.mouse.get_pos() - dragDelta
    elif isDragging == 2:
        circle2Pos = pygame.mouse.get_pos() - dragDelta

    # Background
    screen.fill((32, 32, 32))

    # Circles. Draw the first circle on top because when dragging it's checked first
    pygame.draw.circle(screen, (90, 200, 20), circle2Pos, circle2Radius)
    pygame.draw.circle(screen, (255, 60, 60), circle1Pos, circle1Radius)

    pygame.display.flip() # Update the window
    dt = clock.tick(FPS_LIMIT)

pygame.quit()
