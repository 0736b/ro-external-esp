"""
    - Ragnarok Online | Monster, Item ESP

    Environments:
        - game_version: "2021-11-17_Ragexe_4thjob.exe" (running locally by rAthena Server Emulator)
        - game_graphic: windowed 1024x768 (32-bit)

    for Educational purpose only!
"""

import os
import time
import pyray
import colorsys
import numpy as np
from memory import Process
from classes_ro import CGameMode, CRenderer, Vector3D


def clear():
    os.system('cls')

def get_ro_gamemode(ro):
    pattern_pointer_to_gamemode = b"\\x72\\x02\\x8B\\x36\\x8B\\x0D...."     # 72 02 8B 36 8B 0D ?? ?? ?? ??
    addr_pointer_to_gamemode = int.from_bytes(ro.read_bytes(ro.find_pattern(pattern_pointer_to_gamemode) + 0x6, 4), byteorder='little')
    addr_gamemode = ro.read_int(addr_pointer_to_gamemode)
    if CGameMode(ro, addr_gamemode).valid:
        return CGameMode(ro, addr_gamemode)
    return None

def get_ro_renderer(ro, ro_graphics_color_bits):
    pattern_pointer_to_renderer = b"\\xFF\\x15....\\xA1....\\xB9\\x80\\x03\\xF8\\x00\\xFF.\\x28\\xFF.\\x24"     # FF 15 ?? ?? ?? ?? A1 ?? ?? ?? ?? B9 80 03 F8 00 FF ?? 28 FF ?? 24
    addr_pointer_to_renderer = int.from_bytes(ro.read_bytes(ro.find_pattern(pattern_pointer_to_renderer) + 0x7, 4), byteorder='little')
    addr_renderer = ro.read_int(addr_pointer_to_renderer)
    if CRenderer(ro, addr_renderer).rgb_bitcount == ro_graphics_color_bits:
        return CRenderer(ro, addr_renderer)
    return None

def dist_to_hue(dist):
    _dist = dist
    min_dist = 1.0
    max_dist = 96.0
    min_hue = 0.0
    max_hue = 180.0
    if _dist <= min_dist:
        _dist = min_dist
    return (_dist / max_dist) * max_hue


