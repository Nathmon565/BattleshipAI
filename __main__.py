from enum import Enum
import random
import time

class GridState(Enum):
	UNKNOWN = 0
	MISS = 1
	HIT = 2
	OCCUPIED = 3
	SUNK = 4

class Direction(Enum):
	NORTH = 0
	SOUTH = 1
	EAST = 2
	WEST = 3 

def grid_to_string(grid: GridState, is_hidden: bool = False) -> str:
	match grid:
		case GridState.UNKNOWN:
			return " . "
		case GridState.MISS:
			return " O "
		case GridState.HIT:
			return "[X]"
		case GridState.OCCUPIED:
			if(is_hidden):
				return " . "
			return "[ ]"
		case GridState.SUNK:
			return "{X}"

class Vector2:
	x: int = 0
	y: int = 0

	def __init__(self, x = 0, y = 0):
		if(isinstance(x, Direction)):
			self.fromdirection(x)
			return
		self.x = x
		self.y = y

	def fromdirection(self, direction: Direction):
		self.x = -1 if direction == Direction.WEST  else 1 if direction == Direction.EAST  else 0
		self.y = -1 if direction == Direction.SOUTH else 1 if direction == Direction.NORTH else 0
	
	def randomize(self, low: int, hi: int):
		"""Randomizes the contents of the Vector from low to hi (inclusive)"""
		self.x = random.randint(low, hi)
		self.y = random.randint(low, hi)
		return self
	
	def __add__(self, other):
		return Vector2(self.x + other.x, self.y + other.y)
	
	def __mul__(self, other):
		return Vector2(self.x * other, self.y * other)
	
	def __str__(self) -> str:
		return "(" + str(self.x) + ", " + str(self.y) + ")"
	
	def __eq__(self, other) -> bool:
		return self.x == other.x and self.y == other.y

class Ship:
	head: Vector2
	direction: Direction
	len: int
	is_sunk: bool
	health: int

	def __init__(self, head: Vector2, direction: Direction, len: int):
		self.head = head
		self.direction = direction
		self.len = len
		self.is_sunk = False
		self.health = len

	def is_overlapping(self, pos: Vector2) -> bool:
		for i in range(self.len):
			if((self.head + Vector2(self.direction) * i) == pos):
				return True
		return False

	
	def hit(self):
		self.health -= 1
		# print("hit ship, " + str(self.health) + "/" + str(self.len) + " hp left")
		if(self.health == 0):
			# print("you sunk my " + str(self.len) + " length ship!")
			self.is_sunk = True
	
	def get_grids(self) -> list:
		_l: list = []
		for i in range(self.len):
			_l.append(self.head + Vector2(self.direction) * i)
		return _l
	
	def __str__(self) -> str:
		return str(self.len) + " ship @ " + str(self.head) + " facing " + str(self.direction) + " with " + str(self.health) + ". sunk? " + str(self.is_sunk)

class Board:
	grids: list = []
	ships: list = []
	size: int = 0
	is_hidden: bool = False

	def __init__(self, size: int):
		self.grids = []
		self.ships = []
		self.size = size
		self.generate_grid()
	
	def generate_grid(self):
		self.grids = []
		self.ships = []
		for _ in range(self.size):
			_col = []
			for _ in range(self.size):
				_col.append(GridState.UNKNOWN)
			self.grids.append(_col)

	def toggle_visibility(self):
		self.set_is_hidden(not self.is_hidden)
	
	def set_is_hidden(self, is_hidden: bool):
		self.is_hidden = is_hidden
	
	def get_grid(self, pos: Vector2) -> GridState:
		if(pos.y < 0 or pos.x < 0 or pos.y >= len(self.grids) or pos.x >= len(self.grids[0])):
			return None
		return self.grids[pos.y][pos.x]
	
	def set_grid(self, pos: Vector2, state: GridState) -> bool:
		if(self.get_grid(pos) is None):
			return False
		self.grids[pos.y][pos.x] = state
		return True

	def hit_grid(self, pos: Vector2) -> bool:
		if(self.get_grid(pos) == GridState.UNKNOWN):
			self.set_grid(pos, GridState.MISS)
			return
		if(self.get_grid(pos) != GridState.OCCUPIED):
			print("[err] you messed up")
			return
		self.set_grid(pos, GridState.HIT)
		ship: Ship
		for ship in self.ships:
			if(ship.is_overlapping(pos)):
				ship.hit()
				break
		if(ship.is_sunk):
			for grid in ship.get_grids():
				self.set_grid(grid, GridState.SUNK)
	
	# TODO print prettier when len > 10
	def __str__(self) -> str:
		_o = "   "
		for i in range(len(self.grids)):
			_o += " " + str(i) + " "
		_o += "\n"
		for i in range(len(self.grids)):
			_o += str(i) + ") "
			for grid in self.grids[i]:
				_o += grid_to_string(grid, self.is_hidden)
			_o += "\n"
		return _o.strip("\n")
	
	def place_ship(self, len: int, position: Vector2, direction: Direction) -> bool:
		for i in range(len):
			if(self.get_grid(position + Vector2(direction) * i) != GridState.UNKNOWN):
				return False
		for i in range(len):
			if(self.get_grid(position + Vector2(direction) * i) == GridState.UNKNOWN):
				self.set_grid(position + Vector2(direction) * i, GridState.OCCUPIED)
		# print("appending ship length " + str(len))
		self.ships.append(Ship(position, direction, len))
		return True
	
	def place_ship_random(self, len: int):
		while(not self.place_ship(len, Vector2().randomize(0, self.size), Direction(random.randint(0, 3)))):
			pass


# board.set_is_hidden(True)
start: float = time.perf_counter()
for i in range(1):
	board = Board(10)
	board.place_ship_random(2)
	board.place_ship_random(3)
	board.place_ship_random(3)
	board.place_ship_random(4)
	board.place_ship_random(5)
	for y in range(10):
		for x in range(10):
			board.hit_grid(Vector2(x, y))

end = time.perf_counter()
print(board)
print("took " + str((end - start)*1000) + " miliseconds")
# print(str(board))
# while(True):
# 	x = int(input("enter x: "))
# 	y = int(input("enter y: "))
# 	board.hit_grid(Vector2(x, y))
# 	for ship in board.ships:
# 		print(ship)
# 	print(str(board))
