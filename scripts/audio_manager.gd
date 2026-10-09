extends Node

## Central Audio Manager for Pixel Porter (PRD Section 9 & 6).
## Synthesizes and plays authentic retro 8-bit sound effects:
## - Move / Step: Short subtle blip
## - Push Crate: Punchy low square wave thud
## - Level Complete: Cheerful ascending 8-bit arpeggio
## - Restart: Descending rewind sweep
## - UI Click: Crisp feedback click
## Respects SaveManager.sound_enabled toggle.

const MIX_RATE: int = 22050

var save_mgr: Node = null

# Cached procedural streams
var sfx_move: AudioStreamWAV
var sfx_push: AudioStreamWAV
var sfx_win: AudioStreamWAV
var sfx_restart: AudioStreamWAV
var sfx_click: AudioStreamWAV

# AudioStreamPlayer voice pool for overlapping SFX
var _players: Array[AudioStreamPlayer] = []
const POOL_SIZE: int = 6


func _ready() -> void:
	# Retrieve SaveManager if present
	if is_inside_tree() and get_tree().root.has_node("SaveManager"):
		save_mgr = get_tree().root.get_node("SaveManager")

	_create_player_pool()
	_generate_all_sfx()


func _create_player_pool() -> void:
	for i in range(POOL_SIZE):
		var p: AudioStreamPlayer = AudioStreamPlayer.new()
		p.bus = "Master"
		add_child(p)
		_players.append(p)


func is_sound_enabled() -> bool:
	if save_mgr != null and "sound_enabled" in save_mgr:
		return save_mgr.sound_enabled
	return true


func play_stream(stream: AudioStreamWAV, volume_db: float = 0.0) -> void:
	if not is_inside_tree() or not is_sound_enabled() or stream == null:
		return

	# Find an available player or steal the one playing longest
	for p in _players:
		if p.is_inside_tree() and not p.playing:
			p.stream = stream
			p.volume_db = volume_db
			p.play()
			return

	# Fallback: reuse first player if in tree
	if not _players.is_empty() and _players[0].is_inside_tree():
		var fallback_player: AudioStreamPlayer = _players[0]
		fallback_player.stream = stream
		fallback_player.volume_db = volume_db
		fallback_player.play()


## Player movement step sound
func play_move() -> void:
	play_stream(sfx_move, -6.0)


## Crate pushed sound
func play_push() -> void:
	play_stream(sfx_push, -1.0)


## Level won fanfare
func play_win() -> void:
	play_stream(sfx_win, 0.0)


## Level restart sound
func play_restart() -> void:
	play_stream(sfx_restart, -3.0)


## UI button click sound
func play_click() -> void:
	play_stream(sfx_click, -4.0)


# ==============================================================================
# Procedural Retro 8-Bit Audio Synthesis
# ==============================================================================

func _generate_all_sfx() -> void:
	sfx_move = _synth_move()
	sfx_push = _synth_push()
	sfx_win = _synth_win()
	sfx_restart = _synth_restart()
	sfx_click = _synth_click()


func _create_wav(data_bytes: PackedByteArray) -> AudioStreamWAV:
	var wav: AudioStreamWAV = AudioStreamWAV.new()
	wav.format = AudioStreamWAV.FORMAT_16_BITS
	wav.mix_rate = MIX_RATE
	wav.stereo = false
	wav.data = data_bytes
	return wav


## Generates a short 35ms retro step blip
func _synth_move() -> AudioStreamWAV:
	var duration: float = 0.035
	var total_samples: int = int(duration * MIX_RATE)
	var bytes: PackedByteArray = PackedByteArray()
	bytes.resize(total_samples * 2)

	var freq_start: float = 160.0
	var freq_end: float = 90.0
	var phase: float = 0.0

	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var freq: float = lerpf(freq_start, freq_end, t)
		phase += (freq * TAU) / float(MIX_RATE)

		# Soft square wave
		var wave: float = 1.0 if sin(phase) > 0.0 else -1.0
		# Decay envelope
		var envelope: float = (1.0 - t) * (1.0 - t)
		var sample_val: int = int(clampi(int(wave * envelope * 12000.0), -32767, 32767))
		bytes.encode_s16(i * 2, sample_val)

	return _create_wav(bytes)


