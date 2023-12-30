import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image, ImageDraw, ImageEnhance
from tkinter.constants import *
import copy

class Point:
    points = []
    mouse = (0, 0)
    shift = False

    def __init__(self, x, y, place=-1):
        self.pos = (x, y)
        self.point = canvas.create_oval(self.pos[0] - 5, self.pos[1] - 5, self.pos[0] + 5, self.pos[1] + 5, fill='white', width=0)

        self.dragging = False
        self.curve_points = []
        Point.points.insert(place, self)
        self.line = canvas.create_line(*self.pos, *Point.points[(place + 1) % len(Point.points)].pos, width=5, fill='blue')
        canvas.tag_raise(self.point, crop_img)
        canvas.tag_lower(self.line, self.point)
        canvas.tag_raise(self.point, Point.points[Point.points.index(self) - 1].line)
        canvas.tag_raise(self.point, Point.points[Point.points.index(self) - 1].point)

        root.after(0, self.frame)

    def frame(self):
        if self in Point.points:
            after = Point.points[(Point.points.index(self) + 1) % len(Point.points)]
            canvas.coords(self.line, *self.pos, *[val for point in self.curve_points for val in point.pos], *after.pos)
            canvas.itemconfig(self.line, smooth=len(self.curve_points)!=0)
            if self.dragging and tool == 'drag':
                if Point.shift:
                    for point in Point.points:
                        if point == self:
                            continue
                        if abs(self.pos[0] - point.pos[0]) < 10:
                            self.pos = (point.pos[0], self.pos[1])
                            break
                        else:
                            self.pos = (Point.mouse[0], self.pos[1])
                    for point in Point.points:
                        if abs(self.pos[1] - point.pos[1]) < 10:
                            self.pos = (self.pos[0], point.pos[1])
                            break
                        else:
                            self.pos = (self.pos[0], Point.mouse[1])
                else:
                    self.pos = Point.mouse
            canvas.coords(self.point, self.pos[0] -5, self.pos[1] -5, self.pos[0] + 5, self.pos[1] + 5)
            root.after(int(1000/60), self.frame)

    def mouse_down(self, event):
        elm = canvas.find_withtag('current')
        if elm:
            if elm[0] == self.point:
                if tool == 'drag':
                    self.dragging = True
                elif tool == 'delete point':
                    canvas.delete(self.point)
                    canvas.delete(self.line)
                    Point.points.remove(self)
                    del self
            elif elm[0] == self.line:
                if tool == 'add point':
                    Point(event.x, event.y, place=Point.points.index(self) + 1)
                elif tool == 'add curve point':
                    CurvePoint(self, event.x, event.y)
            else:
                for curve_point in self.curve_points:
                    if elm[0] == curve_point.point and tool == 'drag':
                        curve_point.dragging = True
                    elif elm[0] == curve_point.point and tool == 'delete curve point':
                        canvas.delete(curve_point.point)
                        self.curve_points.remove(curve_point)
                        del curve_point

    def mouse_up(self):
        self.dragging = False
        for curve_point in self.curve_points:
            curve_point.dragging = False

    @classmethod
    def run_downs(cls, event):
        for point in cls.points:
            point.mouse_down(event)

    @classmethod
    def run_ups(cls, _):
        for point in cls.points:
            point.mouse_up()

    @classmethod
    def mouse_move(cls, event):
        cls.mouse = (event.x, event.y)

    @classmethod
    def shift_down(cls, _):
        cls.shift = True

    @classmethod
    def shift_up(cls, _):
        cls.shift = False

    @classmethod
    def setup_point_class(cls):
        canvas.bind("<ButtonPress-1>", cls.run_downs)
        canvas.bind("<ButtonRelease-1>", cls.run_ups)
        canvas.bind("<Motion>", cls.mouse_move)
        root.bind('<Shift_L>', cls.shift_down)
        root.bind('<Shift_R>', cls.shift_down)
        root.bind('<KeyRelease-Shift_L>', cls.shift_up)
        root.bind('<KeyRelease-Shift_R>', cls.shift_up)


def bezier_curve(num_steps, *points):
    def cubic_bezier(p, t):
        a = (1.0 - t)**3
        b = 3.0 * t * (1.0 - t)**2
        c = 3.0 * t**2 * (1.0 - t)
        d = t**3

        x = int(a * p[0][0] + b * p[1][0] + c * p[2][0] + d * p[3][0])
        y = int(a * p[0][1] + b * p[1][1] + c * p[2][1] + d * p[3][1])

        return x, y

    curve_points = []
    for i in range(0, len(points) - 3, 3):
        segment_points = points[i:i + 4]
        for step in range(num_steps):
            t = step / float(num_steps - 1)
            curve_points.append(cubic_bezier(segment_points, t))

    return curve_points


def update_bg():
    global new_img
    root.after(15, update_bg)
    mask = Image.new("RGBA", (w, h), 0)
    points = []
    for i, point in enumerate(Point.points):
        if len(point.curve_points) != 0:
            after = Point.points[(i+1) % len(point.points)].pos
            print(bezier_curve(100, point.pos, *point.curve_points, after))
            points.extend(bezier_curve(100, point.pos, *point.curve_points, after)[:-2])
        else:
            points.append(point.pos)
    ImageDraw.Draw(mask).polygon(points, fill='black', outline=None)
    new_img = Image.composite(img, transparent, mask)
    new_img_bg = ImageTk.PhotoImage(new_img)
    canvas.itemconfig(crop_img, image=new_img_bg)
    canvas.image = new_img_bg

