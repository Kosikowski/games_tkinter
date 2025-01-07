import tkinter as tk
from tkinter import ttk
from maze import generate_maze, Cell
from typing import Tuple, List
from collections import deque

class MazeGame(tk.Tk):
    def __init__(self):
        super().__init__()C
        
        self.title("Maze Game")
        self.current_pos = None
        self.path_taken = set()
        
        # Control panel
        self.control_frame = ttk.Frame(self)
        self.control_frame.pack(pady=10)
        
        # Maze size controls
        ttk.Label(self.control_frame, text="Width:").grid(row=0, column=0, padx=5)
        self.width_var = tk.StringVar(value="21")
        ttk.Entry(self.control_frame, textvariable=self.width_var, width=5).grid(row=0, column=1)
        
        ttk.Label(self.control_frame, text="Height:").grid(row=0, column=2, padx=5)
        self.height_var = tk.StringVar(value="21")
        ttk.Entry(self.control_frame, textvariable=self.height_var, width=5).grid(row=0, column=3)
        
        # Complexity control
        ttk.Label(self.control_frame, text="Complexity:").grid(row=0, column=4, padx=5)
        self.complexity_var = tk.StringVar(value="0.7")
        ttk.Entry(self.control_frame, textvariable=self.complexity_var, width=5).grid(row=0, column=5)
        
        # Generate button
        ttk.Button(self.control_frame, text="Generate New Maze", 
                  command=self.generate_new_maze).grid(row=0, column=6, padx=10)
        
        # Reset button
        ttk.Button(self.control_frame, text="Reset Position", 
                  command=self.reset_position).grid(row=0, column=7, padx=10)
        
        # Canvas for maze
        self.cell_size = 30
        self.canvas = tk.Canvas(self, bg='white')
        self.canvas.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)
        
        # Bind arrow keys
        self.bind('<KeyPress>', self.handle_movement)
        
        # Generate initial maze
        self.generate_new_maze()
        
        # Set focus to receive key events
        self.focus_set()
        
        # Add attributes for shortest path
        self.shortest_path = None
        self.game_finished = False

    def generate_new_maze(self):
        """Generate and display a new maze"""
        try:
            width = int(self.width_var.get())
            height = int(self.height_var.get())
            complexity = float(self.complexity_var.get())
        except ValueError:
            print("Invalid input values")
            return
        
        self.maze = generate_maze(width, height, complexity)
        self.current_pos = self.maze.entrance
        self.path_taken = {self.current_pos}
        self.game_finished = False
        self.shortest_path = None
        self.draw_maze()

    def draw_maze(self):
        """Draw the maze on the canvas"""
        width = self.maze.width * self.cell_size
        height = self.maze.height * self.cell_size
        
        self.canvas.delete('all')
        self.canvas.config(width=width, height=height)
        
        # Draw base maze
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                cell = self.maze.grid[y][x]
                x1, y1 = x * self.cell_size, y * self.cell_size
                x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                
                if cell == Cell.WALL:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='black', outline='gray')
                elif cell == Cell.ENTRANCE:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='green', outline='gray')
                elif cell == Cell.EXIT:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='red', outline='gray')
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='white', outline='gray')
        # Draw path taken first

        for pos in self.path_taken:
            y, x = pos
            x1, y1 = x * self.cell_size, y * self.cell_size
            x2, y2 = x1 + self.cell_size, y1 + self.cell_size
            self.canvas.create_rectangle(x1, y1, x2, y2, fill='light blue', outline='gray')
        
        # Draw shortest path on top with transparency effect
        if self.game_finished and self.shortest_path:
            for pos in self.shortest_path:
                if pos not in self.path_taken or pos == self.maze.exit:  # Always show on exit
                    y, x = pos
                    x1, y1 = x * self.cell_size, y * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    # Draw full pink square
                    self.canvas.create_rectangle(x1, y1, x2, y2, fill='pink', outline='gray')
                else:
                    # Draw striped pattern for overlapping paths
                    y, x = pos
                    x1, y1 = x * self.cell_size, y * self.cell_size
                    x2, y2 = x1 + self.cell_size, y1 + self.cell_size
                    # Draw diagonal stripes
                    stripe_width = 4
                    for i in range(0, self.cell_size, stripe_width * 2):
                        self.canvas.create_polygon(
                            x1 + i, y1,
                            min(x1 + i + stripe_width, x2), y1,
                            min(x1 + i + stripe_width, x2), y2,
                            x1 + i, y2,
                            fill='red', outline='')
        
        # Draw current position on top of everything
        y, x = self.current_pos
        x1, y1 = x * self.cell_size, y * self.cell_size
        x2, y2 = x1 + self.cell_size, y1 + self.cell_size
        self.canvas.create_oval(x1+4, y1+4, x2-4, y2-4, fill='blue')
        
        # Check if reached exit
        if self.current_pos == self.maze.exit and not self.game_finished:
            self.game_finished = True
            self.shortest_path = self.find_shortest_path()
            self.show_victory_message()
            self.draw_maze()  # Redraw to show shortest path

    def find_shortest_path(self) -> List[Tuple[int, int]]:
        """Find shortest path from entrance to exit using BFS"""
        queue = deque([(self.maze.entrance, [self.maze.entrance])])
        visited = {self.maze.entrance}
        
        while queue:
            current, path = queue.popleft()
            if current == self.maze.exit:
                return path
            
            y, x = current
            for ny, nx in [(y+1, x), (y-1, x), (y, x+1), (y, x-1)]:
                if (0 <= ny < self.maze.height and 0 <= nx < self.maze.width and 
                    (ny, nx) not in visited and self.maze.grid[ny][nx] != Cell.WALL):
                    visited.add((ny, nx))
                    queue.append(((ny, nx), path + [(ny, nx)]))
        
        return []

    def handle_movement(self, event):
        """Handle arrow key movement"""
        y, x = self.current_pos
        new_pos = None
        
        if event.keysym == 'Up' and y > 0:
            new_pos = (y-1, x)
        elif event.keysym == 'Down' and y < self.maze.height-1:
            new_pos = (y+1, x)
        elif event.keysym == 'Left' and x > 0:
            new_pos = (y, x-1)
        elif event.keysym == 'Right' and x < self.maze.width-1:
            new_pos = (y, x+1)
            
        if new_pos and self.is_valid_move(new_pos):
            self.current_pos = new_pos
            self.path_taken.add(new_pos)
            self.draw_maze()

    def is_valid_move(self, pos: Tuple[int, int]) -> bool:
        """Check if the move is valid (not a wall)"""
        y, x = pos
        return self.maze.grid[y][x] != Cell.WALL

    def reset_position(self):
        """Reset player position to entrance"""
        self.current_pos = self.maze.entrance
        self.path_taken = {self.current_pos}
        self.game_finished = False
        self.shortest_path = None
        self.draw_maze()

    def show_victory_message(self):
        """Show victory message with path comparison"""
        victory_window = tk.Toplevel(self)
        victory_window.title("Victory!")
        
        # Calculate path efficiency
        shortest_length = len(self.shortest_path) - 1  # -1 because path includes start position
        your_length = len(self.path_taken) - 1  # -1 for the same reason
        difference = your_length - shortest_length
        efficiency = (shortest_length / your_length) * 100 if your_length > 0 else 0
        
        message_text = (
            f"Congratulations! You solved the maze!\n\n"
            f"Your path length: {your_length} steps\n"
            f"Shortest path length: {shortest_length} steps\n"
            f"Difference: +{difference} steps\n"
            f"Path efficiency: {efficiency:.1f}%"
        )
        
        message = ttk.Label(victory_window, text=message_text, padding=20)
        message.pack()
        
        close_button = ttk.Button(victory_window, text="OK", 
                                command=victory_window.destroy)
        close_button.pack(pady=10)
        
        # Center the window
        victory_window.geometry("+%d+%d" % (self.winfo_x() + 200, self.winfo_y() + 200))

if __name__ == "__main__":
    game = MazeGame()
    game.mainloop() 
