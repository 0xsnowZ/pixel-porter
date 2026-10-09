extends SceneTree

## Headless test script for Main Menu & Level Select flow (Pixel Porter PRD v1.md Section 6).
## Run via: godot --headless --path . -s tests/test_main_menu.gd

const MainMenuScene = preload("res://scenes/main_menu.tscn")
const SaveManagerScript = preload("res://scripts/save_manager.gd")
const TEST_SAVE_PATH: String = "user://test_main_menu_save.json"

var _passed_suites: int = 0
var _failed_suites: int = 0
var _total_assertions: int = 0
var _failed_assertions: int = 0


func _init() -> void:
	print("==================================================")
	print("    Pixel Porter - Main Menu Headless Tests      ")
	print("==================================================")

	_cleanup_test_file()

	run_suite("Main Menu Initialization & Views", test_menu_initialization)
	run_suite("Progression Reactive State (Continue/Play)", test_continue_and_play_state)
	run_suite("50-Level Select Grid & Status Badges", test_level_select_grid)
	run_suite("Sound Toggle & Credits Modal", test_sound_and_credits)
	run_suite("Settings Modal & Audio Sliders", test_settings_modal_and_sliders)

	_cleanup_test_file()

	print("\n==================================================")
	print("Test Suites: %d passed, %d failed" % [_passed_suites, _failed_suites])
	print("Assertions : %d total, %d failed" % [_total_assertions, _failed_assertions])
	print("==================================================")

	if _failed_assertions > 0 or _failed_suites > 0:
		printerr("FAILED: Test suite had failures.")
		quit(1)
	else:
		print("SUCCESS: All Main Menu tests passed successfully!")
		quit(0)


func _cleanup_test_file() -> void:
	if FileAccess.file_exists(TEST_SAVE_PATH):
		DirAccess.remove_absolute(TEST_SAVE_PATH)


func run_suite(suite_name: String, test_callable: Callable) -> void:
	print("\n--- Running Suite: %s ---" % suite_name)
	var prev_failures: int = _failed_assertions
	test_callable.call()
	if _failed_assertions == prev_failures:
		_passed_suites += 1
	else:
		_failed_suites += 1


func assert_true(condition: bool, message: String) -> void:
	_total_assertions += 1
	if condition:
		print("  [PASS] %s" % message)
	else:
		_failed_assertions += 1
		printerr("  [FAIL] Assertion failed: %s" % message)


func assert_false(condition: bool, message: String) -> void:
	assert_true(not condition, message)


func assert_equal(actual: Variant, expected: Variant, message: String) -> void:
	_total_assertions += 1
	if actual == expected:
		print("  [PASS] %s (got %s)" % [message, str(actual)])
	else:
		_failed_assertions += 1
		printerr("  [FAIL] %s - Expected: %s, Got: %s" % [message, str(expected), str(actual)])


func create_test_menu() -> Control:
	var menu: Control = MainMenuScene.instantiate()
	root.add_child(menu)
	menu._ready()
	return menu


func test_menu_initialization() -> void:
	var menu: Control = create_test_menu()

	assert_true(menu.main_view.visible, "Main view is visible by default")
	assert_false(menu.level_select_view.visible, "Level select view is hidden by default")
	assert_false(menu.credits_modal.visible, "Credits modal is hidden by default")

	# View switching
	menu._show_level_select()
	assert_false(menu.main_view.visible, "Main view hidden when level select is shown")
	assert_true(menu.level_select_view.visible, "Level select visible when activated")

	menu._show_main_view()
	assert_true(menu.main_view.visible, "Main view restored on back")
	assert_false(menu.level_select_view.visible, "Level select hidden on back")

	menu.queue_free()


func test_continue_and_play_state() -> void:
	var menu: Control = create_test_menu()

	# 1. Fresh state: no completed levels
	menu.save_mgr.reset_all_progress(TEST_SAVE_PATH)
	menu._update_menu_state()
	assert_false(menu.continue_btn.visible, "Continue button hidden on fresh game")
	assert_equal(menu.play_btn.text, "PLAY", "Play button text is 'PLAY'")

	# 2. Player has completed level 0 and unlocked level 1
	menu.save_mgr.record_level_completion(0, 10, 5, TEST_SAVE_PATH)
	menu.save_mgr.last_played_level = 0
	menu._update_menu_state()

	assert_true(menu.continue_btn.visible, "Continue button visible after completing a level")
	assert_true("LEVEL 1" in menu.continue_btn.text, "Continue button indicates Level 1")
	assert_equal(menu.play_btn.text, "NEW GAME", "Play button text switches to 'NEW GAME'")

	menu.queue_free()


