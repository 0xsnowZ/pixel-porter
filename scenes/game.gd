extends Control

## Main playable game scene for Pixel Porter.
## Renders the grid, handles swipes and keyboard input, animates moves,
## and implements PRD Section 4 & 5 gameplay and UI requirements.

const GridLogic = preload("res://scripts/grid_logic.gd")
const SaveManagerScript = preload("res://scripts/save_manager.gd")

# Levels available (50 verified solvable levels)
var level_paths: Array[String] = _get_default_level_paths()
var current_level_index: int = 0

static func _get_default_level_paths() -> Array[String]:
	var paths: Array[String] = []
	for i in range(1, 51):
		paths.append("res://levels/level_%02d.sok" % i)
	return paths

var grid: GridLogic
var save_mgr: Node = null
var audio_mgr: Node = null
var loc_mgr: Node = null

# Visual settings
var tile_size: float = 64.0
var grid_origin: Vector2 = Vector2.ZERO
var player_facing_dir: Vector2i = Vector2i.DOWN
var win_particles: Array[Dictionary] = []

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
@onready var menu_button: Button = $TopBar/Margin/HBox/MenuBtn
@onready var level_label: Label = $TopBar/Margin/HBox/LevelLabel
@onready var stats_label: Label = $TopBar/Margin/HBox/StatsLabel
@onready var restart_button: Button = $BottomBar/Margin/HBox/RestartButton
@onready var prev_button: Button = $BottomBar/Margin/HBox/PrevButton
@onready var next_button: Button = $BottomBar/Margin/HBox/NextButton
@onready var win_modal: PanelContainer = $WinModal
@onready var win_title: Label = $WinModal/VBox/WinTitle
@onready var win_stats: Label = $WinModal/VBox/WinStats
@onready var win_menu_button: Button = $WinModal/VBox/WinActions/WinMenuBtn
@onready var next_level_button: Button = $WinModal/VBox/WinActions/NextLevelBtn
@onready var restart_dialog: ConfirmationDialog = $RestartConfirmDialog


func _initialize_nodes() -> void:
	if menu_button == null and has_node("TopBar/Margin/HBox/MenuBtn"):
		menu_button = $TopBar/Margin/HBox/MenuBtn
		level_label = $TopBar/Margin/HBox/LevelLabel
		stats_label = $TopBar/Margin/HBox/StatsLabel
		restart_button = $BottomBar/Margin/HBox/RestartButton
		prev_button = $BottomBar/Margin/HBox/PrevButton
		next_button = $BottomBar/Margin/HBox/NextButton
		win_modal = $WinModal
		win_title = $WinModal/VBox/WinTitle
		win_stats = $WinModal/VBox/WinStats
		win_menu_button = $WinModal/VBox/WinActions/WinMenuBtn
		next_level_button = $WinModal/VBox/WinActions/NextLevelBtn
		restart_dialog = $RestartConfirmDialog


