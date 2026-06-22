# UI Component Catalog

Use this reference when the user asks for a full UI kit, common UI components, a complete game UI pack, or a well-organized output structure. Generate only the requested modules for narrow tasks; generate the full checklist when the user asks for "全套", "完整", "常用 UI", or "覆盖所有需求".

## Output Categories

When packaging a full kit, keep level folders but organize PNGs by category:

```text
<pack>/
├── overview.png
└── level_01_complete_ui_kit/
    ├── overview.png
    ├── png/
    │   ├── panels/
    │   ├── buttons/
    │   ├── bars/
    │   ├── cards/
    │   ├── slots/
    │   ├── hud/
    │   ├── icons/
    │   ├── frames/
    │   └── images/
    └── godot/
```

Use `package_ui_assets.py --category-subdirs` for this structure. Keep JSON/debug/intermediate files out of public delivery unless explicitly requested.

## Generation Scope Tiers

- `minimal`: core panels, one button family, one bar family, basic icons.
- `standard`: most game screens and HUD needs.
- `complete`: broad reusable UI kit covering menus, HUD, inventory, battle, map, shop, settings, popups, icons, and decoration atoms.
- `project-specific`: derive from the game's genre and user request, then add missing common modules from `standard` or `complete`.

## Complete Common UI Checklist

### 01 Foundations and Panels

- `panel_window_large`, `panel_window_medium`, `panel_window_small`
- `panel_modal`, `panel_popup`, `panel_tooltip`, `panel_toast`
- `panel_header`, `panel_footer`, `panel_sidebar`, `panel_topbar`, `panel_bottombar`
- `panel_content_plain`, `panel_content_decorated`, `panel_scroll_area`
- `frame_outer_large`, `frame_outer_medium`, `frame_outer_small`
- `frame_inner`, `frame_highlight`, `frame_selected`, `frame_locked`
- `divider_horizontal`, `divider_vertical`, `divider_ornament`
- `corner_top_left`, `corner_top_right`, `corner_bottom_left`, `corner_bottom_right`
- `background_panel_fill`, `background_dark_fill`, `background_light_fill`, `background_pattern_tile`

### 02 Buttons and States

Generate every button family in `normal`, `hover`, `pressed`, `disabled`, and `selected` when possible.

- `button_primary`, `button_secondary`, `button_danger`, `button_success`, `button_warning`
- `button_confirm`, `button_cancel`, `button_back`, `button_close`
- `button_icon_square`, `button_icon_round`, `button_tab`, `button_pill`
- `button_plus`, `button_minus`, `button_step_left`, `button_step_right`
- `button_checkbox_empty`, `button_checkbox_checked`
- `button_radio_empty`, `button_radio_checked`
- `button_toggle_off`, `button_toggle_on`
- `button_shop_buy`, `button_shop_sell`, `button_equip`, `button_upgrade`
- `button_start`, `button_continue`, `button_pause`, `button_resume`

### 03 Bars, Meters, and Sliders

Generate background/track and fill separately.

- `progress_health_bg`, `progress_health_fill`
- `progress_mana_bg`, `progress_mana_fill`
- `progress_stamina_bg`, `progress_stamina_fill`
- `progress_xp_bg`, `progress_xp_fill`
- `progress_shield_bg`, `progress_shield_fill`
- `progress_boss_bg`, `progress_boss_fill`
- `progress_loading_bg`, `progress_loading_fill`
- `progress_capacity_bg`, `progress_capacity_fill`
- `progress_cooldown_bg`, `progress_cooldown_fill`
- `slider_track`, `slider_fill`, `slider_handle`
- `meter_segment_empty`, `meter_segment_full`, `meter_segment_warning`

### 04 Cards, Slots, and Lists

- `card_character`, `card_item`, `card_skill`, `card_quest`, `card_reward`
- `card_map_node`, `card_level_select`, `card_dialogue`, `card_codex_entry`
- `slot_inventory_empty`, `slot_inventory_filled`, `slot_inventory_selected`, `slot_inventory_locked`
- `slot_equipment_weapon`, `slot_equipment_armor`, `slot_equipment_accessory`
- `slot_skill_empty`, `slot_skill_ready`, `slot_skill_cooldown`, `slot_skill_locked`
- `slot_reward`, `slot_shop_item`, `slot_crafting_ingredient`
- `row_list_default`, `row_list_hover`, `row_list_selected`, `row_list_disabled`
- `rarity_common_frame`, `rarity_uncommon_frame`, `rarity_rare_frame`, `rarity_epic_frame`, `rarity_legendary_frame`

### 05 HUD and In-Game Overlays

