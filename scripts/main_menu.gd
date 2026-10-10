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
@onready var settings_modal: PanelContainer = find_child("SettingsModal", true, false) as PanelContainer

# Main View buttons
@onready var continue_btn: Button = _find_button("ContinueBtn", "MainView/Buttons/ContinueBtn")
@onready var play_btn: Button = _find_button("PlayBtn", "MainView/Buttons/PlayBtn")
@onready var level_select_btn: Button = _find_button("LevelSelectBtn", "MainView/Buttons/LevelSelectBtn")
@onready var settings_btn: Button = _find_button("SettingsBtn", "MainView/Buttons/SettingsBtn")
@onready var sound_btn: Button = _find_button("SoundToggleBtn", "SettingsModal/Margin/VBox/SfxBox/SoundToggleBtn")
@onready var haptics_btn: Button = _find_button("HapticsToggleBtn", "MainView/Buttons/HapticsToggleBtn")
@onready var language_btn: Button = _find_button("LanguageBtn", "MainView/Buttons/LanguageBtn")
@onready var credits_btn: Button = _find_button("CreditsBtn", "MainView/Buttons/CreditsBtn")

# Settings elements
@onready var music_vol_label: Label = find_child("MusicVolLabel", true, false) as Label
@onready var music_slider: HSlider = find_child("MusicSlider", true, false) as HSlider
@onready var music_toggle_btn: Button = _find_button("MusicToggleBtn", "SettingsModal/Margin/VBox/MusicBox/MusicToggleBtn")
@onready var track_label: Label = find_child("TrackLabel", true, false) as Label
@onready var track_cycle_btn: Button = _find_button("TrackCycleBtn", "SettingsModal/Margin/VBox/TrackBox/TrackCycleBtn")
@onready var sfx_vol_label: Label = find_child("SfxVolLabel", true, false) as Label
@onready var sfx_slider: HSlider = find_child("SfxSlider", true, false) as HSlider
@onready var close_settings_btn: Button = _find_button("CloseSettingsBtn", "SettingsModal/Margin/VBox/CloseSettingsBtn")
@onready var control_mode_btn: Button = _find_button("ControlModeBtn", "SettingsModal/Margin/VBox/ControlBox/ControlModeBtn")

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
		settings_modal = find_child("SettingsModal", true, false) as PanelContainer
		continue_btn = _find_button("ContinueBtn", "MainView/Buttons/ContinueBtn")
		play_btn = _find_button("PlayBtn", "MainView/Buttons/PlayBtn")
		level_select_btn = _find_button("LevelSelectBtn", "MainView/Buttons/LevelSelectBtn")
		settings_btn = _find_button("SettingsBtn", "MainView/Buttons/SettingsBtn")
		sound_btn = _find_button("SoundToggleBtn", "SettingsModal/Margin/VBox/SfxBox/SoundToggleBtn")
		haptics_btn = _find_button("HapticsToggleBtn", "MainView/Buttons/HapticsToggleBtn")
		language_btn = _find_button("LanguageBtn", "MainView/Buttons/LanguageBtn")
		credits_btn = _find_button("CreditsBtn", "MainView/Buttons/CreditsBtn")
		music_vol_label = find_child("MusicVolLabel", true, false) as Label
		music_slider = find_child("MusicSlider", true, false) as HSlider
		music_toggle_btn = _find_button("MusicToggleBtn", "SettingsModal/Margin/VBox/MusicBox/MusicToggleBtn")
		track_label = find_child("TrackLabel", true, false) as Label
		track_cycle_btn = _find_button("TrackCycleBtn", "SettingsModal/Margin/VBox/TrackBox/TrackCycleBtn")
		sfx_vol_label = find_child("SfxVolLabel", true, false) as Label
		sfx_slider = find_child("SfxSlider", true, false) as HSlider
		close_settings_btn = _find_button("CloseSettingsBtn", "SettingsModal/Margin/VBox/CloseSettingsBtn")
		control_mode_btn = _find_button("ControlModeBtn", "SettingsModal/Margin/VBox/ControlBox/ControlModeBtn")
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
	if sound_btn and not sound_btn.pressed.is_connected(_on_sound_toggle_pressed):
		sound_btn.pressed.connect(_on_sound_toggle_pressed)
	if haptics_btn and not haptics_btn.pressed.is_connected(_on_haptics_toggle_pressed):
		haptics_btn.pressed.connect(_on_haptics_toggle_pressed)
	if not language_btn.pressed.is_connected(_on_language_pressed):
		language_btn.pressed.connect(_on_language_pressed)
	if not credits_btn.pressed.is_connected(_show_credits):
		credits_btn.pressed.connect(_show_credits)
	if settings_btn and not settings_btn.pressed.is_connected(_show_settings):
		settings_btn.pressed.connect(_show_settings)
	if close_settings_btn and not close_settings_btn.pressed.is_connected(_hide_settings):
		close_settings_btn.pressed.connect(_hide_settings)
	if control_mode_btn and not control_mode_btn.pressed.is_connected(_on_control_mode_pressed):
		control_mode_btn.pressed.connect(_on_control_mode_pressed)
	if music_slider and not music_slider.value_changed.is_connected(_on_music_slider_changed):
		music_slider.value_changed.connect(_on_music_slider_changed)
	if music_toggle_btn and not music_toggle_btn.pressed.is_connected(_on_music_toggle_pressed):
		music_toggle_btn.pressed.connect(_on_music_toggle_pressed)
	if track_cycle_btn and not track_cycle_btn.pressed.is_connected(_on_track_cycle_pressed):
		track_cycle_btn.pressed.connect(_on_track_cycle_pressed)
	if sfx_slider and not sfx_slider.value_changed.is_connected(_on_sfx_slider_changed):
		sfx_slider.value_changed.connect(_on_sfx_slider_changed)
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
		logo.pivot_offset = Vector2(115, 115)
		var tw: Tween = create_tween().set_loops()
		tw.tween_property(logo, "scale", Vector2(1.03, 1.03), 1.6).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)
		tw.tween_property(logo, "scale", Vector2(1.0, 1.0), 1.6).set_trans(Tween.TRANS_SINE).set_ease(Tween.EASE_IN_OUT)

	# Tactile arcade button physics
	for b in [continue_btn, play_btn, level_select_btn, settings_btn, sound_btn, haptics_btn, language_btn, credits_btn, back_btn, close_credits_btn, close_settings_btn, music_toggle_btn, track_cycle_btn, control_mode_btn]:
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
	if settings_modal:
		settings_modal.hide()
	_update_menu_state()


