"""
Enemy ship classes
Represents AI-controlled enemy spaceships
"""

import random
import math

class Enemy:
    """Base enemy ship class"""
    
    TYPES = {
        'fighter': {
            'name': 'Fighter',
            'health': 30,
            'speed': 20,
            'damage': 8,
            'attack_range': 25,
            'attack_cooldown': 1.0,
            'color': (255, 100, 100),
        },
        'scout': {
            'name': 'Scout',
            'health': 15,
            'speed': 35,
            'damage': 5,
            'attack_range': 20,
            'attack_cooldown': 1.5,
            'color': (255, 200, 100),
        },
    }
    
    def __init__(self, x, z, enemy_type='fighter'):
        """
        Initialize enemy ship
        
        Args:
            x: Starting X position
            z: Starting Z position
            enemy_type: Type of enemy
        """
        self.enemy_type = enemy_type
        self.stats = self.TYPES[enemy_type].copy()
        
        # Position
        self.x = x
        self.y = 0
        self.z = z
        
        # Velocity
        self.vel_x = 0
        self.vel_z = 0
        
        # Health
        self.health = self.stats['health']
        self.max_health = self.stats['health']
        
        # AI state
        self.target = None
        self.attack_cooldown = 0
        self.behavior_timer = 0
        self.behavior = 'patrol'  # patrol, chase, attack
        
        # Size for collision detection
        self.radius = 1.5
    
    def update(self, dt, player=None, world_bounds=(-100, 100, -100, 100)):
        """
        Update enemy state with AI behavior
        
        Args:
            dt: Delta time since last frame
            player: Reference to player object
            world_bounds: World boundary constraints
        """
        # Update position
        self.x += self.vel_x * dt
        self.z += self.vel_z * dt
        
        # Keep within bounds
        min_x, max_x, min_z, max_z = world_bounds
        self.x = max(min_x, min(max_x, self.x))
        self.z = max(min_z, min(max_z, self.z))
        
        # Update cooldowns
        self.attack_cooldown -= dt
        self.behavior_timer -= dt
        
        # AI behavior
        if player and player.is_alive():
            self._update_ai(dt, player)
    
    def _update_ai(self, dt, player):
        """
        Update AI behavior
        
        Args:
            dt: Delta time
            player: Player object for targeting
        """
        # Calculate distance to player
        dx = player.x - self.x
        dz = player.z - self.z
        distance = math.sqrt(dx**2 + dz**2)
        
        # Decide behavior based on distance
        if distance < self.stats['attack_range']:
            self.behavior = 'attack'
        elif distance < 50:
            self.behavior = 'chase'
        else:
            self.behavior = 'patrol'
        
        # Execute behavior
        if self.behavior == 'chase':
            # Move toward player
            if distance > 0:
                speed = self.stats['speed']
                self.vel_x = (dx / distance) * speed
                self.vel_z = (dz / distance) * speed
        
        elif self.behavior == 'attack':
            # Close in and attack
            if distance > self.stats['attack_range'] * 0.8:
                speed = self.stats['speed']
                self.vel_x = (dx / distance) * speed * 0.5
                self.vel_z = (dz / distance) * speed * 0.5
            else:
                self.vel_x *= 0.5
                self.vel_z *= 0.5
            
            # Try to attack
            if self.attack_cooldown <= 0:
                self.attack()
        
        elif self.behavior == 'patrol':
            # Wander randomly
            if self.behavior_timer <= 0:
                self.behavior_timer = random.uniform(2, 4)
                angle = random.uniform(0, 2 * math.pi)
                speed = self.stats['speed'] * 0.5
                self.vel_x = math.cos(angle) * speed
                self.vel_z = math.sin(angle) * speed
    
    def attack(self):
        """Perform attack"""
        self.attack_cooldown = self.stats['attack_cooldown']
        return self.stats['damage']
    
    def take_damage(self, damage):
        """
        Take damage
        
        Args:
            damage: Damage amount
        """
        self.health -= damage
        if self.health < 0:
            self.health = 0
    
    def is_alive(self):
        """Check if enemy is alive"""
        return self.health > 0
    
    def get_position(self):
        """Get current position"""
        return (self.x, self.y, self.z)
    
    def get_info(self):
        """Get enemy info"""
        return {
            'type': self.stats['name'],
            'health': self.health,
            'max_health': self.max_health,
        }
