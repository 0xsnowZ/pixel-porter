extends Node

## Manages local persistence for Pixel Porter (PRD Sections 2, 6, & 11).
## Stores highest unlocked level, level records (best moves/pushes), and settings.
## Works both as an Autoload singleton and as an instantiable node for tests.

signal progress_saved
signal progress_loaded
signal level_unlocked(level_index: int)

const DEFAULT_SAVE_PATH: String = "user://pixel_porter_save.json"

# Progression state (0-indexed: level 0 is Level 1)
var unlocked_level: int = 0
var last_played_level: int = 0
var completed_levels: Dictionary = {} # String(level_index) -> { "best_moves": int, "best_pushes": int }

# Settings (PRD Sections 6, 8, 9, 10)
var sound_enabled: bool = true
var music_enabled: bool = true
var haptics_enabled: bool = true
var language: String = "en"


func _ready() -> void:
	load_data()


## Returns true if the level at level_index is unlocked and playable.
func is_level_unlocked(level_index: int) -> bool:
	return level_index <= unlocked_level


## Unlocks up to target_level_index if it is higher than current unlocked_level.
func unlock_level(target_level_index: int) -> bool:
	if target_level_index > unlocked_level:
		unlocked_level = target_level_index
		level_unlocked.emit(unlocked_level)
		return true
	return false


## Records a level completion.
## Unlocks the next level (level_index + 1) and saves best scores.
func record_level_completion(level_index: int, moves: int, pushes: int, file_path: String = "") -> void:
	var key: String = str(level_index)
	var prev_record: Dictionary = completed_levels.get(key, {})

	var best_moves: int = moves
	var best_pushes: int = pushes

	if not prev_record.is_empty():
		best_moves = mini(prev_record.get("best_moves", moves), moves)
		best_pushes = mini(prev_record.get("best_pushes", pushes), pushes)

	completed_levels[key] = {
		"best_moves": best_moves,
		"best_pushes": best_pushes,
		"last_moves": moves,
		"last_pushes": pushes
	}

	unlock_level(level_index + 1)
	last_played_level = level_index
	save_data(file_path)


## Retrieves the record for a given level, or an empty Dictionary if not yet completed.
func get_level_record(level_index: int) -> Dictionary:
	return completed_levels.get(str(level_index), {})


## Checks if a level has been completed at least once.
func is_level_completed(level_index: int) -> bool:
	return completed_levels.has(str(level_index))


## Serializes all progression and settings into a Dictionary.
func to_dict() -> Dictionary:
	return {
		"version": 1,
		"unlocked_level": unlocked_level,
		"last_played_level": last_played_level,
		"completed_levels": completed_levels,
		"settings": {
			"sound_enabled": sound_enabled,
			"music_enabled": music_enabled,
			"haptics_enabled": haptics_enabled,
			"language": language
		}
	}


## Deserializes progression and settings from a Dictionary.
func from_dict(data: Dictionary) -> void:
	unlocked_level = data.get("unlocked_level", 0)
	last_played_level = data.get("last_played_level", 0)
	completed_levels = data.get("completed_levels", {}).duplicate()

	var settings: Dictionary = data.get("settings", {})
	sound_enabled = settings.get("sound_enabled", true)
	music_enabled = settings.get("music_enabled", true)
	haptics_enabled = settings.get("haptics_enabled", true)
	language = settings.get("language", "en")


## Saves game state to JSON on disk.
func save_data(custom_path: String = "") -> bool:
	var target_path: String = custom_path if not custom_path.is_empty() else DEFAULT_SAVE_PATH
	var file: FileAccess = FileAccess.open(target_path, FileAccess.WRITE)
	if not file:
		push_error("SaveManager: Failed to open save file for writing at: %s (Error: %s)" % [target_path, FileAccess.get_open_error()])
		return false

	var json_string: String = JSON.stringify(to_dict(), "\t")
	file.store_string(json_string)
	file.close()

	progress_saved.emit()
	return true


## Loads game state from JSON on disk. Returns false if file doesn't exist or is invalid.
func load_data(custom_path: String = "") -> bool:
	var target_path: String = custom_path if not custom_path.is_empty() else DEFAULT_SAVE_PATH
	if not FileAccess.file_exists(target_path):
		return false

	var file: FileAccess = FileAccess.open(target_path, FileAccess.READ)
	if not file:
		push_error("SaveManager: Failed to open save file for reading at: %s" % target_path)
		return false

	var content: String = file.get_as_text()
	file.close()

	if content.strip_edges().is_empty():
		return false

	var json: JSON = JSON.new()
	var error: Error = json.parse(content)
	if error != OK:
		push_warning("SaveManager: JSON parse error in save file: %s (Line: %d)" % [json.get_error_message(), json.get_error_line()])
		return false

	var parsed_data: Variant = json.data
	if not parsed_data is Dictionary:
		push_warning("SaveManager: Expected Dictionary in save file, got %s" % typeof(parsed_data))
		return false

	from_dict(parsed_data)
	progress_loaded.emit()
	return true


## Resets all progression back to initial new-game state.
func reset_all_progress(custom_path: String = "") -> void:
	unlocked_level = 0
	last_played_level = 0
	completed_levels.clear()
	sound_enabled = true
	music_enabled = true
	haptics_enabled = true
	language = "en"
	save_data(custom_path)
