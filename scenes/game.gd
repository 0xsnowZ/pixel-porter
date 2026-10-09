extends Control

## Main playable game scene for Pixel Porter.
## Renders the grid, handles swipes and keyboard input, animates moves,
## and implements PRD Section 4 & 5 gameplay and UI requirements.

const GridLogic = preload("res://scripts/grid_logic.gd")

# Levels available
var level_paths: Array[String] = [
	"res://levels/level_01.sok",
	"res://levels/level_02.sok",
	"res://levels/level_03.sok"
]
var current_level_index: int = 0

var grid: GridLogic

# Visual settings
var tile_size: float = 64.0
var grid_origin: Vector2 = Vector2.ZERO

# Animation state
var is_animating: bool = false
var queued_move_dir: Vector2i = Vector2i.ZERO # PRD Section 5: "A swipe made during a move animation is queued (one move only)"
var visual_player_pos: Vector2 = Vector2.ZERO
var visual_crates: Dictionary = {} # Vector2i (current logical) -> Vector2 (interpolated visual)

# Touch / Swipe handling (PRD Section 5)
var touch_start_pos: Vector2 = Vector2.ZERO
var is_touching: bool = false
const SWIPE_THRESHOLD_PIXELS: float = 30.0

# UI references
@onready var level_label: Label = $TopBar/Margin/HBox/LevelLabel
@onready var stats_label: Label = $TopBar/Margin/HBox/StatsLabel
@onready var restart_button: Button = $BottomBar/Margin/HBox/RestartButton
@onready var prev_button: Button = $BottomBar/Margin/HBox/PrevButton
@onready var next_button: Button = $BottomBar/Margin/HBox/NextButton
@onready var win_modal: PanelContainer = $WinModal
@onready var win_title: Label = $WinModal/VBox/WinTitle
@onready var win_stats: Label = $WinModal/VBox/WinStats
@onready var next_level_button: Button = $WinModal/VBox/NextLevelBtn
@onready var restart_dialog: ConfirmationDialog = $RestartConfirmDialog


func _ready() -> void:
	grid = GridLogic.new()
	grid.crate_pushed.connect(_on_crate_pushed)
	grid.player_moved.connect(_on_player_moved)
	grid.level_won.connect(_on_level_won)
	grid.level_reset.connect(_on_level_reset)

	restart_button.pressed.connect(_on_restart_pressed)
	prev_button.pressed.connect(_on_prev_level_pressed)
	next_button.pressed.connect(_on_next_level_pressed)
	next_level_button.pressed.connect(_on_next_level_pressed)
	restart_dialog.confirmed.connect(_do_restart)

	load_level(0)
	get_viewport().size_changed.connect(queue_redraw)


func load_level(index: int) -> void:
	current_level_index = clampi(index, 0, level_paths.size() - 1)
	var path: String = level_paths[current_level_index]
	var ok: bool = grid.load_from_file(path)
	if not ok:
		push_error("Failed to load level: %s" % path)
		return

	is_animating = false
	queued_move_dir = Vector2i.ZERO
	win_modal.hide()

	# Sync visual positions
	visual_player_pos = Vector2(grid.get_player_pos())
	visual_crates.clear()
	for crate_pos in grid.crates.keys():
		visual_crates[crate_pos] = Vector2(crate_pos)

	_update_ui()
	queue_redraw()


func _update_ui() -> void:
	level_label.text = "LEVEL %d / %d" % [current_level_index + 1, level_paths.size()]
	stats_label.text = "MOVES: %d  |  PUSHES: %d" % [grid.moves_count, grid.pushes_count]
	prev_button.disabled = (current_level_index == 0)
	next_button.disabled = (current_level_index == level_paths.size() - 1)


func _on_player_moved(from_pos: Vector2i, to_pos: Vector2i) -> void:
	_update_ui()
	_animate_player(from_pos, to_pos)


func _on_crate_pushed(from_pos: Vector2i, to_pos: Vector2i) -> void:
	_animate_crate(from_pos, to_pos)


func _on_level_won() -> void:
	_update_ui()
	# Delay win popup slightly so player sees the crate snap to goal
	await get_tree().create_timer(0.2).timeout
	win_title.text = "LEVEL %d COMPLETED!" % [current_level_index + 1]
	win_stats.text = "Solved in %d moves (%d pushes)" % [grid.moves_count, grid.pushes_count]
	win_modal.show()


func _on_level_reset() -> void:
	visual_player_pos = Vector2(grid.get_player_pos())
	visual_crates.clear()
	for crate_pos in grid.crates.keys():
		visual_crates[crate_pos] = Vector2(crate_pos)
	_update_ui()
	queue_redraw()


