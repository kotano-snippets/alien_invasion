import sys
from time import sleep

import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from scoreboard import Scoreboard
from button import Button


class AlienInvasion:
    def __init__(self) -> None:
        """Initialize the game, and create game resources."""
        pygame.init()
        pygame.display.set_caption("Alien Invasion")

        self.settings = Settings()
        self.screen = self.draw_screen(
            fullscreen=False, settings=self.settings)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        # Create an instance to store game statistics.
        # and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = Scoreboard(self)

        # Make the Play button.
        self.play_button = Button(self, 'Play')

        self._create_fleet()

    def draw_screen(self, fullscreen=False, settings=object()):
        if fullscreen:
            screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            settings.screen_width = screen.get_rect().width
            settings.screen_height = screen.get_rect().height
        else:
            import os
            x, y = 0, 30
            os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (x, y)
            screen = pygame.display.set_mode((
                settings.screen_width,
                settings.screen_height))
        return screen

    def run_game(self):
        """Start the main loop for the game."""
        while True:
            self._check_events()
            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
            self._update_screen()

# Create
    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Make an alien.
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        available_space_x = self.settings.screen_width - (2 * alien_width)
        number_alien_x = available_space_x // (2 * alien_width)

        # Determine the number of rows of aliens that fit on the screen.
        ship_height = self.ship.rect.height
        available_space_y = (
            self.settings.screen_height - (3 * alien_height) - ship_height)
        number_rows = available_space_y // (2 * alien_height)

        # Create the full fleet of aliens.
        for row_number in range(number_rows):
            for alien_number in range(number_alien_x):
                self._create_alien(alien_number, row_number)

    def _create_alien(self, alien_number, row_number):
        """Create an alien and place it in the row."""
        alien = Alien(self)
        alien_width, alien_height = alien.rect.size
        alien.x = alien_width + 2 * alien_width * alien_number
        alien.rect.x = alien.x
        alien.rect.y = alien.rect.height + 2 * alien.rect.height * row_number
        self.aliens.add(alien)

# Check
    def _check_events(self):
        """Respong to keypress and mouse events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_keydown_events(self, event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            # Move the ship to the right.
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_q:
            sys.exit()
        elif event.key == pygame.K_SPACE:
            if self.stats.game_active is True:
                self._fire_bullet()
            else:
                self.play_pause()
        elif event.key == pygame.K_p:
            # Play/pause the game.
            self.play_pause()
        elif event.key == pygame.K_RETURN:
            # Start new game.
            self._start_new_game()

    def _check_keyup_events(self, event):
        """Respond to key releases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _check_play_button(self, mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.stats.game_active:
            self._start_new_game()

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge."""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _check_bullet_alien_collisions(self):
        """Respond to bullet-alien collisions."""
        # Remove any bullets and aliens that have collided.
        collisions = pygame.sprite.groupcollide(  # noqa: F841
            self.bullets, self.aliens, True, True)

        for aliens in collisions.values():
            self.stats.score += self.settings.alien_points * len(aliens)
        self.sb.prep_score()
        self.sb.check_high_score()

        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            print("Speed increased: {}".format(self.settings.alien_speed))

            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _check_aliens_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        screen_rect = self.screen.get_rect()
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                # Treat this the same as if the ship got hit.
                self._ship_hit()
                break

# Action
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _change_fleet_direction(self):
        """Drop the entire fleet and change the fleet's direction."""
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""

        if self.stats.ships_left > 0:
            # Decrement ships_left.
            self.stats.ships_left -= 1
            self.sb.prep_ships()

            # Get rid of any remaining aliens and bullets.
            self.aliens.empty()
            self.bullets.empty()

            # Create a new fleet and center the ship.
            self._create_fleet()
            self.bullets.empty()

            # Pause.
            sleep(0.5)
        else:
            self.stats.game_active = False
            pygame.mouse.set_visible(True)

        print("Ships left: %d" % self.stats.ships_left)

    def play_pause(self):
        # Play/pause the game.
        self.stats.game_active = not self.stats.game_active

    def _start_new_game(self):
        # Reset the game settings.
        self.settings.initialize_dynamic_settings()

        # Reset the game statistics.
        self.stats.reset_stats()
        self.stats.game_active = True
        self.sb.prep_score()
        self.sb.prep_level()
        self.sb.prep_ships()

        # Get rid of any remining aliens and bullets.
        self.aliens.empty()
        self.bullets.empty()

        # Create a new fleet and center the ship.
        self._create_fleet()
        self.ship.center_ship()

        # Hide the mouse cursor.
        pygame.mouse.set_visible(False)

# Update
    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # Update bullet positions.
        self.bullets.update()

        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

    def _update_aliens(self):
        """Check if the fleet is at an edge,
        then update the positions of all aliens in the fleet."""
        self._check_fleet_edges()
        self.aliens.update()

        # Check for any bullets that have hit aliens.
        self._check_bullet_alien_collisions()

        # Look for alien-ship collisions.
        if pygame.sprite.spritecollideany(self.ship, self.aliens):
            self._ship_hit()

        # Look for aliens hitting the bottom of the screen.
        self._check_aliens_bottom()

    def _update_screen(self):
        self.screen.fill(self.settings.bg_color)
        self.ship.blitme()
        for bullet in self.bullets.sprites():
            bullet.draw_bullet()
        self.aliens.draw(self.screen)

        # Draw the score information.
        self.sb.show_score()

        # Draw the play button if the game is inactive.
        if not self.stats.game_active:
            self.play_button.draw_button()

        # Make the most recently drawn screen visible.
        pygame.display.flip()


if __name__ == "__main__":
    # Make a game instance, and run the game.
    ai = AlienInvasion()
    ai.run_game()
