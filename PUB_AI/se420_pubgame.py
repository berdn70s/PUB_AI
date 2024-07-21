import tkinter as tk
from tkinter import PhotoImage
import heapq


class RobotGameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("PUB Robot Game")
        self.root.configure(bg='lightblue')

        self.canvas = tk.Canvas(self.root, width=300, height=300, bg='lightblue')
        self.canvas.pack()

        self.robot_image = PhotoImage(file="robot.png")
        self.resized_image = self.robot_image.subsample(20, 20)

        self.rooms = {
            'A': {'right': 'B', 'down': 'D'},
            'B': {'left': 'A', 'right': 'C', 'down': 'E'},
            'C': {'left': 'B', 'down': 'F'},
            'D': {'up': 'A', 'right': 'E', 'down': 'G'},
            'E': {'up': 'B', 'left': 'D', 'right': 'F', 'down': 'H'},
            'F': {'up': 'C', 'left': 'E', 'down': 'I'},
            'G': {'up': 'D', 'right': 'H'},
            'H': {'up': 'E', 'left': 'G', 'right': 'I'},
            'I': {'up': 'F', 'left': 'H'}
        }
        self.room_coordinates = {
            'A': (0, 0), 'B': (1, 0), 'C': (2, 0),
            'D': (0, 1), 'E': (1, 1), 'F': (2, 1),
            'G': (0, 2), 'H': (1, 2), 'I': (2, 2)
        }

        self.start_room = ''
        self.goal_room = ''
        self.walls = set()

        self.create_widgets()

        self.path_label = tk.Label(self.root, text="Path taken: ")
        self.path_label.pack()
        self.expanded_label = tk.Label(self.root, text="Expanded nodes: ")
        self.expanded_label.pack()
        self.path_label.config(bg='lightblue', fg='black', font=('Impact', 16))
        self.expanded_label.config(bg='lightblue', fg='black', font=('Impact', 16))

    def create_widgets(self):
        self.draw_rooms()
        self.draw_robot()

        tk.Label(self.root, text="Enter Start Room", bg='lightblue', fg='black', font=('Impact', 16), pady=10).pack()
        self.frame = tk.Frame(self.root, bd=3, relief=tk.RAISED, bg='white')
        self.frame.pack(pady=5)
        self.start_entry = tk.Entry(self.frame, width=5)
        self.start_entry.pack()

        tk.Label(self.root, text="Enter Goal Room", bg='lightblue', fg='black', font=('Impact', 16), pady=5).pack()
        self.frame = tk.Frame(self.root, bd=3, relief=tk.RAISED, bg='white')
        self.frame.pack(pady=5)
        self.goal_entry = tk.Entry(self.frame, width=5)
        self.goal_entry.pack()

        tk.Label(self.root, text="Enter Walls (e.g., AD GH)", bg='lightblue', fg='black', font=('Impact', 16),
                 pady=10).pack()
        self.frame = tk.Frame(self.root, bd=3, relief=tk.RAISED, bg='white')
        self.frame.pack(pady=5)
        self.walls_entry = tk.Entry(self.frame, width=10)
        self.walls_entry.pack()

        self.algorithm_var = tk.StringVar(value="Uniform Cost")
        self.choose = tk.Label(self.root, text="Choose Search Algorithm:", bg='lightblue', fg='black',
                               font=('Impact', 16))
        self.choose.pack()
        self.frame = tk.Frame(self.root, bd=4, relief=tk.RAISED, bg='white')
        self.frame.pack(pady=5)
        tk.Radiobutton(self.frame, text="Uniform Cost", variable=self.algorithm_var, value="Uniform Cost", bg='white',
                       fg='black', font=('Impact', 16)).pack()
        tk.Radiobutton(self.frame, text="A* Search", variable=self.algorithm_var, value="A* Search", bg='white',
                       fg='black', font=('Impact', 16)).pack()

        self.start_button = tk.Button(self.root, text="Start Search", command=self.start_search,
                                      highlightcolor='lightblue', font=('Impact', 16))
        self.start_button.pack()

        self.restart_button = tk.Button(self.root, text="Restart", command=self.restart_game,
                                        highlightcolor='lightblue', font=('Impact', 16))
        self.restart_button.pack()


    def draw_rooms(self):
        room_size = 100
        row_index = 0
        col_index = 0

        for room_name, connections in self.rooms.items():
            x1 = col_index * room_size
            y1 = row_index * room_size
            x2 = x1 + room_size
            y2 = y1 + room_size

            color = 'white'
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
            self.canvas.create_text(x1 + room_size / 2, y1 + room_size / 2, text=room_name)

            col_index += 1
            if col_index >= 3:
                col_index = 0
                row_index += 1

        for wall in self.walls:
            x1, y1, x2, y2 = self.calculate_wall_coordinates(wall)
            self.canvas.create_line(x1, y1, x2, y2, fill='black', width=2)
            self.canvas.configure(borderwidth=2, relief='ridge')

    def draw_robot(self):
        if hasattr(self, 'robot_icon'):
            self.canvas.delete(self.robot_icon)

        room_coordinates = {'A': (50, 50), 'B': (150, 50), 'C': (250, 50),
                            'D': (50, 150), 'E': (150, 150), 'F': (250, 150),
                            'G': (50, 250), 'H': (150, 250), 'I': (250, 250)}

        start_room_coordinates = room_coordinates.get(self.start_room, (30, 30))

        self.robot_icon = self.canvas.create_image(start_room_coordinates[0], start_room_coordinates[1],
                                                   image=self.resized_image, anchor='center')

    def update_room_color(self, room_name, color):
        room_size = 100
        row_index = 0
        col_index = 0

        for room, connections in self.rooms.items():
            if room == room_name:
                x1 = col_index * room_size
                y1 = row_index * room_size
                x2 = x1 + room_size
                y2 = y1 + room_size

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)
                self.canvas.create_text(x1 + room_size / 2, y1 + room_size / 2, text=room)

                break

            col_index += 1
            if col_index >= 3:
                col_index = 0
                row_index += 1

    # def hamming_distance(self, state, goal):
    #     distance = 0
    #     for i in range(len(state)):
    #         if state[i] != goal[i]:
    #             distance += 1
    #     return distance

    def hamming_distance(self, state, goal):
        x1, y1 = self.room_to_coordinates(state)
        x2, y2 = self.room_to_coordinates(goal)
        distance = abs(x1 - x2) + abs(y1 - y2)
        return distance

    def room_to_coordinates(self,rooms):

        index = ord(rooms) - ord('A')
        return index % 3, index // 3

    def calculate_wall_coordinates(self, wall):
        wall_positions = {
            'AB': (0, 0, 100, 0),
            'BC': (100, 0, 200, 0),
            'DE': (0, 100, 0, 200),
            'EF': (100, 100, 100, 200),
            'GH': (200, 0, 300, 0),
            'HI': (300, 0, 400, 0),
            'AD': (0, 0, 0, 100),
            'DG': (0, 100, 0, 200),
            'BE': (100, 0, 100, 100),
            'EH': (100, 100, 100, 200),
            'CF': (200, 0, 200, 100),
            'FI': (200, 100, 200, 200),
            'BA': (0, 0, 100, 0),
            'CB': (100, 0, 200, 0),
            'ED': (0, 100, 0, 200),
            'FE': (100, 100, 100, 200),
            'HG': (200, 0, 300, 0),
            'IH': (300, 0, 400, 0),
            'DA': (0, 0, 0, 100),
            'GD': (0, 100, 0, 200),
            'EB': (100, 0, 100, 100),
            'HE': (100, 100, 100, 200),
            'FC': (200, 0, 200, 100),
            'IF': (200, 100, 200, 200)
        }
        return wall_positions[wall]

    def restart_game(self):
        self.start_entry.delete(0, tk.END)
        self.goal_entry.delete(0, tk.END)
        self.walls_entry.delete(0, tk.END)
        self.path_label.config(text="Path taken: ")
        self.expanded_label.config(text="Expanded nodes: ")

        self.canvas.delete("all")

        self.start_room = self.start_entry.get().upper()
        self.goal_room = self.goal_entry.get().upper()

        self.draw_rooms()
        self.draw_robot()

        self.canvas.delete("trace")

    def start_search(self):
        self.start_room = self.start_entry.get().upper()
        self.goal_room = self.goal_entry.get().upper()

        self.update_room_color(self.start_room, 'lightgreen')
        self.update_room_color(self.goal_room, 'lightcoral')

        self.walls = set(self.walls_entry.get().upper().split())

        if self.start_room + self.rooms[self.start_room].get('left', '') in self.walls:
            self.path_label.config(text="Error: Start room is blocked by walls.")
            return

        if self.goal_room + self.rooms[self.goal_room].get('left', '') in self.walls:
            self.path_label.config(text="Error: Goal room is blocked by walls.")
            return

        strategy = self.algorithm_var.get().lower()
        path = self.search(self.start_room, self.goal_room, self.walls, strategy)

        self.draw_robot()

        if path:
            self.animate_robot(path)
            self.canvas.delete("trace")
            self.draw_trace(path)
        else:
            self.path_label.config(text="Error: Goal not reached within 10 expanded nodes.")

    def search(self, source, goal, walls, strategy):
        visited = []
        frontier = [(0, source, [])]
        expanded_nodes_sequence = []

        while frontier:
            cost, current_room, path = heapq.heappop(frontier)
            expanded_nodes_sequence.append(current_room)

            if current_room == goal:
                self.expanded_label.config(text=f"Expanded nodes: {' -> '.join(visited)}")
                self.path_label.config(text=f"Path taken: {' -> '.join(path + [current_room])}")
                return path + [current_room]

            if current_room not in visited:

                visited.append(current_room)
                print(current_room)

                for direction, neighbor in self.rooms[current_room].items():
                    if direction in ['up', 'down', 'left', 'right']:
                        new_room = self.rooms[current_room][direction]
                        if current_room + new_room not in walls and new_room not in visited:
                            new_cost = cost + (2 if direction in ['right', 'left'] else 1)
                            new_path = path + [current_room]
                            priority = new_cost if strategy == 'uniform cost' else new_cost + self.hamming_distance(new_room,goal)
                            heapq.heappush(frontier, (priority, new_room, new_path))
                            print(expanded_nodes_sequence)

        print("Goal not reached within 10 expanded nodes.")
        return None




    def animate_robot(self, path):
        self.path_label.config(text=f"Path taken: {' -> '.join(path)}")
        movements = {'A': (50, 50), 'B': (150, 50), 'C': (250, 50),
                     'D': (50, 150), 'E': (150, 150), 'F': (250, 150),
                     'G': (50, 250), 'H': (150, 250), 'I': (250, 250)}

        trace = []
        for room in path:
            dest_x, dest_y = movements[room]

            while trace:
                x1, y1 = trace.pop(0)
                x2, y2 = trace[0] if trace else (dest_x, dest_y)
                self.canvas.create_line(x1, y1, x2, y2, fill='blue', width=2)
                self.root.update()
                self.root.after(10)

            trace.append((dest_x, dest_y))

            self.canvas.coords(self.robot_icon, dest_x, dest_y)
            self.root.update()
            self.root.after(500)

    def draw_trace(self, path):
        movements = {'A': (50, 50), 'B': (150, 50), 'C': (250, 50),
                     'D': (50, 150), 'E': (150, 150), 'F': (250, 150),
                     'G': (50, 250), 'H': (150, 250), 'I': (250, 250)}

        for i in range(len(path) - 1):
            start_room = path[i]
            end_room = path[i + 1]

            x1, y1 = movements[start_room]
            x2, y2 = movements[end_room]

            self.canvas.create_line(x1, y1, x2, y2, fill='red', width=2, tags="trace")


if __name__ == "__main__":
    root = tk.Tk()
    root.geometry('800x800')
    game_gui = RobotGameGUI(root)
    game_gui.choose.pack(pady=5)
    game_gui.start_button.pack(pady=5)
    game_gui.path_label.pack(pady=5)
    game_gui.expanded_label.pack(pady=5)
    root.mainloop()