func _animate_player(from_pos: Vector2i, to_pos: Vector2i) -> void:
	is_animating = true
	var tween: Tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	visual_player_pos = Vector2(from_pos)
	tween.tween_property(self, "visual_player_pos", Vector2(to_pos), 0.12)
	tween.tween_callback(func():
		is_animating = false
		visual_player_pos = Vector2(to_pos)
		queue_redraw()
		# Process queued move if one was buffered during animation (PRD Section 5)
		if queued_move_dir != Vector2i.ZERO:
			var dir_to_run: Vector2i = queued_move_dir
			queued_move_dir = Vector2i.ZERO
			try_move(dir_to_run)
	)


func _animate_crate(from_pos: Vector2i, to_pos: Vector2i) -> void:
	visual_crates.erase(from_pos)
	visual_crates[to_pos] = Vector2(from_pos)
	var tween: Tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tween.tween_method(func(val: Vector2):
		visual_crates[to_pos] = val
		queue_redraw()
	, Vector2(from_pos), Vector2(to_pos), 0.12)


func try_move(dir: Vector2i) -> void:
	if win_modal.visible:
		return

	if is_animating:
		# PRD Section 5: "A swipe made during a move animation is queued (one move only)."
		queued_move_dir = dir
		return

	grid.move(dir)


func _unhandled_input(event: InputEvent) -> void:
	if win_modal.visible:
		return

	# Keyboard navigation (Desktop / Testing)
	if event is InputEventKey and event.is_pressed() and not event.is_echo():
		match event.keycode:
			KEY_UP, KEY_W:
				try_move(Vector2i.UP)
			KEY_DOWN, KEY_S:
				try_move(Vector2i.DOWN)
			KEY_LEFT, KEY_A:
				try_move(Vector2i.LEFT)
			KEY_RIGHT, KEY_D:
				try_move(Vector2i.RIGHT)
			KEY_R:
				_on_restart_pressed()

	# Touch & Mouse swipe detection (PRD Section 5)
	if event is InputEventMouseButton:
		if event.button_index == MOUSE_BUTTON_LEFT:
			if event.pressed:
				is_touching = true
				touch_start_pos = event.position
			else:
				if is_touching:
					_handle_swipe(event.position - touch_start_pos)
					is_touching = false

	elif event is InputEventScreenTouch:
		if event.pressed:
			is_touching = true
			touch_start_pos = event.position
		else:
			if is_touching:
				_handle_swipe(event.position - touch_start_pos)
				is_touching = false


func _handle_swipe(delta: Vector2) -> void:
	if delta.length() < SWIPE_THRESHOLD_PIXELS:
		return # Ignore taps and tiny movements (PRD Section 5)

	# Dominant axis decides direction (PRD Section 5)
	if abs(delta.x) > abs(delta.y):
		if delta.x > 0:
			try_move(Vector2i.RIGHT)
		else:
			try_move(Vector2i.LEFT)
	else:
		if delta.y > 0:
			try_move(Vector2i.DOWN)
		else:
			try_move(Vector2i.UP)


func _on_restart_pressed() -> void:
	if win_modal.visible:
		return
	# PRD Section 5: "After 5 or more moves, Restart asks for one confirmation tap."
	if grid.moves_count >= 5:
		restart_dialog.dialog_text = "You've made %d moves. Restart this level?" % grid.moves_count
		restart_dialog.popup_centered()
	else:
		_do_restart()


func _do_restart() -> void:
	grid.restart()


func _on_prev_level_pressed() -> void:
	if current_level_index > 0:
		load_level(current_level_index - 1)


func _on_next_level_pressed() -> void:
	if current_level_index < level_paths.size() - 1:
		load_level(current_level_index + 1)


func _process(_delta: float) -> void:
	if is_animating:
		queue_redraw()


