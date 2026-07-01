"""
Level management system
Handles level data, enemies, and progression
"""

from game.enemy import Enemy

class Level:
    """Manages a game level"""
    
    # Level definitions
    LEVELS = {
        1: {
            'name': 'First Encounter',
            'description': 'Learn the basics of combat',
            'enemies': [
                {'type': 'scout', 'x': 20, 'z': 30},
                {'type': 'scout', 'x': -20, 'z': 30},
                {'type': 'fighter', 'x': 0, 'z': 50},
            ],
            'objective': 'Defeat all enemies',
        },
        2: {
            'name': 'Deep Space',
            'description': 'Face tougher opposition',
            'enemies': [
                {'type': 'fighter', 'x': 30, 'z': 40},
                {'type': 'fighter', 'x': -30, 'z': 40},
                {'type': 'fighter', 'x': 0, 'z': 60},
                {'type': 'scout', 'x': 40, 'z': 20},
                {'type': 'scout', 'x': -40, 'z': 20},
            ],
            'objective': 'Defeat all enemies',
        },
    }
    
    def __init__(self, level_number=1):
        """
        Initialize level
        
        Args:
            level_number: Which level to load (1 or 2 for beta)
        """
        if level_number not in self.LEVELS:
            level_number = 1
        
        self.level_number = level_number
        self.data = self.LEVELS[level_number].copy()
        
        # Enemies in this level
        self.enemies = []
        self._load_enemies()
        
        # Level state
        self.enemies_defeated = 0
        self.waves_completed = 0
        self.completed = False
        self.start_time = 0
    
    def _load_enemies(self):
        """Load enemies for this level"""
        self.enemies = []
        for enemy_data in self.data['enemies']:
            enemy = Enemy(
                enemy_data['x'],
                enemy_data['z'],
                enemy_data['type']
            )
            self.enemies.append(enemy)
    
    def update(self, dt, player):
        """
        Update level state
        
        Args:
            dt: Delta time
            player: Player object
        """
        # Update all enemies
        alive_enemies = []
        for enemy in self.enemies:
            enemy.update(dt, player)
            if enemy.is_alive():
                alive_enemies.append(enemy)
            else:
                self.enemies_defeated += 1
        
        self.enemies = alive_enemies
        
        # Check if level is complete
        if len(self.enemies) == 0 and not self.completed:
            self.completed = True
    
    def check_collisions(self, player):
        """
        Check collisions between player and enemies/asteroids
        
        Args:
            player: Player object
            
        Returns:
            Dictionary with collision info
        """
        collisions = {
            'player_hit': False,
            'player_damage': 0,
            'enemies_hit': [],
        }
        
        # Check melee attacks vs enemies
        # This would check collision circles and player attack range
        
        # Check asteroids vs enemies
        for asteroid in player.asteroids[:]:
            for enemy in self.enemies:
                ax, ay, az = asteroid['x'], asteroid['y'], asteroid['z']
                ex, ey, ez = enemy.get_position()
                
                # Simple distance check
                dist = ((ax - ex)**2 + (az - ez)**2)**0.5
                if dist < asteroid['radius'] + enemy.radius:
                    # Hit!
                    enemy.take_damage(asteroid['damage'])
                    collisions['enemies_hit'].append(enemy)
                    if asteroid in player.asteroids:
                        player.asteroids.remove(asteroid)
                    break
        
        # Check enemy collisions with player
        for enemy in self.enemies:
            px, py, pz = player.get_position()
            ex, ey, ez = enemy.get_position()
            
            dist = ((px - ex)**2 + (pz - ez)**2)**0.5
            if dist < player.radius + enemy.radius + 5:
                # Enemy in attack range
                collisions['player_hit'] = True
                collisions['player_damage'] = enemy.stats['damage']
        
        return collisions
    
    def is_complete(self):
        """Check if level is complete"""
        return self.completed
    
    def get_objective(self):
        """Get current objective"""
        remaining = len(self.enemies)
        if remaining == 0:
            return "Level Complete!"
        return f"{self.data['objective']} ({remaining} enemies remaining)"
    
    def get_info(self):
        """Get level info for UI"""
        return {
            'level': self.level_number,
            'name': self.data['name'],
            'enemies_remaining': len(self.enemies),
            'enemies_defeated': self.enemies_defeated,
            'completed': self.completed,
        }
