extends SceneTree

func _init() -> void:
	var theme = Theme.new()

	# -------------------------------------------------------------
	# 1. Base Button Styles (Arcade Slate with Gold Trim)
	# -------------------------------------------------------------
	var btn_normal = StyleBoxFlat.new()
	btn_normal.bg_color = Color(0.13, 0.17, 0.24, 1.0)
	btn_normal.border_color = Color(0.72, 0.54, 0.20, 1.0)
	btn_normal.border_width_left = 2
	btn_normal.border_width_top = 2
	btn_normal.border_width_right = 2
	btn_normal.border_width_bottom = 4
	btn_normal.set_corner_radius_all(10)
	btn_normal.content_margin_left = 18
	btn_normal.content_margin_top = 10
	btn_normal.content_margin_right = 18
	btn_normal.content_margin_bottom = 12
	btn_normal.shadow_color = Color(0.0, 0.0, 0.0, 0.4)
	btn_normal.shadow_size = 4
	btn_normal.shadow_offset = Vector2(0, 2)

	var btn_hover = StyleBoxFlat.new()
	btn_hover.bg_color = Color(0.20, 0.26, 0.36, 1.0)
	btn_hover.border_color = Color(0.98, 0.82, 0.28, 1.0)
	btn_hover.border_width_left = 2
	btn_hover.border_width_top = 2
	btn_hover.border_width_right = 2
	btn_hover.border_width_bottom = 4
	btn_hover.set_corner_radius_all(10)
	btn_hover.content_margin_left = 18
	btn_hover.content_margin_top = 10
	btn_hover.content_margin_right = 18
	btn_hover.content_margin_bottom = 12
	btn_hover.shadow_color = Color(0.98, 0.82, 0.28, 0.35)
	btn_hover.shadow_size = 6

	var btn_pressed = StyleBoxFlat.new()
	btn_pressed.bg_color = Color(0.09, 0.12, 0.17, 1.0)
	btn_pressed.border_color = Color(0.55, 0.40, 0.14, 1.0)
	btn_pressed.border_width_left = 2
	btn_pressed.border_width_top = 3
	btn_pressed.border_width_right = 2
	btn_pressed.border_width_bottom = 2
	btn_pressed.set_corner_radius_all(10)
	btn_pressed.content_margin_left = 18
	btn_pressed.content_margin_top = 13
	btn_pressed.content_margin_right = 18
	btn_pressed.content_margin_bottom = 9

	var btn_disabled = StyleBoxFlat.new()
	btn_disabled.bg_color = Color(0.10, 0.12, 0.16, 0.85)
	btn_disabled.border_color = Color(0.25, 0.30, 0.38, 0.7)
	btn_disabled.border_width_left = 2
	btn_disabled.border_width_top = 2
	btn_disabled.border_width_right = 2
	btn_disabled.border_width_bottom = 2
	btn_disabled.set_corner_radius_all(10)
	btn_disabled.content_margin_left = 18
	btn_disabled.content_margin_top = 10
	btn_disabled.content_margin_right = 18
	btn_disabled.content_margin_bottom = 12

	var btn_focus = StyleBoxEmpty.new()

	theme.set_stylebox("normal", "Button", btn_normal)
	theme.set_stylebox("hover", "Button", btn_hover)
	theme.set_stylebox("pressed", "Button", btn_pressed)
	theme.set_stylebox("disabled", "Button", btn_disabled)
	theme.set_stylebox("focus", "Button", btn_focus)

	theme.set_color("font_color", "Button", Color(0.94, 0.96, 0.98, 1.0))
	theme.set_color("font_hover_color", "Button", Color(1.0, 1.0, 1.0, 1.0))
	theme.set_color("font_pressed_color", "Button", Color(0.98, 0.82, 0.25, 1.0))
	theme.set_color("font_disabled_color", "Button", Color(0.45, 0.50, 0.58, 0.8))
	theme.set_color("font_shadow_color", "Button", Color(0.0, 0.0, 0.0, 0.7))
	theme.set_constant("shadow_offset_y", "Button", 1)

	# -------------------------------------------------------------
	# 2. PrimaryButton Variation (Glowing Gold/Amber for Play/Continue)
	# -------------------------------------------------------------
	theme.add_type("PrimaryButton")
	theme.set_type_variation("PrimaryButton", "Button")

	var pri_normal = StyleBoxFlat.new()
	pri_normal.bg_color = Color(0.85, 0.54, 0.12, 1.0) # Warm amber gold
	pri_normal.border_color = Color(1.0, 0.85, 0.45, 1.0) # Highlight rim
	pri_normal.border_width_left = 2
	pri_normal.border_width_top = 2
	pri_normal.border_width_right = 2
	pri_normal.border_width_bottom = 5 # Big 3D bottom bevel
	pri_normal.set_corner_radius_all(10)
	pri_normal.content_margin_left = 18
	pri_normal.content_margin_top = 10
	pri_normal.content_margin_right = 18
	pri_normal.content_margin_bottom = 13
	pri_normal.shadow_color = Color(0.85, 0.54, 0.12, 0.45)
	pri_normal.shadow_size = 6
	pri_normal.shadow_offset = Vector2(0, 2)

	var pri_hover = StyleBoxFlat.new()
	pri_hover.bg_color = Color(0.95, 0.64, 0.18, 1.0)
	pri_hover.border_color = Color(1.0, 0.94, 0.65, 1.0)
	pri_hover.border_width_left = 2
	pri_hover.border_width_top = 2
	pri_hover.border_width_right = 2
	pri_hover.border_width_bottom = 5
	pri_hover.set_corner_radius_all(10)
	pri_hover.content_margin_left = 18
	pri_hover.content_margin_top = 10
	pri_hover.content_margin_right = 18
	pri_hover.content_margin_bottom = 13
	pri_hover.shadow_color = Color(1.0, 0.75, 0.20, 0.6)
	pri_hover.shadow_size = 8

	var pri_pressed = StyleBoxFlat.new()
	pri_pressed.bg_color = Color(0.68, 0.38, 0.08, 1.0)
	pri_pressed.border_color = Color(0.42, 0.22, 0.04, 1.0)
	pri_pressed.border_width_left = 2
	pri_pressed.border_width_top = 4
	pri_pressed.border_width_right = 2
	pri_pressed.border_width_bottom = 2
	pri_pressed.set_corner_radius_all(10)
	pri_pressed.content_margin_left = 18
	pri_pressed.content_margin_top = 14
	pri_pressed.content_margin_right = 18
	pri_pressed.content_margin_bottom = 9

	theme.set_stylebox("normal", "PrimaryButton", pri_normal)
	theme.set_stylebox("hover", "PrimaryButton", pri_hover)
	theme.set_stylebox("pressed", "PrimaryButton", pri_pressed)
	theme.set_stylebox("disabled", "PrimaryButton", btn_disabled)
	theme.set_stylebox("focus", "PrimaryButton", btn_focus)
	theme.set_color("font_color", "PrimaryButton", Color(1.0, 1.0, 1.0, 1.0))
	theme.set_color("font_hover_color", "PrimaryButton", Color(1.0, 1.0, 0.9, 1.0))
	theme.set_color("font_pressed_color", "PrimaryButton", Color(1.0, 0.9, 0.7, 1.0))
	theme.set_color("font_shadow_color", "PrimaryButton", Color(0.25, 0.12, 0.02, 0.9))

	# -------------------------------------------------------------
	# 3. SuccessButton Variation (Emerald for Next Level)
	# -------------------------------------------------------------
	theme.add_type("SuccessButton")
	theme.set_type_variation("SuccessButton", "Button")

	var suc_normal = StyleBoxFlat.new()
	suc_normal.bg_color = Color(0.18, 0.58, 0.32, 1.0) # Emerald green
	suc_normal.border_color = Color(0.45, 0.90, 0.58, 1.0)
	suc_normal.border_width_left = 2
	suc_normal.border_width_top = 2
	suc_normal.border_width_right = 2
	suc_normal.border_width_bottom = 4
	suc_normal.set_corner_radius_all(10)
	suc_normal.content_margin_left = 18
	suc_normal.content_margin_top = 10
	suc_normal.content_margin_right = 18
	suc_normal.content_margin_bottom = 12
	suc_normal.shadow_color = Color(0.18, 0.58, 0.32, 0.4)
	suc_normal.shadow_size = 5

	var suc_hover = StyleBoxFlat.new()
	suc_hover.bg_color = Color(0.24, 0.68, 0.38, 1.0)
	suc_hover.border_color = Color(0.65, 0.98, 0.75, 1.0)
	suc_hover.border_width_left = 2
	suc_hover.border_width_top = 2
	suc_hover.border_width_right = 2
	suc_hover.border_width_bottom = 4
	suc_hover.set_corner_radius_all(10)
	suc_hover.content_margin_left = 18
	suc_hover.content_margin_top = 10
	suc_hover.content_margin_right = 18
	suc_hover.content_margin_bottom = 12

	var suc_pressed = StyleBoxFlat.new()
	suc_pressed.bg_color = Color(0.12, 0.42, 0.22, 1.0)
	suc_pressed.border_color = Color(0.08, 0.26, 0.14, 1.0)
	suc_pressed.border_width_left = 2
	suc_pressed.border_width_top = 3
	suc_pressed.border_width_right = 2
	suc_pressed.border_width_bottom = 2
	suc_pressed.set_corner_radius_all(10)
	suc_pressed.content_margin_left = 18
	suc_pressed.content_margin_top = 13
	suc_pressed.content_margin_right = 18
	suc_pressed.content_margin_bottom = 9

	theme.set_stylebox("normal", "SuccessButton", suc_normal)
	theme.set_stylebox("hover", "SuccessButton", suc_hover)
	theme.set_stylebox("pressed", "SuccessButton", suc_pressed)
	theme.set_stylebox("disabled", "SuccessButton", btn_disabled)
	theme.set_stylebox("focus", "SuccessButton", btn_focus)
	theme.set_color("font_color", "SuccessButton", Color(1.0, 1.0, 1.0, 1.0))
	theme.set_color("font_shadow_color", "SuccessButton", Color(0.05, 0.2, 0.08, 0.9))

	# -------------------------------------------------------------
	# 4. PanelContainer (Arcade Console Card & HUD Plaque)
	# -------------------------------------------------------------
	var panel_box = StyleBoxFlat.new()
	panel_box.bg_color = Color(0.09, 0.12, 0.17, 0.94)
	panel_box.border_color = Color(0.68, 0.50, 0.18, 1.0)
	panel_box.border_width_left = 2
	panel_box.border_width_top = 2
	panel_box.border_width_right = 2
	panel_box.border_width_bottom = 2
	panel_box.set_corner_radius_all(14)
	panel_box.content_margin_left = 16
	panel_box.content_margin_top = 16
	panel_box.content_margin_right = 16
	panel_box.content_margin_bottom = 16
	panel_box.shadow_color = Color(0.0, 0.0, 0.0, 0.65)
	panel_box.shadow_size = 14
	panel_box.shadow_offset = Vector2(0, 4)
	theme.set_stylebox("panel", "PanelContainer", panel_box)

	# -------------------------------------------------------------
	# 5. TopBar & BottomBar Panel Variations
	# -------------------------------------------------------------
	theme.add_type("TopBarPanel")
	theme.set_type_variation("TopBarPanel", "PanelContainer")
	var topbar_box = StyleBoxFlat.new()
	topbar_box.bg_color = Color(0.08, 0.11, 0.16, 0.96)
	topbar_box.border_color = Color(0.72, 0.54, 0.20, 1.0)
	topbar_box.border_width_bottom = 2
	theme.set_stylebox("panel", "TopBarPanel", topbar_box)

	theme.add_type("BottomBarPanel")
	theme.set_type_variation("BottomBarPanel", "PanelContainer")
	var botbar_box = StyleBoxFlat.new()
	botbar_box.bg_color = Color(0.08, 0.11, 0.16, 0.96)
	botbar_box.border_color = Color(0.72, 0.54, 0.20, 1.0)
	botbar_box.border_width_top = 2
	theme.set_stylebox("panel", "BottomBarPanel", botbar_box)

	# -------------------------------------------------------------
	# 6. Window / Dialogs
	# -------------------------------------------------------------
	theme.set_stylebox("panel", "Window", panel_box)
	theme.set_color("title_color", "Window", Color(0.98, 0.82, 0.25, 1.0))

	# -------------------------------------------------------------
	# 7. Labels
	# -------------------------------------------------------------
	theme.set_color("font_color", "Label", Color(0.92, 0.95, 0.98, 1.0))
	theme.set_color("font_shadow_color", "Label", Color(0.0, 0.0, 0.0, 0.75))
	theme.set_constant("shadow_offset_x", "Label", 1)
	theme.set_constant("shadow_offset_y", "Label", 1)

	var err = ResourceSaver.save(theme, "res://assets/theme.tres")
	if err == OK:
		print("Theme successfully updated with variations at res://assets/theme.tres")
	else:
		printerr("Failed to save theme: ", err)

	quit(0)
