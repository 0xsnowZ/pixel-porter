extends SceneTree

## Headless Unit Test Suite for Game Scene (scenes/game.tscn & scenes/game.gd).
## Tests:
## - Instantiation and initial UI setup
## - Player directional facing (UP, DOWN, LEFT, RIGHT)
## - Move animation & queued move handling
## - Restart confirmation at >= 5 moves (localized)
## - Win state and celebration particle spawning & simulation
## - Board layout calculations with decorative framing, bevels, and pulsing goals

const GameScene = preload("res://scenes/game.tscn")
const LocalizationManagerScript = preload("res://scripts/localization_manager.gd")
const SaveManagerScript = preload("res://scripts/save_manager.gd")

var passes: int = 0
var fails: int = 0


func _init() -> void:
	print("\n" + "=".repeat(54))
	print("    Pixel Porter - Game Scene Headless Test Suite    ")
	print("=".repeat(54) + "\n")

	test_game_initialization_and_ui()
	test_player_facing_directions()
	test_walking_sprite_cycle()
	test_restart_confirmation_threshold()
	test_win_celebration_and_particles()
	test_layout_and_framing()
	test_undo_button_interaction()
	test_juice_and_micro_interactions()
	test_win_modal_three_star_system()

	print("\n" + "=".repeat(54))
	print("Game Scene Results: %d passed, %d failed" % [passes, fails])
	print("=".repeat(54))

	if fails > 0:
		print("FAILURE: %d game scene tests failed." % fails)
		quit(1)
	else:
		print("SUCCESS: All game scene tests passed!\n")
		quit(0)


func assert_true(cond: bool, msg: String) -> void:
	if cond:
		passes += 1
		print("  [PASS] %s" % msg)
	else:
		fails += 1
		print("  [FAIL] %s" % msg)


func assert_eq(actual: Variant, expected: Variant, msg: String) -> void:
	if actual == expected:
		passes += 1
		print("  [PASS] %s (got %s)" % [msg, str(actual)])
	else:
		fails += 1
		print("  [FAIL] %s: Expected %s but got %s" % [msg, str(expected), str(actual)])


func create_test_game(loc_node: Node = null, save_node: Node = null) -> Control:
	var game: Control = GameScene.instantiate()
	if loc_node:
		game.loc_mgr = loc_node
	if save_node:
		game.save_mgr = save_node
	root.add_child(game)
	game._ready()
	return game


func test_game_initialization_and_ui() -> void:
	print("--- Running Suite: Game Scene Initialization & UI ---")
	var loc: Node = LocalizationManagerScript.new()
	var save_mgr: Node = SaveManagerScript.new()

	var game: Control = create_test_game(loc, save_mgr)

	assert_true(game.grid != null, "Grid logic initialized")
	assert_eq(game.current_level_index, 0, "Initial level index is 0")
	assert_eq(game.level_label.text, "LEVEL 1 / 50", "Level label in EN")
	assert_true(game.restart_button.text == "Restart ↺", "Restart button localized in EN")
	assert_true(game.undo_button != null, "Undo button initialized in game")
	assert_true(game.undo_button.text == "Undo ↶", "Undo button localized in EN")
	assert_true(game.undo_button.disabled, "Undo button is disabled initially")
	assert_true(game.prev_button.disabled, "Prev button is disabled on first level")

	# Test switching language updates UI
	loc.set_language("fr")
	game._update_ui()
	assert_eq(game.level_label.text, "NIVEAU 1 / 50", "Level label in FR")
	assert_eq(game.restart_button.text, "Recommencer ↺", "Restart button localized in FR")
	assert_eq(game.undo_button.text, "Annuler ↶", "Undo button localized in FR")

	game.free()
	save_mgr.free()
	loc.free()


func test_player_facing_directions() -> void:
	print("--- Running Suite: Player Directional Facing ---")
	var game: Control = create_test_game()

	# Initial facing direction is DOWN
	assert_eq(game.player_facing_dir, Vector2i.DOWN, "Default facing direction is DOWN")

	# Move UP
	game.try_move(Vector2i.UP)
	assert_eq(game.player_facing_dir, Vector2i.UP, "Player facing updated to UP")

	# Move LEFT
	game.try_move(Vector2i.LEFT)
	assert_eq(game.player_facing_dir, Vector2i.LEFT, "Player facing updated to LEFT")

	# Move RIGHT
	game.try_move(Vector2i.RIGHT)
	assert_eq(game.player_facing_dir, Vector2i.RIGHT, "Player facing updated to RIGHT")

	# Move DOWN
	game.try_move(Vector2i.DOWN)
	assert_eq(game.player_facing_dir, Vector2i.DOWN, "Player facing updated to DOWN")

	game.free()
	
	
