class_name GridLogic
extends RefCounted

## Pure logic class for Sokoban grid mechanics in Pixel Porter (Godot 4).
## Implements the core gameplay rules from PRD Sections 4 and 5:
## - 4-directional turn-based movement (Up, Down, Left, Right), one tile per move.
## - Pushes crates one tile if the tile behind is empty floor or a goal.
## - Two crates cannot be pushed at once; crates cannot be pulled.
## - Walls and boundaries block movement.
## - Level is won when every crate sits on a goal tile.
## - Supports restart/reset and tracks move/push counts.

signal player_moved(from_pos: Vector2i, to_pos: Vector2i)
signal crate_pushed(from_pos: Vector2i, to_pos: Vector2i)
signal move_undone(player_pos: Vector2i, had_crate: bool, crate_from: Vector2i, crate_to: Vector2i)
signal level_won
signal level_reset

# Standard Sokoban characters:
# '#' = Wall
# ' ' = Floor / empty
# '.' = Goal
# '$' = Crate
# '*' = Crate on Goal
# '@' = Player
# '+' = Player on Goal

var width: int = 0
var height: int = 0

var player_pos: Vector2i = Vector2i.ZERO
var walls: Dictionary = {}   # Dictionary[Vector2i, bool]
var goals: Dictionary = {}   # Dictionary[Vector2i, bool]
var crates: Dictionary = {}  # Dictionary[Vector2i, bool]

var moves_count: int = 0
var pushes_count: int = 0
var last_move_pushed_crate: bool = false
var history: Array[Dictionary] = []

# Snapshot of the initial state for level restart
var _initial_player_pos: Vector2i = Vector2i.ZERO
var _initial_crates: Dictionary = {}
var _raw_level_text: String = ""


func _init(level_text: String = "") -> void:
	if not level_text.is_empty():
		load_from_text(level_text)


## Clears all existing board state.
func clear() -> void:
	width = 0
	height = 0
	player_pos = Vector2i.ZERO
	walls.clear()
	goals.clear()
	crates.clear()
	moves_count = 0
	pushes_count = 0
	last_move_pushed_crate = false
	history.clear()
	_initial_player_pos = Vector2i.ZERO
	_initial_crates.clear()
	_raw_level_text = ""


## Loads a level from standard Sokoban text format.
## Returns true on success, false if the level is invalid (e.g. no player or empty).
func load_from_text(level_text: String) -> bool:
	clear()
	_raw_level_text = level_text

	var normalized_text: String = level_text.replace("\r\n", "\n").replace("\r", "\n")
	var raw_lines: PackedStringArray = normalized_text.split("\n")

	# Collect map lines, skipping comment lines that start with ';'
	var map_lines: Array[String] = []
	for line in raw_lines:
		if line.begins_with(";"):
			continue
		map_lines.append(line)

	# Trim leading and trailing completely empty lines
	while not map_lines.is_empty() and map_lines[0].strip_edges().is_empty():
		map_lines.pop_front()
	while not map_lines.is_empty() and map_lines[map_lines.size() - 1].strip_edges().is_empty():
		map_lines.pop_back()

	if map_lines.is_empty():
		push_warning("GridLogic: Level text contains no map data.")
		return false

	height = map_lines.size()
	width = 0
	for line in map_lines:
		if line.length() > width:
			width = line.length()

	var found_player: bool = false

	for y in range(height):
		var line: String = map_lines[y]
		for x in range(line.length()):
			var char_code: String = line[x]
			var pos: Vector2i = Vector2i(x, y)

			match char_code:
				"#":
					walls[pos] = true
				".":
					goals[pos] = true
				"$":
					crates[pos] = true
				"*":
					crates[pos] = true
					goals[pos] = true
				"@":
					player_pos = pos
					found_player = true
				"+":
					player_pos = pos
					goals[pos] = true
					found_player = true
				" ", "-", "_":
					# Floor / empty space
					pass
				_:
					# Any unrecognized characters are treated as empty space
					pass

	if not found_player:
		push_warning("GridLogic: Level has no player starting position ('@' or '+').")
		return false

	_initial_player_pos = player_pos
	_initial_crates = crates.duplicate()
	moves_count = 0
	pushes_count = 0
	last_move_pushed_crate = false

	return true


