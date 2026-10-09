extends Control

## Main menu and Level Select controller for Pixel Porter.
## Implements PRD Section 6 flow:
## - Continue / Play navigation
## - Level select 50-level grid with locked/completed visual states
## - Sound on/off toggle persisted via SaveManager
## - Credits popup

const SaveManagerScript = preload("res://scripts/save_manager.gd")
const TOTAL_LEVELS_COUNT: int = 50
const AVAILABLE_LEVELS_COUNT: int = 50 # All 50 verified solvable levels active

var save_mgr: Node = null
var audio_mgr: Node = null
var loc_mgr: Node = null
var haptic_mgr: Node = null
var safe_area_mgr: Node = null

# Node references
@onready var main_view: VBoxContainer = $MainView
@onready var level_select_view: VBoxContainer = $LevelSelectView
@onready var credits_modal: PanelContainer = $CreditsModal

# Main View buttons
@onready var continue_btn: Button = _find_button("ContinueBtn", "MainView/Buttons/ContinueBtn")
@onready var play_btn: Button = _find_button("PlayBtn", "MainView/Buttons/PlayBtn")
@onready var level_select_btn: Button = _find_button("LevelSelectBtn", "MainView/Buttons/LevelSelectBtn")
@onready var sound_btn: Button = _find_button("SoundToggleBtn", "MainView/Buttons/SoundToggleBtn")
@onready var haptics_btn: Button = _find_button("HapticsToggleBtn", "MainView/Buttons/HapticsToggleBtn")
@onready var language_btn: Button = _find_button("LanguageBtn", "MainView/Buttons/LanguageBtn")
@onready var credits_btn: Button = _find_button("CreditsBtn", "MainView/Buttons/CreditsBtn")

# Level Select elements
@onready var level_grid: GridContainer = find_child("LevelGrid", true, false) as GridContainer
@onready var back_btn: Button = _find_button("BackBtn", "LevelSelectView/TopBar/Margin/HBox/BackBtn")
@onready var close_credits_btn: Button = _find_button("CloseCreditsBtn", "CreditsModal/VBox/CloseCreditsBtn")


func _find_button(btn_name: String, fallback_path: String) -> Button:
	var b: Button = find_child(btn_name, true, false) as Button
	if b != null:
		return b
	if has_node(fallback_path):
		return get_node(fallback_path) as Button
	return null


func _initialize_nodes() -> void:
	if main_view == null and has_node("MainView"):
		main_view = $MainView
		level_select_view = $LevelSelectView
		credits_modal = $CreditsModal
		continue_btn = _find_button("ContinueBtn", "MainView/Buttons/ContinueBtn")
		play_btn = _find_button("PlayBtn", "MainView/Buttons/PlayBtn")
		level_select_btn = _find_button("LevelSelectBtn", "MainView/Buttons/LevelSelectBtn")
		sound_btn = _find_button("SoundToggleBtn", "MainView/Buttons/SoundToggleBtn")
		haptics_btn = _find_button("HapticsToggleBtn", "MainView/Buttons/HapticsToggleBtn")
		language_btn = _find_button("LanguageBtn", "MainView/Buttons/LanguageBtn")
		credits_btn = _find_button("CreditsBtn", "MainView/Buttons/CreditsBtn")
		level_grid = find_child("LevelGrid", true, false) as GridContainer
		back_btn = _find_button("BackBtn", "LevelSelectView/TopBar/Margin/HBox/BackBtn")
		close_credits_btn = _find_button("CloseCreditsBtn", "CreditsModal/VBox/CloseCreditsBtn")


