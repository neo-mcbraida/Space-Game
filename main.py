''' 
screen resolution: 1366x768
cheat codes:
score = n # where n in any int you choose
closing_indexes = [] # stops the doors closing
'''

import json
from math import tan, pi
from tkinter import *
import random
from sys import platform

window = Tk()

window.geometry("1366x768")

canvWidth, canvHeight = 1366, 768
x1, y1 = canvWidth // 2, canvHeight // 2


game_frame = Frame(window, width=canvWidth, height=canvHeight)

canvas = Canvas(game_frame, width=canvWidth, height=canvHeight)
canvas.pack()
class AbsoluteShape:
    def __init__(self, coords):
        self.x_coords = coords[0]
        self.y_coords = coords[1]
        self.z_coords = coords[2]
        self.width = 0
        self.height = 0
        self.offset_x = 0
        self.offset_y = 0
    
    def Set_Coords(self, changes): # strictly for enlarging door
        for i in [1, 3]: # zeroth index is always corner
            self.x_coords[i] =  self.x_coords[i] + changes[0]
        for i in [2, 4]:
            self.y_coords[i] =  self.y_coords[i] + changes[1]
        for i in range(len(self.z_coords)):
            self.z_coords[i] += changes[2]
        self.width = abs(self.x_coords[0] - self.x_coords[1])
        self.height = abs(self.y_coords[0] - self.y_coords[1])

    def Shift_Coords(self, changes):
        self.offset_x += changes[0]
        self.offset_y += changes[1]
        for i in range(len(self.x_coords)):
            self.x_coords[i] += changes[0]
            self.y_coords[i] += changes[1]
            self.z_coords[i] += changes[2]

class PerspectShape(AbsoluteShape):
    def __init__(self, coords, width, height):
        self.width = width
        self.height = height
        self.perspect_coords_x = [0]
        self.perspect_coords_y = [0]
        self.perspect_coords_z = [0]
        self.shape_coords = []
        self.working_distance = 100 # constant
        super(PerspectShape, self).__init__(coords)

    def Set_Scaled_Coords(self):
        perspect_coords_y = []
        perspect_coords_x = []
        cancel = False
        for coord_ind in range(len(self.x_coords)):
            ratio = self.z_coords[coord_ind] / self.working_distance
            if ratio != 0:
                rel_x = self.x_coords[coord_ind] / ratio
                rel_y = self.y_coords[coord_ind] / ratio
                perspect_coords_x.append(rel_x)
                perspect_coords_y.append(rel_y)
            else:
                cancel = True
                break
        if not cancel:
            self.perspect_coords_x = perspect_coords_x
            self.perspect_coords_y = perspect_coords_y

    def Get_OffSet_Coords(self, canv_width=1366, canv_height=768):
        coords_x = []
        coords_y = []
        change_x = 0.5 * canv_width
        change_y = 0.5 * canv_height
        for i in range(len(self.perspect_coords_x)):
            coords_x.append(self.perspect_coords_x[i] + change_x)
            coords_y.append(self.perspect_coords_y[i] + change_y)
        return coords_x, coords_y

class Edge(PerspectShape):
    def __init__(self, coords, colour):
        self.edge = canvas.create_polygon((0, 0), (0, 0))
        self.colour = colour
        super(Edge, self).__init__(coords, 10, 10)

    def Move_Forward(self, change):
        if self.z_coords[1] > 10:
            self.z_coords[1] += change[2]
            self.z_coords[2] += change[2]

    def Step(self, speed, move_forward=False):
        canvas.delete(self.edge)
        if move_forward:
            self.Move_Forward([0, 0, -speed])
        self.Set_Scaled_Coords()
        self.offset_coords_x, self.offset_coords_y = self.Get_OffSet_Coords()
        self.Update_Polygon()

    def Update_Polygon(self):        
        self.edge = canvas.create_polygon(
            (self.offset_coords_x[0], self.offset_coords_y[0]),
            (self.offset_coords_x[1], self.offset_coords_y[1]),
            (self.offset_coords_x[2], self.offset_coords_y[2]),
            (self.offset_coords_x[3], self.offset_coords_y[3]),
            fill=self.colour,
            outline="black"
        )

    def __del__(self):
        canvas.delete(self.edge)