def download():
    xs = [point.pos[0] for point in Point.points]
    ys = [point.pos[1] for point in Point.points]
    new_img.crop((min(xs), min(ys), max(xs), max(ys))).show('Cropped')


tool = 'drag'


def set_tool(name):
    global tool
    if tool == 'drag':
        button = drag
    elif tool == 'add point':
        button = add_point
    elif tool == 'delete point':
        button = delete_point
    elif tool == 'add curve point':
        button = add_curve_point
    elif tool == 'delete curve point':
        button = delete_curve_point
    button.config(style='Normal.TButton')
    tool = name
    if tool == 'drag':
        button = drag
    elif tool == 'add point':
        button = add_point
    elif tool == 'delete point':
        button = delete_point
    elif tool == 'add curve point':
        button = add_curve_point
    elif tool == 'delete curve point':
        button = delete_curve_point
    button.config(style='Blue.TButton')


class CurvePoint:
    def __init__(self, point, x, y, place=-1):
        self.parent_point = point
        self.pos = x, y
        self.dragging = False
        self.parent_point.curve_points.insert(place, self)
        self.point = canvas.create_oval(self.pos[0] - 5, self.pos[1] - 5, self.pos[0] + 5, self.pos[1] + 5, fill='yellow', width=0)
        root.after(0, self.frame)

    def frame(self):
        root.after(15, self.frame)
        if self.dragging:
            self.pos = Point.mouse
        canvas.coords(self.point, self.pos[0] - 5, self.pos[1] - 5, self.pos[0] + 5, self.pos[1] + 5)




root = tk.Tk()
img = Image.open('image.png')
w, h = img.size


if h < w:
    h = int(800/w*h)
    w = 800
else:
    w = int(800/h*w)
    h = 800
img = img.resize((w, h))
transparent = Image.new("RGBA", (w, h), (0,0,0,0))
img_tk = ImageTk.PhotoImage(img)
canvas = tk.Canvas(root, width=w, height=h)
crop_img = canvas.create_image(0, 0, image=img_tk, anchor=NW)
darken = copy.deepcopy(img)
darken = ImageTk.PhotoImage(ImageEnhance.Brightness(darken).enhance(0.5))
bg_img = canvas.create_image(0, 0, image=darken, anchor=NW)


canvas.tag_lower(crop_img)
canvas.tag_lower(bg_img, crop_img)
tools = tk.Frame(root, height=40)
style = ttk.Style()
style.theme_use('alt')

# Define a custom button style that doesn't change color on hover
style.configure('Blue.TButton', background='lightblue', foreground='white')
style.map('Blue.TButton',
          background=[('active', 'lightblue'), ('pressed', 'lightblue'), ('!disabled', 'lightblue')],
          foreground=[('active', 'white'), ('pressed', 'white'), ('!disabled', 'white')])
style.configure('Normal.TButton', background='White', foreground='white')
style.map('White.TButton',
          background=[('active', 'lightblue'), ('pressed', 'White'), ('!disabled', 'White')],
          foreground=[('active', 'white'), ('pressed', 'white'), ('!disabled', 'white')])


drag_icon = ImageTk.PhotoImage(Image.open('icons/move.png').resize((40, 40)))
drag = ttk.Button(tools, image=drag_icon, command=lambda: set_tool('drag'), style='Blue.TButton')
drag.pack(side=tk.LEFT)
add_icon = ImageTk.PhotoImage(Image.open('icons/plus_point.png').resize((40, 40)))
add_point = ttk.Button(tools, image=add_icon, command=lambda: set_tool('add point'), style='Normal.TButton')
add_point.pack(side=tk.LEFT)
delete_icon = ImageTk.PhotoImage(Image.open('icons/minus_point.png').resize((40, 40)))
delete_point = ttk.Button(tools, image=delete_icon, command=lambda: set_tool('delete point'), style='Normal.TButton')
delete_point.pack(side=tk.LEFT)
add_curve_icon = ImageTk.PhotoImage(Image.open('icons/plus_curve_point.png').resize((40, 40)))
add_curve_point = ttk.Button(tools, image=add_curve_icon, command=lambda: set_tool('add curve point'), style='Normal.TButton')
add_curve_point.pack(side=tk.LEFT)
delete_curve_icon = ImageTk.PhotoImage(Image.open('icons/minus_curve_point.png').resize((40, 40)))
delete_curve_point = ttk.Button(tools, image=delete_curve_icon, command=lambda: set_tool('delete curve point'), style='Normal.TButton')
delete_curve_point.pack(side=tk.LEFT)
download = ttk.Button(root, text="Download", command=download)
tools.pack(pady=0, ipady=0)
canvas.pack(pady=0, padx=0, ipady=0)
download.pack()
Point(w/4, h/4)
Point(w/4*3, h/4)
Point(w/4*3, h/4*3)
Point(w/4, h/4*3)
Point.setup_point_class()
root.after(0, update_bg)


root.mainloop()