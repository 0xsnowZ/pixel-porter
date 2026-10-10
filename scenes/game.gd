extends Control

## Main playable game scene for Pixel Porter.
## Renders the grid, handles swipes and keyboard input, animates moves,
## and implements PRD Section 4 & 5 gameplay and UI requirements.

const SaveManagerScript = preload("res://scripts/save_manager.gd")
const SokobanSolverScript = preload("res://scripts/sokoban_solver.gd")

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
var ad_mgr: Node = null
var haptic_mgr: Node = null
var safe_area_mgr: Node = null

# Visual settings
var tile_size: float = 64.0
var grid_origin: Vector2 = Vector2.ZERO
var player_facing_dir: Vector2i = Vector2i.DOWN
var win_particles: Array[Dictionary] = []

# Juice & Micro-interaction state
var board_trauma: float = 0.0
var board_shake_offset: Vector2 = Vector2.ZERO
var crate_squash: Dictionary = {} # Vector2i -> Vector2 scale
var dust_particles: Array[Dictionary] = []
var goal_effects: Array[Dictionary] = []
var _last_hud_moves: int = 0

# Animation state
var is_animating: bool = false
var queued_move_dir: Vector2i = Vector2i.ZERO # PRD Section 5: "A swipe made during a move animation is queued (one move only)"
var visual_player_pos: Vector2 = Vector2.ZERO
var visual_crates: Dictionary = {} # Vector2i (current logical) -> Vector2 (interpolated visual)
var walk_step_count: int = 0
var current_walk_frame: int = 0 # 0: idle stance, 1: walk frame 1, 2: walk frame 2

# Hint state (P3: Hint via Solver)
var active_hint_dir: Vector2i = Vector2i.ZERO
var hint_player_target: Vector2i = Vector2i.ZERO
var hint_crate_target: Vector2i = Vector2i.ZERO
var hint_has_crate: bool = false
var hint_time_remaining: float = 0.0
var hint_pulse_timer: float = 0.0

# Touch / Swipe handling (PRD Section 5)
var touch_start_pos: Vector2 = Vector2.ZERO
var is_touching: bool = false
const SWIPE_THRESHOLD_PIXELS: float = 30.0

# UI references
@onready var top_bar_margin: MarginContainer = $TopBar/Margin
@onready var bottom_bar_margin: MarginContainer = $BottomBar/Margin
@onready var menu_button: Button = $TopBar/Margin/HBox/MenuBtn
@onready var music_button: Button = find_child("MusicBtn", true, false) as Button
@onready var control_button: Button = find_child("ControlBtn", true, false) as Button
@onready var dpad_overlay: Control = find_child("DPadOverlay", true, false) as Control
@onready var dpad_up: Button = find_child("DPadUp", true, false) as Button
@onready var dpad_down: Button = find_child("DPadDown", true, false) as Button
@onready var dpad_left: Button = find_child("DPadLeft", true, false) as Button
@onready var dpad_right: Button = find_child("DPadRight", true, false) as Button
@onready var level_label: Label = $TopBar/Margin/HBox/LevelLabel
@onready var stats_label: Label = $TopBar/Margin/HBox/StatsLabel
@onready var prev_button: Button = $BottomBar/Margin/HBox/PrevButton
@onready var undo_button: Button = $BottomBar/Margin/HBox/UndoButton if has_node("BottomBar/Margin/HBox/UndoButton") else null
@onready var hint_button: Button = $BottomBar/Margin/HBox/HintButton if has_node("BottomBar/Margin/HBox/HintButton") else null
@onready var hint_toast: PanelContainer = $HintToast if has_node("HintToast") else null
@onready var hint_toast_label: Label = $HintToast/Margin/Label if has_node("HintToast/Margin/Label") else ($HintToast/Label if has_node("HintToast/Label") else null)
@onready var restart_button: Button = $BottomBar/Margin/HBox/RestartButton
@onready var next_button: Button = $BottomBar/Margin/HBox/NextButton
@onready var win_modal: PanelContainer = $WinModal
@onready var win_blur_overlay: ColorRect = $WinBlurOverlay if has_node("WinBlurOverlay") else null
@onready var win_title: Label = $WinModal.find_child("WinTitle", true, false) if has_node("WinModal") else null
@onready var win_stats: Label = $WinModal.find_child("WinStats", true, false) if has_node("WinModal") else null
@onready var win_menu_button: Button = $WinModal.find_child("WinMenuBtn", true, false) if has_node("WinModal") else null
@onready var next_level_button: Button = $WinModal.find_child("NextLevelBtn", true, false) if has_node("WinModal") else null
@onready var win_retry_button: Button = $WinModal.find_child("WinRetryBtn", true, false) if has_node("WinModal") else null
@onready var level_placard_label: Label = $WinModal.find_child("LevelPlacardLabel", true, false) if has_node("WinModal") else null
@onready var star_1: Label = $WinModal.find_child("Star1", true, false) if has_node("WinModal") else null
@onready var star_2: Label = $WinModal.find_child("Star2", true, false) if has_node("WinModal") else null
@onready var star_3: Label = $WinModal.find_child("Star3", true, false) if has_node("WinModal") else null
@onready var restart_dialog: ConfirmationDialog = $RestartConfirmDialog

var level_start_time: int = 0

# Board sprite textures
var tex_wall: Texture2D = preload("res://assets/wall_brick.png")
var tex_floor_1: Texture2D = preload("res://assets/floor_tile_1.png")
var tex_floor_2: Texture2D = preload("res://assets/floor_tile_2.png")
var tex_goal: Texture2D = preload("res://assets/goal_pad.png")
var tex_crate: Texture2D = preload("res://assets/crate_normal.png")
var tex_crate_goal: Texture2D = preload("res://assets/crate_goal.png")
var tex_player_down: Texture2D = preload("res://assets/player_down.png")
var tex_player_down_w1: Texture2D = preload("res://assets/player_down_walk1.png")
var tex_player_down_w2: Texture2D = preload("res://assets/player_down_walk2.png")
var tex_player_up: Texture2D = preload("res://assets/player_up.png")
var tex_player_up_w1: Texture2D = preload("res://assets/player_up_walk1.png")
var tex_player_up_w2: Texture2D = preload("res://assets/player_up_walk2.png")
var tex_player_left: Texture2D = preload("res://assets/player_left.png")
var tex_player_left_w1: Texture2D = preload("res://assets/player_left_walk1.png")
var tex_player_left_w2: Texture2D = preload("res://assets/player_left_walk2.png")
var tex_player_right: Texture2D = preload("res://assets/player_right.png")
var tex_player_right_w1: Texture2D = preload("res://assets/player_right_walk1.png")
var tex_player_right_w2: Texture2D = preload("res://assets/player_right_walk2.png")


