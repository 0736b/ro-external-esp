import win32gui
import pyray as pr

# pr.set_config_flags(pr.FLAG_WINDOW_TRANSPARENT | pr.FLAG_WINDOW_TOPMOST | pr.FLAG_WINDOW_MOUSE_PASSTHROUGH)
# pr.init_window(800, 450, "Hello")
# pr.set_window_state(pr.FLAG_WINDOW_UNDECORATED | pr.FLAG_WINDOW_ALWAYS_RUN)
# while not pr.window_should_close():
#     pr.begin_drawing()
#     pr.clear_background(pr.BLANK)
#     pr.draw_text("Hello world", 190, 200, 20, pr.VIOLET)
#     pr.end_drawing()
#     pr.begin_drawing()
#     pr.clear_background(pr.BLANK)
#     pr.draw_text("Hello Hi", 190, 200, 20, pr.VIOLET)
#     pr.end_drawing()
# pr.close_window()

class Overlay:

    @staticmethod
    def get_window_coord(window_name):
        window = win32gui.FindWindow(None, window_name)
        if window != 0:
            rect = win32gui.GetWindowRect(window)
            x = rect[0]
            y = rect[1]
            w = rect[2] - x
            h = rect[3] - y
            return (x, y, w, h)

    def __init__(self, target_window_title):
        self.target_window_title = target_window_title
        self.window_info = Overlay.get_window_coord(self.target_window_title)
        self._pr = pr

    def init(self):
        self._pr.set_config_flags(pr.FLAG_WINDOW_TRANSPARENT | pr.FLAG_WINDOW_TOPMOST | pr.FLAG_WINDOW_MOUSE_PASSTHROUGH)
        self._pr.init_window(self.window_info[2], self.window_info[3], "OverlayByRayLib")
        self._pr.set_window_state(pr.FLAG_WINDOW_UNDECORATED | pr.FLAG_WINDOW_ALWAYS_RUN)

    def update(self):
        return self._pr.window_should_close()

    def get_color_rgb(self, r, g, b, a):
        return self._pr.Color(r, g, b, a)

    def draw_text(self, text, pos_x, pos_y, size, color):
        self._pr.begin_drawing()
        self._pr.draw_text(text, pos_x, pos_y, size, color)
        self._pr.end_drawing()

    def draw_line(self, start_x, start_y, end_x, end_y, color):
        self._pr.begin_drawing()
        self._pr.draw_line(start_x, start_y, end_x, end_y, color)
        self._pr.end_drawing()

    def draw_circle(self, center_x, center_y, radius, color):
        self._pr.begin_drawing()
        self._pr.draw_circle(center_x, center_y, radius, color)
        self._pr.end_drawing()

    def close(self):
        return self._pr.close_window()


if __name__ == "__main__":
    overlay = Overlay(target_window_title="RO Offline 2022")
    overlay.init()
    while overlay.update():
        overlay.draw_text("Overlay test!", 0, 0, 20, overlay.get_color_rgb(255, 255, 255, 255))
    # overlay.close()