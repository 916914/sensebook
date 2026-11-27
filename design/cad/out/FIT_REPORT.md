# SenseBook: fit report

> Worked out from the CAD by `build_model.py` and `check_model.py`. The bought parts are drawn at their published sizes (see `../SOURCES.md`). **Nothing here has been printed or measured.** CAD can prove that the drawn parts do not clash; only a print proves the real fit.

## 1. Tolerances the model is drawn for

| What | Value | Where it is used |
|---|---|---|
| Printed PETG part, general | ±0.2 mm | every printed part |
| Sliding fit, printed | 0.15 mm clearance per side (0.3 mm on the width) | button caps, mute slider, cover tongue |
| Steel pin in a drilled hole | 0.05 mm per side | leg hinge pin, knuckle pin (holes are drilled to size after printing) |
| Bought part to anything it must not touch | at least 0.3 mm | boards, cells, speaker, camera |
| Cut sheet metal outline | ±0.1 mm | blades, heat spreader |
| Cut length of tube or pin | ±0.2 mm | stick tubes, hinge pins |
| Turned part | ±0.05 mm | lens bezel, thumb nut |

## 2. Interference check

- Bodies checked: **89**, every pair whose boxes come within 0.6 mm, by exact solid intersection.
- Clashes in the assembled pose: **0**.
- Clashes between parts that move against each other, in each pose: table hardcover **0**, table paperback **0**, tripod no book **0**, in hand **0**, extended **0**, stowed **0**.
- Pairs that overlap on purpose (a screw in its boss, a wire on its pad): 13. They are listed in section 3 as *joined*.

## 3. Clearance between every pair of parts that touch or come within 0.5 mm

144 pairs. **0** need a check on the first print because the gap is smaller than the print tolerance, **0** are closer than our 0.3 mm rule, **0** are tighter than the fit they were drawn for, 57 are designed fits at their drawn clearance, 20 are clear, and 67 touch or overlap on purpose.