func _ready() -> void:
	_initialize_nodes()
	if save_mgr == null:
		if is_inside_tree() and get_tree().root.has_node("SaveManager"):
			save_mgr = get_tree().root.get_node("SaveManager")
		else:
			save_mgr = SaveManagerScript.new()
			add_child(save_mgr)

	if audio_mgr == null and is_inside_tree() and get_tree().root.has_node("AudioManager"):
		audio_mgr = get_tree().root.get_node("AudioManager")

	if loc_mgr == null and is_inside_tree() and get_tree().root.has_node("LocalizationManager"):
		loc_mgr = get_tree().root.get_node("LocalizationManager")

	grid = GridLogic.new()
	grid.crate_pushed.connect(_on_crate_pushed)
	grid.player_moved.connect(_on_player_moved)
	grid.level_won.connect(_on_level_won)
	grid.level_reset.connect(_on_level_reset)

	if not menu_button.pressed.is_connected(_on_menu_pressed):
		menu_button.pressed.connect(_on_menu_pressed)
	if not win_menu_button.pressed.is_connected(_on_menu_pressed):
		win_menu_button.pressed.connect(_on_menu_pressed)
	if not restart_button.pressed.is_connected(_on_restart_pressed):
		restart_button.pressed.connect(_on_restart_pressed)
	if not prev_button.pressed.is_connected(_on_prev_level_pressed):
		prev_button.pressed.connect(_on_prev_level_pressed)
	if not next_button.pressed.is_connected(_on_next_level_pressed):
		next_button.pressed.connect(_on_next_level_pressed)
	if not next_level_button.pressed.is_connected(_on_next_level_pressed):
		next_level_button.pressed.connect(_on_next_level_pressed)
	if not restart_dialog.confirmed.is_connected(_do_restart):
		restart_dialog.confirmed.connect(_do_restart)
	if loc_mgr:
		restart_dialog.ok_button_text = loc_mgr.tr_text("BTN_RESTART")
		restart_dialog.cancel_button_text = loc_mgr.tr_text("BTN_CLOSE")

	var initial_level: int = 0
	if save_mgr and save_mgr.last_played_level >= 0 and save_mgr.last_played_level < level_paths.size():
		initial_level = save_mgr.last_played_level
	load_level(initial_level)
	if get_viewport():
		get_viewport().size_changed.connect(queue_redraw)


func load_level(index: int) -> void:
	var target_index: int = clampi(index, 0, level_paths.size() - 1)
	if save_mgr and not save_mgr.is_level_unlocked(target_index):
		return

	current_level_index = target_index
	if save_mgr:
		save_mgr.last_played_level = current_level_index

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
	var best_str: String = ""
	if save_mgr and save_mgr.is_level_completed(current_level_index):
		var rec: Dictionary = save_mgr.get_level_record(current_level_index)
		var best_m: int = rec.get("best_moves", 0)
		best_str = " | %s" % (loc_mgr.tr_text("GAME_BEST", [best_m]) if loc_mgr else "BEST: %d" % best_m)

	if loc_mgr:
		level_label.text = loc_mgr.tr_text("GAME_LEVEL_LABEL", [current_level_index + 1, level_paths.size()])
		stats_label.text = "%s  |  %s%s" % [
			loc_mgr.tr_text("GAME_MOVES", [grid.moves_count]),
			loc_mgr.tr_text("GAME_PUSHES", [grid.pushes_count]),
			best_str
		]
		restart_button.text = loc_mgr.tr_text("BTN_RESTART")
		prev_button.text = loc_mgr.tr_text("BTN_PREV")
		next_button.text = loc_mgr.tr_text("BTN_NEXT")
		win_menu_button.text = loc_mgr.tr_text("WIN_MENU_BTN")
		next_level_button.text = loc_mgr.tr_text("WIN_NEXT_BTN")
	else:
		level_label.text = "LEVEL %d / %d" % [current_level_index + 1, level_paths.size()]
		stats_label.text = "MOVES: %d  |  PUSHES: %d%s" % [grid.moves_count, grid.pushes_count, best_str]

	prev_button.disabled = (current_level_index == 0)
	var can_advance: bool = (current_level_index < level_paths.size() - 1)
	if save_mgr:
		can_advance = can_advance and save_mgr.is_level_unlocked(current_level_index + 1)
	next_button.disabled = not can_advance


func _on_player_moved(from_pos: Vector2i, to_pos: Vector2i) -> void:
	_update_ui()
	_animate_player(from_pos, to_pos)
	if not grid.last_move_pushed_crate and audio_mgr:
		audio_mgr.play_move()


func _on_crate_pushed(from_pos: Vector2i, to_pos: Vector2i) -> void:
	_animate_crate(from_pos, to_pos)
	if audio_mgr:
		audio_mgr.play_push()