func test_walking_sprite_cycle() -> void:
	print("--- Running Suite: Walking Sprite Cycle & Locomotion Polish ---")
	var game: Control = create_test_game()

	# Verify all walking cycle textures are loaded
	assert_true(game.tex_player_down_w1 != null, "tex_player_down_w1 loaded")
	assert_true(game.tex_player_down_w2 != null, "tex_player_down_w2 loaded")
	assert_true(game.tex_player_up_w1 != null, "tex_player_up_w1 loaded")
	assert_true(game.tex_player_up_w2 != null, "tex_player_up_w2 loaded")
	assert_true(game.tex_player_left_w1 != null, "tex_player_left_w1 loaded")
	assert_true(game.tex_player_left_w2 != null, "tex_player_left_w2 loaded")
	assert_true(game.tex_player_right_w1 != null, "tex_player_right_w1 loaded")
	assert_true(game.tex_player_right_w2 != null, "tex_player_right_w2 loaded")

	# Initial state: idle frame (0)
	assert_eq(game.current_walk_frame, 0, "Initial walk frame is 0 (idle stance)")
	assert_eq(game.walk_step_count, 0, "Initial walk step count is 0")

	# Trigger an animation step
	game._animate_player(Vector2i(2, 3), Vector2i(2, 4))
	assert_true(game.is_animating, "Player is animating during locomotion step")
	assert_eq(game.walk_step_count, 1, "Walk step count incremented to 1")
	assert_true(game.current_walk_frame in [1, 2], "Walking frame is active (1 or 2) during stride")

	# Test reset returns to idle stance (frame 0)
	game._on_level_reset()
	assert_eq(game.current_walk_frame, 0, "Reset restores idle frame 0")
	assert_eq(game.walk_step_count, 0, "Reset zeroes walk step count")

	# Test undo returns to idle stance (frame 0)
	game.current_walk_frame = 2
	game._on_move_undone(Vector2i(2, 3), false, Vector2i.ZERO, Vector2i.ZERO)
	assert_eq(game.current_walk_frame, 0, "Undo restores idle frame 0")

	game.free()


func test_restart_confirmation_threshold() -> void:
	print("--- Running Suite: Restart Confirmation Threshold ---")
	var loc: Node = LocalizationManagerScript.new()
	var game: Control = create_test_game(loc)

	# Under 5 moves: restarts without dialog confirmation
	game.grid.moves_count = 3
	game._on_restart_pressed()
	assert_eq(game.grid.moves_count, 0, "Restarted immediately when moves < 5")

	# At >= 5 moves: dialog text is prepared and populated
	game.grid.moves_count = 6
	game._on_restart_pressed()
	assert_true(game.restart_dialog.dialog_text.contains("6"), "Restart confirmation contains move count 6")
	assert_eq(game.restart_dialog.dialog_text, "You've made 6 moves. Restart this level?", "Restart text matches EN")

	# Switch to Arabic
	loc.set_language("ar")
	game._on_restart_pressed()
	assert_true(game.restart_dialog.dialog_text.contains("6"), "AR Restart text contains move count 6")
	assert_true(game.restart_dialog.dialog_text.contains("إعادة"), "AR Restart text is in Arabic")

	game.free()
	loc.free()


func test_win_celebration_and_particles() -> void:
	print("--- Running Suite: Win Celebration & Particles ---")
	var game: Control = create_test_game()

	assert_eq(game.win_particles.size(), 0, "No particles initially")

	# Trigger celebration
	game._spawn_celebration_particles()
	assert_true(game.win_particles.size() > 30, "Celebration spawned particles (got %d)" % game.win_particles.size())

	var first_p: Dictionary = game.win_particles[0]
	assert_true(first_p.has("pos"), "Particle has position")
	assert_true(first_p.has("vel"), "Particle has velocity")
	assert_true(first_p.has("color"), "Particle has color")
	assert_true(first_p.has("life"), "Particle has life")

	# Simulate 0.1s of physics in _process
	game._process(0.1)
	assert_true(game.win_particles.size() > 0, "Particles active during lifetime")

	# Simulate past max life (3.5 seconds) to verify cleanup
	game._process(3.5)
	assert_eq(game.win_particles.size(), 0, "Particles expired and cleared after duration")

	game.free()


func test_layout_and_framing() -> void:
	print("--- Running Suite: Layout & Framing Calculations ---")
	var game: Control = create_test_game()

	# Compute layout for 720x1280 mobile portrait viewport
	game.calculate_layout(Vector2(720, 1280))
	assert_true(game.tile_size > 0.0, "Tile size calculated properly (got %f)" % game.tile_size)
	assert_true(game.grid_origin.y > 0.0, "Grid origin placed in playable area (got %s)" % str(game.grid_origin))
	assert_true(game.grid_origin.x >= 0.0, "Grid origin centered horizontally (got %s)" % str(game.grid_origin))

	game.free()


