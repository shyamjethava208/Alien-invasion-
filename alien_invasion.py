import sys
import pygame
from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from time import sleep
from game_stats import GameStats
from random import randint
from alien_bullet import AlienBullet
from button import Button
from score_board import ScoreBoard
from pathlib import Path

class AlienInvasion:

    """overall class to manage game assets and behavior."""

    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = Settings()
        # self.screen = pygame.display.set_mode((0,0),pygame.FULLSCREEN)
        # self.settings.screen_height = self.screen.get_rect().height
        # self.settings.screen_width = self.screen.get_rect().width
        self.screen = pygame.display.set_mode((self.settings.screen_width,self.settings.screen_height))
        pygame.display.set_caption("Alien Invasion")
        # Create an instance to store game statistics,
        # and create a scoreboard.
        self.stats = GameStats(self)
        self.sb = ScoreBoard(self)
        self.ship = Ship(self)
        self.bullets = pygame.sprite.Group()
        self.alien_bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()
        self._create_fleet()
        # Start alien invasion in inactive state.
        self.game_active = False
        # Make the Play button
        self.play_button = Button(self,"Play")
        self.path = Path("high_score.txt")

    def run_game(self):
        """start the main loop for the game"""
        while True:
            self._check_events()
            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()
                self._update_alien_bullet()
            self._update_screen()
            self.clock.tick(60)

    def _check_events(self):
        # watch for keyboard and mouse events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.path.write_text(str(self.stats.high_score))
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    self._check_keydown_events(event)
                elif event.type == pygame.KEYUP:
                    self._check_keyup_events(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    self._check_play_button(mouse_pos)
    
    def _check_keydown_events(self,event):
        """Respond to keypresses."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        if event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        if event.key == pygame.K_ESCAPE:
            self.path.write_text(str(self.stats.high_score))
            sys.exit()
        if event.key == pygame.K_SPACE:
            self._fire_bullet()
        
    
    def _check_keyup_events(self,event):
        """respond to keyreleases."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        
    
    def _check_play_button(self,mouse_pos):
        """Start a new game when the player clicks Play."""
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            # Hide the mouse cursor.
            pygame.mouse.set_visible(False)
            # Reset the game statistics.
            self.stats.reset_stats()
            self.sb.prep_score()
            self.sb.prep_level()
            self.sb.prep_ships()
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.alien_bullets.empty()
            self.aliens.empty()
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            self.game_active = True
            # Reset the game settings.
            self.settings.initialize_dynamic_settings()
    
    def _fire_bullet(self):
        """Create a new bullet and add it to the bullets group."""
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

    def _update_bullets(self):
        """Update position of bullets and get rid of old bullets."""
        # calling bullet.update() for each bullet in group
        self.bullets.update()
        # Get rid of bullets that have disappeared.
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)
        # print(len(self.bullets))
        self._check_bullet_alien_collision()
    
    def _check_bullet_alien_collision(self):
        """Respond to bullet-alien collisions."""
        # check for any bullets that have hit aliens.
        # if so, get rid of the bullet and the alien.
        collisions = pygame.sprite.groupcollide(self.bullets,self.aliens,True,True)
        if collisions:
            for aliens in collisions.values():
                self.stats.score += self.settings.alien_points * len(aliens)
            self.sb.prep_score()
            self.sb.check_high_score()
        if not self.aliens:
            # Destroy existing bullets and create new fleet.
            self.bullets.empty()
            self.alien_bullets.empty()
            self._create_fleet()
            self.settings.increase_speed()
            # Increase level.
            self.stats.level += 1
            self.sb.prep_level()

    def _create_fleet(self):
        """Create the fleet of aliens."""
        # Create an alien and keep adding aliens until there's no room left.
        # Spacing between aliens is one alien width and one alien height

        alien = Alien(self)
        # size attribute is a tuple containing width and height
        alien_width,alien_height = alien.rect.size
        current_x = alien_width
        current_y = alien_height
        while current_y < (self.settings.screen_height - 3 * alien_height):
            while current_x < (self.settings.screen_width - 2 * alien_width):
                self._create_alien(current_x,current_y)
                current_x += 2 * alien_width
            # Finished a row; reset x value, and increment y value.
            current_x = alien_width
            current_y += 2 * alien_height

    def _create_alien(self,x_position,y_position):
        """Create an alien and place it in the row."""
        new_alien = Alien(self)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.aliens.add(new_alien)

    def _update_aliens(self):
        """Check if the fleet is at an edge, then update positions."""
        self._check_fleet_edges()
        self.aliens.update()
        # Look for alien-ship collisions.
        # this function looks for any member of the group that has collided with the sprite
        if pygame.sprite.spritecollideany(self.ship,self.aliens):
            self._ship_hit()
        # Look for aliens hitting the bottom of the screen.
        self._check_alien_bottom()
        self._fire_alien_bullet()
    
    def _fire_alien_bullet(self):
        """fires alien bullet"""
        if len(self.alien_bullets) < self.settings.alien_bullets_allowed:
            list_alien = list(self.aliens)
            if list_alien:
                # select random alien to fire bullets
                range = len(list_alien) - 1
                alien_to_fire_bullet = randint(0,range)
                new_alien_bullet = AlienBullet(self,list_alien[alien_to_fire_bullet])
                self.alien_bullets.add(new_alien_bullet)
        
    def _update_alien_bullet(self):
        self.alien_bullets.update()
        for alien_bullet in self.alien_bullets.copy():
            if alien_bullet.rect.bottom >= self.settings.screen_height:
                self.alien_bullets.remove(alien_bullet)
        if pygame.sprite.spritecollideany(self.ship,self.alien_bullets):
            self._ship_hit()

    def _check_fleet_edges(self):
        """Respond appropriately if any aliens have reached an edge"""
        for alien in self.aliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break
    
    def _change_fleet_direction(self):
        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self):
        """Respond to the ship being hit by an alien."""
        if self.stats.ships_left > 1:
            # Decrement ships_left, and update scoreboard.
            self.stats.ships_left -= 1
            self.sb.prep_ships()
            # Get rid of any remaining bullets and aliens.
            self.bullets.empty()
            self.aliens.empty()
            self.alien_bullets.empty()
            # Create a new fleet and center the ship.
            self._create_fleet()
            self.ship.center_ship()
            # pause
            sleep(0.5)
        else:
            self.game_active = False
            pygame.mouse.set_visible(True)

    def _check_alien_bottom(self):
        """Check if any aliens have reached the bottom of the screen."""
        for alien in self.aliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                self._ship_hit()
                break
    
    def _update_screen(self):
        # redrew the screen durint each pass through the loop
            self.screen.fill(self.settings.bg_color)
            
            for bullet in self.bullets.sprites():
                bullet.draw_bullet()
            for alien_bullet in self.alien_bullets.sprites():
                alien_bullet.draw_bullet()
            self.aliens.draw(self.screen)
            self.ship.blitme()
            # Draw the score information
            self.sb.show_score()
            # Draw the play button if the game is inactive.
            if not self.game_active:
                self.play_button.draw_button()
            
        # make the most recent drawn screen visible
            pygame.display.flip()
            
if __name__ == "__main__":
    # make the game instance and run the game
    ai = AlienInvasion()
    ai.run_game()