func _on_level_won() -> void:
	if audio_mgr:
		audio_mgr.play_win()
	if save_mgr:
		save_mgr.record_level_completion(current_level_index, grid.moves_count, grid.pushes_count)

	_spawn_celebration_particles()
	_update_ui()

	# Delay win popup slightly so player sees the celebration burst and crate snap to goal
	await get_tree().create_timer(0.35).timeout
	var rec: Dictionary = save_mgr.get_level_record(current_level_index) if save_mgr else {}
	var best_m: int = rec.get("best_moves", grid.moves_count)
	var best_p: int = rec.get("best_pushes", grid.pushes_count)

	if loc_mgr:
		win_title.text = loc_mgr.tr_text("WIN_TITLE", [current_level_index + 1])
		win_stats.text = loc_mgr.tr_text("WIN_STATS", [grid.moves_count, grid.pushes_count, best_m, best_p])
	else:
		win_title.text = "LEVEL %d COMPLETED!" % [current_level_index + 1]
		win_stats.text = "Solved in %d moves (%d pushes)\nBest: %d moves (%d pushes)" % [grid.moves_count, grid.pushes_count, best_m, best_p]
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
	player_facing_dir = dir
	if win_modal != null and win_modal.visible:
		return

	if is_animating:
		# PRD Section 5: "A swipe made during a move animation is queued (one move only)."
		queued_move_dir = dir
		return

	if grid != null:
		grid.move(dir)


func _unhandled_input(event: InputEvent) -> void:
	if win_modal != null and win_modal.visible:
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
	if win_modal != null and win_modal.visible:
		return
	# PRD Section 5: "After 5 or more moves, Restart asks for one confirmation tap."
	var current_moves: int = grid.moves_count if grid != null else 0
	if current_moves >= 5:
		if loc_mgr:
			restart_dialog.dialog_text = loc_mgr.tr_text("RESTART_CONFIRM", [current_moves])
		else:
			restart_dialog.dialog_text = "You've made %d moves. Restart this level?" % current_moves
		if restart_dialog.is_inside_tree():
			restart_dialog.popup_centered()
	else:
		_do_restart()


func _do_restart() -> void:
	if audio_mgr:
		audio_mgr.play_restart()
	if grid:
		grid.restart()


func _on_prev_level_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if current_level_index > 0:
		load_level(current_level_index - 1)


func _on_next_level_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if current_level_index < level_paths.size() - 1:
		var next_idx: int = current_level_index + 1
		if not save_mgr or save_mgr.is_level_unlocked(next_idx):
			load_level(next_idx)


func _on_menu_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _spawn_celebration_particles() -> void:
	win_particles.clear()
	var palette: Array[Color] = [
		Color(1.0, 0.84, 0.20), # Gold
		Color(0.20, 0.88, 0.40), # Emerald
		Color(0.95, 0.25, 0.30), # Ruby
		Color(0.30, 0.75, 1.00), # Sky / Diamond
		Color(1.0, 0.95, 0.85), # Warm Pearl
		Color(1.0, 0.58, 0.18)  # Amber
	]

	var spawn_points: Array[Vector2] = []
	if grid and not grid.goals.is_empty():
		for goal_pos in grid.goals.keys():
			var pt: Vector2 = grid_origin + Vector2(goal_pos) * tile_size + Vector2(tile_size / 2.0, tile_size / 2.0)
			spawn_points.append(pt)

	if spawn_points.is_empty():
		spawn_points.append(size / 2.0 if size != Vector2.ZERO else Vector2(360, 640))

	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.randomize()

	for i in range(48):
		var origin_pt: Vector2 = spawn_points[rng.randi() % spawn_points.size()]
		var angle: float = rng.randf_range(-PI * 0.92, -PI * 0.08)
		var speed: float = rng.randf_range(160.0, 440.0)
		var p_color: Color = palette[rng.randi() % palette.size()]
		var p_size: float = rng.randf_range(5.0, 10.0)
		var life: float = rng.randf_range(1.2, 2.0)

		win_particles.append({
			"pos": origin_pt + Vector2(rng.randf_range(-8, 8), rng.randf_range(-8, 8)),
			"vel": Vector2(cos(angle), sin(angle)) * speed,
			"color": p_color,
			"size": p_size,
			"life": life,
			"max_life": life,
			"rot": rng.randf_range(0.0, TAU),
			"vrot": rng.randf_range(-7.0, 7.0)
		})