func _ready() -> void:
	_initialize_nodes()
	if is_inside_tree() and get_tree().root.has_node("SaveManager"):
		save_mgr = get_tree().root.get_node("SaveManager")
	else:
		save_mgr = SaveManagerScript.new()
		add_child(save_mgr)

	if is_inside_tree() and get_tree().root.has_node("AudioManager"):
		audio_mgr = get_tree().root.get_node("AudioManager")

	if is_inside_tree() and get_tree().root.has_node("LocalizationManager"):
		loc_mgr = get_tree().root.get_node("LocalizationManager")

	if is_inside_tree() and get_tree().root.has_node("HapticManager"):
		haptic_mgr = get_tree().root.get_node("HapticManager")

	if is_inside_tree() and get_tree().root.has_node("SafeAreaManager"):
		safe_area_mgr = get_tree().root.get_node("SafeAreaManager")
		safe_area_mgr.safe_area_changed.connect(_on_safe_area_changed)
		_apply_safe_area()

	if not continue_btn.pressed.is_connected(_on_continue_pressed):
		continue_btn.pressed.connect(_on_continue_pressed)
	if not play_btn.pressed.is_connected(_on_play_pressed):
		play_btn.pressed.connect(_on_play_pressed)
	if not level_select_btn.pressed.is_connected(_show_level_select):
		level_select_btn.pressed.connect(_show_level_select)
	if not sound_btn.pressed.is_connected(_on_sound_toggle_pressed):
		sound_btn.pressed.connect(_on_sound_toggle_pressed)
	if haptics_btn and not haptics_btn.pressed.is_connected(_on_haptics_toggle_pressed):
		haptics_btn.pressed.connect(_on_haptics_toggle_pressed)
	if not language_btn.pressed.is_connected(_on_language_pressed):
		language_btn.pressed.connect(_on_language_pressed)
	if not credits_btn.pressed.is_connected(_show_credits):
		credits_btn.pressed.connect(_show_credits)
	if not back_btn.pressed.is_connected(_show_main_view):
		back_btn.pressed.connect(_show_main_view)
	if not close_credits_btn.pressed.is_connected(_hide_credits):
		close_credits_btn.pressed.connect(_hide_credits)

	_show_main_view()
	_update_menu_state()
	_build_level_grid()

	# Ambient breathing animation on logo
	if has_node("MainView/Header/LogoRect"):
		var logo: TextureRect = $MainView/Header/LogoRect as TextureRect
		logo.pivot_offset = Vector2(90, 90)
		var tw: Tween = create_tween().set_loops()
		tw.tween_property(logo, "scale", Vector2(1.03, 1.03), 1.6).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		tw.tween_property(logo, "scale", Vector2(1.0, 1.0), 1.6).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

	# Tactile arcade button physics
	for b in [continue_btn, play_btn, level_select_btn, sound_btn, haptics_btn, language_btn, credits_btn, back_btn, close_credits_btn]:
		_attach_spring_physics(b)


func _apply_safe_area() -> void:
	if safe_area_mgr != null and has_node("LevelSelectView/TopBar/Margin"):
		var level_top_bar: MarginContainer = get_node("LevelSelectView/TopBar/Margin") as MarginContainer
		if level_top_bar != null:
			safe_area_mgr.apply_safe_area_margins(level_top_bar, 16, 12, 16, 12, true, false)