func _show_level_select() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	main_view.hide()
	level_select_view.show()
	credits_modal.hide()
	if settings_modal:
		settings_modal.hide()
	_refresh_level_grid_buttons()


func _show_credits() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if settings_modal:
		settings_modal.hide()
	credits_modal.show()


func _hide_credits() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	credits_modal.hide()


func _show_settings() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	credits_modal.hide()
	if settings_modal:
		_update_settings_ui()
		settings_modal.show()


func _hide_settings() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if settings_modal:
		settings_modal.hide()
	if save_mgr and save_mgr.has_method("save_data"):
		save_mgr.save_data()
	_update_menu_state()


func _update_settings_ui() -> void:
	if save_mgr == null:
		return

	var m_vol: float = save_mgr.music_volume if "music_volume" in save_mgr else 0.7
	var s_vol: float = save_mgr.sfx_volume if "sfx_volume" in save_mgr else 0.8
	var m_on: bool = save_mgr.music_enabled if "music_enabled" in save_mgr else true
	var track_idx: int = save_mgr.selected_bgm_track if "selected_bgm_track" in save_mgr else 0

	if music_slider:
		music_slider.set_value_no_signal(m_vol)
	if music_vol_label:
		if loc_mgr:
			music_vol_label.text = loc_mgr.tr_text("SETTINGS_MUSIC_VOL", [int(m_vol * 100)])
		else:
			music_vol_label.text = "MUSIC: %d%%" % int(m_vol * 100)

	if music_toggle_btn:
		var status_text: String = "ON" if m_on else "OFF"
		music_toggle_btn.text = "MUSIC: " + status_text

	if sfx_slider:
		sfx_slider.set_value_no_signal(s_vol)
	if sfx_vol_label:
		if loc_mgr:
			sfx_vol_label.text = loc_mgr.tr_text("SETTINGS_SFX_VOL", [int(s_vol * 100)])
		else:
			sfx_vol_label.text = "SOUND FX: %d%%" % int(s_vol * 100)

	if track_cycle_btn:
		var track_name: String = "Warehouse Chill" if track_idx == 0 else "Industrial Pulse"
		if loc_mgr:
			var key: String = "TRACK_LOFI" if track_idx == 0 else "TRACK_INDUSTRIAL"
			track_name = loc_mgr.tr_text(key)
		track_cycle_btn.text = "♪ " + track_name + " ▾"

	if control_mode_btn:
		var mode_name: String = save_mgr.get_control_scheme_name() if save_mgr and save_mgr.has_method("get_control_scheme_name") else "SWIPE"
		var mode_key: String = "CONTROL_" + mode_name.replace("-", "")
		var mode_text: String = loc_mgr.tr_text(mode_key) if loc_mgr else mode_name
		control_mode_btn.text = loc_mgr.tr_text("SETTINGS_CONTROLS", [mode_text]) if loc_mgr else "CONTROLS: %s" % mode_name

	if close_settings_btn and loc_mgr:
		close_settings_btn.text = loc_mgr.tr_text("SETTINGS_CLOSE")