## Generates a 90ms punchy crate push thud
func _synth_push() -> AudioStreamWAV:
	var duration: float = 0.09
	var total_samples: int = int(duration * MIX_RATE)
	var bytes: PackedByteArray = PackedByteArray()
	bytes.resize(total_samples * 2)

	var freq_start: float = 120.0
	var freq_end: float = 55.0
	var phase: float = 0.0

	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var freq: float = lerpf(freq_start, freq_end, t)
		phase += (freq * TAU) / float(MIX_RATE)

		# Combined square and triangle for a heavy crate impact
		var sq: float = 1.0 if sin(phase) > 0.0 else -1.0
		var tri: float = 2.0 * abs(fmod(phase / PI, 2.0) - 1.0) - 1.0
		var wave: float = 0.7 * sq + 0.3 * tri

		# Punchy attack and decay envelope
		var envelope: float = (1.0 - t)
		var sample_val: int = int(clampi(int(wave * envelope * 24000.0), -32767, 32767))
		bytes.encode_s16(i * 2, sample_val)

	return _create_wav(bytes)


## Generates a 320ms celebratory chip-tune ascending arpeggio
func _synth_win() -> AudioStreamWAV:
	var duration: float = 0.32
	var total_samples: int = int(duration * MIX_RATE)
	var bytes: PackedByteArray = PackedByteArray()
	bytes.resize(total_samples * 2)

	# 4 notes: C5 (523Hz), E5 (659Hz), G5 (784Hz), C6 (1046Hz)
	var notes: Array[float] = [523.25, 659.25, 783.99, 1046.50]
	var samples_per_note: int = total_samples / notes.size()
	var phase: float = 0.0

	for i in range(total_samples):
		var note_idx: int = mini(i / samples_per_note, notes.size() - 1)
		var note_freq: float = notes[note_idx]
		phase += (note_freq * TAU) / float(MIX_RATE)

		var note_t: float = float(i % samples_per_note) / float(samples_per_note)
		var wave: float = 1.0 if sin(phase) > 0.0 else -1.0
		# Crisp pulse width modulation
		if sin(phase * 2.0) > 0.5:
			wave *= 0.8

		var envelope: float = 1.0 - (note_t * 0.4)
		if note_idx == notes.size() - 1:
			envelope = 1.0 - (note_t * 0.7) # ringing tail on top note

		var sample_val: int = int(clampi(int(wave * envelope * 20000.0), -32767, 32767))
		bytes.encode_s16(i * 2, sample_val)

	return _create_wav(bytes)


## Generates an 80ms descending restart whistle
func _synth_restart() -> AudioStreamWAV:
	var duration: float = 0.08
	var total_samples: int = int(duration * MIX_RATE)
	var bytes: PackedByteArray = PackedByteArray()
	bytes.resize(total_samples * 2)

	var freq_start: float = 380.0
	var freq_end: float = 160.0
	var phase: float = 0.0

	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		var freq: float = lerpf(freq_start, freq_end, t)
		phase += (freq * TAU) / float(MIX_RATE)

		var wave: float = sin(phase)
		var envelope: float = (1.0 - t)
		var sample_val: int = int(clampi(int(wave * envelope * 18000.0), -32767, 32767))
		bytes.encode_s16(i * 2, sample_val)

	return _create_wav(bytes)


## Generates a 20ms UI click blip
func _synth_click() -> AudioStreamWAV:
	var duration: float = 0.02
	var total_samples: int = int(duration * MIX_RATE)
	var bytes: PackedByteArray = PackedByteArray()
	bytes.resize(total_samples * 2)

	var freq: float = 780.0
	var phase: float = 0.0

	for i in range(total_samples):
		var t: float = float(i) / float(total_samples)
		phase += (freq * TAU) / float(MIX_RATE)
		var wave: float = 1.0 if sin(phase) > 0.0 else -1.0
		var envelope: float = (1.0 - t) * (1.0 - t)
		var sample_val: int = int(clampi(int(wave * envelope * 14000.0), -32767, 32767))
		bytes.encode_s16(i * 2, sample_val)

	return _create_wav(bytes)
