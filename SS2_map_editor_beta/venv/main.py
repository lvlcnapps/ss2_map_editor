import tkinter as tk
import tkinter.messagebox as mb
from functools import partial
import json

# TODO
# сетка
# GUI:
# равнение по сетке на <Shift>

class App(tk.Tk):
    # Данные камеры
    camera_x = 0
    camera_y = 0
    scale = 1

    # Необходимые переменные
    now = 0
    curr_bu = 0
    speed_scale = 1.2

    # Тексты для кнопок
    texts = ("внешние границы", "внутренние границы")

    # Массивы данных и их доп. данные
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
        # Кнопки
        for form in self.texts:
            btn = tk.Button(frame, text=form.capitalize())
            btn.config(command=partial(self.set_selection, btn, form))
            btn.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        # Бинд событий и текстового поля
        self.canvas.bind("<Button-1>", self.append_point)
        self.canvas.bind("<Button-3>", self.draw_item)
        self.pressed_keys = {}
        self.bind("<KeyPress>", self.key_press)
        self.bind("<KeyRelease>", self.key_release)
        self.bind("<MouseWheel>", self.mouse_w)
        self.canvas.bind("<Motion>", self.mouse_xy)
        self.canvas.pack()
        frame.pack(fill=tk.BOTH)
        self.T = tk.Text()
        self.T.pack()

        # Функция считывания с клавиатуры и отрисовки полигонов
        self.somebody_touches_my_keyboard()

    # Добавление в массив событий кручение колесика мышки
    def mouse_w(self, event):
        self.pressed_keys["m_w"] = event.delta

    def mouse_xy(self, event):
        self.pressed_keys["m_x"] = event.x
        self.pressed_keys["m_y"] = event.y

    # Добавление в массив событий нажатие на клавиши
    def key_press(self, event):
        self.pressed_keys[event.keysym] = True

    # Добавление в массив событий отпускания клавиши
    def key_release(self, event):
        self.pressed_keys.pop(event.keysym, None)

    # Отрисовка полигона по точкам и цвету
    def draw_polygon(self, polygon, color):
        copy = polygon.copy()
        p = 0
        for r in copy:
            if (p % 2 == 0):
                copy[p] = (copy[p] + self.camera_x) * self.scale + int(self.canvas['width']) / 2
            else:
                copy[p] = (copy[p] + self.camera_y) * self.scale + int(self.canvas['height']) / 2
            p += 1
        poly_cords = tuple(copy)
        self.canvas.create_polygon(*poly_cords, fill=color)

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

    def my_read(self, file_name):
        f = open(f'{file_name}.txt', 'r')
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

    # Функция обработки событий нажатия на клавиатуру и отрисовка
    def somebody_touches_my_keyboard(self):
        self.canvas.delete("all")
        speed = 3
        # События кнопок
        if 'Right' in self.pressed_keys:
            self.camera_x += speed / self.scale
        if 'Left' in self.pressed_keys:
            self.camera_x -= speed / self.scale
        if 'Down' in self.pressed_keys:
            self.camera_y += speed / self.scale
        if 'Up' in self.pressed_keys:
            self.camera_y -= speed / self.scale

        # Колесико мыши
        if 'm_w' in self.pressed_keys:
            if (self.pressed_keys["m_w"] > 0):
                self.scale *= self.speed_scale
            else:
                self.scale /= self.speed_scale
            self.pressed_keys.pop("m_w", None)

        if "m_x" in self.pressed_keys:
            mouse_x = (self.pressed_keys["m_x"] - int(self.canvas['width']) / 2) / self.scale - self.camera_x
            mouse_y = (self.pressed_keys["m_y"] - int(self.canvas['height']) / 2) / self.scale - self.camera_y
            self.label["text"] = f'Координаты мыши: x={mouse_x}, y={mouse_y} Масштаб: {self.scale}'

        one_time = 0
        if (self.one_t == 0):
            one_time = 1
            self.one_t = 5
        else:
            self.one_t -= 1

        # Отмена действия
        if ('Control_L' in self.pressed_keys and 'z' in self.pressed_keys):
            if ((self.curr_bu > 0) and (one_time == 1)):
                self.load_it = self.back_up[self.curr_bu - 1].copy()
                self.curr_bu -= 1
                one_time = 0

        if ('Control_L' in self.pressed_keys and 'w' in self.pressed_keys):
            raise SystemExit(1)

        # Сохранение в файл
        if ('Control_L' in self.pressed_keys and 's' in self.pressed_keys):
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

            f = open(f'{file_name}.txt', 'w')
            f.write(saving)
            self.title(f'Редактор карт SS2 beta. Открыт файл {file_name}.txt')
            f.close()

        # Новая карта
        if ('Control_L' in self.pressed_keys and 'n' in self.pressed_keys):
            self.load_it.clear()
            self.back_up.clear()
            self.curr_bu = 0
            self.camera_x = 0
            self.camera_y = 0
            self.scale = 1
            self.one_t = 0
            for w in range(0, 10):
                self.T.delete(1.0 + w / 10)
            self.poly_points.clear()
            self.now = 0
            self.canvas.delete("all")
            self.title("Редактор карт SS2 beta")

        # Открыть файл
        if ('Control_L' in self.pressed_keys and 'o' in self.pressed_keys):
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
                self.title(f'Редактор карт SS2 beta. Открыт файл {file_name}.txt')
                self.back_up.clear()
                self.curr_bu = 0
                self.poly_points.clear()
                self.camera_x = 0
                self.camera_y = 0
                self.scale = 1
                self.one_t = 0
                self.now = 0
            except BaseException:
                print("fail to open this")

        if ('Control_L' in self.pressed_keys and 'r' in self.pressed_keys):
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

        # Draw black polygon
        for polygon in self.load_it:
            copy = polygon.copy()
            self.draw_polygon(copy[1:], "black")

        # Draw red line
        if (self.now == 2):
            line_copy = self.poly_points.copy()
            line_copy[0] = (line_copy[0] + self.camera_x) * self.scale + int(self.canvas['width']) / 2
            line_copy[1] = (line_copy[1] + self.camera_y) * self.scale + int(self.canvas['height']) / 2
            line_copy[2] = (line_copy[2] + self.camera_x) * self.scale + int(self.canvas['width']) / 2
            line_copy[3] = (line_copy[3] + self.camera_y) * self.scale + int(self.canvas['height']) / 2
            line = tuple(line_copy)
            self.canvas.create_line(*line, fill="red", width=2)

        # Draw red polygon
        if (self.now > 2):
            self.draw_polygon(self.poly_points, "red")
            can_be = self.poly_points.copy()
            if "m_x" in self.pressed_keys:
                # mouse_x = (self.pressed_keys["m_x"] + self.camera_x) * self.scale + int(self.canvas['width']) / 2
                # mouse_y = (self.pressed_keys["m_y"] + self.camera_y) * self.scale + int(self.canvas['height']) / 2
                new_x = (self.pressed_keys["m_x"] - int(self.canvas['width']) / 2) / self.scale - self.camera_x
                new_y = (self.pressed_keys["m_y"] - int(self.canvas['height']) / 2) / self.scale - self.camera_y
                can_be.append(new_x)
                can_be.append(new_y)
            self.draw_polygon(can_be, "red")
            can_be.clear()

        self.after(20, self.somebody_touches_my_keyboard)

    # че то там для кнопок
    def set_selection(self, widget, form):
        for w in widget.master.winfo_children():
            w.config(relief=tk.RAISED)
        widget.config(relief=tk.SUNKEN)
        self.form = form

    # Добавление точки в редактируемый полигон
    def append_point(self, event):
        x = (event.x - int(self.canvas['width']) / 2) / self.scale - self.camera_x
        y = (event.y - int(self.canvas['height']) / 2) / self.scale - self.camera_y
        self.poly_points.append(x)
        self.poly_points.append(y)
        self.now += 1

    # Процесс добавления нового отредактированного полигона
    def draw_item(self, event):
        if (self.now != 0):
            self.now = 0
            if ((self.form == None) or (self.form == "внешние границы")):
                self.poly_points.reverse()
                self.poly_points.append(0)
                self.poly_points.reverse()
            if (self.form == "внутренние границы"):
                self.poly_points.reverse()
                self.poly_points.append(1)
                self.poly_points.reverse()
            #self.load_it.append(json.dumps(self.poly_points))
            self.load_it.append(self.poly_points.copy())

            self.back_up.insert(self.curr_bu + 1, self.load_it.copy())
            self.curr_bu += 1
            #print(self.load_it)
            self.poly_points.clear()

if __name__ == "__main__":
    app = App()
    app.mainloop()