class Door:
    def __init__(self, coords, dir_x, dir_y, shut_speed, move_speed, edge_colour, triangle_colour):
        self.offset_coords_x = []
        self.offset_coords_y = []
        self.object = PerspectShape(coords, canvWidth, canvHeight)
        self.edge_colour = edge_colour
        self.triangle_colour = triangle_colour
        self.shut_speed = shut_speed
        self.move_speed = move_speed
        self.dir_x = dir_x
        self.dir_y = dir_y
        self.canv_height = 768
        self.canv_width = 1366
        self.edge = canvas.create_polygon((0, 0), (0, 0))
        self.triangle = canvas.create_polygon((0, 0), (0, 0))

    def __del__(self):
        self.Delete_Polygons()

    def Close(self):
        change_x = self.shut_speed * self.dir_x * (self.canv_width/self.canv_height)
        change_y = self.shut_speed * self.dir_y
        change_z = 0
        self.object.Set_Coords((change_x, change_y, change_z))

    def Move_Forward(self):
        change_z = -self.move_speed
        self.object.Set_Coords((0, 0, change_z))

    def Delete_Polygons(self):
        canvas.delete(self.triangle)
        canvas.delete(self.edge)

    def Update_Polygon(self):
        self.Delete_Polygons()
        self.edge = canvas.create_polygon(
            (self.offset_coords_x[1], self.offset_coords_y[1]),
            (self.offset_coords_x[2], self.offset_coords_y[2]),
            (self.offset_coords_x[4], self.offset_coords_y[4]),
            (self.offset_coords_x[3], self.offset_coords_y[3]),
            fill=self.edge_colour,
            outline="black"
        )
        self.triangle = canvas.create_polygon(
            (self.offset_coords_x[0], self.offset_coords_y[0]),
            (self.offset_coords_x[1], self.offset_coords_y[1]),
            (self.offset_coords_x[2], self.offset_coords_y[2]),
            fill=self.triangle_colour,
            outline="black"
        )

    def Step(self):
        self.Move_Forward()
        self.object.Set_Scaled_Coords()
        self.offset_coords_x, self.offset_coords_y = self.object.Get_OffSet_Coords(self.canv_width, self.canv_height)
        self.Update_Polygon()

    def Get_Line_Equation(self):
        x_diff = abs(self.object.x_coords[0] - self.object.x_coords[1]) * self.dir_x
        if x_diff == 0:
            grad = NONE
            intercept = NONE
        else:
            grad = (-self.dir_y * abs(self.object.y_coords[0] - self.object.y_coords[2])) / x_diff # negative because of y dir on canvasas
            intercept = self.object.y_coords[1] - (grad * self.object.x_coords[1]) + (0.5 * 768)
        return grad, intercept

