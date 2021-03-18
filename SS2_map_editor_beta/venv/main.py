import tkinter as tk
import tkinter.messagebox as mb
from functools import partial
import json
import math

# TODO
# deleting polygons

class App(tk.Tk):
    # Camera data
    camera_x = 0
    camera_y = 0
    scale = 50

    # params
    now = 0
    curr_bu = 0
    speed_scale = 1.2
    ras = "lvl"
    speed = 3

    # texts
    texts = ("внешние границы", "внутренние границы")

    # arrays, data
    poly_points = []
    load_it = []
    back_up = [[]]
    one_t = 0

    def __init__(self):
        super().__init__()
        self.title("Редактор карт SS2 beta")
        self.form = None
        self.label = tk.Label(text="Начало работы")
        self.label.pack()
        self.canvas = tk.Canvas(self, width=640, height=480, bg="white")
        frame = tk.Frame(self)
        # Buttons
        for form in self.texts:
            btn = tk.Button(frame, text=form.capitalize())
            btn.config(command=partial(self.set_selection, btn, form))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Bindings events to functions
        self.canvas.bind("<Button-1>", self.append_point)
        self.canvas.bind("<Button-3>", self.draw_item)
        self.pressed_keys = {}
        self.released_keys = {}
        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)
        self.bind("<MouseWheel>", self.mouse_w)
        self.canvas.bind("<Motion>", self.mouse_xy)
        self.canvas.pack()
        frame.pack(fill=tk.BOTH)
        self.T = tk.Text()
        self.T.pack()

        # main loop
        self.somebody_touches_my_keyboard()

    # mouse wheel delay event
    def mouse_w(self, event):
        self.pressed_keys["m_w"] = event.delta

    # mouse motion event
    def mouse_xy(self, event):
        self.pressed_keys["m_x"] = event.x
        self.pressed_keys["m_y"] = event.y

    # keyboard
    def key_press(self, event):
        self.pressed_keys[event.keysym] = True

    def key_release(self, event):
        self.released_keys[event.keysym] = True
        self.pressed_keys.pop(event.keysym, None)

    # draw polygon fuction /list [x1,y1,x2,y2,...]/string color/1 or 0 = filled or outlined/
    def draw_polygon(self, polygon, color, filled):
        copy = polygon.copy()
        p = 0
        for r in copy:
            if (p % 2 == 0):
                copy[p] = self.convert_x_to_my_cords(copy[p])
            else:
                copy[p] = self.convert_y_to_my_cords(copy[p])
            p += 1
        poly_cords = tuple(copy)
        if (filled == 1):
            self.canvas.create_polygon(*poly_cords, fill=color)
        else:
            self.canvas.create_polygon(*poly_cords, outline=color, fill='', width=2)

    # making huge string of polygons to save it
    def my_printing(self, load_it):
        sum_text = ""
        for poly in load_it:
            sum_text += "WALL\n"
            if (poly[0] == 1) :
                sum_text += "    OUTER\n"
            else:
                sum_text += "    INNER\n"
            x = 0
            for cords_out in poly:
                if ((x > 0) and (x % 2)):
                    new_t = f'    POINT {poly[x]} {poly[x + 1]}\n'
                    sum_text += new_t
                x += 1
            sum_text += "END\n"
        sum_text += "END"
        return sum_text

    # converting from string to polygon (file reading)
    def my_read(self, file_name):
        f = open(f'{file_name}.{self.ras}', 'r')
        load_it = []
        while (True):
            str = f.readline()
            if (str == "END"):
                break
            if (str.startswith("WALL")):
                new_poly = []
                in_out = f.readline()
                if (in_out == "    OUTER\n"):
                    new_poly.append(1)
                else:
                    new_poly.append(0)
                while (True):
                    str = f.readline()
                    if (str == "END\n"):
                        break
                    if (str.startswith("    POINT")):
                        kom = str.split()
                        new_poly.append(float(kom[1]))
                        new_poly.append(float(kom[2]))
                load_it.append(new_poly.copy())
        return load_it

    # converting from/to my cords system
    def convert_x_to_my_cords(self, old_c):
        return (old_c + self.camera_x) * self.scale + int(self.canvas['width']) / 2

    def convert_y_to_my_cords(self, old_c):
        return (old_c + self.camera_y) * self.scale + int(self.canvas['height']) / 2

    def convert_x_from_my_cords(self, new_c):
        return (new_c - int(self.canvas['width']) / 2) / self.scale - self.camera_x

    def convert_y_from_my_cords(self, new_c):
        return (new_c - int(self.canvas['height']) / 2) / self.scale - self.camera_y

    # drawing grid and Oxy
    def draw_grid(self):
        x_initial = int(-self.camera_x) - math.ceil(int(self.canvas['width']) / self.scale / 2)  - 1
        col_x = math.ceil(int(self.canvas['width']) / self.scale) + 1
        for i in range(col_x):
            x_initial += 1
            line_copy = [x_initial, -1000, x_initial, 1000]
            line_copy[0] = self.convert_x_to_my_cords(line_copy[0])
            line_copy[1] = self.convert_y_to_my_cords(line_copy[1])
            line_copy[2] = self.convert_x_to_my_cords(line_copy[2])
            line_copy[3] = self.convert_y_to_my_cords(line_copy[3])
            line = tuple(line_copy)
            if (x_initial == 0):
                self.canvas.create_line(*line, fill="blue", width=3)
            else:
                self.canvas.create_line(*line, fill="gray", width=2)
        y_initial = int(-self.camera_y) - math.ceil(int(self.canvas['height']) / self.scale/ 2)  - 1
        col_y = math.ceil(int(self.canvas['height']) / self.scale) + 1
        for i in range(col_y):
            y_initial += 1
            line_copy = [-1000, y_initial, 1000, y_initial]
            line_copy[0] = self.convert_x_to_my_cords(line_copy[0])
            line_copy[1] = self.convert_y_to_my_cords(line_copy[1])
            line_copy[2] = self.convert_x_to_my_cords(line_copy[2])
            line_copy[3] = self.convert_y_to_my_cords(line_copy[3])
            line = tuple(line_copy)
            if (y_initial == 0):
                self.canvas.create_line(*line, fill="blue", width=3)
            else:
                self.canvas.create_line(*line, fill="gray", width=2)

    # main loop
    def somebody_touches_my_keyboard(self):
        self.canvas.delete("all")

        # movement
        if 'Right' in self.pressed_keys:
            self.camera_x += self.speed / self.scale
        if 'Left' in self.pressed_keys:
            self.camera_x -= self.speed / self.scale
        if 'Down' in self.pressed_keys:
            self.camera_y += self.speed / self.scale
        if 'Up' in self.pressed_keys:
            self.camera_y -= self.speed / self.scale
        if ('Alt_L' in self.pressed_keys and 'd' in self.pressed_keys):
            self.camera_x -= self.speed / self.scale
        if ('Alt_L' in self.pressed_keys and 'a' in self.pressed_keys):
            self.camera_x += self.speed / self.scale
        if ('Alt_L' in self.pressed_keys and 's' in self.pressed_keys):
            self.camera_y -= self.speed / self.scale
        if ('Alt_L' in self.pressed_keys and 'w' in self.pressed_keys):
            self.camera_y += self.speed / self.scale

        # changing scale with mouse wheel
        if 'm_w' in self.pressed_keys:
            if (self.pressed_keys["m_w"] > 0):
                self.scale *= round(self.speed_scale, 2)
            else:
                self.scale /= round(self.speed_scale, 2)
            self.pressed_keys.pop("m_w", None)

        # constantly tracking mouse cords
        if "m_x" in self.pressed_keys:
            mouse_x = self.convert_x_from_my_cords(self.pressed_keys["m_x"])
            mouse_y = self.convert_y_from_my_cords(self.pressed_keys["m_y"])
            self.label["text"] = f'Координаты мыши: x={mouse_x}, y={mouse_y} Масштаб: {self.scale}'

        # undo
        if (not 'Control_L' in self.pressed_keys and 'z' in self.released_keys):
            self.released_keys.pop('z', None)
        if ('Control_L' in self.pressed_keys and 'z' in self.released_keys):
            self.released_keys.pop('z', None)
            if (self.curr_bu > 0):
                self.load_it = self.back_up[self.curr_bu - 1].copy()
                self.curr_bu -= 1

        # close
        if ('Control_L' in self.pressed_keys and 'w' in self.pressed_keys):
            raise SystemExit(1)

        # save
        if (not 'Control_L' in self.pressed_keys and 's' in self.released_keys):
            self.released_keys.pop('s', None)
        if ('Control_L' in self.pressed_keys and 's' in self.released_keys):
            self.released_keys.pop('s', None)
            file_name = ""
            cord = 1.0
            if (self.T.get(cord) == '\n'):
                file_name = "default_name"
            else:
                for sy in range(0, 10):
                    s = self.T.get(cord + sy / 10)
                    if (s != '\n'):
                        file_name += s

            saving = self.my_printing(self.load_it)

            f = open(f'{file_name}.{self.ras}', 'w')
            f.write(saving)
            self.title(f'Редактор карт SS2 beta. Открыт файл {file_name}.{self.ras}')
            f.close()

        # new
        if (not 'Control_L' in self.pressed_keys and 'n' in self.released_keys):
            self.released_keys.pop('n', None)
        if ('Control_L' in self.pressed_keys and 'n' in self.released_keys):
            self.released_keys.pop('n', None)
            self.load_it.clear()
            self.back_up.clear()
            self.curr_bu = 0
            self.camera_x = 0
            self.camera_y = 0
            self.scale = 50
            self.one_t = 0
            for w in range(0, 10):
                self.T.delete(1.0 + w / 10)
            self.poly_points.clear()
            self.now = 0
            self.canvas.delete("all")
            self.title("Редактор карт SS2 beta")

        # open
        if (not 'Control_L' in self.pressed_keys and 'o' in self.released_keys):
            self.released_keys.pop('o', None)
        if ('Control_L' in self.pressed_keys and 'o' in self.released_keys):
            self.released_keys.pop('o', None)
            file_name = ""
            cord = 1.0
            if (self.T.get(cord) == '\n'):
                file_name = "default_name"
            else:
                for sy in range(0, 10):
                    s = self.T.get(cord + sy / 10)
                    if (s != '\n'):
                        file_name += s
            try:
                self.load_it = self.my_read(file_name)
                self.title(f'Редактор карт SS2 beta. Открыт файл {file_name}.{self.ras}')
                self.back_up.clear()
                self.curr_bu = 0
                self.poly_points.clear()
                self.camera_x = 0
                self.camera_y = 0
                self.scale = 50
                self.one_t = 0
                self.now = 0
            except BaseException:
                print("failed to open")

        # execute
        if (not 'Control_L' in self.pressed_keys and 'r' in self.released_keys):
            self.released_keys.pop('r', None)
        if ('Control_L' in self.pressed_keys and 'r' in self.released_keys):
            print("hmm")
            self.released_keys.pop('r', None)
            command = ""
            cord = 1.0
            if (self.T.get(cord) == '\n'):
                command = "default_name"
            else:
                for sy in range(0, 10):
                    s = self.T.get(cord + sy / 10)
                    symbs = " ._-"
                    if ('a' <= s <= 'z' or '0' <= s <= '9' or s in symbs):
                        command += s
            if (command.startswith("scale")):
                cum = command.split()
                try:
                    if (float(cum[1]) != 0):
                        self.scale = float(cum[1])
                except BaseException:
                    self.scale = 1
            if (command.startswith("cam_x")):
                cum = command.split()
                try:
                    self.camera_x = int(cum[1])
                except BaseException:
                    self.camera_x = 0
            if (command.startswith("cam_y")):
                cum = command.split()
                try:
                    self.camera_y = int(cum[1])
                except BaseException:
                    self.camera_y = 0
            if (command.startswith("del_now")):
                self.poly_points.clear()
                self.now = 0
            if (command.startswith("invert")):
                self.speed = -self.speed

        # drawing grig
        self.draw_grid()

        # draw saved polygons
        for polygon in self.load_it:
            copy = polygon.copy()
            if (copy[0] == 0):
                self.draw_polygon(copy[1:], "black", 0) # outline/outer
            else:
                self.draw_polygon(copy[1:], "black", 1) # filled/inner

        # draw red line
        if (self.now == 2):
            line_copy = self.poly_points.copy()
            line_copy[0] = self.convert_x_to_my_cords(line_copy[0])
            line_copy[1] = self.convert_y_to_my_cords(line_copy[1])
            line_copy[2] = self.convert_x_to_my_cords(line_copy[2])
            line_copy[3] = self.convert_y_to_my_cords(line_copy[3])
            line = tuple(line_copy)
            self.canvas.create_line(*line, fill="red", width=2)

        # draw red polygon
        if (self.now > 2):
            if ((self.form == None) or (self.form == "внешние границы")):
                self.draw_polygon(self.poly_points, "red", 1) # inner
            else:
                self.draw_polygon(self.poly_points, "red", 0) # outer
            can_be = self.poly_points.copy()
            if "m_x" in self.pressed_keys: # if mouse on canvas: draw possible red polygon
                new_x = self.convert_x_from_my_cords(self.pressed_keys["m_x"])
                new_y = self.convert_y_from_my_cords(self.pressed_keys["m_y"])
                can_be.append(new_x)
                can_be.append(new_y)
            if ((self.form == None) or (self.form == "внешние границы")):
                self.draw_polygon(can_be, "red", 1) # inner
            else:
                self.draw_polygon(can_be, "red", 0) # outer
            can_be.clear()

        self.after(20, self.somebody_touches_my_keyboard) # delay

    # buttons
    def set_selection(self, widget, form):
        for w in widget.master.winfo_children():
            w.config(relief=tk.RAISED)
        widget.config(relief=tk.SUNKEN)
        self.form = form

    # appending point to red polygon
    def append_point(self, event):
        x = self.convert_x_from_my_cords(event.x)
        y = self.convert_y_from_my_cords(event.y)
        self.poly_points.append(round(x, 2))
        self.poly_points.append(round(y, 2))
        self.now += 1

    # appending new polygon
    def draw_item(self, event):
        if (self.now != 0):
            self.now = 0
            if ((self.form == None) or (self.form == "внешние границы")):
                self.poly_points.reverse()
                self.poly_points.append(1)
                self.poly_points.reverse()
            if (self.form == "внутренние границы"):
                self.poly_points.reverse()
                self.poly_points.append(0)
                self.poly_points.reverse()
            self.load_it.append(self.poly_points.copy())
            self.back_up.insert(self.curr_bu + 1, self.load_it.copy())
            self.curr_bu += 1
            self.poly_points.clear()

# run
if __name__ == "__main__":
    app = App()
    app.mainloop()