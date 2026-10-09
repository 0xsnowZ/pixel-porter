shader_type canvas_item;

// Hardware-accelerated mipmap screen blur with dark cinematic vignette
uniform float blur_amount : hint_range(0.0, 5.0) = 2.8;
uniform vec4 tint_color : source_color = vec4(0.03, 0.05, 0.08, 0.68);
uniform sampler2D screen_texture : hint_screen_texture, filter_linear_mipmap;

void fragment() {
	vec4 blurred = textureLod(screen_texture, SCREEN_UV, blur_amount);
	COLOR = mix(blurred, tint_color, tint_color.a);
}