class Scene:
    def __init__(self, door0, door1, door2, door3, width, height):
        self.pressed_keys = set(())
        self.cont = True
        self.door0 = door0
        self.door1 = door1
        self.door2 = door2
        self.door3 = door3
        self.canv_width = width
        self.canv_height = height
        self.doors = [self.door0, self.door1, self.door2, self.door3]
        self.open_indexes = [0, 1, 2, 3]
        self.closing_indexes = []
        self.objects = [self.door0, self.door1, self.door2, self.door3]
        self.walls = []
        self.front_edges = []
        self.back_edges = []
        self.offset = [0, 0]
        self.pos = [0, 0]
        self.restart = True
        self.move_speed = 1
        self.shut_speed = 0.5
        self.hitbox = [683, 384]
        self.score = 0
        self.Make_Score_Label()
        self.Create_Edges()

    def Save_Json(self):
        info = [self.move_speed, self.shut_speed, self.score]
        with open('game_state.json', 'w') as f:
            json.dump(info, f)

    def Make_Score_Label(self):
        self.score_label = Label(canvas, text="score: " + str(self.score), fg='white', bg='black', font=("Helvetica", 32))
        self.score_window = canvas.create_window(1100, 100, window=self.score_label)

    def Load_Json(self):
        with open("game_state.json") as f:
            info = json.load(f)
        self.score = info[2]
        self.shut_speed = info[1]
        self.move_speed = info[0]
        self.score_label.configure(text="score: " + str(self.score))
        for i in range(len(self.doors)):
            self.doors[i].shut_speed = self.shut_speed
            self.doors[i].move_speed = self.move_speed
        self.front_edges[0].move_speed = self.move_speed

    def Passed_Door(self):
        if self.door0.object.z_coords[0] <= 10:
            self.move_speed += 0.1
            self.shut_speed += 0.05
            self.Create_Doors()
            self.Create_Edges()
            self.score += 1
            self.score_label.configure(text="score: " + str(self.score))
            offset = [self.pos[0], self.pos[1], 0]
            for i in range(4):
               del self.doors[0]
               self.doors[3].object.Shift_Coords(offset)
               self.objects.pop(0)
               del self.front_edges[0]
               del self.back_edges[0]
               self.back_edges[3].Shift_Coords(offset)

    def Create_Doors(self):
        coords = Create_Coords()
        self.door0 = Door(coords[0], 1, -1, self.shut_speed, self.move_speed, "#53575c", "#212224")
        self.door1 = Door(coords[1], -1, -1, self.shut_speed, self.move_speed, "#53575c", "#212224")
        self.door2 = Door(coords[2], 1, 1, self.shut_speed, self.move_speed, "#53575c", "#212224")
        self.door3 = Door(coords[3], -1, 1, self.shut_speed, self.move_speed, "#53575c", "#212224")
        self.doors.append(self.door0)
        self.objects.append(self.door0)
        self.doors.append(self.door1)
        self.objects.append(self.door1)
        self.doors.append(self.door2)
        self.objects.append(self.door2)
        self.doors.append(self.door3)
        self.objects.append(self.door3)

    def Check_Crash(self):
        if self.door0.object.z_coords[0] <= 10:
            for i in range(4):
                m, c = self.doors[i].Get_Line_Equation()
                dir_y = self.doors[i].dir_y
                coords = [self.hitbox[0]-self.pos[0], self.hitbox[1]-self.pos[1]]
                if m != NONE:
                    y = m * self.hitbox[0] + c
                    if (dir_y == 1 and coords[1] < y) or (dir_y == -1 and coords[1] > y):
                        self.cont = False
                        self.Save_Json()
                        canvas.create_image(0, 0, image=black_screen, anchor=NW)
                        Restart()

    def Create_Edges(self):
        offset_x = 100
        offset_y = 100
        _canv_width = 0.5 * 1366
        _canv_height = 0.5 * 768
        corner1 = [-_canv_width, _canv_height]
        corner2 = [_canv_width, _canv_height]
        colour = "#8a8888"
        self.Create_Edge(corner1, corner2, colour)
        corner1 = [_canv_width, _canv_height]
        corner2 = [_canv_width, -_canv_height]
        colour = "#615e5e"
        self.Create_Edge(corner1, corner2, colour)
        corner1 = [_canv_width, -_canv_height]
        corner2 = [-_canv_width, -_canv_height]
        colour = "#4d4d4d"
        self.Create_Edge(corner1, corner2, colour)
        corner1 = [-_canv_width, -_canv_height]
        corner2 = [-_canv_width, _canv_height]
        colour = "#8a8888"
        self.Create_Edge(corner1, corner2, colour)
        
    def Create_Edge(self, corner1, corner2, colour, z_coord=500):
        x = [corner1[0], corner1[0], corner2[0], corner2[0]]
        y = [corner1[1], corner1[1], corner2[1], corner2[1]]
        coords = [x, y, [10, z_coord, z_coord, 10]]
        edge1 = Edge(coords, colour)
        self.front_edges.append(edge1)
        coords = [x, y, [10, z_coord + 1000050, z_coord + 1000050, 10]]
        edge2 = Edge(coords, colour)
        self.back_edges.append(edge2)

    def Get_Start_Doors(self):
        index1 = random.randint(0, 1)
        index2 = random.randint(2, 3)
        self.open_indexes.remove(index1)
        self.open_indexes.remove(index2)
        self.closing_indexes.append(index1)
        self.closing_indexes.append(index2)

    def Set_Shut_Start(self):
        temp = self.open_indexes
        for i in range(len(temp)):
            to_shut = int(round(random.randint(0, 5001) / 10000)) # number between 0 and 0.5005 rounded to nearest 1
            if to_shut == 1:
                self.closing_indexes.append(self.open_indexes[i])
                self.open_indexes.pop(i)

    def Set_Shutting_Doors(self):
        if self.restart:
            self.Get_Start_Doors()
            self.restart = False
        self.Set_Shut_Start()

    def Shift_Objects(self):
        shift = [self.offset[0], self.offset[1], 0]
        for object in self.objects:
            object.object.Shift_Coords(shift)
        for i in range(len(self.front_edges)):
            self.front_edges[i].Shift_Coords(shift)

    def Move(self):
        if platform == "win32":
            change = 10
        else:
            change = 17
        x_offset = 0
        y_offset = 0
        if 'a' in self.pressed_keys and self.pos[0] < (0.5 * self.canv_width - 80):
            x_offset += change
        if 'd' in self.pressed_keys and -self.pos[0] < (0.5 * self.canv_width - 80):
            x_offset += -change
        if 'w' in self.pressed_keys and self.pos[1] < (0.5 * self.canv_height - 50):
            y_offset += change
        if 's' in self.pressed_keys and -self.pos[1] < (0.5 * self.canv_height - 50):
            y_offset += -change
        self.offset = [x_offset, y_offset]
        self.pos[0] += x_offset
        self.pos[1] += y_offset
        if platform != "win32":
            self.pressed_keys = set(()) # as linux keyrelease function doesnt work

    def Step(self):
        if door0.object.z_coords[0] <= 10:
            print("testing")
        self.Move()
        self.Shift_Objects()
        self.Set_Shutting_Doors()
        for i in range(len(self.back_edges)):
            self.back_edges[i].Step(self.move_speed)
        for i in range(len(self.objects)):
            self.doors[i].Step()
            if i in self.closing_indexes:
                self.doors[i].Close()
        for i in range(len(self.front_edges)):
            self.front_edges[i].Step(self.move_speed, True)
        self.Check_Crash()
        self.Passed_Door()
        
    def Add_Key(self, key):
        self.pressed_keys.add(key)

    def Remove_Key(self, key):
        self.pressed_keys.remove(key)

    def Run_Cheat_Code(self, code):
        command = code.split('=')
        instruction = "self." + command[0] + "=" + command[1]
        try:
            exec(instruction)
            return "run"
        except:
            return "not valid instruction"