func test_level_select_grid() -> void:
	var menu: Control = create_test_menu()

	var grid_buttons = menu.level_grid.get_children()
	assert_equal(grid_buttons.size(), 50, "Level grid contains 50 level buttons as required by PRD")

	# Set level 0 as completed, level 1 as unlocked, level 2 as available
	menu.save_mgr.reset_all_progress(TEST_SAVE_PATH)
	menu.save_mgr.record_level_completion(0, 7, 3, TEST_SAVE_PATH)
	menu._refresh_level_grid_buttons()

	var btn0: Button = grid_buttons[0] as Button
	assert_false(btn0.disabled, "Level 1 button is enabled (completed)")
	assert_true("★" in btn0.text, "Level 1 button shows completed star badge")
	assert_true("7m" in btn0.text, "Level 1 button shows best moves record (7m)")

	var btn1: Button = grid_buttons[1] as Button
	assert_false(btn1.disabled, "Level 2 button is enabled (current unlocked)")
	assert_true("▶" in btn1.text, "Level 2 button shows playable arrow indicator")

	var btn2: Button = grid_buttons[2] as Button
	assert_true(btn2.disabled, "Level 3 button is locked until level 2 completed")
	assert_true("🔒" in btn2.text, "Level 3 button shows lock indicator")

	var btn10: Button = grid_buttons[10] as Button
	assert_true(btn10.disabled, "Level 11 button is locked until unlocked")
	assert_true("🔒" in btn10.text, "Level 11 button shows lock indicator")

	menu.queue_free()


func test_sound_and_credits() -> void:
	var menu: Control = create_test_menu()

	# Sound toggle
	menu.save_mgr.sound_enabled = true
	menu._update_menu_state()
	assert_equal(menu.sound_btn.text, "SOUND: ON", "Sound button displays 'SOUND: ON'")

	menu._on_sound_toggle_pressed()
	assert_false(menu.save_mgr.sound_enabled, "Sound setting toggled to false")
	assert_equal(menu.sound_btn.text, "SOUND: OFF", "Sound button displays 'SOUND: OFF'")

	menu._on_sound_toggle_pressed()
	assert_true(menu.save_mgr.sound_enabled, "Sound setting toggled back to true")
	assert_equal(menu.sound_btn.text, "SOUND: ON", "Sound button displays 'SOUND: ON'")

	# Haptics toggle
	menu.save_mgr.haptics_enabled = true
	menu._update_menu_state()
	assert_true(menu.haptics_btn != null, "Haptics button exists in MainMenu")
	assert_equal(menu.haptics_btn.text, "HAPTICS: ON", "Haptics button displays 'HAPTICS: ON'")

	menu._on_haptics_toggle_pressed()
	assert_false(menu.save_mgr.haptics_enabled, "Haptics setting toggled to false")
	assert_equal(menu.haptics_btn.text, "HAPTICS: OFF", "Haptics button displays 'HAPTICS: OFF'")

	menu._on_haptics_toggle_pressed()
	assert_true(menu.save_mgr.haptics_enabled, "Haptics setting toggled back to true")
	assert_equal(menu.haptics_btn.text, "HAPTICS: ON", "Haptics button displays 'HAPTICS: ON'")

	# Credits modal
	menu._show_credits()
	assert_true(menu.credits_modal.visible, "Credits modal is visible after _show_credits")

	menu._hide_credits()
	assert_false(menu.credits_modal.visible, "Credits modal is hidden after _hide_credits")

	menu.queue_free()


func test_settings_modal_and_sliders() -> void:
	var menu: Control = create_test_menu()

	# 1. Elements exist
	assert_true(menu.settings_btn != null, "Settings button exists on MainMenu")
	assert_true(menu.settings_modal != null, "Settings modal exists")
	assert_false(menu.settings_modal.visible, "Settings modal is hidden initially")
	assert_true(menu.music_slider != null, "Music slider exists")
	assert_true(menu.sfx_slider != null, "SFX slider exists")
	assert_true(menu.track_cycle_btn != null, "Track cycle button exists")

	# 2. Open / Close modal
	menu._show_settings()
	assert_true(menu.settings_modal.visible, "Settings modal opens via _show_settings")

	# 3. Sliders update save_mgr
	menu._on_music_slider_changed(0.45)
	assert_equal(menu.save_mgr.music_volume, 0.45, "Music volume updated via slider to 0.45")
	assert_true("45%" in menu.music_vol_label.text, "Music label reflects 45%")

	menu._on_sfx_slider_changed(0.85)
	assert_equal(menu.save_mgr.sfx_volume, 0.85, "SFX volume updated via slider to 0.85")
	assert_true("85%" in menu.sfx_vol_label.text, "SFX label reflects 85%")

	# 4. Track cycle button
	menu.save_mgr.selected_bgm_track = 0
	menu._update_settings_ui()
	assert_true("Warehouse Chill" in menu.track_cycle_btn.text, "Track button shows Warehouse Chill")

	menu._on_track_cycle_pressed()
	assert_equal(menu.save_mgr.selected_bgm_track, 1, "Track cycled to 1 (Industrial Pulse)")
	assert_true("Industrial Pulse" in menu.track_cycle_btn.text, "Track button shows Industrial Pulse")

	# 5. Music toggle
	menu.save_mgr.music_enabled = true
	menu._on_music_toggle_pressed()
	assert_false(menu.save_mgr.music_enabled, "Music toggled to false")
	assert_equal(menu.music_toggle_btn.text, "MUSIC: OFF", "Music toggle button text is OFF")

	menu._on_music_toggle_pressed()
	assert_true(menu.save_mgr.music_enabled, "Music toggled back to true")
	assert_equal(menu.music_toggle_btn.text, "MUSIC: ON", "Music toggle button text is ON")

	# Close modal
	menu._hide_settings()
	assert_false(menu.settings_modal.visible, "Settings modal hidden via _hide_settings")

	menu.queue_free()
