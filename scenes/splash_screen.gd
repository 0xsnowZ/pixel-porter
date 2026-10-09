extends Control

## Splash Screen Controller for Pixel Porter.
## Fulfills PRD Section 6 screen #1 (Splash screen with the logo).
## Features smooth progress animation, localized status updates,
## tactile tap-to-skip, and graceful fade transition to Main Menu.

const MAIN_MENU_SCENE_PATH: String = "res://scenes/main_menu.tscn"

@export var duration: float = 1.8

@onready var background: TextureRect = get_node_or_null("Background")
@onready var fade_overlay: ColorRect = get_node_or_null("FadeOverlay")
@onready var progress_bar: ProgressBar = get_node_or_null("Margin/BottomVBox/LoadingBar")
@onready var status_label: Label = get_node_or_null("Margin/BottomVBox/StatusLabel")
@onready var prompt_label: Label = get_node_or_null("Margin/BottomVBox/PromptLabel")

var _is_transitioning: bool = false
var _progress_tween: Tween
var _pulse_tween: Tween


func _ready() -> void:
	_ensure_node_refs()
	if fade_overlay:
		fade_overlay.modulate.a = 0.0

	_update_localized_text(0.0)
	_start_loading_animation()
	_start_prompt_pulse()


func _ensure_node_refs() -> void:
	if not background:
		background = get_node_or_null("Background")
	if not fade_overlay:
		fade_overlay = get_node_or_null("FadeOverlay")
	if not progress_bar:
		progress_bar = get_node_or_null("Margin/BottomVBox/LoadingBar")
	if not status_label:
		status_label = get_node_or_null("Margin/BottomVBox/StatusLabel")
	if not prompt_label:
		prompt_label = get_node_or_null("Margin/BottomVBox/PromptLabel")


func _unhandled_input(event: InputEvent) -> void:
	if _is_transitioning:
		return

	# Any tap, click, or keypress triggers instant skip to main menu
	if event is InputEventMouseButton and event.pressed:
		skip_to_main_menu()
	elif event is InputEventScreenTouch and event.pressed:
		skip_to_main_menu()
	elif event is InputEventKey and event.pressed and not event.echo:
		skip_to_main_menu()


func _start_loading_animation() -> void:
	_ensure_node_refs()
	if not progress_bar:
		return

	progress_bar.value = 0.0
	_progress_tween = create_tween()
	if _progress_tween:
		_progress_tween.set_trans(Tween.TRANS_QUAD)
		_progress_tween.set_ease(Tween.EASE_OUT)
		_progress_tween.tween_method(_on_progress_update, 0.0, 100.0, duration)
		_progress_tween.tween_callback(_on_loading_finished)


func _on_progress_update(val: float) -> void:
	_ensure_node_refs()
	if progress_bar:
		progress_bar.value = val
	_update_localized_text(val)


func _update_localized_text(val: float) -> void:
	_ensure_node_refs()
	if not status_label:
		return

	var loc_mgr: Node = null
	if is_inside_tree() and get_tree() and get_tree().root:
		loc_mgr = get_tree().root.get_node_or_null("LocalizationManager")
	var key: String = "SPLASH_INIT"

	if val < 40.0:
		key = "SPLASH_INIT"
	elif val < 90.0:
		key = "SPLASH_LEVELS"
	else:
		key = "SPLASH_READY"

	if loc_mgr and loc_mgr.has_method("get_text"):
		status_label.text = loc_mgr.get_text(key)
	else:
		match key:
			"SPLASH_INIT":
				status_label.text = "INITIALIZING SYSTEM..."
			"SPLASH_LEVELS":
				status_label.text = "LOADING 50 PUZZLE LEVELS..."
			"SPLASH_READY":
				status_label.text = "READY! TAP TO START"


func _start_prompt_pulse() -> void:
	_ensure_node_refs()
	if not prompt_label:
		return

	_pulse_tween = create_tween()
	if _pulse_tween:
		_pulse_tween.set_loops()
		_pulse_tween.tween_property(prompt_label, "modulate:a", 0.3, 0.6)
		_pulse_tween.tween_property(prompt_label, "modulate:a", 1.0, 0.6)


func _on_loading_finished() -> void:
	if not _is_transitioning:
		_transition_to_menu()


## Skips remainder of loading animation and immediately enters main menu
func skip_to_main_menu() -> void:
	if _is_transitioning:
		return

	if _progress_tween and _progress_tween.is_valid():
		_progress_tween.kill()
	if _pulse_tween and _pulse_tween.is_valid():
		_pulse_tween.kill()

	_transition_to_menu(0.15)


func _transition_to_menu(fade_time: float = 0.35) -> void:
	if _is_transitioning:
		return
	_is_transitioning = true

	_ensure_node_refs()
	if fade_overlay:
		var fade = create_tween()
		if fade:
			fade.tween_property(fade_overlay, "modulate:a", 1.0, fade_time)
			fade.tween_callback(_change_scene)
		else:
			_change_scene()
	else:
		_change_scene()


func _change_scene() -> void:
	var tree = get_tree()
	if tree:
		tree.change_scene_to_file(MAIN_MENU_SCENE_PATH)