# load score
try:
    path = "scores.json"
    with open(path) as f:
        scores = json.load(f)
    print(scores)
except:
    scores = {}
    print("no scores")


high_score_path = "highscore.png"
hs_im = PhotoImage(file=high_score_path)
menu_bg_path = "menu.png"
bg_im = PhotoImage(file=menu_bg_path)
boss_path = "boss.png"
boss = PhotoImage(file=boss_path)
game_over_path = "game_over.png"
game_over = PhotoImage(file=game_over_path)
black_screen_path = "black.png"
black_screen = PhotoImage(file=black_screen_path)
ship = PhotoImage(file="cockpit.png")
items = []

menu_frame = Frame(window, width=canvWidth, height=canvHeight)
menu_buttons = []
name = "RND"
boss_cover = NONE
buttons = ['w', 'a', 's', 'd', 'p', 'b']

menu_canv = Canvas(menu_frame, width=canvWidth, height=canvHeight)
menu_canv.create_image(0, 0, image=bg_im, anchor=NW)
menu_canv.place(x=0, y=0)


window.grid_rowconfigure(0, weight = 1)
window.grid_columnconfigure(0, weight = 1)

scrollbar = Scrollbar(menu_frame, width=100)
scrollbar.place(x=40, y=450)

mylist = Listbox(menu_frame, yscrollcommand = scrollbar.set, width=100)

