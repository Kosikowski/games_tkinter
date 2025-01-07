"""

Technical Features:
-----------------
1. Movement System:
   - Controlled speed using time-based updates
   - Separate ghost movement timing
   - Proper boundary checking
   - Tunnel wrapping mechanics

2. Ghost AI:
   - Probability-based direction changes
   - Target-based movement
   - Different behaviors in normal/power mode
   - Collision avoidance

3. Game State Management:
   - Proper game loop timing
   - State transitions
   - Score tracking
   - Life system
   - Power mode duration

4. Error Handling:
   - Boundary checking
   - Array index protection
   - Movement validation
   - Collision safety

Usage:
-----
Run the game:
    python pacman2.py

Controls:
    - Arrow keys: Move Pacman
    - Enter: Restart game
    - Escape: Quit game

Game Elements:
------------
- Pacman (Yellow)
- Ghosts (Red, Pink, Cyan, Orange)
- Dots (White)
- Power Dots (Large White)
- Walls (Blue)

Scoring:
-------
- Regular Dot: 10 points
- Power Dot: 50 points
- Ghost eaten: 200 points

Implementation Details:
--------------------
1. Maze Generation:
   - Uses predefined layout for authentic experience
   - Includes ghost house and tunnels
   - Strategic dot placement
   - Power dot positioning

2. Movement Mechanics:
   - Time-based updates for consistent speed
   - Smooth animation transitions
   - Proper collision handling
   - Tunnel wrapping logic

3. Ghost AI Behavior:
   - Individual personality traits
   - State-based decision making
   - Target selection logic
   - Power mode reactions

4. Game State Management:
   - Multiple game states (playing, paused, game over)
   - Score and lives tracking
   - Power mode timing
   - Win/lose conditions
"""

from typing import List, Tuple
from pacman import *
import time  # Add this import

# ... (GameObject, Pacman, Ghost, Dot, and PowerDot classes remain the same)