func _process(delta: float) -> void:
	var needs_redraw: bool = is_animating

	# Subtle continuous breathing pulse for goals
	if grid and not grid.goals.is_empty():
		needs_redraw = true

	# Update celebration particles
	if not win_particles.is_empty():
		needs_redraw = true
		var i: int = win_particles.size() - 1
		while i >= 0:
			var p: Dictionary = win_particles[i]
			p["life"] -= delta
			if p["life"] <= 0.0:
				win_particles.remove_at(i)
			else:
				p["pos"] += p["vel"] * delta
				p["vel"].y += 340.0 * delta # Gravity
				p["vel"].x *= (1.0 - 0.4 * delta) # Air resistance
				p["rot"] += p["vrot"] * delta
			i -= 1

	if needs_redraw:
		queue_redraw()


func calculate_layout(custom_viewport_size: Vector2 = Vector2.ZERO) -> void:
	if not grid or grid.width == 0 or grid.height == 0:
		return

	var viewport_size: Vector2 = custom_viewport_size if custom_viewport_size != Vector2.ZERO else size
	if viewport_size.x <= 0.0 or viewport_size.y <= 0.0:
		viewport_size = Vector2(720.0, 1280.0)
	var playable_height: float = viewport_size.y - 140.0 # Space between top and bottom bars
	var max_tile_w: float = (viewport_size.x - 36.0) / float(grid.width)
	var max_tile_h: float = playable_height / float(grid.height)
	tile_size = floor(min(max_tile_w, max_tile_h))

	var board_pixel_size: Vector2 = Vector2(grid.width * tile_size, grid.height * tile_size)
	grid_origin = Vector2(
		floor((viewport_size.x - board_pixel_size.x) / 2.0),
		floor(70.0 + (playable_height - board_pixel_size.y) / 2.0)
	)


