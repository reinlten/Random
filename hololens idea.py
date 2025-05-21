import pygame
import sys

# Pygame initialisieren
pygame.init()

# Fenstergröße definieren
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 400
SCREEN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Wanderndes Quadrat")

# Farben definieren
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Quadratgröße und Startposition definieren
SQUARE_SIZE = 15
x, y = 0, 0

# Schrittweite
STEP = 15

# Frame-Rate Controller
clock = pygame.time.Clock()
FPS = 1

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Bildschirm füllen
    SCREEN.fill(BLACK)

    # Quadrat zeichnen
    pygame.draw.rect(SCREEN, WHITE, (x, y, SQUARE_SIZE, SQUARE_SIZE))

    # Position aktualisieren
    x += STEP
    if x >= WINDOW_WIDTH:  # Wenn rechter Rand erreicht
        x = 0  # Zurück zum linken Rand
        y += STEP  # Einen Schritt nach unten

    if y >= WINDOW_HEIGHT:  # Wenn unteres Ende erreicht
        x, y = 0, 0  # Zurück zum Anfang

    # Display aktualisieren
    pygame.display.flip()

    # Frame-Rate begrenzen
    clock.tick(FPS)

pygame.quit()
sys.exit()