func test_undo_button_interaction() -> void:
	print("--- Running Suite: Undo Button UI Interaction ---")
	var game: Control = create_test_game()

	assert_true(game.undo_button != null, "Undo button initialized in game")
	assert_true(game.undo_button.disabled, "Undo button disabled at start")

	var init_pos: Vector2i = game.grid.player_pos

	# Make a move down
	game.try_move(Vector2i.DOWN)
	assert_eq(game.grid.moves_count, 1, "Moves count incremented to 1")
	assert_true(not game.undo_button.disabled, "Undo button enabled after move")

	# Trigger undo via button handler
	game._on_undo_pressed()
	assert_eq(game.grid.moves_count, 0, "Moves count restored to 0 after undo")
	assert_eq(game.grid.player_pos, init_pos, "Player position restored after undo")
	assert_true(game.undo_button.disabled, "Undo button disabled after rolling back all moves")

	game.free()


func test_juice_and_micro_interactions() -> void:
	print("--- Running Suite: Juice & Micro-Interactions ---")
	var game: Control = create_test_game()

	assert_eq(game.board_trauma, 0.0, "Board trauma starts at 0.0")
	assert_eq(game.dust_particles.size(), 0, "No dust particles initially")
	assert_eq(game.goal_effects.size(), 0, "No goal effects initially")

	# Push crate UP in Level 1
	game.try_move(Vector2i.UP)
	assert_true(game.dust_particles.size() > 0, "Dust particles spawned on crate push")
	assert_true(game.board_trauma > 0.0, "Board trauma added on crate push")
	assert_true(game.crate_squash.has(Vector2i(2, 1)), "Crate squash & stretch deformation tracked")

	# Process decay
	game._process(0.5)
	assert_eq(game.dust_particles.size(), 0, "Dust particles expired and cleared after duration")

	# Test goal effect spawning
	game._spawn_goal_effect(Vector2i(1, 3))
	assert_true(game.goal_effects.size() > 0, "Goal effect spawned shockwave and sparks")

	game._process(0.5)
	assert_eq(game.goal_effects.size(), 0, "Goal effects expired and cleared after duration")

	# Test trauma decay to 0
	game._process(1.0)
	assert_eq(game.board_trauma, 0.0, "Trauma decayed back to 0.0")
	assert_eq(game.board_shake_offset, Vector2.ZERO, "Board shake offset returned to Vector2.ZERO")

	game.free()


func test_win_modal_three_star_system() -> void:
	print("--- Running Suite: 3-Star Victory Modal & Stat Badges ---")
	var loc: Node = LocalizationManagerScript.new()
	var save_mgr: Node = SaveManagerScript.new()
	var game: Control = create_test_game(loc, save_mgr)

	assert_true(game.win_modal != null, "Win modal initialized")
	assert_true(game.star_1 != null, "Star 1 label initialized")
	assert_true(game.star_2 != null, "Star 2 label initialized")
	assert_true(game.star_3 != null, "Star 3 label initialized")
	assert_true(game.level_placard_label != null, "Level placard initialized")
	assert_true(game.win_retry_button != null, "Win retry button initialized")
	assert_true(game.win_blur_overlay != null, "Win blur backdrop overlay initialized")
	assert_true(not game.win_modal.visible, "Win modal hidden during normal play")
	assert_true(not game.win_blur_overlay.visible, "Win blur overlay hidden during normal play")

	# Test Retry button functionality
	game.grid.moves_count = 5
	game.win_modal.show()
	game.win_blur_overlay.show()
	assert_true(game.win_modal.visible, "Win modal shown for test")
	assert_true(game.win_blur_overlay.visible, "Win blur overlay shown for test")
	game._on_win_retry_pressed()
	assert_true(not game.win_modal.visible, "Win modal hidden on retry")
	assert_true(not game.win_blur_overlay.visible, "Win blur overlay hidden on retry")
	assert_eq(game.grid.moves_count, 0, "Level reset to 0 moves on retry")

	# Test Star rating calculation integration with save manager
	assert_eq(save_mgr.calculate_stars(0, 5), 3, "Optimal moves achieves 3 stars")
	assert_eq(save_mgr.calculate_stars(0, 10), 2, "Moderate moves achieves 2 stars")
	assert_eq(save_mgr.calculate_stars(0, 20), 1, "Completed with high moves achieves 1 star")

	game.free()
	save_mgr.free()
	loc.free()
