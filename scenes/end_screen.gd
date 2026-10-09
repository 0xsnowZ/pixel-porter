extends Control

## End Screen controller shown after completing all 50 levels (PRD Section 6).
## Displays:
## - "Thank you for playing!" message
## - Total campaign statistics (levels solved, total best moves, total pushes)
## - "More levels coming soon!" teaser
## - Celebratory victory particles and fanfare
## - Multi-language localization (EN, FR, AR)
## - Replay / Level select and Main Menu navigation buttons

const SaveManagerScript = preload("res://scripts/save_manager.gd")

var save_mgr: Node = null
var audio_mgr: Node = null
var loc_mgr: Node = null
var haptic_mgr: Node = null

var celebration_particles: Array[Dictionary] = []
var particle_spawn_timer: float = 0.0

@onready var title_label: Label = $Margin/VBox/Title
@onready var thanks_label: Label = $Margin/VBox/StatsPanel/PanelMargin/PanelVBox/ThanksLabel
@onready var stats_label: Label = $Margin/VBox/StatsPanel/PanelMargin/PanelVBox/SummaryStatsLabel
@onready var more_levels_label: Label = $Margin/VBox/StatsPanel/PanelMargin/PanelVBox/MoreLevelsLabel
@onready var level_select_btn: Button = $Margin/VBox/Actions/LevelSelectBtn
@onready var menu_btn: Button = $Margin/VBox/Actions/MenuBtn


func _initialize_nodes() -> void:
	if title_label == null and has_node("Margin/VBox/Title"):
		title_label = $Margin/VBox/Title
		thanks_label = $Margin/VBox/StatsPanel/PanelMargin/PanelVBox/ThanksLabel
		stats_label = $Margin/VBox/StatsPanel/PanelMargin/PanelVBox/SummaryStatsLabel
		more_levels_label = $Margin/VBox/StatsPanel/PanelMargin/PanelVBox/MoreLevelsLabel
		level_select_btn = $Margin/VBox/Actions/LevelSelectBtn
		menu_btn = $Margin/VBox/Actions/MenuBtn


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

	if haptic_mgr == null and is_inside_tree() and get_tree().root.has_node("HapticManager"):
		haptic_mgr = get_tree().root.get_node("HapticManager")

	if not level_select_btn.pressed.is_connected(_on_level_select_pressed):
		level_select_btn.pressed.connect(_on_level_select_pressed)
	if not menu_btn.pressed.is_connected(_on_menu_pressed):
		menu_btn.pressed.connect(_on_menu_pressed)

	_update_ui()
	_spawn_initial_confetti()

	if audio_mgr:
		audio_mgr.play_win()
	if haptic_mgr:
		haptic_mgr.vibrate_win()


func _update_ui() -> void:
	var total_solved: int = 0
	var total_moves: int = 0
	var total_pushes: int = 0

	if save_mgr and "completed_levels" in save_mgr:
		for key in save_mgr.completed_levels.keys():
			total_solved += 1
			var rec: Dictionary = save_mgr.completed_levels[key]
			total_moves += rec.get("best_moves", 0)
			total_pushes += rec.get("best_pushes", 0)

	if loc_mgr:
		title_label.text = loc_mgr.tr_text("END_TITLE")
		thanks_label.text = loc_mgr.tr_text("END_THANKS")
		more_levels_label.text = loc_mgr.tr_text("END_MORE_LEVELS")
		stats_label.text = loc_mgr.tr_text("END_STATS_SUMMARY", [total_solved, total_moves, total_pushes])
		level_select_btn.text = loc_mgr.tr_text("BTN_REPLAY_LEVELS")
		menu_btn.text = loc_mgr.tr_text("BTN_MAIN_MENU")
	else:
		title_label.text = "CAMPAIGN COMPLETED!"
		thanks_label.text = "Thank you for playing Pixel Porter!\nYou have mastered all 50 warehouse puzzles."
		more_levels_label.text = "★ More levels coming soon! ★"
		stats_label.text = "Levels Solved: %d / 50\nTotal Best Moves: %d\nTotal Best Pushes: %d" % [total_solved, total_moves, total_pushes]
		level_select_btn.text = "Level Select"
		menu_btn.text = "Main Menu"


func _spawn_initial_confetti() -> void:
	var viewport_sz: Vector2 = size if size != Vector2.ZERO else Vector2(540, 960)
	var rng: RandomNumberGenerator = RandomNumberGenerator.new()
	rng.randomize()

	var palette: Array[Color] = [
		Color(1.0, 0.84, 0.2), # Gold
		Color(0.2, 0.88, 0.4), # Emerald
		Color(0.95, 0.25, 0.3), # Ruby
		Color(0.3, 0.75, 1.0), # Sky
		Color(1.0, 0.95, 0.85) # Pearl
	]

	for i in range(50):
		var p_pos: Vector2 = Vector2(rng.randf_range(40, viewport_sz.x - 40), rng.randf_range(100, viewport_sz.y * 0.7))
		var angle: float = rng.randf_range(-PI, PI)
		var speed: float = rng.randf_range(80.0, 260.0)
		var life: float = rng.randf_range(1.5, 3.0)

		celebration_particles.append({
			"pos": p_pos,
			"vel": Vector2(cos(angle), sin(angle)) * speed,
			"color": palette[rng.randi() % palette.size()],
			"size": rng.randf_range(6.0, 11.0),
			"life": life,
			"max_life": life,
			"rot": rng.randf_range(0.0, TAU),
			"vrot": rng.randf_range(-6.0, 6.0)
		})


func _process(delta: float) -> void:
	particle_spawn_timer += delta
	# Continuous slow celebratory confetti shower
	if particle_spawn_timer >= 0.2:
		particle_spawn_timer = 0.0
		var viewport_sz: Vector2 = size if size != Vector2.ZERO else Vector2(540, 960)
		var rng: RandomNumberGenerator = RandomNumberGenerator.new()
		var palette: Array[Color] = [
			Color(1.0, 0.84, 0.2),
			Color(0.2, 0.88, 0.4),
			Color(0.95, 0.25, 0.3),
			Color(0.3, 0.75, 1.0)
		]
		celebration_particles.append({
			"pos": Vector2(rng.randf_range(20, viewport_sz.x - 20), -10),
			"vel": Vector2(rng.randf_range(-40, 40), rng.randf_range(80, 160)),
			"color": palette[rng.randi() % palette.size()],
			"size": rng.randf_range(6.0, 10.0),
			"life": 3.0,
			"max_life": 3.0,
			"rot": rng.randf_range(0.0, TAU),
			"vrot": rng.randf_range(-4.0, 4.0)
		})

	var i: int = celebration_particles.size() - 1
	while i >= 0:
		var p: Dictionary = celebration_particles[i]
		p["life"] -= delta
		if p["life"] <= 0.0:
			celebration_particles.remove_at(i)
		else:
			p["pos"] += p["vel"] * delta
			p["vel"].y += 120.0 * delta # Gravity
			p["rot"] += p["vrot"] * delta
		i -= 1

	queue_redraw()


func _draw() -> void:
	for p in celebration_particles:
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


func _on_level_select_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")


func _on_menu_pressed() -> void:
	if audio_mgr:
		audio_mgr.play_click()
	if haptic_mgr:
		haptic_mgr.vibrate_click()
	get_tree().change_scene_to_file("res://scenes/main_menu.tscn")