| Part A | Part B | Gap in CAD (mm) | Fit | Drawn clearance (mm) | What it is | Result |
|---|---|---|---|---|---|---|
| `camera_lens_m12` | `camera_holder_m12` | 0.02 | thread | 0.02 | M12 lens thread in its holder (one bought assembly) | as designed |
| `blade_left` | `blade_knuckle_left` | 0.03 | clamped | 0.03 | blade in the knuckle slit, pinched by the clamp screw (saw the slit to 0.45 mm) | as designed |
| `blade_right` | `blade_knuckle_right` | 0.03 | clamped | 0.03 | blade in the knuckle slit, pinched by the clamp screw (saw the slit to 0.45 mm) | as designed |
| `camera_lens_m12` | `camera_lens_glass` | 0.04 | bonded | 0.04 | front element in the lens barrel (one bought part) | as designed |
| `stick_outer_tube` | `stick_glide_bush` | 0.04 | sliding | 0.04 | glide bush on the inner tube runs in the outer tube | as designed |
| `blade_knuckle_left` | `knuckle_pin` | 0.05 | pin | 0.05 | knuckle turns on the pin: drill to 1.7 mm | as designed |
| `blade_knuckle_right` | `knuckle_pin` | 0.05 | pin | 0.05 | knuckle turns on the pin: drill to 1.7 mm | as designed |
| `hub_body` | `knuckle_pin` | 0.05 | pin | 0.05 | knuckle pin: drill the printed hole to 1.6 mm | as designed |
| `hub_body` | `leg_pin` | 0.05 | pin | 0.05 | hinge pin: drill the printed hole to 2.0 mm | as designed |
| `pi_gpio_pads` | `harness_left` | 0.05 | bonded | 0.05 | wires soldered to the Pi's GPIO pads | as designed |
| `pi_gpio_pads` | `harness_right` | 0.05 | bonded | 0.05 | wires soldered to the Pi's GPIO pads | as designed |
| `rear_leg` | `leg_pin` | 0.05 | pin | 0.05 | hinge pin through the leg barrel: drill to 2.1 mm so the leg turns freely | as designed |
| `shell_front_tub` | `status_dot_pipes` | 0.05 | press | 0.05 | clear pins pushed into the dot holes, a drop of glue | as designed |
| `tilt_joint_head` | `tilt_pivot_screw` | 0.05 | pin | 0.05 | M3 pivot through the joint tongue: drill to 3.1 mm | as designed |
| `amp_board_max98357a` | `speaker_leads` | 0.06 | bonded | 0.05 | leads soldered to the amp board | as designed |
| `blade_left` | `blade_clamp_screw_left` | 0.10 | pin | 0.1 | M1.6 clamp screw through the 1.8 mm hole in the blade | as designed |
| `blade_right` | `blade_clamp_screw_right` | 0.10 | pin | 0.1 | M1.6 clamp screw through the 1.8 mm hole in the blade | as designed |
| `pi_zero_2w_pcb` | `harness_left` | 0.10 | bonded | 0.05 | wires soldered to the Pi's GPIO pads | as designed |
| `pi_zero_2w_pcb` | `harness_right` | 0.10 | bonded | 0.05 | wires soldered to the Pi's GPIO pads | as designed |
| `shell_front_tub` | `haptic_motor` | 0.10 | bonded | 0.1 | motor stuck to the front wall with its own adhesive pad | as designed |
| `shell_front_tub` | `light_ring_diffuser` | 0.10 | press | 0.1 | diffuser ring glued into the lens opening | as designed |
| `shell_front_tub` | `speaker` | 0.10 | bonded | 0.1 | speaker held on the front wall by a 0.1 mm glue or tape line | as designed |
| `status_leds` | `status_dot_pipes` | 0.10 | bonded | 0.1 | LED faces the end of its light pipe | as designed |
| `stick_inner_tube` | `stick_collar` | 0.10 | sliding | 0.1 | inner tube slides through the collar, which grips it when twisted | as designed |
| `cell_foam_left` | `camera_flex` | 0.15 | bonded | 0.15 | flex passes behind the foam pad | as designed |
| `hub_body` | `hub_sensor_lead` | 0.15 | sliding | 0.15 | lead laid in its 1.2 mm groove in the hub | as designed |
| `mic_mute_slider` | `mic_mute_flag` | 0.15 | sliding | 0.15 | flag sits beside the cap, in the same slot | as designed |
| `pi_gpio_pads` | `camera_flex` | 0.15 | bonded | 0.15 | flex lies along the Pi, held by a strip of tape | as designed |
| `rear_leg` | `torsion_spring_left` | 0.15 | hinge | 0.15 | spring rides on the leg barrel | as designed |
| `rear_leg` | `torsion_spring_right` | 0.15 | hinge | 0.15 | spring rides on the leg barrel | as designed |
| `shell_front_tub` | `mic_mute_flag` | 0.15 | sliding | 0.15 | orange flag (paint or sticker on the slider) seen through the slot | as designed |
| `shell_front_tub` | `mic_mute_slider` | 0.15 | sliding | 0.15 | slider cap in its slot | as designed |
| `stick_outer_tube` | `hub_sensor_lead` | 0.15 | sliding | 0.15 | lead through the notch filed in the foot of the outer tube | as designed |
| `pi_gpio_pads` | `hub_cord_tail` | 0.15 | bonded | 0.1 | cord soldered to the Pi's GPIO pads | as designed |
| `mic_mute_switch` | `mic_mute_slider` | 0.18 | sliding | 0.1 | slider cap pocket over the switch lever | as designed |
| `hub_body` | `blade_clamp_screw_left` | 0.20 | hinge | 0.2 | clamp screw head swings past the hub | as designed |
| `hub_body` | `blade_clamp_screw_right` | 0.20 | hinge | 0.2 | clamp screw head swings past the hub | as designed |
| `hub_body` | `blade_knuckle_left` | 0.20 | hinge | 0.2 | knuckle in its notch, turns on the pin | as designed |
| `hub_body` | `blade_knuckle_right` | 0.20 | hinge | 0.2 | knuckle in its notch, turns on the pin | as designed |
| `light_ring_diffuser` | `light_ring_leds` | 0.20 | bonded | 0.2 | LEDs face the back of the diffuser | as designed |
| `pi_zero_2w_pcb` | `camera_flex` | 0.20 | bonded | 0.15 | flex lies along the Pi, held by a strip of tape | as designed |
| `shell_front_tub` | `dac_jack` | 0.20 | sliding | 0.2 | headphone jack nose in its hole in the side wall | as designed |
| `shell_front_tub` | `tilt_joint_head` | 0.20 | hinge | 0.2 | lugs swing over the joint collar (0.2) and beside its tongue (0.3) | as designed |
| `shell_front_tub` | `usb_c_receptacle` | 0.20 | sliding | 0.2 | USB-C shell in its opening in the side wall | as designed |
| `pi_zero_2w_pcb` | `hub_cord_tail` | 0.20 | bonded | 0.1 | cord soldered to the Pi's GPIO pads | as designed |
| `shell_front_tub` | `camera_flex` | 0.21 | bonded | 0.2 | flex passes under the top wall | as designed |
| `lens_bezel` | `camera_lens_m12` | 0.21 | sliding | 0.2 | lens rim inside the bezel opening | as designed |
| `hub_body` | `torsion_spring_left` | 0.25 | hinge | 0.1 | spring in its pocket, free to wind: 0.25 around it, 0.1 at its end face | as designed |
| `hub_body` | `torsion_spring_right` | 0.25 | hinge | 0.1 | spring in its pocket, free to wind: 0.25 around it, 0.1 at its end face | as designed |
| `pi_zero_2w_pcb` | `microsd_card` | 0.25 | bonded | 0.25 | card in its slot on the Pi | as designed |
| `hub_body` | `rear_leg` | 0.30 | hinge | 0.3 | leg barrel and arm in the hub slot | as designed |
| `stick_inner_tube` | `hub_cord_riser` | 0.30 | sliding | 0.3 | cord leaving the joint head just above the top of the tube | as designed |
| `tilt_joint_head` | `hub_cord_riser` | 0.30 | sliding | 0.3 | cord in the hole and slot of the joint head | as designed |
| `stick_outer_tube` | `hub_sensor_switch` | 0.33 | bonded | 0.25 | sensor board glued in its pocket, beside the tube | as designed |
| `hub_body` | `blade_left` | 0.40 | hinge | 0.3 | blade root swings with its knuckle | as designed |
| `hub_body` | `blade_right` | 0.40 | hinge | 0.3 | blade root swings with its knuckle | as designed |
| `stick_outer_tube` | `stick_inner_tube` | 0.50 | sliding | 0.5 | telescope: 8 mm tube in the 9 mm bore, guided by the bush and collar | as designed |
| `dac_board_pcm5102` | `button_vol_down` | 0.30 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `charger_board` | 0.30 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `dac_board_pcm5102` | 0.30 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `light_ring_pcb` | 0.30 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `amp_board_max98357a` | 0.32 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `fuel_gauge_max17048` | 0.32 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `pi_zero_2w_pcb` | 0.32 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `cell_left` | 0.39 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `cell_right` | 0.39 | clearance | 0.3 | neighbours that must not touch | ok |
| `camera_board_imx708` | `cell_left` | 0.40 | clearance | 0.3 | neighbours that must not touch | ok |
| `camera_board_imx708` | `cell_right` | 0.40 | clearance | 0.3 | neighbours that must not touch | ok |
| `camera_connector` | `camera_flex` | 0.40 | clearance | 0.3 | neighbours that must not touch | ok |
| `dac_board_pcm5102` | `mic_mute_switch` | 0.40 | clearance | 0.3 | neighbours that must not touch | ok |
| `dac_board_pcm5102` | `volume_board` | 0.40 | clearance | 0.3 | neighbours that must not touch | ok |
| `light_ring_pcb` | `camera_lens_m12` | 0.40 | clearance | 0.3 | neighbours that must not touch | ok |
| `speaker` | `speaker_leads` | 0.45 | clearance | 0.3 | neighbours that must not touch | ok |
| `pi_gpio_pads` | `cell_foam_left` | 0.45 | clearance | 0.3 | neighbours that must not touch | ok |
| `pi_gpio_pads` | `cell_foam_right` | 0.45 | clearance | 0.3 | neighbours that must not touch | ok |
| `shell_front_tub` | `status_leds` | 0.50 | clearance | 0.3 | neighbours that must not touch | ok |
| `light_ring_leds` | `camera_lens_m12` | 0.50 | clearance | 0.3 | neighbours that must not touch | ok |
| `amp_board_max98357a` | `amp_board_parts` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `blade_left` | `blade_coat_left` | 0 (touching) | bonded | 0 | coating on the blade | by design |
| `blade_right` | `blade_coat_right` | 0 (touching) | bonded | 0 | coating on the blade | by design |
| `button_ask` | `ask_button_board` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `button_back` | `top_bar_switches` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `button_forward` | `top_bar_switches` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `button_play_pause` | `top_bar_switches` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `button_vol_down` | `volume_board` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `button_vol_up` | `volume_board` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `camera_board_imx708` | `camera_connector` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `camera_board_imx708` | `camera_screws` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `camera_holder_m12` | `camera_board_imx708` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `cell_left` | `cell_foam_left` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `cell_left` | `cell_pcm_left` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `cell_right` | `cell_foam_right` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `cell_right` | `cell_pcm_right` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `charger_board` | `charger_board_parts` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `charger_board` | `usb_c_receptacle` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `dac_board_pcm5102` | `dac_jack` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `heat_spreader` | `thermal_pad` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `hub_body` | `hub_sensor_switch` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `hub_body` | `stick_outer_tube` | 0 (touching) | press | 0.08 | tube pushed into the hub bore and glued | by design |
| `hub_sensor_lead` | `hub_sensor_switch` | 0 (touching) | bonded | 0 | lead soldered to the sensor board | by design |
| `lens_bezel` | `light_ring_diffuser` | 0 (touching) | press | 0 | bezel ring glued inside the diffuser | by design |
| `light_ring_pcb` | `light_ring_leds` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `pi_zero_2w_chips` | `thermal_pad` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `pi_zero_2w_pcb` | `pi_gpio_pads` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `pi_zero_2w_pcb` | `pi_zero_2w_chips` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `pi_zero_2w_pcb` | `pi_zero_2w_connectors` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `rear_leg` | `rear_leg_pad` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_back_cover` | `cover_screw_1` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_back_cover` | `cover_screw_2` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_back_cover` | `cover_screw_3` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_back_cover` | `cover_screw_4` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_back_cover` | `heat_spreader` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_back_cover` | `pi_zero_2w_pcb` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_front_tub` | `button_ask` | 0 (touching) | sliding | 0.15 | button cap in its opening, held in by its inner lip | by design |
| `shell_front_tub` | `button_back` | 0 (touching) | sliding | 0.15 | button cap in its opening, held in by its inner lip | by design |
| `shell_front_tub` | `button_forward` | 0 (touching) | sliding | 0.15 | button cap in its opening, held in by its inner lip | by design |
| `shell_front_tub` | `button_play_pause` | 0 (touching) | sliding | 0.15 | button cap in its opening, held in by its inner lip | by design |
| `shell_front_tub` | `button_vol_down` | 0 (touching) | sliding | 0.15 | button cap in its opening, held in by its inner lip | by design |
| `shell_front_tub` | `button_vol_up` | 0 (touching) | sliding | 0.15 | button cap in its opening, held in by its inner lip | by design |
| `shell_front_tub` | `camera_board_imx708` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_front_tub` | `mic_left` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_front_tub` | `mic_right` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `shell_front_tub` | `shell_back_cover` | 0 (touching) | sliding | 0.15 | cover tongue inside the tub wall; the two shells meet at the seam | by design |
| `shell_front_tub` | `tilt_pivot_screw` | 0 (touching) | pin | 0.1 | M3 pivot through the two lugs: drill to 3.2 mm | by design |
| `shell_front_tub` | `tilt_thumb_nut` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `status_led_board` | `status_leds` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `stick_inner_tube` | `stick_glide_bush` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `stick_inner_tube` | `tilt_joint_head` | 0 (touching) | press | 0.05 | joint spigot pushed into the inner tube and glued | by design |
| `stick_outer_tube` | `stick_collar` | 0 (touching) | press | 0.06 | collar pushed onto the outer tube | by design |
| `tilt_pivot_screw` | `tilt_thumb_nut` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `top_bar_board` | `top_bar_switches` | 0 (touching) | seated | 0 | parts touch by design: seated, glued, taped or soldered | by design |
| `blade_knuckle_left` | `blade_clamp_screw_left` | overlap | joined | 0 | clamp screw threaded into the knuckle | by design |
| `blade_knuckle_right` | `blade_clamp_screw_right` | overlap | joined | 0 | clamp screw threaded into the knuckle | by design |
| `cell_pcm_left` | `battery_leads` | overlap | joined |  | leads soldered to the board or leaving the pack | by design |
| `cell_pcm_right` | `battery_leads` | overlap | joined |  | leads soldered to the board or leaving the pack | by design |
| `hub_cord_riser` | `hub_cord` | overlap | joined |  | cord joined to the coil | by design |
| `hub_cord_tail` | `hub_cord_riser` | overlap | joined |  | cord joined to the next length of cord | by design |
| `hub_sensor_lead` | `hub_cord` | overlap | joined |  | lead joined to the coil or soldered to the sensor | by design |
| `pi_zero_2w_chips` | `camera_flex` | overlap | bonded | 0.15 | flex lies along the Pi, held by a strip of tape | by design |
| `shell_front_tub` | `camera_screws` | overlap | joined |  | tapping screw through the camera board into its post | by design |
| `shell_front_tub` | `cover_screw_1` | overlap | joined |  | tapping screw in its printed boss | by design |
| `shell_front_tub` | `cover_screw_2` | overlap | joined |  | tapping screw in its printed boss | by design |
| `shell_front_tub` | `cover_screw_3` | overlap | joined |  | tapping screw in its printed boss | by design |
| `shell_front_tub` | `cover_screw_4` | overlap | joined |  | tapping screw in its printed boss | by design |

## 4. Wall thickness of the printed parts

Measured on the STL files by casting rays inward from 6,000 points on each part. The minimum is usually a chamfer, a rib edge or the rim of a hole, so read the 5th percentile and the share under 0.8 mm as well. 0.8 mm is two passes of a 0.4 mm nozzle.

| Part | Thinnest (mm) | 5th percentile (mm) | Median (mm) | Under 0.8 mm | Under 1.2 mm | Volume (cm³) | Watertight |
|---|---|---|---|---|---|---|---|
| `blade_knuckle_left` | 0.28 | 1.27 | 3.67 | 0.5% | 4.2% | 0.41 | yes |
| `blade_knuckle_right` | 0.36 | 1.29 | 3.66 | 0.6% | 4.0% | 0.41 | yes |
| `button_ask` | 0.67 | 1.00 | 3.00 | 0.4% | 19.4% | 0.44 | yes |
| `button_back` | 0.08 | 1.00 | 3.60 | 0.8% | 20.4% | 0.17 | yes |
| `button_forward` | 0.08 | 1.00 | 3.60 | 0.9% | 20.5% | 0.17 | yes |
| `button_play_pause` | 1.00 | 1.00 | 3.60 | 0.0% | 20.0% | 0.17 | yes |
| `button_vol_down` | 1.00 | 1.00 | 3.50 | 0.0% | 18.6% | 0.08 | yes |
| `button_vol_up` | 1.00 | 1.00 | 3.50 | 0.0% | 18.5% | 0.08 | yes |
| `hub_body` | 0.05 | 1.62 | 9.43 | 1.2% | 2.0% | 8.40 | yes |
| `light_ring_diffuser` | 2.40 | 2.40 | 2.40 | 0.0% | 0.0% | 0.46 | yes |
| `mic_mute_slider` | 0.50 | 0.50 | 2.20 | 13.5% | 24.6% | 0.02 | yes |
| `rear_leg` | 1.55 | 1.55 | 2.60 | 0.0% | 0.0% | 3.23 | yes |
| `rear_leg_pad` | 2.00 | 2.00 | 2.00 | 0.0% | 0.0% | 1.38 | yes |
| `shell_back_cover` | 0.05 | 0.90 | 1.80 | 3.2% | 11.7% | 8.64 | yes |
| `shell_front_tub` | 0.75 | 1.80 | 1.80 | 0.7% | 1.8% | 18.72 | yes |
| `status_dot_pipes` | 2.05 | 2.05 | 2.40 | 0.0% | 0.0% | 0.04 | yes |
| `stick_collar` | 1.00 | 1.00 | 1.44 | 0.0% | 7.7% | 0.42 | yes |
| `tilt_joint_head` | 0.09 | 1.95 | 2.60 | 0.3% | 0.6% | 0.59 | yes |

## 5. Cable routes

Each bundle is drawn as a solid along its route and goes through the same clash check as every other part. Runs are drawn straight with sharp corners; real wire takes a radius, so allow the spare length shown.

| Route | What it carries | Bundle (mm) | Length (mm) | Bends | Stock | Spare (mm) | Clashes | Least clearance (mm) |
|---|---|---|---|---|---|---|---|---|
| `harness_left` | Harness, left: I2S to the amp and DAC, buttons, LEDs, motor | 1.4 | 40.1 | 4 | cut to length |  | 0 | 0.05 to `pi_gpio_pads` |
| `harness_right` | Harness, right: 5 V, I2C to the fuel gauge | 1.4 | 32.5 | 3 | cut to length |  | 0 | 0.05 to `pi_gpio_pads` |
| `battery_leads` | Battery leads: both packs in parallel to the charger board | 1.4 | 85.3 | 5 | pack leads, 150 mm each (Akyga sheet) | 214.7 | 0 | 0.5 or more |
| `speaker_leads` | Speaker leads from the amp | 0.9 | 43.2 | 2 | cut to length |  | 0 | 0.06 to `amp_board_max98357a` |
| `hub_cord_tail` | Hub-sensor cord: from the joint head into the unit, up to the Pi (GPIO 8 and ground) | 0.9 | 50.6 | 5 | cut to length |  | 0 | 0.15 to `pi_gpio_pads` |
| `camera_flex` | Camera flex, 22-pin to 15-pin, folded along the Pi and over the camera | 0.15 | 78.9 |  | stock cable, 150 mm (Raspberry Pi drawing) | 71.1 | 0 | 0.15 to `cell_foam_left` |
| `hub_cord_riser` | Hub-sensor cord: up through the joint head and out of its back | 0.9 | 16.2 | 2 | cut to length |  | 0 | 0.30 to `stick_inner_tube` |
| `hub_sensor_lead` | Hub-sensor lead: from the sensor, down a groove in the hub, into the foot of the stick | 0.9 | 26.2 | 6 | cut to length |  | 0 | 0.15 to `hub_body` |
| `hub_cord` | Coiled 2-wire cord to the hub sensor | 0.9 | 304 |  | cut to length |  | 0 | 0.5 or more |

- **Camera flex:** the route is 78.9 mm, the stock cable is 150 mm. The spare length has to be folded flat behind the Pi; the model does not draw that fold. Do not crease the flex: fold it over a 1 mm rod.
- **Hub cord:** a coil of 5.5 mm outside diameter inside the 7 mm bore of the inner tube, 304 mm of cord, stretching by 90 mm when the stick is pulled out. Whether a hand-wound coil stretches that far without snagging is not proven: test it on the first build.
- **Battery leads:** both packs are joined in parallel at the charger board. The packs come with 150 mm leads; cut them to the route length plus 15 mm.

## 6. Mass and centre of mass

- Assembled mass in the model: **167.3 g** (unit 113.4 g). Printed parts are volume times density; bought parts use the published mass, or an EST where none is published.
- Centre of mass of the unit, in the unit frame: x -0.3, y -20.6, z 22.5 mm.

| Group | Model (g) | `sb_params.MASS` (g) | Difference (g) |
|---|---|---|---|
| unit shells | 37.1 | 37.1 | +0.0 |
| pi zero 2w | 10.3 | 10.3 | +0.0 |
| camera m12 | 9.0 | 9.0 | +0.0 |
| lipo cells | 32.0 | 32.0 | +0.0 |
| speaker | 2.0 | 2.0 | +0.0 |
| audio boards | 4.8 | 4.8 | +0.0 |
| power boards | 5.6 | 5.6 | +0.0 |
| leds buttons motor | 4.0 | 4.0 | +0.0 |
| spreader wiring | 8.2 | 8.2 | -0.0 |
| tilt joint | 3.1 | 3.1 | -0.0 |
| stick tubes cord | 24.4 | 24.4 | -0.0 |
| hub spring | 15.2 | 15.2 | +0.0 |
| blades | 5.9 | 5.9 | -0.0 |
| rear leg pad | 5.8 | 5.8 | -0.0 |

## 7. Tripod stability (no book)

| Case | Mass (g) | Centre of mass height (mm) | Nearest edge of the feet (mm) | Tips at | Sideways push at the unit that tips it (N) |
|---|---|---|---|---|---|
| Model, stick 9 cm | 167.3 | 112.2 | 31.2 (side) | 15.5° | 0.33 |
| Model, stick 18 cm | 167.3 | 179.5 | 31.3 (side) | 9.9° | 0.21 |
| `analysis.py` (point masses from `sb_params.MASS`) | 167.4 | 113.5 | 31.3 | 15.4° | 0.33 |

Sizes in each pose (mm): table hardcover 93.2 x 178.3 x 171.6; table paperback 93.2 x 178.3 x 171.6; tripod no book 93.2 x 178.3 x 171.6; in hand 93.2 x 120.7 x 177.9; extended 93.2 x 174.2 x 281.9; stowed 93.2 x 37.6 x 170.
