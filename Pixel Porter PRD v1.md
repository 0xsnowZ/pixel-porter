# Pixel Porter: Product Requirements Document (v1)

Working title | Android | Free with ads | Draft for review. Items marked **(Assumption)** are defaults I chose where no decision was made yet. They are collected in section 17.

## 1. Summary

Pixel Porter is a free, ad-supported Android puzzle game in the classic box-pushing genre, with a retro pixel-art look. The player pushes crates onto goal tiles across 50 numbered levels that get steadily harder. Levels are made by an offline generator, proven solvable by a solver, and hand-checked before they ship inside the app. There is no undo, only restart. The game is built in Godot, earns money only from interstitial ads, and is discovered through Google Play search in English, French and Arabic.

## 2. Goals and non-goals

**Goals**

- Ship a polished, stable v1 with 50 verified-solvable levels.
- Reach about 5,000 installs in the first 3 months after launch.
- Earn ad revenue without hurting early retention.
- Stand out with the retro pixel look and a fair, well-paced difficulty curve.

**Non-goals for v1**

Undo, hints, star ratings, rewarded ads, banner ads, in-app purchases, accounts or cloud save, analytics, leaderboards, a level editor, and social features.

## 3. Target players

Casual to core puzzle fans on Android who enjoy logic puzzles and retro games, searching in English, French or Arabic for box-pushing or crate puzzle games. Sessions are short (a few minutes) and played one-handed. **(Assumption)** Portrait orientation only.

## 4. Core gameplay

- The player moves one tile at a time: up, down, left or right.
- Moving into a crate pushes it one tile if the tile behind it is empty floor or a goal. Crates cannot be pulled, and two crates cannot be pushed at once.
- A level is complete when every crate sits on a goal tile.
- A crate pushed into a dead spot (for example a corner) can make the level unwinnable. The player's only remedy is restart.
- The game is turn-based with no timers.
- Visual reference: the supplied screenshot (brick walls, green floor, decorative border, level number bar at the bottom). It is a style reference only. Do not copy its artwork.

## 5. Controls

- Swipe anywhere on the screen to move one tile in that direction.
- The dominant axis of the swipe decides the direction. Taps and tiny movements are ignored. **(Assumption)** Minimum swipe distance is tuned in playtests; start around 3 to 4 mm of finger travel.
- A swipe made during a move animation is queued (one move only). **(Assumption)**
- A Restart button is always visible, with a touch target of at least 48 dp, placed away from the screen edges to avoid accidental taps. **(Assumption)** After 5 or more moves, Restart asks for one confirmation tap.
- Move animation is quick, around 100 to 150 ms per tile. **(Assumption)**

## 6. Screens and flow

1. Splash screen with the logo.
2. Main menu: Play or Continue, Level select, Sound on/off, Language, Credits.
3. Gameplay: the grid, a level number bar at the bottom (as in the reference), and the Restart button.
4. Level complete: a short celebration, then the next level. An interstitial ad may appear here (section 8).
5. End screen after level 50: a thank-you message and 'more levels coming soon'.

Level select is a simple grid of the 50 levels. Completed levels and the next level are playable, later ones are locked. **(Assumption)** This is the first feature to cut if the schedule slips, since Continue works without it.

## 7. Levels and difficulty

**Pipeline (all offline, on your computer)**

1. A generator builds candidate levels by working backwards from a solved state (pulling crates away from goals), which makes every candidate solvable.
2. A solver checks each candidate and reports minimum moves, minimum pushes, crate count and grid size. These numbers give each level a difficulty score.
3. Weak candidates are removed: trivial ones, near-duplicates, and levels with very low move counts for their size. **(Assumption)** Generate at least 300 candidates, then keep the best 50.
4. You personally play every one of the final 50 and put them in difficulty order.
5. The final set ships as a plain text data file inside the app. The game does not generate levels on the phone.

**Difficulty ramp (Balanced).** The numbers below are starting assumptions to calibrate with the solver and with playtests.