func _initialize_nodes() -> void:
	if has_node("Background"):
		$Background.show_behind_parent = true
	if has_node("DimOverlay"):
		$DimOverlay.show_behind_parent = true
	if top_bar_margin == null and has_node("TopBar/Margin"):
		top_bar_margin = $TopBar/Margin
		bottom_bar_margin = $BottomBar/Margin
	if menu_button == null and has_node("TopBar/Margin/HBox/MenuBtn"):
		menu_button = $TopBar/Margin/HBox/MenuBtn
		if has_node("TopBar/Margin/HBox/MusicBtn"):
			music_button = $TopBar/Margin/HBox/MusicBtn
		if has_node("TopBar/Margin/HBox/ControlBtn"):
			control_button = $TopBar/Margin/HBox/ControlBtn
		dpad_overlay = find_child("DPadOverlay", true, false) as Control
		dpad_up = find_child("DPadUp", true, false) as Button
		dpad_down = find_child("DPadDown", true, false) as Button
		dpad_left = find_child("DPadLeft", true, false) as Button
		dpad_right = find_child("DPadRight", true, false) as Button
		level_label = $TopBar/Margin/HBox/LevelLabel
		stats_label = $TopBar/Margin/HBox/StatsLabel
		prev_button = $BottomBar/Margin/HBox/PrevButton
		if has_node("BottomBar/Margin/HBox/UndoButton"):
			undo_button = $BottomBar/Margin/HBox/UndoButton
		if has_node("BottomBar/Margin/HBox/HintButton"):
			hint_button = $BottomBar/Margin/HBox/HintButton
		if has_node("HintToast"):
			hint_toast = $HintToast
			if has_node("HintToast/Margin/Label"):
				hint_toast_label = $HintToast/Margin/Label
			elif has_node("HintToast/Label"):
				hint_toast_label = $HintToast/Label
		restart_button = $BottomBar/Margin/HBox/RestartButton
		next_button = $BottomBar/Margin/HBox/NextButton
		restart_dialog = $RestartConfirmDialog

	if win_modal == null and has_node("WinModal"):
		win_modal = $WinModal
	if win_blur_overlay == null and has_node("WinBlurOverlay"):
		win_blur_overlay = $WinBlurOverlay
	if win_modal != null:
		win_title = win_modal.find_child("WinTitle", true, false)
		win_stats = win_modal.find_child("WinStats", true, false)
		win_menu_button = win_modal.find_child("WinMenuBtn", true, false)
		next_level_button = win_modal.find_child("NextLevelBtn", true, false)
		win_retry_button = win_modal.find_child("WinRetryBtn", true, false)
		level_placard_label = win_modal.find_child("LevelPlacardLabel", true, false)
		star_1 = win_modal.find_child("Star1", true, false)
		star_2 = win_modal.find_child("Star2", true, false)
		star_3 = win_modal.find_child("Star3", true, false)


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

	if ad_mgr == null and is_inside_tree() and get_tree().root.has_node("AdManager"):
		ad_mgr = get_tree().root.get_node("AdManager")

	if haptic_mgr == null and is_inside_tree() and get_tree().root.has_node("HapticManager"):
		haptic_mgr = get_tree().root.get_node("HapticManager")

	if safe_area_mgr == null and is_inside_tree() and get_tree().root.has_node("SafeAreaManager"):
		safe_area_mgr = get_tree().root.get_node("SafeAreaManager")
	if safe_area_mgr:
		safe_area_mgr.safe_area_changed.connect(_on_safe_area_changed)
		_apply_safe_area()

	grid = GridLogic.new()
	grid.crate_pushed.connect(_on_crate_pushed)
	grid.player_moved.connect(_on_player_moved)
	grid.move_undone.connect(_on_move_undone)
	grid.level_won.connect(_on_level_won)
	grid.level_reset.connect(_on_level_reset)

	if not menu_button.pressed.is_connected(_on_menu_pressed):
		menu_button.pressed.connect(_on_menu_pressed)
	if not win_menu_button.pressed.is_connected(_on_menu_pressed):
		win_menu_button.pressed.connect(_on_menu_pressed)
	if undo_button != null and not undo_button.pressed.is_connected(_on_undo_pressed):
		undo_button.pressed.connect(_on_undo_pressed)
	if hint_button != null and not hint_button.pressed.is_connected(_on_hint_pressed):
		hint_button.pressed.connect(_on_hint_pressed)
	if not restart_button.pressed.is_connected(_on_restart_pressed):
		restart_button.pressed.connect(_on_restart_pressed)
	if not prev_button.pressed.is_connected(_on_prev_level_pressed):
		prev_button.pressed.connect(_on_prev_level_pressed)
	if not next_button.pressed.is_connected(_on_next_level_pressed):
		next_button.pressed.connect(_on_next_level_pressed)
	if next_level_button != null and not next_level_button.pressed.is_connected(_on_next_level_pressed):
		next_level_button.pressed.connect(_on_next_level_pressed)
	if win_retry_button != null and not win_retry_button.pressed.is_connected(_on_win_retry_pressed):
		win_retry_button.pressed.connect(_on_win_retry_pressed)
	if not restart_dialog.confirmed.is_connected(_do_restart):
		restart_dialog.confirmed.connect(_do_restart)
	if not restart_dialog.canceled.is_connected(_on_restart_dialog_canceled):
		restart_dialog.canceled.connect(_on_restart_dialog_canceled)
	if music_button != null and not music_button.pressed.is_connected(_on_music_btn_pressed):
		music_button.pressed.connect(_on_music_btn_pressed)
	if control_button != null and not control_button.pressed.is_connected(_on_control_button_pressed):
		control_button.pressed.connect(_on_control_button_pressed)
	if dpad_up != null and not dpad_up.pressed.is_connected(_on_dpad_up_pressed):
		dpad_up.pressed.connect(_on_dpad_up_pressed)
	if dpad_down != null and not dpad_down.pressed.is_connected(_on_dpad_down_pressed):
		dpad_down.pressed.connect(_on_dpad_down_pressed)
	if dpad_left != null and not dpad_left.pressed.is_connected(_on_dpad_left_pressed):
		dpad_left.pressed.connect(_on_dpad_left_pressed)
	if dpad_right != null and not dpad_right.pressed.is_connected(_on_dpad_right_pressed):
		dpad_right.pressed.connect(_on_dpad_right_pressed)
	_update_music_button_ui()
	_update_control_scheme_ui()

	if star_1:
		star_1.pivot_offset = Vector2(28, 28)
		star_1.rotation_degrees = -10.0
	if star_2:
		star_2.pivot_offset = Vector2(34, 34)
		star_2.rotation_degrees = 0.0
	if star_3:
		star_3.pivot_offset = Vector2(28, 28)
		star_3.rotation_degrees = 10.0

	if loc_mgr:
		restart_dialog.ok_button_text = loc_mgr.tr_text("BTN_RESTART")
		restart_dialog.cancel_button_text = loc_mgr.tr_text("BTN_CLOSE")

	var initial_level: int = 0
	if save_mgr and save_mgr.last_played_level >= 0 and save_mgr.last_played_level < level_paths.size():
		initial_level = save_mgr.last_played_level
	load_level(initial_level)
	if get_viewport():
		get_viewport().size_changed.connect(queue_redraw)

	# Tactile arcade button physics
	_attach_spring_physics(menu_button)
	_attach_spring_physics(prev_button)
	_attach_spring_physics(undo_button)
	if hint_button != null:
		_attach_spring_physics(hint_button)
	_attach_spring_physics(restart_button)
	_attach_spring_physics(next_button)
	if hint_toast != null:
		hint_toast.hide()
	if win_menu_button:
		_attach_spring_physics(win_menu_button)
	if next_level_button:
		_attach_spring_physics(next_level_button)
	if win_retry_button:
		_attach_spring_physics(win_retry_button)
	for b in [control_button, dpad_up, dpad_down, dpad_left, dpad_right]:
		if b != null:
			_attach_spring_physics(b)