mylist.place(x=600, y=40)
scrollbar.config( command = mylist.yview)

def Show_Scores():
    global mylist, scores
    raw_scores = []
    mylist.delete(0, END)
    for key in scores:
        score = scores[key]
        if len(raw_scores) == 0:
            raw_scores.append(score)
            mylist.insert(END, key + ": " + str(scores[key]))
        else:
            for i in range(len(raw_scores)):
                if score > raw_scores[i]:
                    mylist.insert(i, key + ": " + str(scores[key]))
                    raw_scores.insert(i, score)
                    break
                elif i == len(raw_scores) - 1:
                    mylist.insert(END, key + ": " + str(scores[key]))
                    raw_scores.append(score)


def Save_Name():
    global name
    print("saved name")
    temp_name = initials_ent.get()
    if len(temp_name) == 3:
        name = temp_name.upper()
    else:
        initials_ent.delete(0, END)
        initials_ent.insert(END, "must be 3 characters")

def Create_Coords(offset=[0, 0]):
    coords = []
    corner_x = -0.5 * canvWidth
    corner_y = 0.5 * canvHeight
    z = 500
    for i in range(4):
        x = corner_x + offset[0]
        y = corner_y + offset[1]
        coord = [
            [x, x, x, x, x],
            [y, y, y, y, y],
            [z, z, z, z+50, z+50]
        ]
        coords.append(coord)
        corner_x *= -1
        if corner_x < 0:
            corner_y *= -1
        z = 500
        if i == 0 or i == 1:
            z += 50

    return coords

paused = False

coords = Create_Coords()
door0 = Door(coords[0], 1, -1, 0.5, 1, "#53575c", "#212224")
door1 = Door(coords[1], -1, -1, 0.5, 1, "#53575c", "#212224")
door2 = Door(coords[2], 1, 1, 0.5, 1, "#53575c", "#212224")
door3 = Door(coords[3], -1, 1, 0.5, 1, "#53575c", "#212224")

scene = Scene(door1, door2, door0, door3, canvWidth, canvHeight)

initials_ent = Entry(menu_frame, width=20, validate="focusout", validatecommand=lambda:Validate())
initials_ent.place(x=500, y=300)
initials_ent.insert(END, 'enter 3 digit name')
save_name = Button(menu_frame, text="save name", command=lambda:Save_Name())
save_name.place(x=700, y=300)

pause_lab = Label(menu_frame, text="pause button: ")
pause_lab.place(x=500, y=400)
pause_ent = Entry(menu_frame, width=2, validate="focusout", validatecommand=lambda:Validate())
pause_ent.place(x=587, y=400)
pause_ent.insert(END, 'p')
up_lab = Label(menu_frame, text="up button: ")
up_lab.place(x=625, y=400)
up_ent = Entry(menu_frame, width=2, validate="focusout", validatecommand=lambda:Validate())
up_ent.place(x=695, y=400)
up_ent.insert(END, 'w')
left_lab = Label(menu_frame, text="left button: ")
left_lab.place(x=735, y=400)
left_ent = Entry(menu_frame, width=2, validate="focusout", validatecommand=lambda:Validate())
left_ent.place(x=807, y=400)
left_ent.insert(END, 'a')
down_lab = Label(menu_frame, text="down button: ")
down_lab.place(x=850, y=400)
down_ent = Entry(menu_frame, width=2, validate="focusout", validatecommand=lambda:Validate())
down_ent.place(x=935, y=400)
down_ent.insert(END, 's')
right_lab = Label(menu_frame, text="right button")
right_lab.place(x=970, y=400)
right_ent = Entry(menu_frame, width=2, validate="focusout", validatecommand=lambda:Validate())
right_ent.place(x=1045, y=400)
right_ent.insert(END, 'd')
boss_lab = Label(menu_frame, text="boss button")
boss_lab.place(x=1090, y=400)
boss_ent = Entry(menu_frame, width=2, validate="focusout", validatecommand=lambda:Validate())
boss_ent.place(x=1165, y=400)
boss_ent.insert(END, 'b')
save_buttons = Button(menu_frame, text="save buttons", width=10, height=2, command=lambda:Save_Buttons())
save_buttons.place(x=500, y=440)