func _on_safe_area_changed(_insets: Dictionary) -> void:
	_apply_safe_area()


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
	var has_progress: bool = (unlocked_lvl > 0 or (save_mgr and save_mgr.is_level_completed(0)))
	var is_sound_on: bool = save_mgr.sound_enabled if save_mgr else true
	var is_haptics_on: bool = save_mgr.haptics_enabled if save_mgr else true

	if loc_mgr:
		if has_progress:
			continue_btn.visible = true
			continue_btn.text = loc_mgr.tr_text("MENU_CONTINUE", [last_lvl + 1])
			play_btn.text = loc_mgr.tr_text("MENU_NEW_GAME")
		else:
			continue_btn.visible = false
			play_btn.text = loc_mgr.tr_text("MENU_PLAY")

		var sound_status: String = loc_mgr.tr_text("MENU_SOUND_ON" if is_sound_on else "MENU_SOUND_OFF")
		sound_btn.text = loc_mgr.tr_text("MENU_SOUND", [sound_status])

		if haptics_btn:
			var haptic_status: String = loc_mgr.tr_text("MENU_HAPTICS_ON" if is_haptics_on else "MENU_HAPTICS_OFF")
			haptics_btn.text = loc_mgr.tr_text("MENU_HAPTICS", [haptic_status])

		language_btn.text = loc_mgr.tr_text("MENU_LANGUAGE", [loc_mgr.get_language_display_name()])
		level_select_btn.text = loc_mgr.tr_text("MENU_LEVEL_SELECT")
		credits_btn.text = loc_mgr.tr_text("MENU_CREDITS")
		back_btn.text = loc_mgr.tr_text("BTN_BACK")
		$LevelSelectView/TopBar/Margin/HBox/Title.text = loc_mgr.tr_text("LEVEL_SELECT_TITLE")
		$CreditsModal/VBox/Title.text = loc_mgr.tr_text("CREDITS_TITLE")
		$CreditsModal/VBox/Description.text = loc_mgr.tr_text("CREDITS_BODY")
		close_credits_btn.text = loc_mgr.tr_text("BTN_CLOSE")
	else:
		if has_progress:
			continue_btn.visible = true
			continue_btn.text = "CONTINUE (LEVEL %d)" % (last_lvl + 1)
			play_btn.text = "NEW GAME"
		else:
			continue_btn.visible = false
			play_btn.text = "PLAY"
		sound_btn.text = "SOUND: %s" % ("ON" if is_sound_on else "OFF")
		if haptics_btn:
			haptics_btn.text = "HAPTICS: %s" % ("ON" if is_haptics_on else "OFF")
		language_btn.text = "LANGUAGE: English"


func _on_language_pressed() -> void:
	if loc_mgr:
		loc_mgr.cycle_language()
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	_update_menu_state()
	_refresh_level_grid_buttons()


func _on_continue_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	var target_lvl: int = save_mgr.last_played_level if save_mgr else 0
	_start_game_at_level(target_lvl)


func _on_play_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	_start_game_at_level(0)


func _on_sound_toggle_pressed() -> void:
	if save_mgr:
		save_mgr.sound_enabled = not save_mgr.sound_enabled
		save_mgr.save_data()
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	_update_menu_state()


func _on_haptics_toggle_pressed() -> void:
	if save_mgr:
		save_mgr.haptics_enabled = not save_mgr.haptics_enabled
		save_mgr.save_data()
		if haptic_mgr:
			haptic_mgr.set_haptic_enabled(save_mgr.haptics_enabled)
	elif haptic_mgr:
		haptic_mgr.toggle_haptics()

	if save_mgr and save_mgr.haptics_enabled and haptic_mgr:
		haptic_mgr.vibrate_click()

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
		_attach_spring_physics(btn)
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
			child.theme_type_variation = &"SuccessButton"
			child.modulate = Color(1.0, 1.0, 1.0)
		elif is_unlocked:
			child.text = "%d\n▶" % [lvl_idx + 1]
			child.disabled = false
			child.theme_type_variation = &"PrimaryButton"
			child.modulate = Color(1.0, 1.0, 1.0)
		else:
			if is_available:
				child.text = "%d\n🔒" % [lvl_idx + 1]
			else:
				child.text = "%d\n—" % [lvl_idx + 1]
			child.disabled = true
			child.theme_type_variation = &"Button"
			child.modulate = Color(0.65, 0.65, 0.70, 0.85)


func _on_level_button_pressed(level_index: int) -> void:
	if level_index < AVAILABLE_LEVELS_COUNT:
		if save_mgr and not save_mgr.is_level_unlocked(level_index):
			return
		_start_game_at_level(level_index)


func _attach_spring_physics(btn: Button) -> void:
	if btn == null:
		return
	btn.pivot_offset = btn.size / 2.0
	btn.button_down.connect(func():
		btn.pivot_offset = btn.size / 2.0
		var tw: Tween = create_tween().set_trans(Tween.TRANS_QUAD).set_ease(Tween.EASE_OUT)
		tw.tween_property(btn, "scale", Vector2(0.94, 0.94), 0.07)
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