func _apply_safe_area() -> void:
	if safe_area_mgr != null:
		if top_bar_margin != null:
			safe_area_mgr.apply_safe_area_margins(top_bar_margin, 16, 10, 16, 10, true, false)
		if bottom_bar_margin != null:
			safe_area_mgr.apply_safe_area_margins(bottom_bar_margin, 16, 10, 16, 10, false, true)
	calculate_layout()
	queue_redraw()


func _on_safe_area_changed(_insets: Dictionary) -> void:
	_apply_safe_area()


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
	current_walk_frame = 0
	walk_step_count = 0
	clear_hint()
	level_start_time = Time.get_ticks_msec()
	if win_modal:
		win_modal.hide()
	if win_blur_overlay:
		win_blur_overlay.hide()
	if ad_mgr:
		ad_mgr.preload_interstitial()
	if audio_mgr and audio_mgr.has_method("unduck_music"):
		audio_mgr.unduck_music(0.8)

	# Sync visual positions
	visual_player_pos = Vector2(grid.get_player_pos())
	visual_crates.clear()
	for crate_pos in grid.crates.keys():
		visual_crates[crate_pos] = Vector2(crate_pos)

	_last_hud_moves = 0
	board_trauma = 0.0
	board_shake_offset = Vector2.ZERO
	dust_particles.clear()
	goal_effects.clear()
	crate_squash.clear()

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
		if undo_button != null:
			undo_button.text = loc_mgr.tr_text("BTN_UNDO")
		if hint_button != null:
			hint_button.text = loc_mgr.tr_text("BTN_HINT")
		prev_button.text = loc_mgr.tr_text("BTN_PREV")
		next_button.text = loc_mgr.tr_text("BTN_NEXT")
		if win_menu_button != null:
			win_menu_button.text = "⌂ " + loc_mgr.tr_text("WIN_MENU_BTN")
		if next_level_button != null:
			next_level_button.text = "▶ " + loc_mgr.tr_text("WIN_NEXT_BTN")
		if win_retry_button != null:
			win_retry_button.text = loc_mgr.tr_text("WIN_RETRY_BTN")
	else:
		level_label.text = "LEVEL %d / %d" % [current_level_index + 1, level_paths.size()]
		stats_label.text = "MOVES: %d  |  PUSHES: %d%s" % [grid.moves_count, grid.pushes_count, best_str]
		if undo_button != null:
			undo_button.text = "Undo ↶"
		if hint_button != null:
			hint_button.text = "Hint 💡"
		if win_menu_button != null:
			win_menu_button.text = "⌂ MENU"
		if next_level_button != null:
			next_level_button.text = "▶ NEXT"
		if win_retry_button != null:
			win_retry_button.text = "↺ RETRY"

	if undo_button != null:
		undo_button.disabled = (grid == null or not grid.can_undo())
	if hint_button != null:
		hint_button.disabled = (grid == null or grid.is_won())
	prev_button.disabled = (current_level_index == 0)
	var can_advance: bool = (current_level_index < level_paths.size() - 1)
	if save_mgr:
		can_advance = can_advance and save_mgr.is_level_unlocked(current_level_index + 1)
	next_button.disabled = not can_advance

	# Numeric pop animation on moves counter
	if grid != null and grid.moves_count > _last_hud_moves:
		_last_hud_moves = grid.moves_count
		if stats_label != null and stats_label.is_inside_tree():
			stats_label.pivot_offset = stats_label.size / 2.0
			var pop_tw: Tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
			stats_label.scale = Vector2(1.14, 1.14)
			pop_tw.tween_property(stats_label, "scale", Vector2.ONE, 0.16)
	elif grid != null and grid.moves_count < _last_hud_moves:
		_last_hud_moves = grid.moves_count


func _on_player_moved(from_pos: Vector2i, to_pos: Vector2i) -> void:
	_update_ui()
	_animate_player(from_pos, to_pos)
	if not grid.last_move_pushed_crate and audio_mgr:
		audio_mgr.play_move()


func _on_crate_pushed(from_pos: Vector2i, to_pos: Vector2i) -> void:
	_animate_crate(from_pos, to_pos)
	_spawn_push_dust(from_pos, to_pos)
	add_trauma(0.24)
	if grid != null and grid.goals.has(to_pos):
		_spawn_goal_effect(to_pos)
		add_trauma(0.38)
		if audio_mgr:
			if audio_mgr.has_method("play_goal_lock"):
				audio_mgr.play_goal_lock()
			else:
				audio_mgr.play_push()
	else:
		if audio_mgr:
			audio_mgr.play_push()

	if haptic_mgr:
		if grid != null and grid.goals.has(to_pos):
			haptic_mgr.vibrate_target()
		else:
			haptic_mgr.vibrate_push()


