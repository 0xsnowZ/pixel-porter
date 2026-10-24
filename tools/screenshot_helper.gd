extends Node

var screenshot_dir := "/home/snowz/.gemini/antigravity-ide/brain/477add50-8654-4bdf-af99-792233434d1f"
var timer := 0.0
var step := 0

func _ready() -> void:
	print("Screenshot helper loaded")

func _process(delta: float) -> void:
	timer += delta
	match step:
		0:
			if timer > 3.0:
				_take_screenshot("screenshot_main_menu_raw.png")
				step = 1
				timer = 0.0
		1:
			if timer > 0.5:
				var menu = get_tree().current_scene
				if menu:
					var btn = menu.find_child("LevelSelectBtn", true, false)
					if btn:
						btn.emit_signal("pressed")
						print("Clicked Level Select")
				step = 2
				timer = 0.0
		2:
			if timer > 1.5:
				_take_screenshot("screenshot_level_select_raw.png")
				step = 3
				timer = 0.0
		3:
			if timer > 0.5:
				var menu = get_tree().current_scene
				if menu:
					var back_btn = menu.find_child("BackBtn", true, false)
					if back_btn:
						back_btn.emit_signal("pressed")
						print("Clicked Back")
				step = 4
				timer = 0.0
		4:
			if timer > 1.0:
				var menu = get_tree().current_scene
				if menu:
					var play_btn = menu.find_child("ContinueBtn", true, false)
					if not play_btn:
						play_btn = menu.find_child("PlayBtn", true, false)
					if play_btn:
						play_btn.emit_signal("pressed")
						print("Clicked Continue/Play")
				step = 5
				timer = 0.0
		5:
			if timer > 2.5:
				_take_screenshot("screenshot_gameplay_raw.png")
				step = 6
				timer = 0.0
		6:
			if timer > 0.5:
				print("All screenshots taken!")
				get_tree().quit()

func _take_screenshot(filename: String) -> void:
	var img = get_viewport().get_texture().get_image()
	var path = screenshot_dir + "/" + filename
	var err = img.save_png(path)
	if err == OK:
		print("Saved: " + path)
	else:
		print("Error saving: " + path + " err=" + str(err))