## Loads a level from a file containing standard Sokoban text.
func load_from_file(file_path: String) -> bool:
	if not FileAccess.file_exists(file_path):
		push_error("GridLogic: File does not exist: %s" % file_path)
		return false

	var file: FileAccess = FileAccess.open(file_path, FileAccess.READ)
	if not file:
		push_error("GridLogic: Failed to open file: %s" % file_path)
		return false

	var text: String = file.get_as_text()
	return load_from_text(text)


## Converts a direction variant into a normalized cardinal Vector2i.
## Supports Vector2i, Vector2, and direction strings ("up", "down", "left", "right", "u", "d", "l", "r", "w", "s", "a", "d").
static func parse_direction(direction: Variant) -> Vector2i:
	if direction is Vector2i:
		return direction
	elif direction is Vector2:
		return Vector2i(int(round(direction.x)), int(round(direction.y)))
	elif direction is String:
		var s: String = direction.strip_edges().to_lower()
		match s:
			"up", "u", "w":
				return Vector2i.UP
			"down", "d", "s":
				return Vector2i.DOWN
			"left", "l", "a":
				return Vector2i.LEFT
			"right", "r":
				return Vector2i.RIGHT
	return Vector2i.ZERO


## Attempts to move the player in the specified direction.
## Follows PRD rules:
## - 1 tile move per turn.
## - Moving into wall or out of bounds is blocked.
## - Moving into a crate pushes it if the tile behind is empty floor or goal.
## - Cannot push two crates at once. Crates cannot be pulled.
## Returns true if the move was successfully made, false if blocked.
func move(direction: Variant) -> bool:
	last_move_pushed_crate = false
	var dir: Vector2i = parse_direction(direction)

	if dir != Vector2i.UP and dir != Vector2i.DOWN and dir != Vector2i.LEFT and dir != Vector2i.RIGHT:
		return false

	var target_pos: Vector2i = player_pos + dir

	# Bounds and wall check for player destination
	if not is_in_bounds(target_pos) or is_wall(target_pos):
		return false

	var pushed: bool = false
	var c_from: Vector2i = Vector2i.ZERO
	var c_to: Vector2i = Vector2i.ZERO

	# Check if target tile has a crate
	if has_crate(target_pos):
		var behind_pos: Vector2i = target_pos + dir

		# Bounds and wall check for crate destination
		if not is_in_bounds(behind_pos) or is_wall(behind_pos):
			return false

		# Rule: Two crates cannot be pushed at once
		if has_crate(behind_pos):
			return false

		# Push the crate
		crates.erase(target_pos)
		crates[behind_pos] = true
		pushes_count += 1
		last_move_pushed_crate = true
		pushed = true
		c_from = target_pos
		c_to = behind_pos
		crate_pushed.emit(target_pos, behind_pos)

	# Move the player
	var old_pos: Vector2i = player_pos
	player_pos = target_pos
	moves_count += 1

	history.append({
		"player_from": old_pos,
		"player_to": target_pos,
		"pushed_crate": pushed,
		"crate_from": c_from,
		"crate_to": c_to,
		"dir": dir
	})

	player_moved.emit(old_pos, target_pos)

	if is_won():
		level_won.emit()

	return true


## Returns true if there is at least one move in history to undo.
func can_undo() -> bool:
	return not history.is_empty()


## Undoes the last move, reverting player and crate positions, and updating counters.
## Returns true if a move was undone, false if history is empty.
func undo() -> bool:
	if history.is_empty():
		return false

	var entry: Dictionary = history.pop_back()
	var prev_player_pos: Vector2i = entry["player_from"]
	var had_crate: bool = entry["pushed_crate"]
	var c_from: Vector2i = entry.get("crate_from", Vector2i.ZERO)
	var c_to: Vector2i = entry.get("crate_to", Vector2i.ZERO)

	if had_crate:
		crates.erase(c_to)
		crates[c_from] = true
		pushes_count = max(0, pushes_count - 1)

	player_pos = prev_player_pos
	moves_count = max(0, moves_count - 1)
	last_move_pushed_crate = false

	move_undone.emit(player_pos, had_crate, c_from, c_to)
	return true


## Restarts the level back to its initial loaded state.
## Resets player position, crates, moves_count, and pushes_count.
func restart() -> void:
	player_pos = _initial_player_pos
	crates = _initial_crates.duplicate()
	moves_count = 0
	pushes_count = 0
	last_move_pushed_crate = false
	history.clear()
	level_reset.emit()


## Alias for restart().
func reset() -> void:
	restart()