- `hud_health_cluster`, `hud_resource_cluster`, `hud_currency_cluster`
- `hud_objective_tracker`, `hud_quest_tracker`, `hud_notification`
- `hud_minimap_frame`, `hud_compass_frame`, `hud_timer_frame`
- `hud_day_counter`, `hud_wave_counter`, `hud_score_frame`
- `hud_combo_badge`, `hud_rank_badge`, `hud_level_badge`
- `hud_party_member_frame`, `hud_target_frame`, `hud_status_strip`
- `hud_interaction_prompt`, `hud_pickup_prompt`, `hud_warning_banner`

### 06 Menus, Popups, and System Screens

- `panel_main_menu`, `panel_pause_menu`, `panel_settings_menu`
- `panel_confirm_dialog`, `panel_message_dialog`, `panel_error_dialog`
- `panel_inventory_screen`, `panel_equipment_screen`, `panel_skills_screen`
- `panel_shop_screen`, `panel_crafting_screen`, `panel_upgrade_screen`
- `panel_quest_log`, `panel_map_screen`, `panel_level_select`
- `panel_results_victory`, `panel_results_defeat`, `panel_reward_claim`
- `panel_save_slot`, `panel_load_slot`, `panel_profile_card`

### 07 Forms and Settings Controls

- `input_text_bg`, `input_number_bg`, `input_search_bg`
- `dropdown_closed`, `dropdown_open`, `dropdown_item`
- `toggle_on`, `toggle_off`
- `checkbox_empty`, `checkbox_checked`
- `radio_empty`, `radio_checked`
- `keybind_row`, `volume_slider`, `quality_selector`
- `scrollbar_track`, `scrollbar_thumb`, `scrollbar_button_up`, `scrollbar_button_down`

### 08 Map, Progression, and Navigation

- `node_map_normal`, `node_map_current`, `node_map_completed`, `node_map_locked`
- `node_map_elite`, `node_map_boss`, `node_map_shop`, `node_map_rest`, `node_map_event`
- `path_map_available`, `path_map_completed`, `path_map_locked`
- `marker_player`, `marker_target`, `marker_warning`, `marker_exit`
- `breadcrumb_segment`, `tab_selected`, `tab_unselected`
- `arrow_left`, `arrow_right`, `arrow_up`, `arrow_down`

### 09 Battle, Abilities, and Status

- `button_ability_ready`, `button_ability_hover`, `button_ability_pressed`, `button_ability_cooldown`, `button_ability_locked`
- `frame_turn_order`, `frame_enemy_intent`, `frame_target_marker`
- `badge_buff`, `badge_debuff`, `badge_status_dot`, `badge_status_stun`, `badge_status_shield`
- `tag_damage`, `tag_heal`, `tag_critical`, `tag_miss`
- `panel_battle_log`, `panel_action_bar`, `panel_party_status`

### 10 Economy, Inventory, and Crafting

- `icon_coin`, `icon_gem`, `icon_token`, `icon_key`
- `panel_wallet`, `panel_price_tag`, `panel_discount_tag`
- `panel_recipe`, `panel_ingredient_row`, `panel_crafting_queue`
- `progress_crafting_bg`, `progress_crafting_fill`
- `badge_new`, `badge_owned`, `badge_sold_out`, `badge_equipped`

### 11 Icons

Generate icons as transparent PNGs with consistent silhouette, stroke, lighting, and palette.

- Navigation: home, back, close, settings, info, help, search, filter, sort
- Gameplay: attack, defend, magic, heal, stealth, move, inspect, interact
- Resources: coin, gem, food, wood, stone, metal, potion, scroll, key, rope, torch
- Stats: health, mana, stamina, attack, defense, speed, luck, accuracy, crit
- Status: poison, burn, freeze, bleed, stun, shield, curse, blessing
- Rarity: common, uncommon, rare, epic, legendary
- Social/team: party, friend, leader, class, role, morale, loyalty
- Map: camp, shop, boss, treasure, event, exit, locked, completed

### 12 Decoration Atoms and Effects

- `ornament_corner`, `ornament_top`, `ornament_bottom`, `ornament_side`
- `rivet_small`, `rivet_large`, `bolt`, `nail`
- `banner_short`, `banner_long`, `ribbon`, `seal`, `medallion`
- `glow_soft`, `glow_selected`, `sparkle`, `shine_streak`
- `shadow_panel`, `shadow_button`, `edge_highlight`
- `texture_scratches`, `texture_noise_tile`, `texture_paper_tile`, `texture_metal_tile`

## Prompt Rule for Full Kits

For complete kits, generate in batches by category instead of one huge atlas when quality drops. Keep the same style lock, palette, key color, and naming scheme across every batch. Validate each batch before moving to the next category.