func _draw() -> void:
	if not grid or grid.width == 0 or grid.height == 0:
		return

	var viewport_size: Vector2 = size
	var playable_height: float = viewport_size.y - 140.0 # Leave room for top & bottom bars
	var max_tile_w: float = (viewport_size.x - 32.0) / float(grid.width)
	var max_tile_h: float = playable_height / float(grid.height)
	tile_size = floor(min(max_tile_w, max_tile_h))

	var board_pixel_size: Vector2 = Vector2(grid.width * tile_size, grid.height * tile_size)
	grid_origin = Vector2(
		floor((viewport_size.x - board_pixel_size.x) / 2.0),
		floor(70.0 + (playable_height - board_pixel_size.y) / 2.0)
	)

	# 1. Draw floor and board borders
	for y in range(grid.height):
		for x in range(grid.width):
			var pos: Vector2i = Vector2i(x, y)
			var rect: Rect2 = Rect2(grid_origin + Vector2(x, y) * tile_size, Vector2(tile_size, tile_size))

			if grid.is_wall(pos):
				_draw_wall(rect)
			else:
				# Green retro floor (PRD Section 4: "brick walls, green floor")
				var is_alt: bool = ((x + y) % 2 == 0)
				var floor_col: Color = Color(0.24, 0.44, 0.28) if is_alt else Color(0.21, 0.40, 0.25)
				draw_rect(rect, floor_col)
				draw_rect(rect, Color(0.18, 0.35, 0.22), false, 1.0)

	# 2. Draw goals
	for goal_pos in grid.goals.keys():
		var center: Vector2 = grid_origin + Vector2(goal_pos) * tile_size + Vector2(tile_size / 2.0, tile_size / 2.0)
		var radius: float = tile_size * 0.22
		# Subtle target rings
		draw_circle(center, radius + 3.0, Color(0.9, 0.75, 0.2, 0.4))
		draw_circle(center, radius, Color(0.95, 0.8, 0.2, 0.9))
		draw_circle(center, radius * 0.4, Color(0.98, 0.95, 0.7, 1.0))

	# 3. Draw crates (using animated visual positions)
	for logical_pos in grid.crates.keys():
		var draw_tile_pos: Vector2 = visual_crates.get(logical_pos, Vector2(logical_pos))
		var rect: Rect2 = Rect2(grid_origin + draw_tile_pos * tile_size + Vector2(3, 3), Vector2(tile_size - 6, tile_size - 6))
		var is_on_goal: bool = grid.is_goal(logical_pos)
		_draw_crate(rect, is_on_goal)

	# 4. Draw player (using animated visual position)
	var player_rect: Rect2 = Rect2(grid_origin + visual_player_pos * tile_size + Vector2(4, 4), Vector2(tile_size - 8, tile_size - 8))
	_draw_player(player_rect)


func _draw_wall(rect: Rect2) -> void:
	# Retro brick wall
	draw_rect(rect, Color(0.48, 0.20, 0.18)) # Brick terracotta
	draw_rect(rect, Color(0.32, 0.12, 0.10), false, 2.0) # Mortar outline
	# Brick details
	var half_h: float = rect.size.y / 2.0
	draw_line(rect.position + Vector2(0, half_h), rect.position + Vector2(rect.size.x, half_h), Color(0.32, 0.12, 0.10), 1.5)
	draw_line(rect.position + Vector2(rect.size.x / 2.0, 0), rect.position + Vector2(rect.size.x / 2.0, half_h), Color(0.32, 0.12, 0.10), 1.5)


func _draw_crate(rect: Rect2, on_goal: bool) -> void:
	var bg_col: Color = Color(0.20, 0.65, 0.35) if on_goal else Color(0.78, 0.50, 0.22)
	var border_col: Color = Color(0.12, 0.45, 0.22) if on_goal else Color(0.50, 0.30, 0.10)
	var cross_col: Color = Color(0.15, 0.52, 0.26) if on_goal else Color(0.60, 0.38, 0.15)

	draw_rect(rect, bg_col)
	draw_rect(rect, border_col, false, 3.0)

	# Crate diagonal cross braces
	var inset: float = 4.0
	draw_line(rect.position + Vector2(inset, inset), rect.end - Vector2(inset, inset), cross_col, 2.5)
	draw_line(Vector2(rect.end.x - inset, rect.position.y + inset), Vector2(rect.position.x + inset, rect.end.y - inset), cross_col, 2.5)

	if on_goal:
		# Draw shiny star/dot badge in center
		var center: Vector2 = rect.get_center()
		draw_circle(center, 5.0, Color(1.0, 0.95, 0.5))


func _draw_player(rect: Rect2) -> void:
	var center: Vector2 = rect.get_center()
	var radius: float = rect.size.x / 2.0

	# Retro porter: body & head
	# Overalls / body
	draw_circle(center, radius * 0.9, Color(0.22, 0.45, 0.85))
	# Face / head
	draw_circle(center - Vector2(0, radius * 0.15), radius * 0.55, Color(0.98, 0.82, 0.65))
	# Porter Cap
	draw_circle(center - Vector2(0, radius * 0.35), radius * 0.45, Color(0.85, 0.25, 0.20))
	# Eyes
	draw_circle(center + Vector2(-radius * 0.2, -radius * 0.1), 2.0, Color(0.1, 0.1, 0.1))
	draw_circle(center + Vector2(radius * 0.2, -radius * 0.1), 2.0, Color(0.1, 0.1, 0.1))
