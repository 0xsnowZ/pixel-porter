extends SceneTree

## Headless Unit Test Suite for AdManager (Monetization & AdMob Framework, PRD Section 8).
## Tests:
## - Levels 1 to 3 are ad-free (indices 0, 1, 2)
## - Cadence: one ad after every 3rd completed level post-tutorial
## - Cooldown: at least 60 seconds between ads
## - Never during level / never after restart
## - Preload behavior and ad lifecycle signals
## - Consent management hooks

const AdManagerScript = preload("res://scripts/ad_manager.gd")

var passes: int = 0
var fails: int = 0


func _init() -> void:
	print("\n" + "=".repeat(56))
	print("   Pixel Porter - AdManager Headless Test Suite   ")
	print("=".repeat(56) + "\n")

	test_initial_state_and_preloading()
	test_levels_1_to_3_ad_free()
	test_cadence_every_3rd_completed_level()
	test_cooldown_restriction()
	test_ad_lifecycle_and_signals()
	test_consent_hooks()

	print("\n" + "=".repeat(56))
	print("AdManager Results: %d passed, %d failed" % [passes, fails])
	print("=".repeat(56))

	if fails > 0:
		print("FAILURE: %d AdManager tests failed." % fails)
		quit(1)
	else:
		print("SUCCESS: All AdManager tests passed!\n")
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


func test_initial_state_and_preloading() -> void:
	print("--- Running Suite: Initial State & Preloading ---")
	var adm: Node = AdManagerScript.new()
	root.add_child(adm)
	adm._ready()

	assert_true(adm.is_test_mode, "Test mode is active by default")
	assert_true(adm.is_interstitial_loaded, "Interstitial ad is preloaded on startup")
	assert_eq(adm.interstitial_ad_unit_id, "ca-app-pub-3940256099942544/1033173712", "Google official Android test ID configured")
	assert_eq(adm.completions_since_last_ad, 0, "Initial completion counter is 0")

	adm.free()


func test_levels_1_to_3_ad_free() -> void:
	print("--- Running Suite: Levels 1 to 3 Ad-Free (PRD Section 8) ---")
	var adm: Node = AdManagerScript.new()
	root.add_child(adm)
	adm._ready()

	# Complete Level 1 (idx 0)
	adm.record_level_completed(0)
	assert_true(not adm.should_show_interstitial(0), "Level 1 is ad-free")
	assert_eq(adm.completions_since_last_ad, 0, "Level 1 does not increment post-tutorial ad counter")

	# Complete Level 2 (idx 1)
	adm.record_level_completed(1)
	assert_true(not adm.should_show_interstitial(1), "Level 2 is ad-free")
	assert_eq(adm.completions_since_last_ad, 0, "Level 2 does not increment post-tutorial ad counter")

	# Complete Level 3 (idx 2)
	adm.record_level_completed(2)
	assert_true(not adm.should_show_interstitial(2), "Level 3 is ad-free")
	assert_eq(adm.completions_since_last_ad, 0, "Level 3 does not increment post-tutorial ad counter")

	# Attempting show on level 1-3 returns false
	var shown: bool = adm.show_interstitial(2)
	assert_true(not shown, "show_interstitial on Level 3 returns false")

	adm.free()


func test_cadence_every_3rd_completed_level() -> void:
	print("--- Running Suite: 3-Level Completion Cadence ---")
	var adm: Node = AdManagerScript.new()
	root.add_child(adm)
	adm._ready()

	# Complete 1st post-tutorial level (Level 4, idx 3)
	adm.record_level_completed(3)
	assert_eq(adm.completions_since_last_ad, 1, "Completed 1 level post-tutorial")
	assert_true(not adm.should_show_interstitial(3), "No ad after 1st completion")

	# Complete 2nd post-tutorial level (Level 5, idx 4)
	adm.record_level_completed(4)
	assert_eq(adm.completions_since_last_ad, 2, "Completed 2 levels post-tutorial")
	assert_true(not adm.should_show_interstitial(4), "No ad after 2nd completion")

	# Complete 3rd post-tutorial level (Level 6, idx 5)
	adm.record_level_completed(5)
	assert_eq(adm.completions_since_last_ad, 3, "Completed 3 levels post-tutorial")
	assert_true(adm.should_show_interstitial(5), "Ad is eligible after 3rd completed level")

	# Show the ad
	var shown: bool = adm.show_interstitial(5)
	assert_true(shown, "show_interstitial succeeded")
	assert_eq(adm.completions_since_last_ad, 0, "Counter reset to 0 after ad shown")
	assert_eq(adm.total_ads_shown, 1, "Total ads shown incremented to 1")

	adm.free()


func test_cooldown_restriction() -> void:
	print("--- Running Suite: 60-Second Cooldown Restriction ---")
	var adm: Node = AdManagerScript.new()
	root.add_child(adm)
	adm._ready()

	# Trigger first ad
	adm.record_level_completed(3)
	adm.record_level_completed(4)
	adm.record_level_completed(5)
	adm.show_interstitial(5)

	# Player immediately completes 3 more levels quickly (e.g. within 5 seconds)
	adm.record_level_completed(6)
	adm.record_level_completed(7)
	adm.record_level_completed(8)

	assert_eq(adm.completions_since_last_ad, 3, "Completed 3 levels again")
	assert_true(not adm.should_show_interstitial(8), "Ad blocked by 60s cooldown even if 3 levels completed")

	# Simulate 65 seconds elapsed since last ad
	adm.last_ad_show_time_msec -= 65000
	assert_true(adm.should_show_interstitial(8), "Ad unblocked once 60s cooldown has elapsed")

	adm.free()


func test_ad_lifecycle_and_signals() -> void:
	print("--- Running Suite: Ad Lifecycle & Signals ---")
	var adm: Node = AdManagerScript.new()
	root.add_child(adm)
	adm._ready()

	var tracker: Dictionary = { "opened": false }
	adm.interstitial_opened.connect(func(): tracker["opened"] = true)

	adm.record_level_completed(3)
	adm.record_level_completed(4)
	adm.record_level_completed(5)

	var shown: bool = adm.show_interstitial(5)
	assert_true(shown, "show_interstitial returned true")
	assert_true(tracker["opened"], "interstitial_opened signal emitted on show")

	adm.free()


func test_consent_hooks() -> void:
	print("--- Running Suite: Consent Management Hooks ---")
	var adm: Node = AdManagerScript.new()
	root.add_child(adm)
	adm._ready()

	assert_true(adm.consent_status != adm.ConsentStatus.UNKNOWN, "Consent status initialized")
	adm.request_consent()
	assert_eq(adm.consent_status, adm.ConsentStatus.OBTAINED, "Default development consent status is OBTAINED")

	adm.free()