## Reports whether the level is won according to PRD Section 4:
## "A level is complete when every crate sits on a goal tile."
func is_won() -> bool:
	if crates.is_empty():
		return false
	for crate_pos in crates.keys():
		if not is_goal(crate_pos):
			return false
	return true


## Returns true if the position is within the rectangular grid bounds.
func is_in_bounds(pos: Vector2i) -> bool:
	return pos.x >= 0 and pos.x < width and pos.y >= 0 and pos.y < height


## Returns true if the position is a wall tile.
func is_wall(pos: Vector2i) -> bool:
	return walls.has(pos)


## Returns true if the position is a goal tile.
func is_goal(pos: Vector2i) -> bool:
	return goals.has(pos)


## Returns true if a crate currently occupies this position.
func has_crate(pos: Vector2i) -> bool:
	return crates.has(pos)


## Returns true if the position is inside bounds, not a wall, not occupied by a crate or player.
func is_empty_tile(pos: Vector2i) -> bool:
	return is_in_bounds(pos) and not is_wall(pos) and not has_crate(pos) and pos != player_pos


## Returns the player's current position.
func get_player_pos() -> Vector2i:
	return player_pos


## Returns an Array of all crate positions.
func get_crates() -> Array[Vector2i]:
	var list: Array[Vector2i] = []
	for pos in crates.keys():
		list.append(pos)
	return list


## Returns an Array of all goal positions.
func get_goals() -> Array[Vector2i]:
	var list: Array[Vector2i] = []
	for pos in goals.keys():
		list.append(pos)
	return list


## Returns an Array of all wall positions.
func get_walls() -> Array[Vector2i]:
	var list: Array[Vector2i] = []
	for pos in walls.keys():
		list.append(pos)
	return list


## Returns the total number of crates.
func get_crate_count() -> int:
	return crates.size()


## Returns the total number of goals.
func get_goal_count() -> int:
	return goals.size()


## Returns how many crates are currently resting on goal tiles.
func get_crates_on_goal_count() -> int:
	var count: int = 0
	for crate_pos in crates.keys():
		if is_goal(crate_pos):
			count += 1
	return count


## Executes a sequence of moves (either a String like "uurrddll" or Array of directions).
## Standard notation: 'u'=UP, 'd'=DOWN, 'l'=LEFT, 'r'=RIGHT (case-insensitive).
## Returns the number of successful moves executed.
func execute_moves(move_sequence: Variant) -> int:
	var success_count: int = 0
	if move_sequence is String:
		for i in range(move_sequence.length()):
			var char_move: String = move_sequence[i]
			var dir: Vector2i = Vector2i.ZERO
			match char_move.to_lower():
				"u": dir = Vector2i.UP
				"d": dir = Vector2i.DOWN
				"l": dir = Vector2i.LEFT
				"r": dir = Vector2i.RIGHT
				_: continue
			if move(dir):
				success_count += 1
	elif move_sequence is Array:
		for dir_item in move_sequence:
			if move(dir_item):
				success_count += 1
	return success_count


## Exports the current board state back to standard Sokoban ASCII format.
func to_text() -> String:
	var result_lines: PackedStringArray = []
	for y in range(height):
		var row_chars: PackedStringArray = []
		for x in range(width):
			var pos: Vector2i = Vector2i(x, y)
			var has_w: bool = walls.has(pos)
			var has_g: bool = goals.has(pos)
			var has_c: bool = crates.has(pos)
			var is_p: bool = (pos == player_pos)

			if has_w:
				row_chars.append("#")
			elif is_p and has_g:
				row_chars.append("+")
			elif is_p:
				row_chars.append("@")
			elif has_c and has_g:
				row_chars.append("*")
			elif has_c:
				row_chars.append("$")
			elif has_g:
				row_chars.append(".")
			else:
				row_chars.append(" ")
		result_lines.append("".join(row_chars).rstrip(" "))
	return "\n".join(result_lines)


## Creates an independent clone of the current GridLogic instance.
func clone() -> RefCounted:
	var copy = (get_script() as GDScript).new()
	copy.width = width
	copy.height = height
	copy.player_pos = player_pos
	copy.walls = walls.duplicate()
	copy.goals = goals.duplicate()
	copy.crates = crates.duplicate()
	copy.moves_count = moves_count
	copy.pushes_count = pushes_count
	copy.last_move_pushed_crate = last_move_pushed_crate
	copy._initial_player_pos = _initial_player_pos
	copy._initial_crates = _initial_crates.duplicate()
	copy._raw_level_text = _raw_level_text
	return copy
