import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image, ImageDraw, ImageEnhance
from tkinter.constants import *
import copy

class Point:
    points = []
    mouse = (0, 0)
    shift = False

    def __init__(self, x, y, point=-1):
        self.pos = (x, y)
        self.point = canvas.create_oval(self.pos[0] - 5, self.pos[1] - 5, self.pos[0] + 5, self.pos[1] + 5, fill='white', width=0)

        self.dragging = False
        Point.points.insert(point, self)
        self.line = canvas.create_line(*self.pos, *Point.points[(point + 1) % len(Point.points)].pos, width=5, fill='blue')
        canvas.tag_raise(self.point, crop_img)
        canvas.tag_lower(self.line, self.point)
        canvas.tag_raise(self.point, Point.points[Point.points.index(self) - 1].line)
        canvas.tag_raise(self.point, Point.points[Point.points.index(self) - 1].point)

        root.after(0, self.frame)

    def frame(self):
        if self in Point.points:
            after = Point.points[(Point.points.index(self) + 1) % len(Point.points)]
            canvas.coords(self.line, *self.pos, *after.pos)
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
            elif elm[0] == self.line and tool == 'add point':
                Point(event.x, event.y, point=Point.points.index(self) + 1)

    def mouse_up(self):
        self.dragging = False

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
        print('down')
        cls.shift = True

    @classmethod
    def shift_up(cls, _):
        print('up')
        cls.shift = False

    @classmethod
    def setup_point_class(cls):
        if cls.points:
            canvas.bind("<ButtonPress-1>", cls.run_downs)
            canvas.bind("<ButtonRelease-1>", cls.run_ups)
            canvas.bind("<Motion>", cls.mouse_move)
            root.bind('<Shift_L>', cls.shift_down)
            root.bind('<Shift_R>', cls.shift_down)
            root.bind('<KeyRelease-Shift_L>', cls.shift_up)
            root.bind('<KeyRelease-Shift_R>', cls.shift_up)


def update_bg():
    global new_img
    root.after(15, update_bg)
    mask = Image.new("RGBA", (w, h), 0)
    ImageDraw.Draw(mask).polygon([point.pos for point in Point.points], fill='black', outline=None)
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
    elif tool == 'curve':
        button = curve_point
    button.config(style='Normal.TButton')
    tool = name
    if tool == 'drag':
        button = drag
    elif tool == 'add point':
        button = add_point
    elif tool == 'delete point':
        button = delete_point
    elif tool == 'curve':
        button = curve_point
    button.config(style='Blue.TButton')



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
curve_icon = ImageTk.PhotoImage(Image.open('icons/curve.png').resize((40, 40)))
curve_point = ttk.Button(tools, image=curve_icon, command=lambda: set_tool('curve'), style='Normal.TButton')
curve_point.pack(side=tk.LEFT)
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