func _on_music_slider_changed(value: float) -> void:
	if audio_mgr and audio_mgr.has_method("set_music_volume"):
		audio_mgr.set_music_volume(value)
	elif save_mgr:
		save_mgr.music_volume = value
	if music_vol_label:
		if loc_mgr:
			music_vol_label.text = loc_mgr.tr_text("SETTINGS_MUSIC_VOL", [int(value * 100)])
		else:
			music_vol_label.text = "MUSIC: %d%%" % int(value * 100)


func _on_sfx_slider_changed(value: float) -> void:
	if audio_mgr and audio_mgr.has_method("set_sfx_volume"):
		audio_mgr.set_sfx_volume(value)
	elif save_mgr:
		save_mgr.sfx_volume = value
	if sfx_vol_label:
		if loc_mgr:
			sfx_vol_label.text = loc_mgr.tr_text("SETTINGS_SFX_VOL", [int(value * 100)])
		else:
			sfx_vol_label.text = "SOUND FX: %d%%" % int(value * 100)


func _on_music_toggle_pressed() -> void:
	var current: bool = save_mgr.music_enabled if save_mgr and "music_enabled" in save_mgr else true
	var new_val: bool = not current
	if audio_mgr and audio_mgr.has_method("set_music_enabled"):
		audio_mgr.set_music_enabled(new_val)
	elif save_mgr:
		save_mgr.music_enabled = new_val
	_update_settings_ui()


func _on_control_mode_pressed() -> void:
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
	_update_settings_ui()