func _draw() -> void:
	if not grid or grid.width == 0 or grid.height == 0:
		return

	calculate_layout()
	var board_pixel_size: Vector2 = Vector2(grid.width * tile_size, grid.height * tile_size)

	# 1. Decorative Wood/Slate Board Framing with Corner Rivets (PRD Section 4)
	var frame_margin: float = 10.0
	var frame_rect: Rect2 = Rect2(
		grid_origin - Vector2(frame_margin, frame_margin),
		board_pixel_size + Vector2(frame_margin * 2.0, frame_margin * 2.0)
	)

	# Board drop shadow
	draw_rect(Rect2(frame_rect.position + Vector2(5, 5), frame_rect.size), Color(0.0, 0.0, 0.0, 0.45))
	# Outer border trim
	draw_rect(frame_rect, Color(0.18, 0.13, 0.10))
	# Brass bevel rim
	draw_rect(frame_rect, Color(0.70, 0.52, 0.20), false, 2.0)
	# Inner slate groove
	draw_rect(Rect2(grid_origin - Vector2(2, 2), board_pixel_size + Vector2(4, 4)), Color(0.32, 0.22, 0.14), false, 1.5)

	# 4 Corner brass bolts
	var corner_offsets: Array[Vector2] = [
		Vector2(frame_margin * 0.5, frame_margin * 0.5),
		Vector2(frame_rect.size.x - frame_margin * 0.5, frame_margin * 0.5),
		Vector2(frame_margin * 0.5, frame_rect.size.y - frame_margin * 0.5),
		Vector2(frame_rect.size.x - frame_margin * 0.5, frame_rect.size.y - frame_margin * 0.5)
	]
	for c_offset in corner_offsets:
		var bolt_center: Vector2 = frame_rect.position + c_offset
		draw_circle(bolt_center, 3.5, Color(0.20, 0.14, 0.08))
		draw_circle(bolt_center, 2.8, Color(0.85, 0.68, 0.25))
		draw_circle(bolt_center - Vector2(0.8, 0.8), 1.0, Color(1.0, 0.92, 0.55))

	# 2. Draw Floor & Walls (PRD Section 4: "brick walls, green floor")
	for y in range(grid.height):
		for x in range(grid.width):
			var pos: Vector2i = Vector2i(x, y)
			var rect: Rect2 = Rect2(grid_origin + Vector2(x, y) * tile_size, Vector2(tile_size, tile_size))

			if grid.is_wall(pos):
				_draw_wall(rect)
			else:
				var is_alt: bool = ((x + y) % 2 == 0)
				var floor_col: Color = Color(0.24, 0.44, 0.28) if is_alt else Color(0.21, 0.40, 0.25)
				draw_rect(rect, floor_col)
				draw_rect(rect, Color(0.17, 0.33, 0.20, 0.6), false, 1.0)

	# 3. Draw Goals with Pulsing Dynamic Golden Rings
	var time_sec: float = float(Time.get_ticks_msec()) / 1000.0
	var pulse: float = sin(time_sec * 3.5) * 0.10
	for goal_pos in grid.goals.keys():
		var center: Vector2 = grid_origin + Vector2(goal_pos) * tile_size + Vector2(tile_size / 2.0, tile_size / 2.0)
		var base_radius: float = tile_size * 0.22
		var dyn_radius: float = base_radius * (1.0 + pulse)

		# Pulsing aura
		draw_circle(center, dyn_radius + 4.0, Color(0.95, 0.80, 0.20, 0.25 + pulse * 0.1))
		# Outer gold ring
		draw_circle(center, dyn_radius, Color(0.95, 0.78, 0.18, 0.90))
		# Inner green floor hole
		draw_circle(center, dyn_radius * 0.65, Color(0.20, 0.40, 0.24))
		# Center golden star dot
		draw_circle(center, dyn_radius * 0.35, Color(1.0, 0.95, 0.50, 1.0))

	# 4. Draw Crates with Drop Shadow & 3D Bevels
	for logical_pos in grid.crates.keys():
		var draw_tile_pos: Vector2 = visual_crates.get(logical_pos, Vector2(logical_pos))
		var rect: Rect2 = Rect2(grid_origin + draw_tile_pos * tile_size + Vector2(3, 3), Vector2(tile_size - 6, tile_size - 6))
		var is_on_goal: bool = grid.is_goal(logical_pos)
		_draw_crate(rect, is_on_goal)

	# 5. Draw Directional Porter
	var player_rect: Rect2 = Rect2(grid_origin + visual_player_pos * tile_size + Vector2(4, 4), Vector2(tile_size - 8, tile_size - 8))
	_draw_player(player_rect)

	# 6. Draw Victory Particles
	for p in win_particles:
		var alpha: float = clampf(p["life"] / p["max_life"], 0.0, 1.0)
		var p_col: Color = p["color"]
		p_col.a = alpha
		var half_sz: float = p["size"] * 0.5
		var pts: PackedVector2Array = [
			p["pos"] + Vector2(-half_sz, -half_sz).rotated(p["rot"]),
			p["pos"] + Vector2(half_sz, -half_sz).rotated(p["rot"]),
			p["pos"] + Vector2(half_sz, half_sz).rotated(p["rot"]),
			p["pos"] + Vector2(-half_sz, half_sz).rotated(p["rot"])
		]
		draw_colored_polygon(pts, p_col)