func _on_level_won() -> void:
	add_trauma(0.50)
	if audio_mgr:
		audio_mgr.play_win()
		if audio_mgr.has_method("duck_music"):
			audio_mgr.duck_music(-18.0, 0.3)
	if haptic_mgr:
		haptic_mgr.vibrate_win()
	if save_mgr:
		save_mgr.record_level_completion(current_level_index, grid.moves_count, grid.pushes_count)
	if ad_mgr:
		ad_mgr.record_level_completed(current_level_index)

	_spawn_celebration_particles()
	_update_ui()

	# Delay win popup slightly so player sees the celebration burst and crate snap to goal
	await get_tree().create_timer(0.35).timeout
	var elapsed_ms: int = Time.get_ticks_msec() - level_start_time
	var elapsed_sec: int = maxi(int(elapsed_ms / 1000.0), 1)
	var time_formatted: String = "%02d:%02d" % [int(elapsed_sec / 60.0), elapsed_sec % 60]

	var earned_stars: int = save_mgr.calculate_stars(current_level_index, grid.moves_count) if save_mgr else 1
	var optimal_moves: int = save_mgr.get_optimal_moves(current_level_index) if save_mgr else 10
	var three_star_target: int = optimal_moves + 2

	# Populate card stats
	var moves_card = win_modal.find_child("MovesCard", true, false) if win_modal else null
	var time_card = win_modal.find_child("TimeCard", true, false) if win_modal else null
	var pushes_card = win_modal.find_child("PushesCard", true, false) if win_modal else null

	var moves_val_lbl = moves_card.find_child("Val", true, false) if moves_card else null
	var time_val_lbl = time_card.find_child("Val", true, false) if time_card else null
	var pushes_val_lbl = pushes_card.find_child("Val", true, false) if pushes_card else null

	var moves_title_lbl = moves_card.find_child("Title", true, false) if moves_card else null
	var time_title_lbl = time_card.find_child("Title", true, false) if time_card else null
	var pushes_title_lbl = pushes_card.find_child("Title", true, false) if pushes_card else null

	if moves_val_lbl: moves_val_lbl.text = str(grid.moves_count)
	if time_val_lbl: time_val_lbl.text = time_formatted
	if pushes_val_lbl: pushes_val_lbl.text = str(grid.pushes_count)

	if level_placard_label:
		level_placard_label.text = "LEVEL %d" % [current_level_index + 1]

	if loc_mgr:
		if moves_title_lbl: moves_title_lbl.text = loc_mgr.tr_text("STAT_MOVES_TITLE")
		if time_title_lbl: time_title_lbl.text = loc_mgr.tr_text("STAT_TIME_TITLE")
		if pushes_title_lbl: pushes_title_lbl.text = loc_mgr.tr_text("STAT_PUSHES_TITLE")
		if win_title: win_title.text = loc_mgr.tr_text("WIN_BANNER")
		if win_menu_button: win_menu_button.text = "⌂ " + loc_mgr.tr_text("WIN_MENU_BTN")
		if win_retry_button: win_retry_button.text = loc_mgr.tr_text("WIN_RETRY_BTN")
		if next_level_button:
			if current_level_index >= level_paths.size() - 1:
				next_level_button.text = "★ " + loc_mgr.tr_text("BTN_CAMPAIGN_COMPLETE")
			else:
				next_level_button.text = "▶ " + loc_mgr.tr_text("WIN_NEXT_BTN")
		if win_stats: win_stats.text = loc_mgr.tr_text("WIN_TARGET_HINT", [three_star_target])
	else:
		if win_title: win_title.text = "LEVEL COMPLETED!"
		if win_menu_button: win_menu_button.text = "⌂ MENU"
		if win_retry_button: win_retry_button.text = "↺ RETRY"
		if next_level_button:
			if current_level_index >= level_paths.size() - 1:
				next_level_button.text = "★ Finish Campaign"
			else:
				next_level_button.text = "▶ NEXT"
		if win_stats: win_stats.text = "3★ Target: ≤ %d moves" % three_star_target

	# Prepare stars in unlit state
	var stars: Array = [star_1, star_2, star_3]
	var dim_color: Color = Color(0.38, 0.40, 0.48, 0.55)
	var gold_color: Color = Color(1.0, 0.88, 0.22, 1.0)
	for s in stars:
		if s:
			s.modulate = dim_color
			s.scale = Vector2.ONE
			var s_sz: Vector2 = s.custom_minimum_size if s.custom_minimum_size != Vector2.ZERO else s.size
			s.pivot_offset = s_sz / 2.0

	if win_blur_overlay:
		win_blur_overlay.modulate.a = 0.0
		win_blur_overlay.show()
		var tw_blur: Tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw_blur.tween_property(win_blur_overlay, "modulate:a", 1.0, 0.25)

	win_modal.show()
	_animate_stars_sequence(stars, earned_stars, gold_color)


func _animate_stars_sequence(stars: Array, earned: int, gold_color: Color) -> void:
	for i in range(mini(earned, stars.size())):
		var s = stars[i]
		if s == null:
			continue
		var star_num: int = i + 1
		var delay: float = 0.22 + float(i) * 0.28
		var tw: Tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		tw.tween_interval(delay)
		tw.tween_callback(func():
			s.modulate = gold_color
			var s_sz: Vector2 = s.size if s.size != Vector2.ZERO else s.custom_minimum_size
			s.pivot_offset = s_sz / 2.0
			s.scale = Vector2(1.35, 1.35)
			if audio_mgr:
				audio_mgr.play_star(star_num)
			if haptic_mgr:
				haptic_mgr.vibrate_target()
		)
		tw.tween_property(s, "scale", Vector2.ONE, 0.22)


func _on_level_reset() -> void:
	current_walk_frame = 0
	walk_step_count = 0
	clear_hint()
	visual_player_pos = Vector2(grid.get_player_pos())
	visual_crates.clear()
	for crate_pos in grid.crates.keys():
		visual_crates[crate_pos] = Vector2(crate_pos)
	_update_ui()
	queue_redraw()


