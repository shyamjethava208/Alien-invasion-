class Settings:
    """a class to store all settings for alien invasion"""

    def __init__(self):
        """initialize the game's static settings"""
        # screen settings
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (230,230,230)
        # ship settings
        self.ship_limit = 3
        # bullet settings
        self.bullet_width = 3
        self.bullet_height = 15
        self.bullet_color =(60,60,60)
        self.bullets_allowed = 5
        # alien settings
        self.fleet_drop_speed = 10
        # alien bullet settings
        self.alien_bullet_width = 3
        self.alien_bullet_height =15
        self.alien_bullet_color = (255,0,0)

        # how quickly the game speeds up
        self.speedup_scale = 1.1
        # How quickly the alien point values increase
        self.score_scale = 1.5
        self.initialize_dynamic_settings()
    
    def initialize_dynamic_settings(self):
        """Initialize settings that change throughout the game."""
        self.ship_speed = 1.5
        self.bullet_speed = 3.0
        self.alien_bullet_speed = 3.0
        self.alien_speed = 1.0
        # fleet_direction of 1 represents right; -1 represents left.
        self.fleet_direction = 1
        self.alien_bullets_allowed = 1
        # Scoring settings
        self.alien_points = 50
        
    
    def increase_speed(self):
        """increase speed settings.and other values"""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale
        self.alien_bullets_allowed += 1
        self.alien_points = int(self.alien_points * self.score_scale)