func _on_track_cycle_pressed() -> void:
	var current: int = save_mgr.selected_bgm_track if save_mgr and "selected_bgm_track" in save_mgr else 0
	var next_track: int = (current + 1) % 2
	if audio_mgr and audio_mgr.has_method("switch_music_track"):
		audio_mgr.switch_music_track(next_track)
	elif save_mgr:
		save_mgr.selected_bgm_track = next_track
	_update_settings_ui()


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

		if sound_btn:
			var sound_status: String = loc_mgr.tr_text("MENU_SOUND_ON" if is_sound_on else "MENU_SOUND_OFF")
			sound_btn.text = loc_mgr.tr_text("MENU_SOUND", [sound_status])

		if haptics_btn:
			var haptic_status: String = loc_mgr.tr_text("MENU_HAPTICS_ON" if is_haptics_on else "MENU_HAPTICS_OFF")
			haptics_btn.text = loc_mgr.tr_text("MENU_HAPTICS", [haptic_status])

		if settings_btn:
			settings_btn.text = loc_mgr.tr_text("MENU_SETTINGS")
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
		if settings_btn:
			settings_btn.text = "SETTINGS ⚙"
		if sound_btn:
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
		btn.custom_minimum_size = Vector2(86, 86)
		btn.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		btn.add_theme_font_size_override("font_size", 14)
		btn.set_meta("level_index", i)
		btn.pressed.connect(_on_level_button_pressed.bind(i))
		_attach_spring_physics(btn)
		level_grid.add_child(btn)

	_refresh_level_grid_buttons()


func _refresh_level_grid_buttons() -> void:
	var unlocked_lvl: int = save_mgr.unlocked_level if save_mgr else 0
	var total_stars: int = save_mgr.get_total_stars() if save_mgr != null else 0

	if has_node("LevelSelectView/TopBar/Margin/HBox/TotalStarsLabel") and save_mgr != null:
		var stars_lbl = get_node("LevelSelectView/TopBar/Margin/HBox/TotalStarsLabel") as Label
		stars_lbl.text = "★ %d/150" % total_stars

	# Update Campaign Banner card if present
	var pb: ProgressBar = find_child("ProgressBar", true, false) as ProgressBar
	if pb != null:
		pb.max_value = 150.0
		pb.value = float(total_stars)

	var stars_count_lbl: Label = find_child("StarsCountLabel", true, false) as Label
	if stars_count_lbl != null:
		stars_count_lbl.text = "★ %d / 150 Stars Collected" % total_stars

	var completion_lbl: Label = find_child("CompletionLabel", true, false) as Label
	if completion_lbl != null and save_mgr != null:
		var completed_count: int = 0
		for i in range(TOTAL_LEVELS_COUNT):
			if save_mgr.is_level_completed(i):
				completed_count += 1
		var pct: int = int((float(completed_count) / float(TOTAL_LEVELS_COUNT)) * 100.0)
		completion_lbl.text = "%d/50 Cleared • %d%%" % [completed_count, pct]

	for child in level_grid.get_children():
		if not child is Button:
			continue
		var lvl_idx: int = child.get_meta("level_index", 0)
		var is_available: bool = (lvl_idx < AVAILABLE_LEVELS_COUNT)
		var is_unlocked: bool = is_available and (lvl_idx <= unlocked_lvl)
		var is_completed: bool = save_mgr != null and save_mgr.is_level_completed(lvl_idx)

		if is_completed:
			var record: Dictionary = save_mgr.get_level_record(lvl_idx)
			var stars: int = record.get("stars", 1)
			var star_str: String = ""
			match stars:
				3: star_str = "★★★"
				2: star_str = "★★☆"
				1: star_str = "★☆☆"
				_: star_str = "★"
			child.text = "%d\n%s" % [lvl_idx + 1, star_str]
			child.disabled = false
			child.theme_type_variation = &"LevelBtnCompleted"
			child.modulate = Color(1.0, 1.0, 1.0)
		elif is_unlocked:
			child.text = "%d\n▶" % [lvl_idx + 1]
			child.disabled = false
			child.theme_type_variation = &"LevelBtnCurrent"
			child.modulate = Color(1.0, 1.0, 1.0)
		else:
			if is_available:
				child.text = "%d\n🔒" % [lvl_idx + 1]
			else:
				child.text = "%d\n—" % [lvl_idx + 1]
			child.disabled = true
			child.theme_type_variation = &"LevelBtnLocked"
			child.modulate = Color(1.0, 1.0, 1.0)


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