func _animate_player(from_pos: Vector2i, to_pos: Vector2i) -> void:
	is_animating = true
	walk_step_count += 1
	var step_base: int = 1 if (walk_step_count % 2 == 1) else 2
	current_walk_frame = step_base
	var tween: Tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	visual_player_pos = Vector2(from_pos)
	tween.tween_method(func(pos: Vector2):
		visual_player_pos = pos
		var dist: float = pos.distance_to(Vector2(from_pos))
		if dist > 0.5:
			current_walk_frame = 2 if step_base == 1 else 1
		else:
			current_walk_frame = step_base
		queue_redraw()
	, Vector2(from_pos), Vector2(to_pos), 0.12)
	tween.tween_callback(func():
		is_animating = false
		current_walk_frame = 0
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

	# Squash & stretch deformation along push axis
	var push_dir: Vector2i = to_pos - from_pos
	var squash_start: Vector2 = Vector2(0.86, 1.14) if push_dir.x != 0 else Vector2(1.14, 0.86)
	crate_squash[to_pos] = squash_start
	var sq_tw: Tween = create_tween().set_trans(Tween.TRANS_ELASTIC).set_ease(Tween.EASE_OUT)
	sq_tw.tween_method(func(s: Vector2):
		crate_squash[to_pos] = s
		queue_redraw()
	, squash_start, Vector2.ONE, 0.22)


func try_move(dir: Vector2i) -> void:
	player_facing_dir = dir
	clear_hint()
	if win_modal != null and win_modal.visible:
		return

	if is_animating:
		# PRD Section 5: "A swipe made during a move animation is queued (one move only)."
		queued_move_dir = dir
		return

	if grid != null:
		var moved: bool = grid.move(dir)
		if not moved:
			add_trauma(0.12)
			if haptic_mgr:
				haptic_mgr.vibrate_bump()


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
			KEY_Z, KEY_U, KEY_BACKSPACE:
				_on_undo_pressed()

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
	if save_mgr and "control_scheme" in save_mgr and save_mgr.control_scheme == 1:
		return # Swipe disabled when D-PAD only mode is active
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
		if audio_mgr and audio_mgr.has_method("duck_music"):
			audio_mgr.duck_music(-10.0, 0.2)
		if restart_dialog.is_inside_tree():
			restart_dialog.popup_centered()
	else:
		_do_restart()


func _do_restart() -> void:
	if audio_mgr:
		audio_mgr.play_restart()
		if audio_mgr.has_method("unduck_music"):
			audio_mgr.unduck_music(0.5)
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	if grid:
		grid.restart()


func _on_restart_dialog_canceled() -> void:
	if audio_mgr and audio_mgr.has_method("unduck_music"):
		audio_mgr.unduck_music(0.5)


func _on_music_btn_pressed() -> void:
	if audio_mgr != null and audio_mgr.has_method("is_music_enabled"):
		var cur_on: bool = audio_mgr.is_music_enabled()
		audio_mgr.set_music_enabled(not cur_on)
		if audio_mgr.has_method("play_click"):
			audio_mgr.play_click()
	elif save_mgr != null and "music_enabled" in save_mgr:
		save_mgr.music_enabled = not save_mgr.music_enabled
		if save_mgr.has_method("save_data"):
			save_mgr.save_data()
	if haptic_mgr != null and haptic_mgr.has_method("vibrate_click"):
		haptic_mgr.vibrate_click()
	_update_music_button_ui()


func _update_music_button_ui() -> void:
	if music_button == null:
		return
	var is_on: bool = true
	if audio_mgr != null and audio_mgr.has_method("is_music_enabled"):
		is_on = audio_mgr.is_music_enabled()
	elif save_mgr != null and "music_enabled" in save_mgr:
		is_on = save_mgr.music_enabled
	music_button.text = "♪" if is_on else "♪̸"
	music_button.modulate = Color(1.0, 0.92, 0.45) if is_on else Color(0.65, 0.70, 0.80, 0.65)


func _on_control_button_pressed() -> void:
	if save_mgr and save_mgr.has_method("cycle_control_scheme"):
		save_mgr.cycle_control_scheme()
	elif save_mgr and "control_scheme" in save_mgr:
		save_mgr.control_scheme = (save_mgr.control_scheme + 1) % 3
		if save_mgr.has_method("save_data"):
			save_mgr.save_data()
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	_update_control_scheme_ui()
	calculate_layout()
	queue_redraw()


func _update_control_scheme_ui() -> void:
	var scheme: int = save_mgr.control_scheme if save_mgr and "control_scheme" in save_mgr else 0
	# 0 = Swipe, 1 = D-Pad, 2 = Dual
	var show_dpad: bool = (scheme == 1 or scheme == 2)
	if dpad_overlay:
		dpad_overlay.visible = show_dpad
	if control_button:
		match scheme:
			0:
				control_button.text = "✋"
				control_button.modulate = Color(0.75, 0.85, 0.98)
			1:
				control_button.text = "✥"
				control_button.modulate = Color(1.0, 0.88, 0.25)
			2:
				control_button.text = "🎮"
				control_button.modulate = Color(0.35, 0.92, 0.55)


func _on_dpad_up_pressed() -> void:
	try_move(Vector2i.UP)


func _on_dpad_down_pressed() -> void:
	try_move(Vector2i.DOWN)


func _on_dpad_left_pressed() -> void:
	try_move(Vector2i.LEFT)


func _on_dpad_right_pressed() -> void:
	try_move(Vector2i.RIGHT)


func _on_undo_pressed() -> void:
	if win_modal != null and win_modal.visible:
		return
	is_animating = false
	queued_move_dir = Vector2i.ZERO
	clear_hint()
	if grid != null and grid.can_undo():
		if audio_mgr:
			audio_mgr.play_click()
		if haptic_mgr:
			haptic_mgr.vibrate_click()
		grid.undo()


func _on_move_undone(p_pos: Vector2i, _had_crate: bool, _crate_from: Vector2i, _crate_to: Vector2i) -> void:
	is_animating = false
	queued_move_dir = Vector2i.ZERO
	current_walk_frame = 0
	clear_hint()
	visual_player_pos = Vector2(p_pos)
	visual_crates.clear()
	for crate_pos in grid.crates.keys():
		visual_crates[crate_pos] = Vector2(crate_pos)
	_update_ui()
	queue_redraw()


func _on_hint_pressed() -> void:
	if is_animating:
		return
	if win_modal != null and win_modal.visible:
		return
	if grid == null or grid.is_won():
		return

	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()

	var result: SokobanSolver.SolverResult = SokobanSolverScript.solve(grid, 25000)
	if not result.is_solvable or result.solution_str.is_empty():
		# Deadlock detected!
		if audio_mgr:
			audio_mgr.play_deadlock()
		if haptic_mgr:
			haptic_mgr.vibrate_impact()
		add_trauma(0.25)
		_show_hint_toast(loc_mgr.tr_text("HINT_DEADLOCK") if loc_mgr else "No solution from here! Tap Undo ↶", Color(1.0, 0.4, 0.4))
		clear_hint()
		return

	# Solvable next step
	if audio_mgr:
		audio_mgr.play_hint()

	var move_char: String = result.solution_str.substr(0, 1)
	match move_char:
		"u": active_hint_dir = Vector2i.UP
		"d": active_hint_dir = Vector2i.DOWN
		"l": active_hint_dir = Vector2i.LEFT
		"r": active_hint_dir = Vector2i.RIGHT
		_: active_hint_dir = Vector2i.ZERO

	if active_hint_dir == Vector2i.ZERO:
		return

	hint_player_target = grid.player_pos + active_hint_dir
	hint_has_crate = grid.has_crate(hint_player_target)
	hint_crate_target = (hint_player_target + active_hint_dir) if hint_has_crate else Vector2i.ZERO
	hint_time_remaining = 4.0 # Active for 4 seconds
	hint_pulse_timer = 0.0

	var dir_key: String = "UP"
	if active_hint_dir == Vector2i.DOWN: dir_key = "DOWN"
	elif active_hint_dir == Vector2i.LEFT: dir_key = "LEFT"
	elif active_hint_dir == Vector2i.RIGHT: dir_key = "RIGHT"

	var toast_msg: String = loc_mgr.tr_text("HINT_STEP_" + dir_key) if loc_mgr else ("💡 Hint: Move " + dir_key)
	_show_hint_toast(toast_msg, Color(1.0, 0.95, 0.6))
	queue_redraw()


func _show_hint_toast(msg: String, color: Color = Color(1.0, 0.95, 0.6)) -> void:
	if hint_toast == null or hint_toast_label == null:
		return
	hint_toast_label.text = msg
	hint_toast_label.modulate = color
	hint_toast.modulate.a = 0.0
	hint_toast.show()
	var tw: Tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
	tw.tween_property(hint_toast, "modulate:a", 1.0, 0.18)
	tw.tween_interval(2.2)
	tw.tween_property(hint_toast, "modulate:a", 0.0, 0.35)
	tw.tween_callback(func():
		if hint_toast:
			hint_toast.hide()
	)


func clear_hint() -> void:
	active_hint_dir = Vector2i.ZERO
	hint_time_remaining = 0.0
	if hint_toast != null:
		hint_toast.hide()
	queue_redraw()


func _on_prev_level_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	if current_level_index > 0:
		load_level(current_level_index - 1)


func _on_next_level_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()

	# If completing the final level (Level 50), navigate to the Campaign End Screen (PRD Section 6)
	if current_level_index >= level_paths.size() - 1:
		get_tree().change_scene_to_file("res://scenes/end_screen.tscn")
		return

	var next_idx: int = current_level_index + 1
	if not save_mgr or save_mgr.is_level_unlocked(next_idx):
		if ad_mgr and ad_mgr.should_show_interstitial(current_level_index):
			ad_mgr.show_interstitial(current_level_index)
			if ad_mgr.is_showing_ad:
				await ad_mgr.interstitial_closed
		load_level(next_idx)


func _on_win_retry_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	if win_modal != null:
		win_modal.hide()
	if win_blur_overlay != null:
		win_blur_overlay.hide()
	load_level(current_level_index)


func _on_menu_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
		if audio_mgr.has_method("unduck_music"):
			audio_mgr.unduck_music(0.5)
	if haptic_mgr:
		haptic_mgr.vibrate_click()
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

	# Update hint ghost timer
	if hint_time_remaining > 0.0:
		needs_redraw = true
		hint_time_remaining -= delta
		hint_pulse_timer += delta
		if hint_time_remaining <= 0.0:
			clear_hint()

	# Subtle continuous breathing pulse for goals
	if grid and not grid.goals.is_empty():
		needs_redraw = true

	# Update board trauma & shake
	if board_trauma > 0.0:
		board_trauma = max(0.0, board_trauma - delta * 4.2)
		var shake_mag: float = board_trauma * board_trauma * 7.5
		var a: float = randf() * TAU
		board_shake_offset = Vector2(cos(a), sin(a)) * shake_mag
		needs_redraw = true
	else:
		board_shake_offset = Vector2.ZERO

	# Update dust particles
	if not dust_particles.is_empty():
		needs_redraw = true
		var di: int = dust_particles.size() - 1
		while di >= 0:
			var dp: Dictionary = dust_particles[di]
			dp["life"] -= delta
			if dp["life"] <= 0.0:
				dust_particles.remove_at(di)
			else:
				dp["pos"] += dp["vel"] * delta
				dp["vel"] *= (1.0 - 5.0 * delta)
				dp["size"] += 2.0 * delta
			di -= 1

	# Update goal shockwaves & sparks
	if not goal_effects.is_empty():
		needs_redraw = true
		var gi: int = goal_effects.size() - 1
		while gi >= 0:
			var ge: Dictionary = goal_effects[gi]
			ge["life"] -= delta
			if ge["life"] <= 0.0:
				goal_effects.remove_at(gi)
			else:
				if ge["type"] == "ring":
					var progress: float = 1.0 - (ge["life"] / ge["max_life"])
					ge["radius"] = lerpf(4.0, ge["max_radius"], progress)
				elif ge["type"] == "spark":
					ge["pos"] += ge["vel"] * delta
					ge["vel"] *= (1.0 - 3.0 * delta)
			gi -= 1

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

	var insets: Dictionary = safe_area_mgr.get_safe_insets(self) if safe_area_mgr else { "top": 0.0, "bottom": 0.0, "left": 0.0, "right": 0.0 }
	var safe_top: float = insets.get("top", 0.0)
	var safe_bottom: float = insets.get("bottom", 0.0)
	var safe_horiz: float = insets.get("left", 0.0) + insets.get("right", 0.0)

	var top_offset: float = 70.0 + safe_top
	var dpad_allowance: float = 160.0 if (dpad_overlay and dpad_overlay.visible) else 0.0
	var bottom_offset: float = 70.0 + safe_bottom + dpad_allowance
	var playable_height: float = viewport_size.y - (top_offset + bottom_offset)
	var playable_width: float = viewport_size.x - (36.0 + safe_horiz)

	var max_tile_w: float = playable_width / float(grid.width)
	var max_tile_h: float = playable_height / float(grid.height)
	tile_size = floor(min(max_tile_w, max_tile_h))

	var board_pixel_size: Vector2 = Vector2(grid.width * tile_size, grid.height * tile_size)
	grid_origin = Vector2(
		floor((viewport_size.x - board_pixel_size.x) / 2.0),
		floor(top_offset + (playable_height - board_pixel_size.y) / 2.0)
	)


func _draw() -> void:
	if not grid or grid.width == 0 or grid.height == 0:
		return

	calculate_layout()
	var effective_origin: Vector2 = grid_origin + board_shake_offset
	var board_pixel_size: Vector2 = Vector2(grid.width * tile_size, grid.height * tile_size)

	# 1. Industrial Warehouse Loading Bay Board Framing (PRD Section 4)
	var frame_margin: float = 12.0
	var frame_rect: Rect2 = Rect2(
		effective_origin - Vector2(frame_margin, frame_margin),
		board_pixel_size + Vector2(frame_margin * 2.0, frame_margin * 2.0)
	)

	# Multi-stage drop shadow
	draw_rect(Rect2(frame_rect.position + Vector2(8, 10), frame_rect.size), Color(0.0, 0.0, 0.0, 0.65))
	draw_rect(Rect2(frame_rect.position + Vector2(4, 5), frame_rect.size), Color(0.0, 0.0, 0.0, 0.40))

	# Heavy dark steel frame base
	draw_rect(frame_rect, Color(0.12, 0.15, 0.20))
	# Polished brass bevel rim
	draw_rect(frame_rect, Color(0.78, 0.60, 0.22), false, 2.5)
	# Inner dark groove
	draw_rect(Rect2(effective_origin - Vector2(2, 2), board_pixel_size + Vector2(4, 4)), Color(0.06, 0.08, 0.12), false, 2.0)

	# 4 Corner industrial brass bolts
	var corner_offsets: Array[Vector2] = [
		Vector2(frame_margin * 0.5, frame_margin * 0.5),
		Vector2(frame_rect.size.x - frame_margin * 0.5, frame_margin * 0.5),
		Vector2(frame_margin * 0.5, frame_rect.size.y - frame_margin * 0.5),
		Vector2(frame_rect.size.x - frame_margin * 0.5, frame_rect.size.y - frame_margin * 0.5)
	]
	for c_offset in corner_offsets:
		var bolt_center: Vector2 = frame_rect.position + c_offset
		draw_circle(bolt_center, 4.5, Color(0.12, 0.09, 0.05))
		draw_circle(bolt_center, 3.5, Color(0.92, 0.74, 0.28))
		draw_circle(bolt_center - Vector2(1.0, 1.0), 1.2, Color(1.0, 0.95, 0.70))

	# 2. Draw Floor & Walls with 3D Depth
	for y in range(grid.height):
		for x in range(grid.width):
			var pos: Vector2i = Vector2i(x, y)
			var rect: Rect2 = Rect2(effective_origin + Vector2(x, y) * tile_size, Vector2(tile_size, tile_size))

			if grid.is_wall(pos):
				_draw_wall(rect)
			else:
				var is_alt: bool = ((x + y) % 2 == 0)
				var floor_tex: Texture2D = tex_floor_1 if is_alt else tex_floor_2
				draw_texture_rect(floor_tex, rect, false)

				# 3D Depth Shadow: if cell above is a wall, cast drop shadow down
				if y > 0 and grid.is_wall(Vector2i(x, y - 1)):
					draw_rect(Rect2(rect.position, Vector2(rect.size.x, tile_size * 0.22)), Color(0.0, 0.0, 0.0, 0.42))

	# 3. Draw Goals with Industrial Pressure Plate & Pulsing Aura
	var time_sec: float = float(Time.get_ticks_msec()) / 1000.0
	var pulse: float = sin(time_sec * 3.5) * 0.12
	for goal_pos in grid.goals.keys():
		var rect: Rect2 = Rect2(effective_origin + Vector2(goal_pos) * tile_size, Vector2(tile_size, tile_size))
		var center: Vector2 = rect.get_center()

		draw_texture_rect(tex_goal, rect, false)

		# Pulsing dynamic golden aura
		var aura_radius: float = (tile_size * 0.26) * (1.0 + pulse)
		draw_circle(center, aura_radius + 4.0, Color(0.98, 0.82, 0.20, 0.22 + pulse * 0.10))
		draw_circle(center, 3.5, Color(1.0, 1.0, 0.85, 0.90))

	# 4. Draw Push Friction Dust Puffs
	for dp in dust_particles:
		var alpha: float = clampf(dp["life"] / dp["max_life"], 0.0, 1.0)
		var col: Color = dp["color"]
		col.a = alpha * 0.70
		draw_circle(dp["pos"], dp["size"], col)

	# 5. Draw Goal Shockwaves & Sparks
	for ge in goal_effects:
		var alpha: float = clampf(ge["life"] / ge["max_life"], 0.0, 1.0)
		if ge["type"] == "ring":
			var ring_col: Color = ge["color"]
			ring_col.a = alpha * 0.85
			draw_arc(ge["pos"], ge["radius"], 0, TAU, 32, ring_col, 3.0, true)
		elif ge["type"] == "spark":
			var spark_col: Color = ge["color"]
			spark_col.a = alpha
			draw_circle(ge["pos"], ge["size"] * alpha, spark_col)

	# 6. Draw Crates with Drop Shadow, 3D Shading & Squash
	for logical_pos in grid.crates.keys():
		var draw_tile_pos: Vector2 = visual_crates.get(logical_pos, Vector2(logical_pos))
		var is_on_goal: bool = grid.is_goal(logical_pos)
		var crate_padding: float = tile_size * 0.04
		var rect: Rect2 = Rect2(
			effective_origin + draw_tile_pos * tile_size + Vector2(crate_padding, crate_padding),
			Vector2(tile_size - crate_padding * 2.0, tile_size - crate_padding * 2.0)
		)
		_draw_crate(rect, is_on_goal, logical_pos)

	# 7. Draw Directional Porter Worker
	var player_padding: float = tile_size * 0.04
	var player_rect: Rect2 = Rect2(
		effective_origin + visual_player_pos * tile_size + Vector2(player_padding, player_padding),
		Vector2(tile_size - player_padding * 2.0, tile_size - player_padding * 2.0)
	)
	_draw_player(player_rect)

	# 7.5. Draw 1-Step Hint Directional Ghost & Indicator
	_draw_hint_ghost(effective_origin)

	# 8. Draw Victory Celebration Particles
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
	draw_texture_rect(tex_wall, rect, false)


func _draw_crate(rect: Rect2, on_goal: bool, logical_pos: Vector2i = Vector2i.ZERO) -> void:
	# Crate soft drop shadow
	var shadow_rect: Rect2 = Rect2(rect.position + Vector2(3, 5), rect.size)
	draw_rect(shadow_rect, Color(0.0, 0.0, 0.0, 0.38))

	var scale_fac: Vector2 = crate_squash.get(logical_pos, Vector2.ONE)
	var c_center: Vector2 = rect.get_center()
	var scaled_sz: Vector2 = rect.size * scale_fac
	var draw_r: Rect2 = Rect2(c_center - scaled_sz * 0.5, scaled_sz)

	var c_tex: Texture2D = tex_crate_goal if on_goal else tex_crate
	draw_texture_rect(c_tex, draw_r, false)

	if on_goal:
		var time_sec: float = float(Time.get_ticks_msec()) / 1000.0
		var star_pulse: float = sin(time_sec * 4.0) * 0.15
		draw_circle(c_center, 8.0 * (1.0 + star_pulse), Color(1.0, 0.95, 0.5, 0.45))


func _draw_player(rect: Rect2) -> void:
	var center: Vector2 = rect.get_center()
	var radius: float = rect.size.x / 2.0

	# Ground contact drop shadow (positioned directly under soles of boots)
	var x_offset: float = 0.0
	if player_facing_dir == Vector2i.LEFT:
		x_offset = -radius * 0.04
	elif player_facing_dir == Vector2i.RIGHT:
		x_offset = radius * 0.04
	var shadow_center: Vector2 = Vector2(center.x + x_offset, rect.position.y + rect.size.y * 0.94)

	# 1. Outer soft ambient shadow
	var pts_outer: PackedVector2Array = []
	var rx_outer: float = radius * 0.54
	var ry_outer: float = radius * 0.18
	for i in range(16):
		var a: float = i * (TAU / 16.0)
		pts_outer.append(shadow_center + Vector2(cos(a) * rx_outer, sin(a) * ry_outer))
	draw_colored_polygon(pts_outer, Color(0.0, 0.0, 0.0, 0.22))

	# 2. Inner core contact shadow (tight under soles)
	var pts_inner: PackedVector2Array = []
	var rx_inner: float = radius * 0.40
	var ry_inner: float = radius * 0.11
	for i in range(16):
		var a: float = i * (TAU / 16.0)
		pts_inner.append(shadow_center + Vector2(cos(a) * rx_inner, sin(a) * ry_inner))
	draw_colored_polygon(pts_inner, Color(0.0, 0.0, 0.0, 0.32))

	# Pick directional sprite (idle vs walk cycle frame 1/2)
	var p_tex: Texture2D = tex_player_down
	if player_facing_dir == Vector2i.UP:
		p_tex = tex_player_up_w1 if current_walk_frame == 1 else (tex_player_up_w2 if current_walk_frame == 2 else tex_player_up)
	elif player_facing_dir == Vector2i.LEFT:
		p_tex = tex_player_left_w1 if current_walk_frame == 1 else (tex_player_left_w2 if current_walk_frame == 2 else tex_player_left)
	elif player_facing_dir == Vector2i.RIGHT:
		p_tex = tex_player_right_w1 if current_walk_frame == 1 else (tex_player_right_w2 if current_walk_frame == 2 else tex_player_right)
	else:
		p_tex = tex_player_down_w1 if current_walk_frame == 1 else (tex_player_down_w2 if current_walk_frame == 2 else tex_player_down)

	draw_texture_rect(p_tex, rect, false)


func _draw_hint_ghost(effective_origin: Vector2) -> void:
	if hint_time_remaining <= 0.0 or active_hint_dir == Vector2i.ZERO:
		return

	var pulse: float = 0.55 + 0.35 * sin(hint_pulse_timer * 7.0)
	var fade: float = clampf(hint_time_remaining / 0.4, 0.0, 1.0)
	var base_alpha: float = pulse * fade

	# 1. Player Target Ghost Tile
	var p_target_rect: Rect2 = Rect2(
		effective_origin + Vector2(hint_player_target) * tile_size,
		Vector2(tile_size, tile_size)
	)
	var p_center: Vector2 = p_target_rect.get_center()

	# Glowing beacon tile highlight
	draw_rect(p_target_rect.grow(-3), Color(0.15, 0.65, 1.0, 0.22 * base_alpha), true)
	draw_rect(p_target_rect.grow(-3), Color(0.35, 0.85, 1.0, 0.75 * base_alpha), false, 2.5)

	# Pick directional ghost player texture
	var p_ghost_tex: Texture2D = tex_player_down
	if active_hint_dir == Vector2i.UP:
		p_ghost_tex = tex_player_up
	elif active_hint_dir == Vector2i.LEFT:
		p_ghost_tex = tex_player_left
	elif active_hint_dir == Vector2i.RIGHT:
		p_ghost_tex = tex_player_right

	var p_draw_padding: float = tile_size * 0.04
	var p_ghost_draw_rect: Rect2 = Rect2(
		p_target_rect.position + Vector2(p_draw_padding, p_draw_padding),
		Vector2(tile_size - p_draw_padding * 2.0, tile_size - p_draw_padding * 2.0)
	)
	draw_texture_rect(p_ghost_tex, p_ghost_draw_rect, false, Color(1.0, 1.0, 1.0, 0.72 * base_alpha))

	# 2. Crate Target Ghost Tile (if move is a push)
	if hint_has_crate:
		var c_target_rect: Rect2 = Rect2(
			effective_origin + Vector2(hint_crate_target) * tile_size,
			Vector2(tile_size, tile_size)
		)
		# Glowing amber beacon for crate push destination
		draw_rect(c_target_rect.grow(-3), Color(1.0, 0.75, 0.15, 0.22 * base_alpha), true)
		draw_rect(c_target_rect.grow(-3), Color(1.0, 0.88, 0.30, 0.75 * base_alpha), false, 2.5)

		var is_target_goal: bool = grid.is_goal(hint_crate_target)
		var c_ghost_tex: Texture2D = tex_crate_goal if is_target_goal else tex_crate
		var c_draw_padding: float = tile_size * 0.04
		var c_ghost_draw_rect: Rect2 = Rect2(
			c_target_rect.position + Vector2(c_draw_padding, c_draw_padding),
			Vector2(tile_size - c_draw_padding * 2.0, tile_size - c_draw_padding * 2.0)
		)
		draw_texture_rect(c_ghost_tex, c_ghost_draw_rect, false, Color(1.0, 1.0, 1.0, 0.72 * base_alpha))

	# 3. Dynamic Directional Trajectory Arrow
	var current_player_center: Vector2 = effective_origin + visual_player_pos * tile_size + Vector2(tile_size * 0.5, tile_size * 0.5)
	var arrow_start: Vector2 = current_player_center + Vector2(active_hint_dir) * (tile_size * 0.32)
	var arrow_end: Vector2 = p_center - Vector2(active_hint_dir) * (tile_size * 0.22)
	var arrow_col: Color = Color(1.0, 0.92, 0.35, 0.85 * base_alpha)
	draw_line(arrow_start, arrow_end, arrow_col, 3.5)

	# Arrow head
	var arrow_norm: Vector2 = Vector2(active_hint_dir).normalized()
	var arrow_perp: Vector2 = Vector2(-arrow_norm.y, arrow_norm.x)
	var head_len: float = tile_size * 0.18
	var head_width: float = tile_size * 0.14
	var p1: Vector2 = arrow_end
	var p2: Vector2 = arrow_end - arrow_norm * head_len + arrow_perp * head_width
	var p3: Vector2 = arrow_end - arrow_norm * head_len - arrow_perp * head_width
	draw_colored_polygon(PackedVector2Array([p1, p2, p3]), arrow_col)


func add_trauma(amount: float) -> void:
	board_trauma = clampf(board_trauma + amount, 0.0, 1.0)


func _spawn_push_dust(from_pos: Vector2i, to_pos: Vector2i) -> void:
	var dir: Vector2i = to_pos - from_pos
	var base_origin: Vector2 = grid_origin + Vector2(from_pos) * tile_size
	var spawn_edge_center: Vector2 = base_origin + Vector2(tile_size * 0.5, tile_size * 0.5) - Vector2(dir) * (tile_size * 0.42)
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.randomize()

	var dust_palette: Array[Color] = [
		Color(0.85, 0.80, 0.72, 0.85),
		Color(0.72, 0.67, 0.60, 0.80),
		Color(0.55, 0.50, 0.45, 0.70)
	]

	for i in range(6):
		var offset: Vector2 = Vector2.ZERO
		if dir.x != 0:
			offset = Vector2(0, rng.randf_range(-tile_size * 0.35, tile_size * 0.35))
		else:
			offset = Vector2(rng.randf_range(-tile_size * 0.35, tile_size * 0.35), 0)

		var back_vel: Vector2 = -Vector2(dir) * rng.randf_range(40.0, 85.0) + Vector2(rng.randf_range(-20.0, 20.0), rng.randf_range(-20.0, 20.0))
		dust_particles.append({
			"pos": spawn_edge_center + offset,
			"vel": back_vel,
			"size": rng.randf_range(3.0, 5.5),
			"color": dust_palette[rng.randi() % dust_palette.size()],
			"life": rng.randf_range(0.22, 0.32),
			"max_life": 0.32
		})


func _spawn_goal_effect(goal_pos: Vector2i) -> void:
	var center: Vector2 = grid_origin + Vector2(goal_pos) * tile_size + Vector2(tile_size * 0.5, tile_size * 0.5)

	# Expanding shockwave ring
	goal_effects.append({
		"type": "ring",
		"pos": center,
		"radius": 4.0,
		"max_radius": tile_size * 0.85,
		"color": Color(1.0, 0.88, 0.25, 0.95),
		"life": 0.35,
		"max_life": 0.35
	})

	# 8 radiating golden sparks
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.randomize()
	for i in range(8):
		var angle: float = (float(i) / 8.0) * TAU + rng.randf_range(-0.15, 0.15)
		var spd: float = rng.randf_range(110.0, 190.0)
		goal_effects.append({
			"type": "spark",
			"pos": center,
			"vel": Vector2(cos(angle), sin(angle)) * spd,
			"size": rng.randf_range(3.5, 6.5),
			"color": Color(1.0, 0.92, 0.40, 1.0) if i % 2 == 0 else Color(1.0, 0.65, 0.20, 1.0),
			"life": rng.randf_range(0.28, 0.42),
			"max_life": 0.42
		})


func _attach_spring_physics(btn: Button) -> void:
	if btn == null:
		return
	btn.pivot_offset = btn.size / 2.0
	btn.button_down.connect(func():
		btn.pivot_offset = btn.size / 2.0
		var tw: Tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.tween_property(btn, "scale", Vector2(0.93, 0.93), 0.07)
	)
	btn.button_up.connect(func():
		btn.pivot_offset = btn.size / 2.0
		var tw: Tween = create_tween().set_trans(Tween.TRANS_BACK).set_ease(Tween.EASE_OUT)
		tw.tween_property(btn, "scale", Vector2.ONE, 0.15)
	)
	btn.mouse_exited.connect(func():
		btn.pivot_offset = btn.size / 2.0
		var tw: Tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.tween_property(btn, "scale", Vector2.ONE, 0.10)
	)