| Levels | Grid size (up to) | Crates | Purpose |
| --- | --- | --- | --- |
| 1 to 5 | 6x6 | 1 | Learn to move and push, no text needed |
| 6 to 15 | 7x7 | 1 to 2 | Learn that crates can get stuck |
| 16 to 30 | 8x8 | 2 to 3 | Planning ahead |
| 31 to 45 | 9x9 | 3 to 4 | Real challenge |
| 46 to 50 | 10x10 | 4 to 5 | Final test |

Because there is no undo, early levels must forgive mistakes: open space and few ways to get stuck.

## 8. Monetization

- Interstitial ads only, through Google AdMob. No banners and no rewarded ads in v1.
- Rules **(Assumption)**: levels 1 to 3 are ad-free. After that, one ad after every 3rd completed level. Never during a level, never after Restart, and at least 60 seconds between ads. The ad appears only on the level-complete transition and is always preloaded so there is no loading delay.
- Show the consent form required for players in the European Economic Area and the UK before serving ads, using Google's consent tooling.
- Use test ads during development and testing. Never tap your own live ads, since that can get the AdMob account banned.
- Godot has no built-in AdMob support, so a community plugin is needed. Confirm in week 0 that it works with the chosen Godot version. If it does not, evaluate alternatives before building further.
- Revenue note: with 50 levels, each install has a limited number of ad impressions. Level updates after launch are the main way to raise lifetime value.

## 9. Art, audio and UI

- Retro pixel art from free or purchased asset packs. Every pack must allow commercial use in a free, ad-supported app. Keep a licenses file listing each pack, its author, its license and its attribution requirement, and show any required credits in the Credits screen.
- Render with nearest-neighbor scaling and whole-number pixel scaling so pixels stay sharp on every screen size. Use safe-area margins for notches and system bars.
- Audio: a few short effects (move, push, level complete, restart) and one or two music loops. Sound on/off toggle in the menu, saved between sessions.
- Keep all in-game text short and use icons wherever possible.

## 10. Localization

- English, French and Arabic in the game and in the store listing.
- Arabic is right to left, so menus and layouts must mirror correctly. Finding an Arabic-capable font that fits the pixel style is a design task. If there is no good match, use a clean, readable font for Arabic.
- All text lives in one translation table so native speakers can review it before launch. Machine translation alone is not enough for the store listing.
- The game defaults to the phone's language, and players can change it in the menu.

## 11. Technical requirements

- Engine: Godot. Pin one stable version in week 0 and do not upgrade during v1.
- Platform: Android phones, published as an Android App Bundle. **(Assumption)** Choose a minimum Android version that covers most active devices; confirm when picking the Godot version. At release, meet Google Play's current target API level requirement (check at build time).
- Offline: the game works with no internet, except for loading ads.
- Saving: store the highest unlocked level and the settings on the device. No accounts and no backend.
- Performance: smooth 60 fps on a low-end phone. **(Assumption)** Download size under 50 MB.
- Quality: no crashes or freezes on test devices. Test at least one low-end and one high-end phone, and one small and one large screen.

## 12. Measurement and success criteria

**Decision:** no analytics SDK in v1. The only measurement is what Google Play Console provides for free.

- Primary goal: about 5,000 installs in the first 3 months.
- Guardrails to watch in Play Console **(Assumption)**: an average rating of 4.0 or higher, and a low crash and freeze rate.
- Trade-off: without analytics you cannot see which levels players restart or quit on, so difficulty problems will only show up in reviews. Adding basic analytics (level completions, restarts, quit points) is the first item for v1.1.
- Even without an analytics SDK, the Play Data safety form must declare the data collected by the ad SDK.

## 13. Store listing and discovery

