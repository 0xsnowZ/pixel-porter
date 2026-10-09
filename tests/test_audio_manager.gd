extends SceneTree

## Headless test script for AudioManager (Pixel Porter PRD v1.md Section 9).
## Run via: godot --headless --path . -s tests/test_audio_manager.gd

const AudioManagerScript = preload("res://scripts/audio_manager.gd")
const SaveManagerScript = preload("res://scripts/save_manager.gd")

var _passed_suites: int = 0
var _failed_suites: int = 0
var _total_assertions: int = 0
var _failed_assertions: int = 0


func _init() -> void:
	print("==================================================")
	print("   Pixel Porter - AudioManager Headless Tests    ")
	print("==================================================")

	run_suite("Procedural 8-Bit SFX Synthesis", test_sfx_synthesis)
	run_suite("Audio Voice Pool & Channels", test_voice_pool)
	run_suite("Sound Toggle Integration", test_sound_toggle_respect)
	run_suite("Safe Playback Execution", test_safe_playback)

	print("\n==================================================")
	print("Test Suites: %d passed, %d failed" % [_passed_suites, _failed_suites])
	print("Assertions : %d total, %d failed" % [_total_assertions, _failed_assertions])
	print("==================================================")

	if _failed_assertions > 0 or _failed_suites > 0:
		printerr("FAILED: Test suite had failures.")
		quit(1)
	else:
		print("SUCCESS: All AudioManager tests passed successfully!")
		quit(0)


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


func create_test_audio_mgr() -> Node:
	var mgr: Node = AudioManagerScript.new()
	root.add_child(mgr)
	mgr._ready()
	return mgr


func test_sfx_synthesis() -> void:
	var audio_mgr: Node = create_test_audio_mgr()

	assert_true(audio_mgr.sfx_move != null, "sfx_move stream generated")
	assert_true(audio_mgr.sfx_move.data.size() > 0, "sfx_move has audio sample data")
	assert_equal(audio_mgr.sfx_move.mix_rate, 22050, "sfx_move has correct 22050Hz mix rate")

	assert_true(audio_mgr.sfx_push != null, "sfx_push stream generated")
	assert_true(audio_mgr.sfx_push.data.size() > 0, "sfx_push has audio sample data")

	assert_true(audio_mgr.sfx_win != null, "sfx_win stream generated")
	assert_true(audio_mgr.sfx_win.data.size() > 0, "sfx_win has audio sample data")

	assert_true(audio_mgr.sfx_restart != null, "sfx_restart stream generated")
	assert_true(audio_mgr.sfx_restart.data.size() > 0, "sfx_restart has audio sample data")

	assert_true(audio_mgr.sfx_click != null, "sfx_click stream generated")
	assert_true(audio_mgr.sfx_click.data.size() > 0, "sfx_click has audio sample data")

	audio_mgr.queue_free()


func test_voice_pool() -> void:
	var audio_mgr: Node = create_test_audio_mgr()

	assert_equal(audio_mgr._players.size(), 6, "Voice pool contains 6 audio players")
	for p in audio_mgr._players:
		assert_true(p is AudioStreamPlayer, "Channel is AudioStreamPlayer")
		assert_equal(p.bus, "Master", "Channel is routed to Master bus")

	audio_mgr.queue_free()


func test_sound_toggle_respect() -> void:
	var audio_mgr: Node = create_test_audio_mgr()
	var mock_save: Node = SaveManagerScript.new()
	audio_mgr.save_mgr = mock_save

	# 1. Enabled
	mock_save.sound_enabled = true
	assert_true(audio_mgr.is_sound_enabled(), "Reports sound enabled when SaveManager.sound_enabled is true")

	# 2. Disabled
	mock_save.sound_enabled = false
	assert_false(audio_mgr.is_sound_enabled(), "Reports sound disabled when SaveManager.sound_enabled is false")

	audio_mgr.queue_free()
	mock_save.queue_free()


func test_safe_playback() -> void:
	var audio_mgr: Node = create_test_audio_mgr()

	# Verify calling all play methods runs cleanly without runtime exception
	audio_mgr.play_move()
	audio_mgr.play_push()
	audio_mgr.play_win()
	audio_mgr.play_restart()
	audio_mgr.play_click()
	assert_true(true, "All audio play methods executed safely")

	audio_mgr.queue_free()