func _draw_wall(rect: Rect2) -> void:
	# Base brick terracotta
	draw_rect(rect, Color(0.48, 0.20, 0.18))

	# 3D highlight top & left
	draw_line(rect.position, Vector2(rect.end.x, rect.position.y), Color(0.66, 0.30, 0.25), 2.0)
	draw_line(rect.position, Vector2(rect.position.x, rect.end.y), Color(0.66, 0.30, 0.25), 2.0)

	# 3D shadow bottom & right
	draw_line(Vector2(rect.position.x, rect.end.y), rect.end, Color(0.24, 0.08, 0.07), 2.0)
	draw_line(Vector2(rect.end.x, rect.position.y), rect.end, Color(0.24, 0.08, 0.07), 2.0)

	# Mortar joints
	var mortar_col: Color = Color(0.28, 0.10, 0.08)
	draw_rect(rect, mortar_col, false, 1.5)

	var half_h: float = rect.size.y / 2.0
	draw_line(rect.position + Vector2(0, half_h), rect.position + Vector2(rect.size.x, half_h), mortar_col, 1.5)
	draw_line(rect.position + Vector2(rect.size.x * 0.5, 0), rect.position + Vector2(rect.size.x * 0.5, half_h), mortar_col, 1.5)
	draw_line(rect.position + Vector2(rect.size.x * 0.25, half_h), rect.position + Vector2(rect.size.x * 0.25, rect.size.y), mortar_col, 1.5)
	draw_line(rect.position + Vector2(rect.size.x * 0.75, half_h), rect.position + Vector2(rect.size.x * 0.75, rect.size.y), mortar_col, 1.5)


func _draw_crate(rect: Rect2, on_goal: bool) -> void:
	# Crate soft drop shadow
	var shadow_rect: Rect2 = Rect2(rect.position + Vector2(3, 4), rect.size)
	draw_rect(shadow_rect, Color(0.0, 0.0, 0.0, 0.32))

	var bg_col: Color = Color(0.24, 0.70, 0.38) if on_goal else Color(0.80, 0.52, 0.22)
	var border_col: Color = Color(0.14, 0.48, 0.24) if on_goal else Color(0.52, 0.31, 0.10)
	var cross_col: Color = Color(0.18, 0.56, 0.28) if on_goal else Color(0.62, 0.39, 0.15)
	var highlight_col: Color = Color(0.40, 0.85, 0.52) if on_goal else Color(0.94, 0.72, 0.42)
	var shadow_edge_col: Color = Color(0.10, 0.36, 0.18) if on_goal else Color(0.38, 0.20, 0.06)

	draw_rect(rect, bg_col)

	# 3D Bevel highlight top & left
	draw_line(rect.position, Vector2(rect.end.x, rect.position.y), highlight_col, 2.5)
	draw_line(rect.position, Vector2(rect.position.x, rect.end.y), highlight_col, 2.5)

	# 3D Bevel shadow bottom & right
	draw_line(Vector2(rect.position.x, rect.end.y), rect.end, shadow_edge_col, 2.5)
	draw_line(Vector2(rect.end.x, rect.position.y), rect.end, shadow_edge_col, 2.5)

	draw_rect(rect, border_col, false, 2.0)

	# Diagonal cross braces
	var inset: float = 5.0
	draw_line(rect.position + Vector2(inset, inset), rect.end - Vector2(inset, inset), cross_col, 2.8)
	draw_line(Vector2(rect.end.x - inset, rect.position.y + inset), Vector2(rect.position.x + inset, rect.end.y - inset), cross_col, 2.8)

	# Corner rivets
	var rivet_color: Color = Color(0.95, 0.85, 0.4) if on_goal else Color(0.35, 0.22, 0.10)
	var r_radius: float = 1.8
	draw_circle(rect.position + Vector2(inset, inset), r_radius, rivet_color)
	draw_circle(Vector2(rect.end.x - inset, rect.position.y + inset), r_radius, rivet_color)
	draw_circle(Vector2(rect.position.x + inset, rect.end.y - inset), r_radius, rivet_color)
	draw_circle(rect.end - Vector2(inset, inset), r_radius, rivet_color)

	if on_goal:
		# Shiny star center badge
		var center: Vector2 = rect.get_center()
		draw_circle(center, 6.0, Color(1.0, 0.95, 0.4))
		draw_circle(center, 3.0, Color(1.0, 1.0, 0.85))


