#!/usr/bin/env python3
"""
Space Drive - Beta Edition
A 3D space combat game where you pilot a starship

Run this file to start the game:
    python main.py
"""

import pygame
from game.game_manager import GameManager


def main():
    """Main entry point"""
    # Initialize pygame
    pygame.init()
    
    # Create and run game
    game = GameManager(width=800, height=600)
    game.state = 'menu'  # Start at menu
    
    try:
        game.run()
    except Exception as e:
        print(f"Error running game: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()


if __name__ == '__main__':
    main()
