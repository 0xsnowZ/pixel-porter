extends Control

## Main menu and Level Select controller for Pixel Porter.
## Implements PRD Section 6 flow:
## - Continue / Play navigation
## - Level select 50-level grid with locked/completed visual states
## - Sound on/off toggle persisted via SaveManager
## - Credits popup

const SaveManagerScript = preload("res://scripts/save_manager.gd")
const TOTAL_LEVELS_COUNT: int = 50
const AVAILABLE_LEVELS_COUNT: int = 10 # 10 verified solvable levels for Week 1

var save_mgr: Node = null
var audio_mgr: Node = null

# Node references
@onready var main_view: VBoxContainer = $MainView
@onready var level_select_view: VBoxContainer = $LevelSelectView
@onready var credits_modal: PanelContainer = $CreditsModal

# Main View buttons
@onready var continue_btn: Button = $MainView/Buttons/ContinueBtn
@onready var play_btn: Button = $MainView/Buttons/PlayBtn
@onready var level_select_btn: Button = $MainView/Buttons/LevelSelectBtn
@onready var sound_btn: Button = $MainView/Buttons/SoundToggleBtn
@onready var credits_btn: Button = $MainView/Buttons/CreditsBtn

# Level Select elements
@onready var level_grid: GridContainer = $LevelSelectView/Scroll/Margin/LevelGrid
@onready var back_btn: Button = $LevelSelectView/TopBar/Margin/HBox/BackBtn
@onready var close_credits_btn: Button = $CreditsModal/VBox/CloseCreditsBtn


func _initialize_nodes() -> void:
	if main_view == null and has_node("MainView"):
		main_view = $MainView
		level_select_view = $LevelSelectView
		credits_modal = $CreditsModal
		continue_btn = $MainView/Buttons/ContinueBtn
		play_btn = $MainView/Buttons/PlayBtn
		level_select_btn = $MainView/Buttons/LevelSelectBtn
		sound_btn = $MainView/Buttons/SoundToggleBtn
		credits_btn = $MainView/Buttons/CreditsBtn
		level_grid = $LevelSelectView/Scroll/Margin/LevelGrid
		back_btn = $LevelSelectView/TopBar/Margin/HBox/BackBtn
		close_credits_btn = $CreditsModal/VBox/CloseCreditsBtn


func _ready() -> void:
	_initialize_nodes()
	if is_inside_tree() and get_tree().root.has_node("SaveManager"):
		save_mgr = get_tree().root.get_node("SaveManager")
	else:
		save_mgr = SaveManagerScript.new()
		add_child(save_mgr)

	if is_inside_tree() and get_tree().root.has_node("AudioManager"):
		audio_mgr = get_tree().root.get_node("AudioManager")

	if not continue_btn.pressed.is_connected(_on_continue_pressed):
		continue_btn.pressed.connect(_on_continue_pressed)
	if not play_btn.pressed.is_connected(_on_play_pressed):
		play_btn.pressed.connect(_on_play_pressed)
	if not level_select_btn.pressed.is_connected(_show_level_select):
		level_select_btn.pressed.connect(_show_level_select)
	if not sound_btn.pressed.is_connected(_on_sound_toggle_pressed):
		sound_btn.pressed.connect(_on_sound_toggle_pressed)
	if not credits_btn.pressed.is_connected(_show_credits):
		credits_btn.pressed.connect(_show_credits)
	if not back_btn.pressed.is_connected(_show_main_view):
		back_btn.pressed.connect(_show_main_view)
	if not close_credits_btn.pressed.is_connected(_hide_credits):
		close_credits_btn.pressed.connect(_hide_credits)

	_show_main_view()
	_update_menu_state()
	_build_level_grid()


func _show_main_view() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	main_view.show()
	level_select_view.hide()
	credits_modal.hide()
	_update_menu_state()


func _show_level_select() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	main_view.hide()
	level_select_view.show()
	credits_modal.hide()
	_refresh_level_grid_buttons()


func _show_credits() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	credits_modal.show()


func _hide_credits() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	credits_modal.hide()


func _update_menu_state() -> void:
	var unlocked_lvl: int = save_mgr.unlocked_level if save_mgr else 0
	var last_lvl: int = save_mgr.last_played_level if save_mgr else 0

	# Show Continue button if player has progressed past level 0 or completed level 0
	var has_progress: bool = (unlocked_lvl > 0 or (save_mgr and save_mgr.is_level_completed(0)))
	if has_progress:
		continue_btn.visible = true
		continue_btn.text = "CONTINUE (LEVEL %d)" % (last_lvl + 1)
		play_btn.text = "NEW GAME"
	else:
		continue_btn.visible = false
		play_btn.text = "PLAY"

	# Sound button status
	var is_sound_on: bool = save_mgr.sound_enabled if save_mgr else true
	sound_btn.text = "SOUND: %s" % ("ON" if is_sound_on else "OFF")


func _on_continue_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	var target_lvl: int = save_mgr.last_played_level if save_mgr else 0
	_start_game_at_level(target_lvl)


func _on_play_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	_start_game_at_level(0)


func _on_sound_toggle_pressed() -> void:
	if save_mgr:
		save_mgr.sound_enabled = not save_mgr.sound_enabled
		save_mgr.save_data()
	if audio_mgr:
		audio_mgr.play_click()
	_update_menu_state()


func _start_game_at_level(level_index: int) -> void:
	if save_mgr:
		save_mgr.last_played_level = level_index
	get_tree().change_scene_to_file("res://scenes/game.tscn")


func _build_level_grid() -> void:
	# Clear existing children
	for child in level_grid.get_children():
		child.queue_free()

	for i in range(TOTAL_LEVELS_COUNT):
		var btn: Button = Button.new()
		btn.custom_minimum_size = Vector2(72, 72)
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.set_meta("level_index", i)
		btn.pressed.connect(_on_level_button_pressed.bind(i))
		level_grid.add_child(btn)

	_refresh_level_grid_buttons()


func _refresh_level_grid_buttons() -> void:
	var unlocked_lvl: int = save_mgr.unlocked_level if save_mgr else 0

	for child in level_grid.get_children():
		if not child is Button:
			continue
		var lvl_idx: int = child.get_meta("level_index", 0)
		var is_available: bool = (lvl_idx < AVAILABLE_LEVELS_COUNT)
		var is_unlocked: bool = is_available and (lvl_idx <= unlocked_lvl)
		var is_completed: bool = save_mgr != null and save_mgr.is_level_completed(lvl_idx)

		if is_completed:
			var record: Dictionary = save_mgr.get_level_record(lvl_idx)
			var moves: int = record.get("best_moves", 0)
			child.text = "%d\n★ %dm" % [lvl_idx + 1, moves]
			child.disabled = false
			child.modulate = Color(0.85, 1.0, 0.85) # Gentle green tint for completed
		elif is_unlocked:
			child.text = "%d\n▶" % [lvl_idx + 1]
			child.disabled = false
			child.modulate = Color(1.0, 1.0, 1.0)
		else:
			if is_available:
				child.text = "%d\n🔒" % [lvl_idx + 1]
			else:
				child.text = "%d\n—" % [lvl_idx + 1]
			child.disabled = true
			child.modulate = Color(0.55, 0.55, 0.55, 0.8)


func _on_level_button_pressed(level_index: int) -> void:
	if level_index < AVAILABLE_LEVELS_COUNT:
		if save_mgr and not save_mgr.is_level_unlocked(level_index):
			return
		_start_game_at_level(level_index)