- Discovery is through Google Play search only, so the listing carries the whole strategy.
- Name: Pixel Porter, pending the checks below. Add a descriptive subtitle for keywords (for example a retro box puzzle line), written in all three languages.
- Do not use the word Sokoban in the app title, short description or keywords. It is a trademark owned by Falcon Co., Ltd., which also runs its own official Android game. This is a risk flag, not legal advice.
- Describe the gameplay in plain terms: push crates, solve puzzles, retro pixel art, brain game, logic puzzle.
- Screenshots should show the retro look and a clear level. Make the icon and feature graphic in the same style.
- Name checks before launch: search the Play Store for the exact name, and check a trademark database for conflicts, including the word Pixel (Google's phone brand).
- Fallback plan **(Assumption)**: a few low-effort launch posts where puzzle fans gather, since search alone is slow for a new app with no install history.
- Have the content rating questionnaire and a privacy policy page ready. A privacy policy URL is needed because the game uses ads.

## 14. Launch plan and timeline

Google Play requires a new personal developer account to run a closed test with at least 12 testers opted in for 14 continuous days before it can apply for production access. Verify the current rule in Play Console when you register. This test, more than development, controls the launch date.

| When | What |
| --- | --- |
| Week 0 (this week) | Create the developer account and finish identity verification. Recruit 15 to 20 testers (friends, family, classmates). Choose and pin the Godot version. Confirm the AdMob plugin works. Pick asset packs and check licenses. Run name checks. |
| Week 1 | Core game: grid, movement, swipe controls, push rules, win detection, restart, saving. Placeholder art. At the end of the week, upload an early build with about 10 levels to the closed test so the 14-day clock starts. |
| Weeks 2 to 3 | Generator, solver and the final 50 levels. Final art and audio, menus, level select, localization, ads and consent form. Ship updated builds to the same closed test and fix tester feedback. Prepare the store listing in 3 languages. |
| End of week 3 | 14 days complete with 12 or more testers opted in: apply for production access. |
| Week 4 | Google review, then launch. Review time varies, so keep a buffer of several days. |

Risk: Google's review of the first build can take a few days, which delays the 14-day clock. If that happens, the realistic launch date moves to week 5.

## 15. Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Testers drop out during the 14 days | Clock resets, launch slips | Recruit 15 to 20, remind them in a group chat, ask them not to uninstall |
| Name or trademark conflict | Listing removed after launch | Avoid the word Sokoban, run name checks in week 0 |
| Bad or unfair levels with no undo | Bad reviews, uninstalls | Solver verification, personal play of all 50, forgiving early levels |
| Search-only discovery is slow | Misses the 5,000 target | Strong localized listing, launch posts as fallback, level updates to earn reviews |
| AdMob plugin incompatible with the Godot version | Delays monetization | Confirm in week 0 |
| Arabic font and mirrored layout issues | Poor experience in Arabic | Test early with a native speaker |
| Asset pack license problems | Takedown risk | License file from day one |
| No analytics in v1 | Blind to difficulty problems | Watch reviews and Play Console, add analytics in v1.1 |
| Only 50 levels | Limited ad revenue per install | Plan post-launch level updates |

## 16. After version 1

Candidates for v1.1 and later, in rough priority order: basic analytics, more levels through updates, undo as a rewarded-ad feature, hints, star ratings, a remove-ads purchase, banner ads, skins or themes, and more languages.

## 17. Assumptions to review

- Portrait orientation only.
- Swipe threshold, one queued swipe, and animation speed.
- Restart confirmation after 5 or more moves.
- Level select screen (first feature to cut).
- Ad rules: 3 ad-free levels, one ad every 3 levels, 60 seconds minimum gap.
- At least 300 generated candidates, best 50 kept.
- The grid size and crate counts in the difficulty table.
- Minimum Android version and a download size under 50 MB.
- Rating guardrail of 4.0 or higher.
- Launch posts as a fallback for discovery.

## 18. Next steps

1. Review section 17 and correct anything you disagree with.
2. Open the Google Play developer account and finish verification.
3. Recruit 15 to 20 testers.
4. Run the name checks for Pixel Porter.
5. Pin the Godot version and confirm the AdMob plugin works with it.
6. Pick asset packs and start the licenses file.
7. Begin the core game.