if __name__ == "__main__":

    clear()

    ro_process_name = "2021-11-17_Ragexe_4thjob.exe"
    ro_window_title = "RO Offline 2022"
   
    ro = Process(ro_process_name)
    (wx, wy, ww, wh) = Process.get_window_coord(ro_window_title)
    print(f"window_info: {wx, wy, ww, wh}")

    ro_graphics_setting_color_bits = 32

    print(f"Scanning addresses...")
    gamemode = get_ro_gamemode(ro)
    renderer = get_ro_renderer(ro, ro_graphics_setting_color_bits)

    if gamemode is None or renderer is None:
        print(f"Failed to get gamemode or renderer address, update pattern!")
        exit(-1)

    print(f"Founded gamemode:{hex(gamemode.addr)}, renderer:{hex(renderer.addr)}, launching overlay in 3 sec.")

    time.sleep(3)

    # overlay init (top-most, transparent, undecorate)
    pyray.set_config_flags(pyray.FLAG_WINDOW_TRANSPARENT | pyray.FLAG_WINDOW_TOPMOST | pyray.FLAG_WINDOW_MOUSE_PASSTHROUGH)
    pyray.init_window(ww, wh, "ro-external-esp")
    pyray.set_window_position(wx, wy)
    pyray.set_window_state(pyray.FLAG_WINDOW_UNDECORATED)
    pyray.set_target_fps(60)

    clear()

    # for drawing
    sx_offset = 10
    sy_offset = 30
    circle_rad = 4.5
    shadow_offset = 2

    # for coloring line based on distance
    max_distance = 96
    min_dist = 97

    while not pyray.window_should_close():

        try:

            if not ro.is_running():
                break

            gamemode = gamemode.update()
            renderer = renderer.update()

            if gamemode.valid and renderer.rgb_bitcount == ro_graphics_setting_color_bits:

                pyray.begin_drawing()
                pyray.clear_background(pyray.BLANK)

                world = gamemode.world
                view = gamemode.view

                viewmatrix = view.viewmatrix_matrix
                c3dattr = world.c3dattr

                # player info
                player = world.player
                player_job = player.job_id_int
                player_pos = player.pos_vector3d
                player_pos_cell = c3dattr.convert_world_to_cell_coord(player_pos.x, player_pos.z)
                player_job_id_text = f"Job ID: {player_job}"
                player_pos_cell_text = f"Coord: {player_pos_cell[0]}, {player_pos_cell[1]}"
                player_screen_x, player_screen_y = renderer.project_vertex(player_pos, viewmatrix)
                
                # draw player info
                pyray.draw_text(player_job_id_text, int(player_screen_x + sx_offset - shadow_offset) - pyray.measure_text(player_job_id_text, 8) // 2, int(player_screen_y) - 20, 8, pyray.BLACK)
                pyray.draw_text(player_job_id_text, int(player_screen_x + sx_offset) - pyray.measure_text(player_job_id_text, 8) // 2, int(player_screen_y) - 20, 8, pyray.WHITE)
                pyray.draw_text(player_pos_cell_text, int(player_screen_x + sx_offset - shadow_offset) - pyray.measure_text(player_pos_cell_text, 8) // 2, int(player_screen_y) - 30, 8, pyray.BLACK)
                pyray.draw_text(player_pos_cell_text, int(player_screen_x + sx_offset) - pyray.measure_text(player_pos_cell_text, 8) // 2, int(player_screen_y) - 30, 8, pyray.WHITE)

                # actors
                len_actor_list = world.len_actor_list
                if len_actor_list != 0:
                    
                    actor_list = world.actor_list

                    # iterate actor_list
                    while actor_list.has_next():

                        actor = actor_list.get_current()

                        if not actor.is_pc: # check if actor is player

                            # actor info
                            actor_id = actor.id_int
                            actor_pos = actor.pos_vector3d
                            actor_pos_cell = c3dattr.convert_world_to_cell_coord(actor_pos.x, actor_pos.z)
                            distance = np.linalg.norm(player_pos.get_array() - actor_pos.get_array())
                            min_dist = distance if distance < min_dist else min_dist
                            actor_id_text = f"Mob ID: {actor_id}"
                            actor_pos_cell_text = f"Coord: {actor_pos_cell[0]}, {actor_pos_cell[1]}"
                            actor_screen_x, actor_screen_y = renderer.project_vertex(actor_pos, viewmatrix)
                            color_by_dist = pyray.color_from_hsv(dist_to_hue(distance), 1, 1)

                            # draw actor info
                            pyray.draw_circle(int(actor_screen_x + sx_offset), int(actor_screen_y + sy_offset), circle_rad, color_by_dist)
                            pyray.draw_line(int(actor_screen_x + sx_offset), int(actor_screen_y + sy_offset), int(player_screen_x + sx_offset), int(player_screen_y + sy_offset), color_by_dist)
                            pyray.draw_text(actor_id_text, int(actor_screen_x + sx_offset - shadow_offset) - pyray.measure_text(actor_id_text, 8) // 2, int(actor_screen_y) - 10, 8, pyray.BLACK)
                            pyray.draw_text(actor_id_text, int(actor_screen_x + sx_offset) - pyray.measure_text(actor_id_text, 8) // 2, int(actor_screen_y) - 10, 8, color_by_dist)
                            pyray.draw_text(actor_pos_cell_text, int(actor_screen_x + sx_offset - shadow_offset) - pyray.measure_text(actor_pos_cell_text, 8) // 2, int(actor_screen_y) - 20, 8, pyray.BLACK)
                            pyray.draw_text(actor_pos_cell_text, int(actor_screen_x + sx_offset) - pyray.measure_text(actor_pos_cell_text, 8) // 2, int(actor_screen_y) - 20, 8, color_by_dist)

                        actor_list.go_next()

                # items (sometime work great, sometime i think this cause overlay updating failed.)
                len_item_list = world.len_item_list
                if len_item_list != 0:

                    item_list = world.item_list

                    # iterate item_list
                    while item_list.has_next():

                        item = item_list.get_current()

                        # item info
                        item_id = item.id_int
                        item_pos = item.pos_vector3d
                        item_pos_cell = c3dattr.convert_world_to_cell_coord(item_pos.x, item_pos.z)
                        item_id_text = f"Item ID: {item_id}"
                        item_pos_cell_text = f"Coord: {item_pos_cell[0]}, {item_pos_cell[1]}"
                        item_screen_x, item_screen_y = renderer.project_vertex(item_pos, viewmatrix)

                        # draw item
                        pyray.draw_circle_lines(int(item_screen_x + sx_offset), int(item_screen_y + sy_offset), circle_rad * 2, pyray.BLACK)
                        pyray.draw_line(int((item_screen_x + sx_offset) - circle_rad), int((item_screen_y + sy_offset) - circle_rad), int(player_screen_x + sx_offset), int(player_screen_y + sy_offset), pyray.BLACK)
                        pyray.draw_text(item_id_text, int(item_screen_x + sx_offset - shadow_offset) - pyray.measure_text(item_id_text, 8) // 2, int(item_screen_y) - 10, 8, pyray.BLACK)
                        pyray.draw_text(item_id_text, int(item_screen_x + sx_offset) - pyray.measure_text(item_id_text, 8) // 2, int(item_screen_y) - 10, 8, pyray.WHITE)
                        pyray.draw_text(item_pos_cell_text, int(item_screen_x + sx_offset - shadow_offset) - pyray.measure_text(item_pos_cell_text, 8) // 2, int(item_screen_y) - 20, 8, pyray.BLACK)
                        pyray.draw_text(item_pos_cell_text, int(item_screen_x + sx_offset) - pyray.measure_text(item_pos_cell_text, 8) // 2, int(item_screen_y) - 20, 8, pyray.WHITE)

                        item_list.go_next()

                pyray.draw_circle(int(player_screen_x + sx_offset), int(player_screen_y + sy_offset), circle_rad, pyray.color_from_hsv(dist_to_hue(min_dist), 1, 1))
                
                min_dist = 97   # reset min dist

                pyray.end_drawing()
            
            else:
                # finding gamemode, renderer again.
                gamemode = get_ro_gamemode(ro)
                renderer = get_ro_renderer(ro, ro_graphics_setting_color_bits)

        except KeyboardInterrupt: break

        except Exception as e: continue

    pyray.close_window()