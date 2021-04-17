import tkinter as tk
import tkinter.messagebox as mb
from functools import partial
import json
import math

# TODO
# moving choosed polygon

class App(tk.Tk):
    # Camera data
    camera_x = 0
    camera_y = 0
    scale = 50
    min_scale = 10
    max_scale = 1000
    choosed_id = -1

    # params
    now = 0
    curr_bu = 0
    speed_scale = 1.2
    ras = "lvl"
    speed = 3
    mouse_x_prev = 0
    mouse_y_prev = 0
    timer = 0

    # texts
    texts = ("внешние границы", "внутренние границы")
    texts_bonuses = ("INSTANT HP", "INSTANT STAMINA", "LASER", "CHARGE", "BERSERK", "IMMORTALITY")
    texts_2 = ("Сохранить", "Открыть", "Новый")

    # arrays, data
    poly_points = []
    bonus_counter = 0
    bonuses_points = [[],[],[],[],[],[]]
    bonuses_images = [[],[],[],[],[],[]]
    load_it = []
    back_up = [[]]
    one_t = 0

    def __init__(self):
        super().__init__()
        self.title("Редактор карт SS2 beta")
        self.form = None
        self.form_2 = None
        self.buttons_w = "30"
        self.buttons_h = "30"
        self.label = tk.Label(text="Начало работы")
        self.label.pack(fill=tk.BOTH)
        self.geometry("1080x646")
        # canv_frame = tk.Frame(self)
        self.canvas = tk.Canvas(self, width=960, height=500, bg="white", cursor="tcross")
        # self.slider = tk.Scale(canv_frame, from_ = 500, to = 1000, orient=tk.VERTICAL)


        frame = tk.Frame(self)
        # Buttons
        ind_walls = 0
        self.photo_walls = [tk.PhotoImage(file = f'outer.png'), tk.PhotoImage(file = f'inner.png')]
        self.buttons_walls = []
        for form in self.texts:
            btn = tk.Button(frame)
            btn.config(command=partial(self.set_selection, btn, form), image = self.photo_walls[ind_walls], width=self.buttons_w, height=self.buttons_h)
            btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.buttons_walls.append(btn)
            ind_walls += 1

        bonuses_frame = tk.Frame(self)
        ind = 0
        self.photoimage = []
        self.buttons_bonuses = []
        for i in range(6):
            self.photoimage.append(tk.PhotoImage(file = f'bonus{i}.png'))
        for form in self.texts_bonuses:
            btn = tk.Button(frame)
            btn.config(command=partial(self.set_selection, btn, form), image = self.photoimage[ind], width=self.buttons_w, height=self.buttons_h)
            btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
            self.buttons_bonuses.append(btn)
            ind += 1

        # Bindings events to functions
        self.canvas.bind("<Button-1>", self.append_point)
        self.canvas.bind("<Button-3>", self.draw_item_2)
        self.pressed_keys = {}
        self.choosed_poly = []
        self.released_keys = {}
        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)
        self.bind("<MouseWheel>", self.mouse_w)
        self.canvas.bind("<Motion>", self.mouse_xy)
        self.canvas.pack(fill = tk.BOTH)
        # self.slider.pack(expand=True, fill=tk.BOTH)
        # canv_frame.pack(fill=tk.BOTH)
        frame.pack(fill=tk.BOTH)
        bonuses_frame.pack(fill=tk.BOTH)
        self.save_info = tk.Label(text="Поле для названия файла:")
        self.save_info.pack(fill=tk.BOTH)
        self.T = tk.Text(height=1, width=10)
        self.T.pack(fill=tk.Y)
        self.file_buttons_frame = tk.Frame(self, width=640)
        # Buttons
        for form in self.texts_2:
            btn = tk.Button(self.file_buttons_frame, text=form.capitalize())
            btn.config(command=partial(self.other_selection, form))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)
        self.file_buttons_frame.pack(fill=tk.BOTH)

        self.label.update()
        frame.update()
        self.save_info.update()
        self.T.update()
        self.file_buttons_frame.update()

        self.sum_ex = self.label.winfo_reqheight() + frame.winfo_reqheight() + self.save_info.winfo_reqheight() + self.T.winfo_reqheight() + self.file_buttons_frame.winfo_reqheight() - 1
        print(self.sum_ex)

        # main loop
        self.somebody_touches_my_keyboard()

    # mouse wheel delay event
    def mouse_w(self, event):
        self.canvas.focus_set()
        self.pressed_keys["m_w"] = event.delta
        self.pressed_keys["m_wx"] = event.x
        self.pressed_keys["m_wy"] = event.y

    # mouse motion event
    def mouse_xy(self, event):
        #print(event.state)
        self.canvas.focus_set()
        if (event.state > 1000):
            if ("ch_id" in self.pressed_keys):
                pass
                #self.move_polygon(event.x, event.y, self.pressed_keys["ch_id"])
        if (500 < event.state < 1000):
            self.canvas["cursor"] = "fleur"
            self.move_camera(event.x, event.y)
        else:
            self.canvas["cursor"] = "tcross"
        self.mouse_x_prev = event.x
        self.mouse_y_prev = event.y
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
        elif (filled == 0):
            self.canvas.create_polygon(*poly_cords, outline=color, fill='', width=2)
        else:
            self.canvas.create_polygon(*poly_cords, fill=color, outline="cyan", width=3)

    # making huge string of polygons to save it
    def my_printing(self, load_it):
        sum_text = ""
        for poly in load_it:
            if (len(poly) < 6):
                continue
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
        for i in range(6):
            sum_text += "BONUS "
            if (i == 0):
                sum_text += "INSTANT_HP\n"
            if (i == 1):
                sum_text += "INSTANT_STAMINA\n"
            if (i == 2):
                sum_text += "LASER\n"
            if (i == 3):
                sum_text += "CHARGE\n"
            if (i == 4):
                sum_text += "BERSERK\n"
            if (i == 5):
                sum_text += "IMMORTALITY\n"

            for point in self.bonuses_points[i]:
                sum_text += f'    POINT {round(point[0], 2)} {round(point[1], 2)}\n'

            sum_text += "END\n"
        sum_text += "END"
        return sum_text

    # converting from string to polygon (file reading)
    def my_read(self, file_name):
        f = open(f'{file_name}.{self.ras}', 'r')
        load_it = []
        counter = 0
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
            if (str.startswith("BONUS")):
                id = 0
                if (str.split()[1] == "INSTANT_HP"):
                    id = 0
                if (str.split()[1] == "INSTANT_STAMINA"):
                    id = 1
                if (str.split()[1] == "LASER"):
                    id = 2
                if (str.split()[1] == "CHARGE"):
                    id = 3
                if (str.split()[1] == "BERSERK"):
                    id = 4
                if (str.split()[1] == "IMMORTALITY"):
                    id = 5
                mega_poly = []
                new_poly = []
                image_new = []
                check = 0

                while (True):
                    str = f.readline()
                    if (str.startswith("END")):
                        break
                    if (str.startswith("    POINT")):
                        kom = str.split()
                        new_poly.append(float(kom[1]))
                        new_poly.append(float(kom[2]))
                        new_poly.append(counter)
                        check = 1
                        image_new.append([tk.PhotoImage(file=f'bonus{id}.png')])
                        counter += 1
                        mega_poly.append(new_poly.copy())
                        new_poly.clear()
                if (check != 0):
                    self.bonuses_points[id] = mega_poly
                    self.bonuses_images[id] = image_new
        # print(self.bonuses_points) # [[[-6.88, 0.28, 0], [-3.58, 0.22, 1]], [], [], [], [], []]
        return load_it

    # converting from/to my cords system
    def convert_x_to_my_cords(self, old_c):
        return (old_c + self.camera_x) * self.scale + int(self.canvas.winfo_width()) / 2

    def convert_y_to_my_cords(self, old_c):
        return (old_c + self.camera_y) * self.scale + int(self.canvas.winfo_height()) / 2

    def convert_x_from_my_cords(self, new_c):
        return (new_c - int(self.canvas.winfo_width()) / 2) / self.scale - self.camera_x

    def convert_y_from_my_cords(self, new_c):
        return (new_c - int(self.canvas.winfo_height()) / 2) / self.scale - self.camera_y

    def draw_bonuses(self):
        for i in range(6):
            iter = 0
            for point in self.bonuses_points[i]:
                self.canvas.create_image(self.convert_x_to_my_cords(point[0]) - 12, self.convert_y_to_my_cords(point[1]) - 12, anchor="nw", image=self.bonuses_images[i][iter])
                self.canvas.image = image=self.bonuses_images[i][iter]
                iter += 1

    # drawing grid and Oxy
    def draw_grid(self):
        #print(self.bonuses_points)
        x_initial = int(-self.camera_x) - math.ceil(int(self.canvas.winfo_width()) / self.scale / 2)  - 1
        col_x = math.ceil(int(self.canvas.winfo_width()) / self.scale) + 2
        for i in range(col_x):
            x_initial += 1
            line_copy = [x_initial, -1000, x_initial, 1000]
            line_copy[0] = self.convert_x_to_my_cords(line_copy[0])
            line_copy[1] = self.convert_y_to_my_cords(line_copy[1])
            line_copy[2] = self.convert_x_to_my_cords(line_copy[2])
            line_copy[3] = self.convert_y_to_my_cords(line_copy[3])
            line = tuple(line_copy)
            if (x_initial == 0):
                self.canvas.create_line(*line, fill="blue", width=4)
            else:
                if (x_initial % 10 == 0):
                    self.canvas.create_line(*line, fill="gray", width=3)
                else:
                    self.canvas.create_line(*line, fill="#D5D5D5", width=2)
        y_initial = int(-self.camera_y) - math.ceil(int(self.canvas.winfo_height()) / self.scale/ 2)  - 1
        col_y = math.ceil(int(self.canvas.winfo_height()) / self.scale) + 1
        for i in range(col_y):
            y_initial += 1
            line_copy = [-1000, y_initial, 1000, y_initial]
            line_copy[0] = self.convert_x_to_my_cords(line_copy[0])
            line_copy[1] = self.convert_y_to_my_cords(line_copy[1])
            line_copy[2] = self.convert_x_to_my_cords(line_copy[2])
            line_copy[3] = self.convert_y_to_my_cords(line_copy[3])
            line = tuple(line_copy)
            if (y_initial == 0):
                self.canvas.create_line(*line, fill="blue", width=4)
            else:
                if (y_initial % 10 == 0):
                    self.canvas.create_line(*line, fill="gray", width=3)
                else:
                    self.canvas.create_line(*line, fill="#D5D5D5", width=2)

    # moving camera by mouse wheel click
    def move_camera(self, mouse_x, mouse_y):
        if "m_x" in self.pressed_keys:
            self.camera_x += (mouse_x - self.mouse_x_prev) / self.scale
            self.camera_y += (mouse_y - self.mouse_y_prev) / self.scale

    # beta
    def move_polygon(self, mouse_x, mouse_y, id):
        new_load_it = []
        count_id = 0

        g = 0
        for pol in self.load_it:
            if (g == id):
                xp = self.getXparse(pol)
                yp = self.getYparse(pol)
                break
            g += 1
        m_x = self.convert_x_from_my_cords(mouse_x)
        m_y = self.convert_y_from_my_cords(mouse_y)
        #print(self.inPolygon(m_x, m_y, xp, yp))
        if (self.inPolygon(m_x, m_y, xp, yp)):
            print("lol")
            for pol in self.load_it:
                if (count_id == id):
                    new = []
                    f = 0
                    for i in pol[1:]:
                        if (f % 2 == 1):
                            new.append(i + (mouse_y - self.mouse_y_prev) / self.scale)
                        else:
                            new.append(i + (mouse_x - self.mouse_x_prev) / self.scale)
                        f += 1
                    print(new)
                    new_load_it.append(new)
                else:
                    new_load_it.append(pol)
                    count_id += 1
            self.load_it = new_load_it

    # parsing polygon's coords to only X coords or only Y coords
    def getXparse(self, polygon):
        f = 1
        new = []
        old = polygon.copy()
        for i in old[1:]:
            if (f % 2):
                new.append(i)
            f += 1
        return new

    def getYparse(self, polygon):
        f = 0
        new = []
        old = polygon.copy()
        for i in old[1:]:
            if (f % 2):
                new.append(i)
            f += 1
        return new

    # main loop
    def somebody_touches_my_keyboard(self):
        # const scale
        if (self.scale < self.min_scale):
            self.scale = self.min_scale
        if (self.scale > self.max_scale):
            self.scale = self.max_scale
        self.canvas.delete("all")
        #print(self.pressed_keys)

        # info
        if 'F1' in self.pressed_keys:
            try:
                load_it = self.my_read("start_info")
                self.camera_x = 0
                self.camera_y = 0
                self.scale = 50
                for i in load_it:
                    copy = i.copy()
                    self.draw_polygon(copy[1:], "black", 1)
            except BaseException:
                print("failed to open")
            self.after(20, self.somebody_touches_my_keyboard)  # delay
            return
        if 'F1' in self.released_keys:
            self.pressed_keys.pop("F1", None)
            self.released_keys.pop("F1", None)

        # changing scale with mouse wheel
        if 'm_w' in self.pressed_keys:
            mouse_x = self.convert_x_from_my_cords(self.pressed_keys["m_wx"])
            mouse_y = self.convert_y_from_my_cords(self.pressed_keys["m_wy"])
            self.label["text"] = f'Координаты мыши: x={round(mouse_x, 2)}, y={round(mouse_y, 2)} Масштаб: {round(self.scale, 2)} Помощь: F1'
            dS = math.pow(1.1, 0.01 * self.pressed_keys["m_w"])
            self.scale *= dS
            self.camera_x -= (int(self.canvas.winfo_width()) / 2 - self.pressed_keys["m_wx"]) / self.scale * (1 - dS)
            self.camera_y -= (int(self.canvas.winfo_height()) / 2 - self.pressed_keys["m_wy"]) / self.scale * (1 - dS)
            self.pressed_keys.pop("m_w", None)
            self.pressed_keys.pop("m_wx", None)
            self.pressed_keys.pop("m_wy", None)

        # if smth choosed
        if "ch_id" in self.pressed_keys:
            id = 0
            for pol in self.load_it:
                if (id == self.pressed_keys["ch_id"]):
                    self.choosed_poly = pol
                id += 1

        if "bonus_ch_id" in self.pressed_keys and "BackSpace" in self.pressed_keys:
            for i in range(6):
                new_points = []
                for point in self.bonuses_points[i]:
                    if (point[2] != self.pressed_keys["bonus_ch_id"]):
                        new_points.append(point)
                    else:
                        self.bonuses_images[i].pop(0)
                #print(new_points)
                #self.pressed_keys.pop("bonus_ch_id")
                self.bonuses_points[i] = new_points.copy()


        # deleting choosed polygon
        if "ch_id" in self.pressed_keys and "Delete" in self.pressed_keys:
            new_load_it = []
            id = 0
            for pol in self.load_it:
                if (id != self.pressed_keys["ch_id"]):
                    new_load_it.append(pol)
                id += 1
            self.pressed_keys.pop("ch_id")
            self.pressed_keys.pop("Delete")
            self.load_it = new_load_it
            self.back_up.insert(self.curr_bu + 1, self.load_it.copy())
            self.curr_bu += 1

        # constantly tracking mouse cords
        if "m_x" in self.pressed_keys:
            mouse_x = self.convert_x_from_my_cords(self.pressed_keys["m_x"])
            mouse_y = self.convert_y_from_my_cords(self.pressed_keys["m_y"])
            id = 0
            pred_id = -1
            for polygon in self.load_it:
                xpol = self.getXparse(polygon)
                ypol = self.getYparse(polygon)
                if ((self.inPolygon(mouse_x, mouse_y, xpol, ypol)) and polygon[0] == 1):
                    pred_id = id
                id += 1

            bon_pred_id = -1
            for i in range(6):
                for point in self.bonuses_points[i]:
                    if (self.inBonus(mouse_x, mouse_y, point[0], point[1])):
                        bon_pred_id = point[2]

            if (bon_pred_id >= 0):
                self.pressed_keys["over_bonus"] = bon_pred_id

            if (pred_id >= 0):
                self.pressed_keys["over"] = pred_id

            self.label["text"] = f'Координаты мыши: x={round(mouse_x, 2)}, y={round(mouse_y, 2)} Масштаб: {round(self.scale, 2)}  Помощь: F1'

        # save polygon
        if "Control_R" in self.pressed_keys:
            self.draw_item()
            self.pressed_keys.pop("Control_R", None)

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
        if ('Control_L' in self.pressed_keys and 's' in self.released_keys) or self.form_2 == "Сохранить":
            self.form_2 = None
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

        #print(self.bonuses_points)

        # new
        if (not 'Control_L' in self.pressed_keys and 'n' in self.released_keys):
            self.released_keys.pop('n', None)
        if ('Control_L' in self.pressed_keys and 'n' in self.released_keys) or self.form_2 == "Новый":
            self.bonuses_points = [[],[],[],[],[],[]]
            self.bonuses_images = [[],[],[],[],[],[]]
            self.bonus_counter = 0
            self.released_keys.pop('n', None)
            self.form_2 = None
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
        if ('Control_L' in self.pressed_keys and 'o' in self.released_keys) or self.form_2 == "Открыть":
            self.released_keys.pop('o', None)
            self.form_2 = None
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
            if (command.startswith("center")):
                self.camera_x = 0
                self.camera_y = 0
                self.scale = 50

        # drawing grid
        self.draw_grid()



        # align to grid
        if "Shift_L" in self.pressed_keys and "m_x" in self.pressed_keys:
            x = round(self.convert_x_from_my_cords(self.pressed_keys["m_x"]))
            y = round(self.convert_y_from_my_cords(self.pressed_keys["m_y"]))
            r = 3
            x_m_r = self.convert_x_to_my_cords(x)
            y_m_r = self.convert_y_to_my_cords(y)
            self.canvas.create_oval(x_m_r - r, y_m_r - r, x_m_r + r, y_m_r + r, fill="green")

        # draw saved polygons
        may_id = 0
        cc_id = -1
        if ("ch_id" in self.pressed_keys):
            cc_id = self.pressed_keys["ch_id"]
        for polygon in self.load_it:
            copy = polygon.copy()
            if (copy[0] == 0):
                self.draw_polygon(copy[1:], "black", 0) # outline/outer
            else:
                if (cc_id == may_id):
                    #print(cc_id)
                    self.draw_polygon(copy[1:], "black", 2) # choosed/filled/inner
                else:
                    self.draw_polygon(copy[1:], "black", 1) # filled/inner
            may_id += 1

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

        # drawing bonuses
        self.draw_bonuses()

        ind = 0
        for form in self.texts_bonuses:
            self.buttons_bonuses[ind].config(image = self.photoimage[ind], width=self.buttons_w, height=self.buttons_h)

        ind = 0
        for form in self.texts:
            self.buttons_walls[ind].config(image = self.photo_walls[ind], width=self.buttons_w, height=self.buttons_h)

        self.canvas["height"] = self.winfo_height() - self.sum_ex

        self.after(20, self.somebody_touches_my_keyboard) # delay

    # buttons
    def set_selection(self, widget, form):
        for w in widget.master.winfo_children():
            w.config(relief=tk.RAISED)
        widget.config(relief=tk.SUNKEN)
        self.form = form

    def other_selection(self, form):
        self.form_2 = form

    # appending point to red polygon
    def append_point(self, event):
        x = self.convert_x_from_my_cords(event.x)
        y = self.convert_y_from_my_cords(event.y)
        if "Shift_L" in self.pressed_keys:
            x = round(x)
            y = round(y)
        if (self.form == self.texts_bonuses[0]): # ("Здоровье", "Стамина", "Лазер", "Ускорение", "Машина убийств", "Бессмертие")
            self.bonuses_points[0].append([x, y, self.bonus_counter])
            self.bonus_counter += 1
            self.bonuses_images[0].append([tk.PhotoImage(file="bonus0.png")])
            #print(self.bonuses_points[0])
            return
        if (self.form == self.texts_bonuses[1]):
            self.bonuses_points[1].append([x, y, self.bonus_counter])
            self.bonus_counter += 1
            self.bonuses_images[1].append([tk.PhotoImage(file="bonus1.png")])
            return
        if (self.form == self.texts_bonuses[2]):
            self.bonuses_points[2].append([x, y, self.bonus_counter])
            self.bonus_counter += 1
            self.bonuses_images[2].append([tk.PhotoImage(file="bonus2.png")])
            return
        if (self.form == self.texts_bonuses[3]):
            self.bonuses_points[3].append([x, y, self.bonus_counter])
            self.bonus_counter += 1
            self.bonuses_images[3].append([tk.PhotoImage(file="bonus3.png")])
            return
        if (self.form == self.texts_bonuses[4]):
            self.bonuses_points[4].append([x, y, self.bonus_counter])
            self.bonus_counter += 1
            self.bonuses_images[4].append([tk.PhotoImage(file="bonus4.png")])
            return
        if (self.form == self.texts_bonuses[5]):
            self.bonuses_points[5].append([x, y, self.bonus_counter])
            self.bonus_counter += 1
            self.bonuses_images[5].append([tk.PhotoImage(file="bonus5.png")])
            return
        self.poly_points.append(round(x, 2))
        self.poly_points.append(round(y, 2))
        self.now += 1

    # appending new polygon
    def draw_item(self):
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

    # check if point (xx, yy) is in polygon with xp as X coords and yp as Y coords
    # use getXparse() and getYparse()
    def inPolygon(self, xx, yy, xp, yp):
        c = 0
        for i in range(len(xp)):
            if (((yp[i] <= yy and yy < yp[i - 1]) or (yp[i - 1] <= yy and yy < yp[i])) and
                    (xx > (xp[i - 1] - xp[i]) * (yy - yp[i]) / (yp[i - 1] - yp[i]) + xp[i])): c = 1 - c
        return c

    def inBonus(self, xx, yy, xp, yp):
        #print("-----------")
        #print(f'{xx} {yy} {xp} {yp}')
        #print("-----------")
        if (abs(xx - xp) < 12 / self.scale and abs(yy - yp) < 12 / self.scale):
            return 1
        return 0

    # appending new polygon
    def draw_item_2(self, event):
        if (self.now != 0):
            self.now = 0
            if ((self.form == None) or (self.form == "внешние границы")):
                self.poly_points.reverse()
                self.poly_points.append(1)
                self.poly_points.reverse()
            elif (self.form == "внутренние границы"):
                self.poly_points.reverse()
                self.poly_points.append(0)
                self.poly_points.reverse()
            else:
                return
            self.load_it.append(self.poly_points.copy())
            self.back_up.insert(self.curr_bu + 1, self.load_it.copy())
            self.curr_bu += 1
            self.poly_points.clear()
        else:
            if ("over" in self.pressed_keys):
                self.pressed_keys["ch_id"] = self.pressed_keys["over"]
            if ("over_bonus" in self.pressed_keys):
                self.pressed_keys["bonus_ch_id"] = self.pressed_keys["over_bonus"]

# run
if __name__ == "__main__":
    app = App()
    app.mainloop()