def Start(continue_game = False):
    global coords, door0, door1, door2, door3, scene, paused, items

    scene.score_label.destroy()
    canvas.delete("all")

    coords = Create_Coords()
    door0 = Door(coords[0], 1, -1, 0.5, 1, "#53575c", "#212224")
    door1 = Door(coords[1], -1, -1, 0.5, 1, "#53575c", "#212224")
    door2 = Door(coords[2], 1, 1, 0.5, 1, "#53575c", "#212224")
    door3 = Door(coords[3], -1, 1, 0.5, 1, "#53575c", "#212224")
    items = Create_Ship()
    scene = Scene(door1, door2, door0, door3, canvWidth, canvHeight)

    paused = False
    if continue_game:
        scene.Load_Json()
    
    Shut()

def Restart():
    global paused, game_over
    Set_HS()
    paused = True
    Show_Pause_Menu(False)
    canvas.create_image(400, -20, image=game_over, anchor=NW)

def Save_Scores():
    global scores
    with open('scores.json', 'w') as fp:
        json.dump(scores, fp)

def Set_HS():
    global name, scores
    score = scene.score
    if name not in scores or scores[name] < score:
        scores[name] = score
        Show_HS()
        Show_Scores()
        Save_Scores()

def Show_HS():
    image = canvas.create_image(685, 300, image=hs_im)

def keypress(event):
    global paused, buttons
    key = event.char.lower()
    if key in buttons:
        if key == buttons[4]:
            Handle_Pause()
        elif key == buttons[5]:
            Handle_Boss()
        else:
            scene.Add_Key(key.lower())

def Handle_Boss():
    global boss_cover, paused
    paused = not paused
    if paused:
        boss_cover = canvas.create_image(0, 0, image=boss, anchor=NW)
        scene.score_label.destroy()
    else:
        canvas.delete(boss_cover)
        scene.Make_Score_Label()

def Handle_Pause():
    global paused
    paused = not paused
    if paused:
        Show_Pause_Menu()
    else:
        Remove_Menu()

def Remove_Menu():
    for i in range(len(menu_buttons)):
        canvas.delete(menu_buttons[i])

def keyup(event):
    global scene
    print(event.type)
    key = event.char.lower()
    for i in range(4):
        if key == buttons[i] and key in scene.pressed_keys:
            scene.Remove_Key(key)

def Quite_Game():
    Remove_Menu()
    menu_frame.tkraise()

def Save_Quit():
    scene.Save_Json()
    Quite_Game()