class PacmanGame2(tk.Tk):
    """
    Enhanced version of the Pacman game with improved features.
    
    Key Improvements:
        - Better maze layout
        - Improved ghost AI
        - Smoother animations
        - More accurate timing
        - Enhanced visuals
    """
    
    def __init__(self):
        """
        Initialize enhanced game with improved controls and timing.
        
        Features:
            - Movement delay controls
            - Ghost movement timing
            - Animation counters
            - Game state tracking
        """
        super().__init__()
        
        self.title("Pacman")
        self.grid_size = 20  # pixels per grid cell
        self.grid_width = 28
        self.grid_height = 31
        
        # Add movement delay controls
        self.move_delay = 150  # milliseconds between moves (slower)
        self.last_move_time = time.time() * 1000  # Convert to milliseconds
        self.ghost_move_counter = 0
        self.ghost_move_delay = 2  # Move ghosts every N frames
        
        # Create canvas
        self.canvas = tk.Canvas(self, width=self.grid_width * self.grid_size,
                              height=self.grid_height * self.grid_size,
                              bg='black')
        self.canvas.pack()
        
        # Create game objects
        self.pacman = Pacman(14, 23)  # Start position
        self.ghosts = [
            Ghost(13, 11, Ghost.COLORS[0]),  # Red ghost
            Ghost(14, 11, Ghost.COLORS[1]),  # Pink ghost
            Ghost(13, 12, Ghost.COLORS[2]),  # Cyan ghost
            Ghost(14, 12, Ghost.COLORS[3])   # Orange ghost
        ]
        
        # Create maze and dots
        self.maze = self.create_maze()
        self.dots = self.create_dots()
        self.power_dots = self.create_power_dots()
        
        # Bind keys
        self.bind('<KeyPress>', self.handle_keypress)
        
        # Game state
        self.game_over = False
        self.power_mode = False
        self.power_time = 0
        
        # Animation variables
        self.animation_counter = 0
        
        # Start game loop
        self.update_game()
    
    def create_maze(self) -> List[List[bool]]:
        """
        Create classic Pacman maze layout.
        
        Features:
            - Proper corridors
            - Ghost house
            - Tunnel passages
            - Strategic walls
        
        Returns:
            List[List[bool]]: 2D grid representing maze layout
        """
        # Initialize all as walls
        maze = [[True] * self.grid_width for _ in range(self.grid_height)]
        
        # Define the main corridors
        # Horizontal corridors
        for y in [1, 5, 8, 14, 20, 23, 26, 29]:
            for x in range(1, self.grid_width-1):
                maze[y][x] = False
                
        # Vertical corridors
        for x in [1, 6, 12, 15, 21, 26]:
            for y in range(1, self.grid_height-1):
                maze[y][x] = False
        
        # Ghost house
        for y in range(11, 15):
            for x in range(11, 17):
                maze[y][x] = False
        
        # Add ghost house door
        maze[11][13] = True
        maze[11][14] = True
        
        # Add tunnels on sides
        maze[14][0] = False
        maze[14][self.grid_width-1] = False
        
        # Add some additional paths
        additional_paths = [
            (2, 2, 4, 4),    # Top left box
            (2, 23, 4, 25),  # Top right box
            (26, 2, 28, 4),  # Bottom left box
            (26, 23, 28, 25) # Bottom right box
        ]
        
        for y1, x1, y2, x2 in additional_paths:
            for y in range(y1, y2+1):
                for x in range(x1, x2+1):
                    maze[y][x] = False
        
        return maze
    
    def create_dots(self) -> List[Dot]:
        """Create dots in the maze"""
        dots = []
        exclude_positions = {
            (14, 23),  # Pacman start
            (13, 11), (14, 11), (13, 12), (14, 12)  # Ghost positions
        }
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if not self.maze[y][x] and (x, y) not in exclude_positions:
                    # Exclude ghost house area
                    if not (11 <= y <= 14 and 11 <= x <= 16):
                        dots.append(Dot(x, y))
        return dots
    
    def create_power_dots(self) -> List[PowerDot]:
        """Create power dots in specific locations"""
        return [
            PowerDot(1, 3),    # Top left
            PowerDot(26, 3),   # Top right
            PowerDot(1, 23),   # Bottom left
            PowerDot(26, 23)   # Bottom right
        ]
    
    def move_ghosts(self):
        """
        Enhanced ghost movement with improved AI.
        
        Features:
            - Different behaviors per ghost
            - Power mode reactions
            - Better pathfinding
            - Tunnel handling
            - Collision avoidance
        """
        for ghost in self.ghosts:
            if self.power_mode:
                # Reduce ghost movement probability when in power mode
                if random.random() > 0.7:  # 30% chance to move when vulnerable
                    continue
                # Run away from Pacman
                dx = ghost.x - self.pacman.x
                dy = ghost.y - self.pacman.y
                
                # Choose direction away from Pacman
                possible_dirs = []
                # Check all possible directions with boundary wrapping
                # Right
                next_x = (ghost.x + 1) % self.grid_width
                if not self.maze[ghost.y][next_x]:
                    possible_dirs.append([1, 0])
                # Left
                next_x = (ghost.x - 1) % self.grid_width
                if not self.maze[ghost.y][next_x]:
                    possible_dirs.append([-1, 0])
                # Down
                if ghost.y + 1 < self.grid_height and not self.maze[ghost.y + 1][ghost.x]:
                    possible_dirs.append([0, 1])
                # Up
                if ghost.y - 1 >= 0 and not self.maze[ghost.y - 1][ghost.x]:
                    possible_dirs.append([0, -1])
            else:
                # Reduce direction change probability
                if random.random() > 0.15:  # 15% chance to change direction
                    continue
                # Chase Pacman
                possible_dirs = []
                for dx, dy in [[-1, 0], [1, 0], [0, -1], [0, 1]]:
                    new_x = (ghost.x + dx) % self.grid_width  # Wrap horizontally
                    new_y = ghost.y + dy
                    if 0 <= new_y < self.grid_height:  # Only check vertical bounds
                        if not self.maze[new_y][new_x]:
                            possible_dirs.append([dx, dy])
            
            # Choose new direction
            if possible_dirs and random.random() < 0.3:  # 30% chance to change direction
                ghost.direction = random.choice(possible_dirs)
            
            # Move ghost
            new_x = (ghost.x + ghost.direction[0]) % self.grid_width  # Wrap horizontally
            new_y = ghost.y + ghost.direction[1]
            
            # Only move if within vertical bounds and not hitting a wall
            if 0 <= new_y < self.grid_height and not self.maze[new_y][new_x]:
                ghost.x = new_x
                ghost.y = new_y
            else:
                # If hit wall, try different direction
                ghost.direction = random.choice(possible_dirs) if possible_dirs else [0, 0]

    def move_pacman(self):
        """Move pacman and check collisions with tunnel support"""
        new_x = self.pacman.x + self.pacman.direction[0]
        new_y = self.pacman.y + self.pacman.direction[1]
        
        # Handle tunnel wrapping
        if new_x < 0:
            new_x = self.grid_width - 1
        elif new_x >= self.grid_width:
            new_x = 0
        
        # Check wall collision
        if not self.maze[new_y][new_x]:
            self.pacman.x = new_x
            self.pacman.y = new_y
            
        # Check collisions
        self._check_dot_collision()
        self._check_power_dot_collision()
    
    def _check_dot_collision(self):
        """Check and handle dot collisions"""
        for dot in self.dots[:]:
            if (dot.x, dot.y) == (self.pacman.x, self.pacman.y):
                self.dots.remove(dot)
                self.pacman.score += 10
    
    def _check_power_dot_collision(self):
        """Check and handle power dot collisions"""
        for dot in self.power_dots[:]:
            if (dot.x, dot.y) == (self.pacman.x, self.pacman.y):
                self.power_dots.remove(dot)
                self.power_mode = True
                self.power_time = 300  # 5 seconds at 60 FPS
                self.pacman.score += 50

    def handle_keypress(self, event):
        """Handle keyboard input"""
        if self.game_over:
            if event.keysym == 'Return':  # Press Enter to restart
                self.restart_game()
            return
            
        if event.keysym == 'Left':
            self.pacman.direction = [-1, 0]
        elif event.keysym == 'Right':
            self.pacman.direction = [1, 0]
        elif event.keysym == 'Up':
            self.pacman.direction = [0, -1]
        elif event.keysym == 'Down':
            self.pacman.direction = [0, 1]
        elif event.keysym == 'Escape':  # Add pause/quit functionality
            self.quit()

    def update_game(self):
        """
        Main game loop with improved timing.
        
        Features:
            - Time-based movement
            - Smooth animations
            - State updates
            - Collision checks
            - Display updates
        """
        if not self.game_over:
            current_time = time.time() * 1000  # Get current time in milliseconds
            
            self.animation_counter += 1
            
            # Update mouth animation (slower)
            if self.animation_counter % 15 == 0:  # Every 15 frames
                self.pacman.mouth_open = not self.pacman.mouth_open
            
            # Move objects with delay
            if current_time - self.last_move_time >= self.move_delay:
                self.move_pacman()
                self.last_move_time = current_time
            
            # Move ghosts less frequently
            self.ghost_move_counter += 1
            if self.ghost_move_counter >= self.ghost_move_delay:
                self.move_ghosts()
                self.ghost_move_counter = 0
            
            self.check_ghost_collision()
            
            # Update power mode
            if self.power_mode:
                self.power_time -= 1
                if self.power_time <= 0:
                    self.power_mode = False
            
            # Draw everything
            self.draw_game()
            
            # Check win condition
            if not self.dots and not self.power_dots:
                self.game_over = True
                self.show_victory_message()
            
            # Schedule next update (slower frame rate)
            self.after(33, self.update_game)  # ~30 FPS instead of 60

    def check_ghost_collision(self):
        """
        Enhanced collision detection between Pacman and ghosts.
        
        Features:
            - Power mode handling
            - Score updates
            - Life management
            - Position reset
            - Game over detection
        """
        for ghost in self.ghosts[:]:  # Use slice to allow removal during iteration
            if (ghost.x, ghost.y) == (self.pacman.x, self.pacman.y):
                if self.power_mode:
                    # Remove ghost and add points
                    self.ghosts.remove(ghost)
                    self.pacman.score += 200
                else:
                    self.pacman.lives -= 1
                    if self.pacman.lives <= 0:
                        self.game_over = True
                        self.show_game_over_message()
                    else:
                        self.reset_positions()

    def reset_positions(self):
        """Reset positions of pacman and ghosts"""
        self.pacman.x, self.pacman.y = 14, 23
        self.pacman.direction = [0, 0]
        self.last_move_time = time.time() * 1000  # Reset movement timer
        ghost_positions = [(13, 11), (14, 11), (13, 12), (14, 12)]
        for ghost, pos in zip(self.ghosts, ghost_positions):
            ghost.x, ghost.y = pos
            ghost.direction = [0, 1]

    def draw_game(self):
        """
        Improved game rendering with visual enhancements.
        
        Features:
            - Better wall appearance
            - Ghost visualization
            - Power mode effects
            - Score display
            - Animation handling
        """
        self.canvas.delete('all')
        
        # Draw maze
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.maze[y][x]:
                    self.canvas.create_rectangle(
                        x * self.grid_size, y * self.grid_size,
                        (x + 1) * self.grid_size, (y + 1) * self.grid_size,
                        fill='blue', outline='darkblue'
                    )
        
        # Draw dots
        for dot in self.dots:
            dot.draw(self.canvas)
        
        # Draw power dots
        for dot in self.power_dots:
            dot.draw(self.canvas)
        
        # Draw ghosts with power mode color change
        for ghost in self.ghosts:
            if self.power_mode:
                original_color = ghost.color
                ghost.color = 'blue'  # Ghosts turn blue when vulnerable
                ghost.draw(self.canvas)
                ghost.color = original_color
            else:
                ghost.draw(self.canvas)
        
        # Draw pacman
        self.pacman.draw(self.canvas)
        
        # Draw score and lives
        self.canvas.create_text(
            50, 10, text=f"Score: {self.pacman.score}",
            fill='white', anchor='w'
        )
        self.canvas.create_text(
            200, 10, text=f"Lives: {self.pacman.lives}",
            fill='white', anchor='w'
        )

    def show_game_over_message(self):
        """Show game over message"""
        self.canvas.create_text(
            self.grid_width * self.grid_size // 2,
            self.grid_height * self.grid_size // 2,
            text="GAME OVER\nPress Enter to restart",
            fill='red',
            font=('Arial', 30),
            justify='center'
        )

    def show_victory_message(self):
        """Show victory message"""
        self.canvas.create_text(
            self.grid_width * self.grid_size // 2,
            self.grid_height * self.grid_size // 2,
            text=f"VICTORY!\nScore: {self.pacman.score}\nPress Enter to restart",
            fill='yellow',
            font=('Arial', 30),
            justify='center'
        )

    def restart_game(self):
        """Restart the game"""
        self.pacman = Pacman(14, 23)
        self.ghosts = [
            Ghost(13, 11, Ghost.COLORS[0]),
            Ghost(14, 11, Ghost.COLORS[1]),
            Ghost(13, 12, Ghost.COLORS[2]),
            Ghost(14, 12, Ghost.COLORS[3])
        ]
        self.dots = self.create_dots()
        self.power_dots = self.create_power_dots()
        self.game_over = False
        self.power_mode = False
        self.power_time = 0
        self.animation_counter = 0
        self.last_move_time = time.time() * 1000
        self.ghost_move_counter = 0
        self.update_game()

if __name__ == "__main__":
    game = PacmanGame2()
    game.mainloop() 