func _draw_player(rect: Rect2) -> void:
	var center: Vector2 = rect.get_center()
	var radius: float = rect.size.x / 2.0

	# Porter drop shadow
	draw_circle(center + Vector2(0, radius * 0.35), radius * 0.75, Color(0.0, 0.0, 0.0, 0.35))

	# Overalls / body
	draw_circle(center + Vector2(0, radius * 0.15), radius * 0.75, Color(0.20, 0.44, 0.82))
	draw_line(center + Vector2(-radius * 0.35, -radius * 0.1), center + Vector2(-radius * 0.35, radius * 0.4), Color(0.14, 0.32, 0.65), 2.0)
	draw_line(center + Vector2(radius * 0.35, -radius * 0.1), center + Vector2(radius * 0.35, radius * 0.4), Color(0.14, 0.32, 0.65), 2.0)

	# Face / head
	var face_offset: Vector2 = Vector2(player_facing_dir) * (radius * 0.12)
	var head_center: Vector2 = center - Vector2(0, radius * 0.18) + face_offset
	draw_circle(head_center, radius * 0.52, Color(0.98, 0.82, 0.65))

	# Red Porter Cap
	var cap_center: Vector2 = head_center - Vector2(0, radius * 0.22)
	draw_circle(cap_center, radius * 0.42, Color(0.85, 0.22, 0.18))

	# Cap visor pointing towards player_facing_dir
	var visor_dir: Vector2 = Vector2(player_facing_dir)
	if visor_dir == Vector2.ZERO or visor_dir == Vector2.DOWN:
		draw_rect(Rect2(cap_center + Vector2(-radius * 0.35, radius * 0.12), Vector2(radius * 0.7, radius * 0.18)), Color(0.65, 0.15, 0.12))
	elif visor_dir == Vector2.UP:
		draw_rect(Rect2(cap_center + Vector2(-radius * 0.3, -radius * 0.32), Vector2(radius * 0.6, radius * 0.16)), Color(0.65, 0.15, 0.12))
	elif visor_dir == Vector2.LEFT:
		draw_rect(Rect2(cap_center + Vector2(-radius * 0.52, -radius * 0.05), Vector2(radius * 0.35, radius * 0.2)), Color(0.65, 0.15, 0.12))
	elif visor_dir == Vector2.RIGHT:
		draw_rect(Rect2(cap_center + Vector2(radius * 0.18, -radius * 0.05), Vector2(radius * 0.35, radius * 0.2)), Color(0.65, 0.15, 0.12))

	# Eyes (pointing towards player_facing_dir)
	if player_facing_dir != Vector2i.UP:
		var eye_offset: Vector2 = Vector2(player_facing_dir) * 2.5
		var eye_y: float = head_center.y - 1.0 + eye_offset.y
		var eye_x1: float = head_center.x - radius * 0.18 + eye_offset.x
		var eye_x2: float = head_center.x + radius * 0.18 + eye_offset.x
		draw_circle(Vector2(eye_x1, eye_y), 2.0, Color(0.1, 0.1, 0.1))
		draw_circle(Vector2(eye_x2, eye_y), 2.0, Color(0.1, 0.1, 0.1))
		draw_circle(Vector2(eye_x1 - 0.5, eye_y - 0.5), 0.8, Color(1.0, 1.0, 1.0))
		draw_circle(Vector2(eye_x2 - 0.5, eye_y - 0.5), 0.8, Color(1.0, 1.0, 1.0))