def Show_Pause_Menu(show_cont = True):
    if show_cont:
        button1 = Button(canvas, text="Resume",
                        command=lambda : Handle_Pause())
        button1.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
        button1_window = canvas.create_window(10, 10, anchor=NW, window=button1)
        menu_buttons.append(button1_window)
        button2 = Button(canvas, text="Save and Quit",
                        command=lambda : Save_Quit())
        button2.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
        button2_window = canvas.create_window(100, 10, anchor=NW, window=button2)
        menu_buttons.append(button2_window)
        code_button = Button(canvas, text="Run", command=lambda:Run_Cheat_Code(code_ent))
        code_button.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
        code_win = canvas.create_window(500, 10, anchor=NW, window=code_button)
        code_ent = Entry(canvas, text="", width=50, validate="focusout", validatecommand=lambda:Validate())
        ent_win = canvas.create_window(600, 10, anchor=NW, window=code_ent)
        
        menu_buttons.append(code_win)
        menu_buttons.append(ent_win)
    button3 = Button(canvas, text="Quit",
                    command=lambda : Quite_Game())
    button3.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
    button3_window = canvas.create_window(190, 10, anchor=NW, window=button3)
    menu_buttons.append(button3_window)

    button4 = Button(canvas, text="Restart", command=lambda : Start())
    button4.configure(width = 10, activebackground = "#33B5E5", relief = FLAT)
    button4_window = canvas.create_window(280, 10, anchor=NW, window=button4)
    menu_buttons.append(button4_window)

def Run_Cheat_Code(code_ent):
    code = code_ent.get()
    out = scene.Run_Cheat_Code(code)
    code_ent.delete(0, END)
    code_ent.insert(END, out)

def Create_Ship():
    items = []
    pol5 = canvas.create_polygon((283, canvHeight), (268, 600), (1234, 600), (1216, canvHeight), fill="#706d6d", 
            outline="black")
    items.append(pol5)
    pol1 = canvas.create_polygon((0, canvHeight), (283, canvHeight), (283, 629), fill="#706d6d", 
            outline="black")
    items.append(pol1)
    pol2 = canvas.create_polygon((1216, canvHeight), (1216, 629), (canvWidth, canvHeight), fill="#423f3f", 
            outline="black")
    items.append(pol2)
    pol3 = canvas.create_polygon((1205, canvHeight), (1216, 640), (canvWidth-40, -50), (canvWidth+50, 40), fill="#423f3f", 
            outline="black")
    items.append(pol3)
    pol4 = canvas.create_polygon((294, canvHeight), (283, 640), (40, -50), (-50, 40), fill="#706d6d", 
            outline="black")
    items.append(pol4)
    ship_im = canvas.create_image(283, 629, image=ship, anchor=NW)
    items.append(ship_im)

    return items

def Lift_Ship():
    for pol in items:
        canvas.lift(pol)

def Shut():
    while True:
        if not paused:
            scene.Step()
            Lift_Ship()
        window.update()

def Show_Menu():
    menu_frame.tkraise()

def Validate():
    print("focussed out")

# takes to game window
def Start_Button():
    print("start")
    
    game_frame.tkraise()
    Start()

def Quit_Button():
    window.destroy()

def Continue_Button():
    game_frame.tkraise()
    Start(True)

def Save_Buttons():
    global buttons
    index = 0
    key = up_ent.get()
    Assign_Button(index, key)
    index += 1
    key = left_ent.get()
    Assign_Button(index, key)
    index += 1
    key = down_ent.get()
    Assign_Button(index, key)
    index += 1
    key = right_ent.get()
    Assign_Button(index, key)
    index += 1
    key = pause_ent.get()
    Assign_Button(index, key)
    index += 1
    key = boss_ent.get()
    Assign_Button(index, key)

def Assign_Button(index, key):
    global buttons
    if len(key) == 1 and key.isalpha():
        buttons[index] = key.lower()

start_button = Button(menu_frame, text="Start!", command = lambda : Start_Button(), width=50, height=10)
start_button.place(x=40, y=40)

continue_button = Button(menu_frame, text="Continue!", command = lambda : Continue_Button(), width=50, height=10)
continue_button.place(x=40, y=250)

quit_button = Button(menu_frame, text="Quit", command = lambda : Quit_Button(), width=50, height=10)
quit_button.place(x=40, y=450)

menu_frame.grid(row = 0, column = 0, sticky ="nsew")
game_frame.grid(row = 0, column = 0, sticky ="nsew")

if platform == "win32":
    #this doesnt work on linux
    window.bind('<KeyRelease>', keyup)

window.bind("<KeyPress>", keypress)

Show_Scores()
Show_Menu()
window.mainloop()