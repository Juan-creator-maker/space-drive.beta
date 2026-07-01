"""
Main game manager
Coordinates all game systems
"""

import pygame
from game.player import Player
from game.level import Level
from game.camera import Camera3D

class GameManager:
    """Main game manager class"""
    
    def __init__(self, width=800, height=600):
        """
        Initialize game manager
        
        Args:
            width: Screen width
            height: Screen height
        """
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Space Drive - Beta")
        
        # Game state
        self.state = 'menu'  # menu, level_select, playing, level_complete, game_over
        self.current_level = None
        self.player = None
        self.camera = Camera3D(width, height)
        
        # FPS
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        
        # Input tracking
        self.keys = {}
        self.mouse_buttons = (False, False, False)
        self.mouse_pos = (0, 0)
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.QUIT:
            return False
        
        # Get current input state
        keys = pygame.key.get_pressed()
        self.keys = {
            'w': keys[pygame.K_w],
            'a': keys[pygame.K_a],
            's': keys[pygame.K_s],
            'd': keys[pygame.K_d],
            'space': keys[pygame.K_SPACE],
            'escape': keys[pygame.K_ESCAPE],
        }
        
        self.mouse_buttons = pygame.mouse.get_pressed()
        self.mouse_pos = pygame.mouse.get_pos()
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                if self.state == 'menu':
                    if event.key == pygame.K_SPACE:
                        self.start_level(1)
                
                elif self.state == 'level_select':
                    if event.key == pygame.K_1:
                        self.start_level(1)
                    elif event.key == pygame.K_2:
                        self.start_level(2)
                
                elif self.state == 'level_complete':
                    if event.key == pygame.K_SPACE:
                        if self.current_level.level_number < 2:
                            self.start_level(self.current_level.level_number + 1)
                        else:
                            self.state = 'menu'
        
        return True
    
    def start_level(self, level_number):
        """Start a specific level"""
        self.current_level = Level(level_number)
        self.player = Player(0, 0, 0, 'SS2')
        self.state = 'playing'
    
    def update(self, dt):
        """
        Update game state
        
        Args:
            dt: Delta time since last frame
        """
        if self.state == 'playing':
            # Handle player input
            self.player.handle_input(self.keys, self.mouse_buttons, self.mouse_pos)
            
            # Update player
            self.player.update(dt)
            
            # Update level (enemies, collisions)
            self.level.update(dt, self.player)
            
            # Check collisions
            collisions = self.current_level.check_collisions(self.player)
            if collisions['player_hit']:
                self.player.take_damage(collisions['player_damage'])
            
            # Update camera
            self.camera.follow_player(*self.player.get_position())
            
            # Check level completion
            if self.current_level.is_complete():
                self.state = 'level_complete'
            
            # Check game over
            if not self.player.is_alive():
                self.state = 'game_over'
    
    def draw(self):
        """Draw the game"""
        self.screen.fill((0, 0, 0))  # Black background
        
        if self.state == 'menu':
            self._draw_menu()
        
        elif self.state == 'level_select':
            self._draw_level_select()
        
        elif self.state == 'playing':
            self._draw_game()
        
        elif self.state == 'level_complete':
            self._draw_level_complete()
        
        elif self.state == 'game_over':
            self._draw_game_over()
        
        pygame.display.flip()
    
    def _draw_menu(self):
        """Draw main menu"""
        title = self.large_font.render("SPACE DRIVE", True, (0, 255, 255))
        subtitle = self.font.render("Press SPACE to start", True, (255, 255, 255))
        version = self.font.render("Beta v0.1", True, (100, 100, 100))
        
        title_rect = title.get_rect(center=(self.width // 2, 100))
        subtitle_rect = subtitle.get_rect(center=(self.width // 2, 250))
        version_rect = version.get_rect(center=(self.width // 2, self.height - 50))
        
        self.screen.blit(title, title_rect)
        self.screen.blit(subtitle, subtitle_rect)
        self.screen.blit(version, version_rect)
    
    def _draw_level_select(self):
        """Draw level select screen"""
        title = self.large_font.render("SELECT LEVEL", True, (0, 255, 255))
        level1 = self.font.render("Press 1: Level 1 - First Encounter", True, (255, 255, 255))
        level2 = self.font.render("Press 2: Level 2 - Deep Space", True, (255, 255, 255))
        
        self.screen.blit(title, (100, 50))
        self.screen.blit(level1, (100, 150))
        self.screen.blit(level2, (100, 200))
    
    def _draw_game(self):
        """Draw gameplay"""
        # Draw stars/background
        self._draw_background()
        
        # Draw player
        player_screen_pos = self.camera.project_point(*self.player.get_position())
        pygame.draw.circle(self.screen, (0, 255, 0), player_screen_pos, 8)
        
        # Draw player asteroids
        for asteroid in self.player.asteroids:
            ast_screen_pos = self.camera.project_point(asteroid['x'], asteroid['y'], asteroid['z'])
            pygame.draw.circle(self.screen, (255, 200, 0), ast_screen_pos, 3)
        
        # Draw enemies
        for enemy in self.current_level.enemies:
            enemy_screen_pos = self.camera.project_point(*enemy.get_position())
            color = enemy.stats['color']
            pygame.draw.circle(self.screen, color, enemy_screen_pos, 6)
        
        # Draw UI
        self._draw_ui()
    
    def _draw_background(self):
        """Draw space background"""
        # Simple starfield effect
        import random
        random.seed(42)  # Consistent stars
        for _ in range(50):
            x = random.randint(0, self.width)
            y = random.randint(0, self.height)
            pygame.draw.circle(self.screen, (200, 200, 200), (x, y), 1)
    
    def _draw_ui(self):
        """Draw UI elements"""
        # Player info
        player_info = self.player.get_info()
        level_info = self.current_level.get_info()
        
        # Health bar
        health_text = self.font.render(
            f"HP: {player_info['health']}/{player_info['max_health']}",
            True, (255, 0, 0)
        )
        self.screen.blit(health_text, (10, 10))
        
        # Level info
        level_text = self.font.render(
            f"Level {level_info['level']}: {level_info['name']}",
            True, (0, 255, 255)
        )
        self.screen.blit(level_text, (10, 40))
        
        # Objective
        objective_text = self.font.render(
            self.current_level.get_objective(),
            True, (255, 255, 255)
        )
        self.screen.blit(objective_text, (10, 70))
        
        # Controls
        controls = self.font.render(
            "WASD: Move | MOUSE: Aim | SPACE: Attack | Click: Asteroid",
            True, (150, 150, 150)
        )
        self.screen.blit(controls, (10, self.height - 30))
    
    def _draw_level_complete(self):
        """Draw level complete screen"""
        text = self.large_font.render("LEVEL COMPLETE!", True, (0, 255, 0))
        
        if self.current_level.level_number < 2:
            next_text = self.font.render("Press SPACE for next level", True, (255, 255, 255))
        else:
            next_text = self.font.render("Press SPACE to return to menu (Beta ends here)", True, (255, 255, 255))
        
        self.screen.blit(text, (self.width // 2 - 200, self.height // 2 - 50))
        self.screen.blit(next_text, (self.width // 2 - 200, self.height // 2 + 50))
    
    def _draw_game_over(self):
        """Draw game over screen"""
        text = self.large_font.render("GAME OVER", True, (255, 0, 0))
        restart = self.font.render("Press SPACE to return to menu", True, (255, 255, 255))
        
        self.screen.blit(text, (self.width // 2 - 150, self.height // 2 - 50))
        self.screen.blit(restart, (self.width // 2 - 150, self.height // 2 + 50))
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            dt = self.clock.tick(self.fps) / 1000.0  # Delta time in seconds
            
            running = self.handle_events()
            self.update(dt)
            self.draw()
        
        pygame.quit()
