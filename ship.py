import pygame

class Ship:
    """A class to manage the ship."""

    def __init__(self, ai_game) -> None:
        """Initialize the ship and set its starting positioin."""
        self.screen = ai_game.screen
        self.screen_rect = ai_game.screen.get_rect()

        self.moving_right = False
        self.moving_left = False
        self.settings = ai_game.settings

        # Load the ship image and get its rect.
        self.image = pygame.image.load('images/ship.bmp')
        self.rect = self.image.get_rect()
        # Start each new ship at the bottom center of the screen.
        self.rect.midbottom = self.screen_rect.midbottom


    def update(self):
        if self.moving_right:
            self.rect.x += 1
        if self.moving_left:
            self.rect.x -= 1



    def blitme(self):
        """Draw the ship at its current location."""
        self.screen.blit(self.image, self.rect)
