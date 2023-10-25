from tkinter import Button, Canvas, colorchooser, Entry, Frame, IntVar, Label, Listbox, Menu, Radiobutton, Checkbutton, Toplevel, Tk
from tkinter.messagebox import askyesnocancel, showerror
from tkinter.filedialog import askopenfilename, asksaveasfilename
from pyautogui import size, moveTo, click, locateOnScreen
from keyboard import on_press_key
from math import sqrt


PATH = __file__[:-8]
FONT = "Consolas 10"
size_window_pos = [0, 0, 500, 500]
center_tile_pos = [250, 250, -50, 50, -25, 25]

class Bot:
    def __init__(self, master):
        self.__master = master
        self.__path = []
        self.__n_buttons = []
        self.__recuperation_time = 5
        self.__wait_ressources = 1
        self.__is_running = False
        self.__is_compute = False
        self.__index = 0

    def change_wait_ressources(self, wait_ressources): self.__wait_ressources = wait_ressources

    def is_running(self): return self.__is_running

    def is_compute(self): return self.__is_compute

    def path_change(self):
        for i in range(len(self.__path)): del self.__path[0]
        self.__is_compute = False

    def get_path(self): return self.__path

    def __path_finding(self, start_x, start_y, end_x, end_y, grid, grid_height):
        l = [(start_x, start_y)]
        closed = []
        grid2 = [[-1 for x in range(len(grid[0]))] for y in range(len(grid))]
        grid2[start_y][start_x] = 0
        grid2[end_y][end_x] = -1
        path = []
        while len(l) > 0:
            for i in range(len(l)):
                if l[0][0] == end_x and l[0][1] == end_y:
                    path += [l[0]]
                    del l[:]
                    break
                n = grid2[l[0][1]][l[0][0]]+1
                for i in [(l[0][0]-1, l[0][1]), (l[0][0]+1, l[0][1]), (l[0][0], l[0][1]-1), (l[0][0], l[0][1]+1)]:
                    if 0 <= i[0] < len(grid[0]) and 0 <= i[1] < len(grid) and (i[0] == end_x and i[1] == end_y or grid[i[1]][i[0]]) and abs(grid_height[i[1]][i[0]]-grid_height[l[0][1]][l[0][0]]) < 2 and not i in closed:
                        l += [i]
                        grid2[i[1]][i[0]] = n
                    closed += [i]
                del l[0]
        if len(path) == 0: return None
        else:
            for i in range(grid2[path[0][1]][path[0][0]], 0, -1):
                for j in [(path[0][0]-1, path[0][1]), (path[0][0]+1, path[0][1]), (path[0][0], path[0][1]-1), (path[0][0], path[0][1]+1)]:
                    if 0 <= j[0] < len(grid[0]) and 0 <= j[1] < len(grid) and grid2[j[1]][j[0]] == i-1:
                        path = [j]+path
                        break
            return path

    def compute_path(self, x, y, grid_walls, grid_height, list_ressources, n_buttons, recuperation_time):
        self.__index = 0
        self.__recuperation_time = float(recuperation_time)
        del self.__n_buttons[:]
        del self.__path[:]
        self.__n_buttons = n_buttons
        if self.__n_buttons[1] > self.__n_buttons[0]: self.__n_buttons[1] = self.__n_buttons[0]
        self.__path += [((x, y), grid_height[y][x])]
        while len(list_ressources) > 0:
            i, b = 0, [None, None]
            while i < len(list_ressources):
                path = self.__path_finding(self.__path[-1][0][0], self.__path[-1][0][1], list_ressources[i][0], list_ressources[i][1], grid_walls, grid_height)
                if path == None: del list_ressources[i]
                else:
                    if b[1] == None or len(path) < len(b[1]):
                        b[0] = i
                        del b[1]
                        b += [path]
                    i += 1
            if b[0] != None and b[1] != None:
                for i in b[1][:-1]: self.__path += [(i, grid_height[i[1]][i[0]])]
                self.__path += [None, (b[1][-1], grid_height[b[1][-1][1]][b[1][-1][0]]), self.__path[-1]]
                del list_ressources[b[0]]
        self.__path += [(i, grid_height[i[1]][i[0]]) for i in self.__path_finding(self.__path[-1][0][0], self.__path[-1][0][1], x, y, grid_walls, grid_height)[:-1]]
        self.__is_compute = True

    def __get_coords_click(self, i):
        x, y, height = self.__path[i][0][0]-self.__path[self.__index][0][0], self.__path[i][0][1]-self.__path[self.__index][0][1], self.__path[i][1]-self.__path[self.__index][1]
        return center_tile_pos[0]+center_tile_pos[3]*(x-y), center_tile_pos[1]+center_tile_pos[5]*(x+y-height)-10

    def __click_on_tile(self):
        if self.is_running():
            if None in self.__path:
                if self.__index < len(self.__path)-1 and self.__path[self.__index+1] == None:
                    x, y = self.__get_coords_click(self.__index+2)
                    click(x, y, button="right")
                    if self.__n_buttons[0] == 1:
                        y -= 40
                        name = "arrow_down.png"
                    elif self.__n_buttons[0] == 2:
                        x += 45*(self.__n_buttons[1]*2-3)
                        y -= 40
                        name = ["arrow_diag_right.png", "arrow_diag_left"][self.__n_buttons[1]-1]
                    elif self.__n_buttons[0] == 3:
                        if self.__n_buttons[1] == 1: y -= 145
                        else:
                            x += 75*(self.__n_buttons[1]-2)
                            y -= 100
                        name = ["arrow_diag_right.png", "arrow_down.png", "arrow_diag_left"][self.__n_buttons[1]-1]
                    moveTo(x, y)
                    # if locateOnScreen(PATH+name) == None:
                    #     if self.__wait_ressources: self.__master.get_window().after(5000, self.__click_on_tile)
                    #     else:
                    #         self.__index += 3
                    #         if self.__index == len(self.__path): self.__index = 0
                    #         click(center_tile_pos[0], center_tile_pos[1], button="left")
                    #         self.__master.get_window().after(1, self.__click_on_tile)
                    # else:
                    click(x, y, button="left")
                    self.__index += 3
                    if self.__index == len(self.__path): self.__index = 0
                    self.__master.get_window().after(int(self.__recuperation_time*1000)+500, self.__click_on_tile)
                else:
                    j, x, y, n = self.__index, size_window_pos[0]+1, size_window_pos[1]+1, 0
                    while size_window_pos[0] < x < size_window_pos[2] and size_window_pos[1] < y < size_window_pos[3]:
                        n += 1
                        j += 1
                        if j == len(self.__path): j = 0
                        if self.__path[j] == None: break
                        else: x, y = self.__get_coords_click(j)
                    j -= 1
                    if j == -1: j = len(self.__path)-1
                    if self.__path[j-1] == None: j -= 2
                    x, y = self.__get_coords_click(j)
                    click(x, y, button="left")
                    self.__index = j
                    self.__master.set_bot_pos(self.__path[self.__index][0][0], self.__path[self.__index][0][1])
                    self.__master.get_window().after(400*(n-1), self.__click_on_tile)
            else: self.__master.start_bot()

    def start(self):
        self.__is_running = True
        self.__click_on_tile()

    def stop(self):
        self.__is_running = False

class SizeWindow:
    def __init__(self):
        self.__window = Tk()
        self.__width, self.__height = size()
        self.__window.geometry(str(self.__width)+"x"+str(self.__height))
        self.__window.overrideredirect(True)
        self.__window.wm_attributes("-transparentcolor", "white")
        self.__screen = Canvas(self.__window, width=self.__width, height=self.__height, bg="white", highlightthickness=0)
        self.__screen.pack(side="top", padx=0, pady=0)
        self.__display()
        self.__selection = None
        self.__screen.bind("<ButtonPress-1>", self.__mouse_button_down)
        self.__screen.bind("<ButtonRelease-1>", self.__mouse_button_up)
        self.__screen.bind("<Motion>", self.__mouse_motion)
        self.__window.after(1, self.__init)

    def __init(self): self.__window.mainloop()

    def destroy(self): self.__window.destroy()

    def __mouse_button_down(self, event):
        if size_window_pos[0]-5 <= event.x <= size_window_pos[0]+5 and size_window_pos[1]-5 <= event.y <= size_window_pos[1]+5: self.__selection = 0
        elif size_window_pos[2]-5 <= event.x <= size_window_pos[2]+5 and size_window_pos[1]-5 <= event.y <= size_window_pos[1]+5: self.__selection = 1
        elif size_window_pos[0]-5 <= event.x <= size_window_pos[0]+5 and size_window_pos[3]-5 <= event.y <= size_window_pos[3]+5: self.__selection = 2
        elif size_window_pos[2]-5 <= event.x <= size_window_pos[2]+5 and size_window_pos[3]-5 <= event.y <= size_window_pos[3]+5: self.__selection = 3
        elif center_tile_pos[0]-5 <= event.x <= center_tile_pos[0]+5 and center_tile_pos[1]-5 <= event.y <= center_tile_pos[1]+5: self.__selection = 4
        elif center_tile_pos[0]+center_tile_pos[2]-5 <= event.x <= center_tile_pos[0]+center_tile_pos[2]+5 and center_tile_pos[1]-5 <= event.y <= center_tile_pos[1]+5: self.__selection = 5
        elif center_tile_pos[0]+center_tile_pos[3]-5 <= event.x <= center_tile_pos[0]+center_tile_pos[3]+5 and center_tile_pos[1]-5 <= event.y <= center_tile_pos[1]+5: self.__selection = 6
        elif center_tile_pos[0]-5 <= event.x <= center_tile_pos[0]+5 and center_tile_pos[1]+center_tile_pos[4]-5 <= event.y <= center_tile_pos[1]+center_tile_pos[4]+5: self.__selection = 7
        elif center_tile_pos[0]-5 <= event.x <= center_tile_pos[0]+5 and center_tile_pos[1]+center_tile_pos[5]-5 <= event.y <= center_tile_pos[1]+center_tile_pos[5]+5: self.__selection = 8

    def __mouse_button_up(self, event): self.__selection = None

    def __mouse_motion(self, event):
        if self.__selection != None and 0 <= event.x < self.__width and 0 <= event.y < self.__height:
            if self.__selection < 4:
                if self.__selection == 0 or self.__selection == 2: size_window_pos[0] = event.x
                else: size_window_pos[2] = event.x
                if self.__selection < 2: size_window_pos[1] = event.y
                else: size_window_pos[3] = event.y
                if size_window_pos[0] > size_window_pos[2]: size_window_pos[0], size_window_pos[2], = size_window_pos[2], size_window_pos[0]
                if size_window_pos[1] > size_window_pos[3]: size_window_pos[1], size_window_pos[3] = size_window_pos[3], size_window_pos[1]
            elif self.__selection == 4: center_tile_pos[0], center_tile_pos[1] = event.x, event.y
            elif self.__selection == 5:
                center_tile_pos[2] = event.x-center_tile_pos[0]
                center_tile_pos[3] = -center_tile_pos[2]
            elif self.__selection == 6:
                center_tile_pos[3] = event.x-center_tile_pos[0]
                center_tile_pos[2] = -center_tile_pos[3]
            elif self.__selection == 7:
                center_tile_pos[4] = event.y-center_tile_pos[1]
                center_tile_pos[5] = -center_tile_pos[4]
            elif self.__selection == 8:
                center_tile_pos[5] = event.y-center_tile_pos[1]
                center_tile_pos[4] = -center_tile_pos[5]
            if center_tile_pos[2] > center_tile_pos[3]: center_tile_pos[2], center_tile_pos[3] = center_tile_pos[3], center_tile_pos[2]
            if center_tile_pos[4] > center_tile_pos[5]: center_tile_pos[4], center_tile_pos[5] = center_tile_pos[5], center_tile_pos[4]
            self.__display()
        else: self.__selection = None

    def __display(self):
        self.__screen.delete("all")
        self.__screen.create_line(size_window_pos[0], size_window_pos[1], size_window_pos[2], size_window_pos[1], fill="#0f0", width=2)
        self.__screen.create_line(size_window_pos[0], size_window_pos[3], size_window_pos[2], size_window_pos[3], fill="#0f0", width=2)
        self.__screen.create_line(size_window_pos[0], size_window_pos[1], size_window_pos[0], size_window_pos[3], fill="#0f0", width=2)
        self.__screen.create_line(size_window_pos[2], size_window_pos[1], size_window_pos[2], size_window_pos[3], fill="#0f0", width=2)
        self.__screen.create_oval(size_window_pos[0]-5, size_window_pos[1]-5, size_window_pos[0]+5, size_window_pos[1]+5, fill="#00f", outline="#00f")
        self.__screen.create_oval(size_window_pos[2]-5, size_window_pos[1]-5, size_window_pos[2]+5, size_window_pos[1]+5, fill="#00f", outline="#00f")
        self.__screen.create_oval(size_window_pos[0]-5, size_window_pos[3]-5, size_window_pos[0]+5, size_window_pos[3]+5, fill="#00f", outline="#00f")
        self.__screen.create_oval(size_window_pos[2]-5, size_window_pos[3]-5, size_window_pos[2]+5, size_window_pos[3]+5, fill="#00f", outline="#00f")
        self.__screen.create_line(center_tile_pos[0]+center_tile_pos[2], center_tile_pos[1], center_tile_pos[0], center_tile_pos[1]+center_tile_pos[4], fill="#0f0", width=2)
        self.__screen.create_line(center_tile_pos[0]+center_tile_pos[2], center_tile_pos[1], center_tile_pos[0], center_tile_pos[1]+center_tile_pos[5], fill="#0f0", width=2)
        self.__screen.create_line(center_tile_pos[0]+center_tile_pos[3], center_tile_pos[1], center_tile_pos[0], center_tile_pos[1]+center_tile_pos[4], fill="#0f0", width=2)
        self.__screen.create_line(center_tile_pos[0]+center_tile_pos[3], center_tile_pos[1], center_tile_pos[0], center_tile_pos[1]+center_tile_pos[5], fill="#0f0", width=2)
        self.__screen.create_oval(center_tile_pos[0]+center_tile_pos[2]-5, center_tile_pos[1]-5, center_tile_pos[0]+center_tile_pos[2]+5, center_tile_pos[1]+5, fill="#00f", outline="#00f")
        self.__screen.create_oval(center_tile_pos[0]+center_tile_pos[3]-5, center_tile_pos[1]-5, center_tile_pos[0]+center_tile_pos[3]+5, center_tile_pos[1]+5, fill="#00f", outline="#00f")
        self.__screen.create_oval(center_tile_pos[0]-5, center_tile_pos[1]+center_tile_pos[4]-5, center_tile_pos[0]+5, center_tile_pos[1]+center_tile_pos[4]+5, fill="#00f", outline="#00f")
        self.__screen.create_oval(center_tile_pos[0]-5, center_tile_pos[1]+center_tile_pos[5]-5, center_tile_pos[0]+5, center_tile_pos[1]+center_tile_pos[5]+5, fill="#00f", outline="#00f")
        self.__screen.create_oval(center_tile_pos[0]-5, center_tile_pos[1]-5, center_tile_pos[0]+5, center_tile_pos[1]+5, fill="#00f", outline="#00f")

class NewTypeWindow:
    def __init__(self, master, goal, name="Nouveau_Type", color="#000", n_buttons="1", can_walk_on="1", recuperation_time="5"):
        self.__master = master
        self.__goal = goal
        self.__window = Toplevel(self.__master.get_window())
        self.__window.grab_set()
        self.__window.title("Nouveau Type...")
        self.__window.resizable(width=False, height=False)
        self.__entry = Entry(self.__window, font=FONT, width=32)
        self.__entry.grid(row=0, column=0, sticky="w")
        self.__entry.insert(0, name)
        self.__button_color = Button(self.__window, text="  ", font=FONT, bg=color, command=self.__choose_color)
        self.__button_color.grid(row=0, column=1, sticky="nw")
        self.__frame = Frame(self.__window, borderwidth=0)
        self.__frame.grid(row=1, column=0, sticky="nw")
        self.__n_buttons = IntVar()
        self.__radiobutton1 = Radiobutton(self.__frame, text="1", font=FONT, variable=self.__n_buttons, value=1)
        self.__radiobutton1.grid(row=0, column=0)
        self.__radiobutton2 = Radiobutton(self.__frame, text="2", font=FONT, variable=self.__n_buttons, value=2)
        self.__radiobutton2.grid(row=0, column=1)
        self.__radiobutton3 = Radiobutton(self.__frame, text="3", font=FONT, variable=self.__n_buttons, value=3)
        self.__radiobutton3.grid(row=0, column=2)
        Label(self.__frame, text="boutons", font=FONT).grid(row=0, column=3)
        self.__n_buttons.set(int(n_buttons))
        self.__can_walk_on = IntVar()
        self.__checkbutton = Checkbutton(self.__window, text="Possible de marcher dessus", font=FONT, variable=self.__can_walk_on, onvalue=1, offvalue=0)
        self.__can_walk_on.set(int(can_walk_on))
        self.__checkbutton.grid(row=2, column=0, sticky="nw")
        self.__frame2 = Frame(self.__window, borderwidth=0)
        self.__frame2.grid(row=3, column=0, sticky="nw")
        Label(self.__frame2, text="Temps de récupération (s) : ", font=FONT).grid(row=0, column=0, sticky="nw")
        self.__entry_time = Entry(self.__frame2, font=FONT, width=4)
        self.__entry_time.grid(row=0, column=1, sticky="nw")
        self.__entry_time.insert(0, recuperation_time)
        self.__button_validate = Button(self.__window, text="Valider", font=FONT, command=self.__validate)
        self.__button_validate.grid(row=4, column=0, sticky="nw")
        self.__window.mainloop()

    def __choose_color(self):
        color = colorchooser.askcolor(title ="Choose color")[1]
        if color != None: self.__button_color["bg"] = color

    def __validate(self):
        if self.__entry.get() != "":
            is_ok = True
            for i in self.__entry_time.get():
                if not i in "0123456789.":
                    is_ok = False
                    break
            if not is_ok or self.__entry_time.get().count(".") > 1:
                showerror("Erreur", "Temps de récupération invalide.")
                return False
            else:
                name = self.__entry.get()
                for i in range(len(name)):
                    if name[i] == " ": name = name[:i]+"_"+name[i+1:]
                if self.__goal == "new": self.__master.add_type(name, self.__button_color["bg"], self.__n_buttons.get(), self.__can_walk_on.get(), self.__entry_time.get())
                else: self.__master.edit_type(self.__goal[4:], name, self.__button_color["bg"], self.__n_buttons.get(), self.__can_walk_on.get(), self.__entry_time.get())
                self.__window.destroy()
        else: showerror("Erreur", "Nom invalide.")

class MainWindow:
    def __init__(self):
        self.__window = Tk()
        self.__window.title("Bot Farming Wakfu")
        self.__window.resizable(width=False,height=False)
        self.__window.protocol("WM_DELETE_WINDOW", self.__destroy)
        self.__window.bind("<Control-n>", self.__new_map)
        self.__window.bind("<Control-o>", self.__open_map)
        self.__window.bind("<Control-s>", self.__save_map)
        self.__window.bind("<Control-Shift-s>", self.__save_map_as)
        self.__window.bind("<Alt-F4>", self.__destroy)
        self.__window.bind("<Up>", self.__camera_up)
        self.__window.bind("<Down>", self.__camera_down)
        self.__window.bind("<Left>", self.__camera_left)
        self.__window.bind("<Right>", self.__camera_right)
        on_press_key("\n", self.start_bot)
        self.__menubar = Menu(self.__window)
        menu = Menu(self.__menubar, tearoff=0)
        menu.add_command(label="Nouvelle carte", command=self.__new_map, accelerator="Ctrl+n", font=FONT)
        menu.add_command(label="Ouvrir une carte...", command=self.__open_map, accelerator="Ctrl+o", font=FONT)
        menu.add_command(label="Enregistrer la carte", command=self.__save_map, accelerator="Ctrl+s", font=FONT)
        menu.add_command(label="Enregistrer la carte sous...", command=self.__save_map_as, accelerator="Ctrl+Shift+s", font=FONT)
        menu.add_separator()
        menu.add_command(label="Quitter", command=self.__destroy, accelerator="Alt+F4", font=FONT)
        self.__menubar.add_cascade(label="Menu", menu=menu)
        self.__window.config(menu=self.__menubar)
        self.__canvas = Canvas(self.__window, width=500, height=500, bg="white")
        self.__canvas.grid(row=0, column=0, rowspan=6)
        self.__canvas.bind("<ButtonPress-1>", self.__draw)
        self.__canvas.bind("<ButtonPress-3>", self.__erase)
        self.__canvas.bind("<B1-Motion>", self.__draw)
        self.__canvas.bind("<B3-Motion>", self.__erase)
        self.__canvas.bind("<MouseWheel>", self.__change_zoom)
        self.__listbox = Listbox(self.__window, height=20, width=63, font=FONT)
        self.__listbox.grid(row=0, column=1, sticky="nw")
        self.__frame = Frame(self.__window, borderwidth=0)
        self.__frame.grid(row=1, column=1, sticky="nw")
        self.__button_add = Button(self.__frame, text="Ajouter un type", font=FONT, command=self.__create_new_type_window)
        self.__button_add.grid(row=0, column=0, sticky="nw")
        self.__button_edit = Button(self.__frame, text="Modifier un type", font=FONT, command=self.__edit_type_window)
        self.__button_edit.grid(row=0, column=1, sticky="nw")
        self.__button_suppr = Button(self.__frame, text="Supprimer un type", font=FONT, command=self.__suppr_type)
        self.__button_suppr.grid(row=0, column=2, sticky="nw")
        self.__button_location = Button(self.__frame, text="Se situer", font=FONT, command=self.__start_locate)
        self.__button_location.grid(row=0, column=3, sticky="nw")
        self.__frame2 = Frame(self.__window, borderwidth=0)
        self.__frame2.grid(row=2, column=1, sticky="nw")
        self.__button_up = Button(self.__frame2, text="Augmenter le niveau d'une case", font=FONT, command=self.__select_tile_up)
        self.__button_up.grid(row=0, column=0, sticky="nw")
        self.__button_down = Button(self.__frame2, text="Abaisser le niveau d'une case", font=FONT, command=self.__select_tile_down)
        self.__button_down.grid(row=0, column=1, sticky="nw")
        self.__button_open_sizewindow = Button(self.__window, text="Ouvrir/Fermer la fenetre de dimensionnement", font=FONT, command=self.__create_size_window)
        self.__button_open_sizewindow.grid(row=3, column=1, sticky="nw")
        self.__frame3 = Frame(self.__window, borderwidth=0)
        self.__frame3.grid(row=4, column=1, sticky="nw")
        self.__button_run_bot = Button(self.__frame3, text="Lancer/Arrêter le bot (Entrée)", font=FONT, bg="#f00", command=self.start_bot)
        self.__button_run_bot.grid(row=0, column=0, sticky="nw")
        self.__button_compute_path = Button(self.__frame3, text="Rechercher un chemin", font=FONT, command=self.__compute_path)
        self.__button_compute_path.grid(row=0, column=1, sticky="nw")
        self.__frame4 = Frame(self.__window, borderwidth=0)
        self.__frame4.grid(row=5, column=1, sticky="nw")
        Label(self.__frame4, text="Chercher (id) : ", font=FONT).grid(row=0, column=0, sticky="nw")
        self.__entry_id = Entry(self.__frame4, font=FONT, width=4)
        self.__entry_id.grid(row=0, column=1, sticky="nw")
        self.__entry_id.insert(0, "73")
        self.__n_buttons = IntVar()
        Label(self.__frame4, text="Bouton n°", font=FONT).grid(row=0, column=2, sticky="nw")
        self.__radiobutton1 = Radiobutton(self.__frame4, text="1", font=FONT, variable=self.__n_buttons, value=1)
        self.__radiobutton1.grid(row=0, column=3, sticky="nw")
        self.__radiobutton2 = Radiobutton(self.__frame4, text="2", font=FONT, variable=self.__n_buttons, value=2)
        self.__radiobutton2.grid(row=0, column=4, sticky="nw")
        self.__radiobutton3 = Radiobutton(self.__frame4, text="3", font=FONT, variable=self.__n_buttons, value=3)
        self.__radiobutton3.grid(row=0, column=5, sticky="nw")
        self.__n_buttons.set(1)
        self.__wait_ressources = IntVar()
        self.__checkbutton = Checkbutton(self.__window, text="Attendre si ressource non disponible", font=FONT, variable=self.__wait_ressources, onvalue=1, offvalue=0, command=self.__change_wait_ressources)
        self.__checkbutton.grid(row=6, column=1, sticky="nw")
        self.__wait_ressources.set(1)
        self.__is_size_window = False
        self.__size_window = None
        self.__path = ""
        self.__map = []
        self.__map_height = []
        self.__types = {}
        self.__is_save = True
        self.__x = 0
        self.__y = 0
        self.__bot_x = 0
        self.__bot_y = 0
        self.__selection = 0
        self.__zoom = 1
        self.__bot = Bot(self)
        self.__display()
        self.__window.mainloop()

    def get_window(self): return self.__window

    def __change_wait_ressources(self): self.__bot.change_wait_ressources(self.__wait_ressources.get())

    def __compute_path(self):
        if not self.__bot.is_running():
            if len(self.__map) == 0 or not (0 <= self.__bot_x < len(self.__map[0]) and 0 <= self.__bot_y < len(self.__map)) or self.__map[self.__bot_y][self.__bot_x] == None or self.__types[self.__map[self.__bot_y][self.__bot_x]][3] == "0":
                showerror("Erreur", "Position du bot invalide.")
                return False
            else:
                ide = self.__entry_id.get()
                if ide == "" or not ide in self.__types:
                    showerror("Erreur", "Identifiant de type incorrect.")
                    return False
                else:
                    grid_walls = [[0 if x == None else int(self.__types[x][3]) for x in y] for y in self.__map]
                    list_ressources = [(x, y) for y in range(len(self.__map)) for x in range(len(self.__map[0])) if self.__map[y][x] == ide]
                    self.__bot.compute_path(self.__bot_x, self.__bot_y, grid_walls, self.__map_height, list_ressources, [int(self.__types[ide][2]), self.__n_buttons.get()], float(self.__types[ide][4]))
                    self.__display()
                    return True

    def start_bot(self, event=None):
        if event == None or self.__bot.is_running():
            if self.__bot.is_running():
                self.__button_run_bot["bg"] = "#f00"
                self.__bot.stop()
            elif self.__bot.is_compute() or self.__compute_path():
                self.__button_run_bot["bg"] = "#0f0"
                self.__x, self.__y = self.__bot_x, self.__bot_y
                self.__display()
                self.__bot.start()

    def set_bot_pos(self, x, y):
        self.__x, self.__y, self.__bot_x, self.__bot_y = x, y, x, y
        self.__display()

    def __change_zoom(self, event):
        if event.delta > 0 and self.__zoom < 4: self.__zoom *= 2
        elif event.delta < 0 and self.__zoom > 0.25: self.__zoom /= 2
        self.__display()

    def __camera_up(self, event):
        self.__y -= 1
        self.__display()

    def __camera_down(self, event):
        self.__y += 1
        self.__display()

    def __camera_left(self, event):
        self.__x -= 1
        self.__display()

    def __camera_right(self, event):
        self.__x += 1
        self.__display()

    def __reset_buttons(self):
        self.__button_location["relief"] = "raised"
        self.__button_up["relief"] = "raised"
        self.__button_down["relief"] = "raised"

    def __start_locate(self):
        self.__reset_buttons()
        if self.__selection == 1: self.__selection = 0
        else:
            self.__selection = 1
            self.__button_location["relief"] = "flat"

    def __select_tile_up(self):
        self.__reset_buttons()
        if self.__selection == 2: self.__selection = 0
        else:
            self.__selection = 2
            self.__button_up["relief"] = "flat"

    def __select_tile_down(self):
        self.__reset_buttons()
        if self.__selection == 3: self.__selection = 0
        else:
            self.__selection = 3
            self.__button_down["relief"] = "flat"

    def __clear_map(self):
        is_suppr = 1
        while len(self.__map) > 0 and is_suppr:
            for i in self.__map[0]:
                if i != None:
                    is_suppr = 0
                    break
            if is_suppr:
                del self.__map[0]
                del self.__map_height[0]
                self.__y -= 1
                self.__bot_y -= 1
        is_suppr = 1
        while len(self.__map) > 0 and is_suppr:
            for i in self.__map[-1]:
                if i != None:
                    is_suppr = 0
                    break
            if is_suppr:
                del self.__map[-1]
                del self.__map_height[-1]
        if len(self.__map) > 0:
            is_suppr = 1
            while len(self.__map[0]) > 0 and is_suppr:
                for i in self.__map:
                    if i[0] != None:
                        is_suppr = 0
                        break
                if is_suppr:
                    for y in range(len(self.__map)):
                        del self.__map[y][0]
                        del self.__map_height[y][0]
                    self.__x -= 1
                    self.__bot_x -= 1
            is_suppr = 1
            while len(self.__map[0]) > 0 and is_suppr:
                for i in self.__map:
                    if i[-1] != None:
                        is_suppr = 0
                        break
                if is_suppr:
                    for y in range(len(self.__map)):
                        del self.__map[y][-1]
                        del self.__map_height[y][-1]
            if len(self.__map[0]) == 0:
                for y in range(len(self.__map)):
                    del self.__map[0]
                    del self.__map_height[0]

    def __get_position(self, event):
        b = [2500, 0, 0]
        n = int(7/self.__zoom)+1
        for y in range(-n, n+1):
            for x in range(-n, n+1):
                x2, y2 = 252+50*(x-y)*self.__zoom, 252+25*(x+y)*self.__zoom
                d = sqrt((event.x-x2)**2+(event.y-y2)**2)
                if d < b[0]: b[0], b[1], b[2] = d, x, y
        return self.__x+b[1], self.__y+b[2]

    def __draw(self, event):
        if (self.__selection or self.__listbox.get("active") != "") and 0 <= event.x < 500 and 0 <= event.y < 500 and not self.__bot.is_running():
            px, py = self.__get_position(event)
            if self.__selection < 2:
                if self.__map == []: self.__map, self.__map_height = [[None]], [[0]]
                while py < 0:
                    self.__map = [[None for x in range(len(self.__map[0]))]]+self.__map
                    self.__map_height = [[0 for x in range(len(self.__map_height[0]))]]+self.__map_height
                    py += 1
                    self.__y += 1
                    self.__bot_y += 1
                while py >= len(self.__map):
                    self.__map += [[None for x in range(len(self.__map[0]))]]
                    self.__map_height += [[0 for x in range(len(self.__map_height[0]))]]
                while px < 0:
                    for y in range(len(self.__map)): self.__map[y], self.__map_height[y] = [None]+self.__map[y], [0]+self.__map_height[y]
                    px += 1
                    self.__x += 1
                    self.__bot_x += 1
                while px >= len(self.__map[0]):
                    for y in range(len(self.__map)):
                        self.__map[y] += [None]
                        self.__map_height[y] += [0]
                if self.__selection == 0: self.__map[py][px], self.__is_save = self.__listbox.get("active").split()[0], False
                else: self.__bot_x, self.__bot_y = px, py
                self.__bot.path_change()
                self.__display()
            elif 0 <= py < len(self.__map) and 0 <= px < len(self.__map[0]):
                self.__map_height[py][px] -= self.__selection*2-5
                self.__bot.path_change()
                self.__display()

    def __erase(self, event):
        if 0 <= event.x < 500 and 0 <= event.y < 500 and not self.__bot.is_running():
            px, py = self.__get_position(event)
            if len(self.__map) > 0 and 0 <= px < len(self.__map[0]) and 0 <= py < len(self.__map): self.__map[py][px], self.__map_height[py][px] = None, 0
            self.__clear_map()
            self.__is_save = False
            self.__bot.path_change()
            self.__display()

    def __get_negative(self, color):
        if len(color) == 4: color = color[1]*2+color[2]*2+color[3]*2
        else: color = color[1:]
        c = "0123456789abcdef"
        return "#"+c[15-c.index(color[0])]+c[15-c.index(color[1])]+c[15-c.index(color[2])]+c[15-c.index(color[3])]+c[15-c.index(color[4])]+c[15-c.index(color[5])]

    def __display(self):
        self.__canvas.delete("all")
        n = int(7/self.__zoom)+1
        for y in range(-n, n+1):
            for x in range(-n, n+1):
                if len(self.__map) > 0 and 0 <= self.__x+x < len(self.__map[0]) and 0 <= self.__y+y < len(self.__map) and not self.__map[self.__y+y][self.__x+x] == None: color, height = self.__types[self.__map[self.__y+y][self.__x+x]][1], self.__map_height[self.__y+y][self.__x+x]
                else: color, height = "#fff", 0
                x2, y2 = 252+50*(x-y)*self.__zoom, 252+25*(x+y)*self.__zoom
                if height > 0:
                    self.__canvas.create_line(x2-50*self.__zoom, y2, x2+50*self.__zoom, y2, fill="#f00")
                    self.__canvas.create_line(x2, y2-25*self.__zoom, x2, y2+25*self.__zoom, fill="#f00")
                y2 -= 12*height*self.__zoom
                self.__canvas.create_polygon(x2-50*self.__zoom, y2, x2, y2-25*self.__zoom, x2+50*self.__zoom, y2, x2, y2+25*self.__zoom, fill=color, outline=self.__get_negative(color))
                if height < 0:
                    y2 += 12*height*self.__zoom
                    self.__canvas.create_line(x2-50*self.__zoom, y2, x2+50*self.__zoom, y2, fill="#f00")
                    self.__canvas.create_line(x2, y2-25*self.__zoom, x2, y2+25*self.__zoom, fill="#f00")
                if self.__x+x == self.__bot_x and self.__y+y == self.__bot_y: self.__canvas.create_polygon(x2, y2, x2-12*self.__zoom, y2-12*self.__zoom, x2-6*self.__zoom, y2-12*self.__zoom, x2-6*self.__zoom, y2-24*self.__zoom, x2+6*self.__zoom, y2-24*self.__zoom, x2+6*self.__zoom, y2-12*self.__zoom, x2+12*self.__zoom, y2-12*self.__zoom, fill="#0f0", outline="#000")
        if self.__bot.is_compute():
            path = [i for i in self.__bot.get_path()]
            path += [path[0]]
            x, y = 252+50*(path[0][0][0]-self.__x-path[0][0][1]+self.__y)*self.__zoom, 252+25*(path[0][0][0]-self.__x+path[0][0][1]-self.__y)*self.__zoom-12*path[0][1]*self.__zoom
            del path[0]
            while len(path) > 0:
                t = path[0] == None
                if t:
                    del path[0]
                    del path[1]
                x2, y2 = 252+50*(path[0][0][0]-self.__x-path[0][0][1]+self.__y)*self.__zoom, 252+25*(path[0][0][0]-self.__x+path[0][0][1]-self.__y)*self.__zoom-12*path[0][1]*self.__zoom
                a, b = 1 if x < x2 else -1, 1 if y < y2 else -1
                self.__canvas.create_line(x, y, x+25*self.__zoom*a, y+12.5*self.__zoom*b, fill=["#ff0", "#0f0"][t])
                self.__canvas.create_line(x+25*self.__zoom*a, y+12.5*self.__zoom*b, x2+25*self.__zoom*(-a), y2+12.5*self.__zoom*(-b), fill=["#ff0", "#0f0"][t])
                self.__canvas.create_line(x2+25*self.__zoom*(-a), y2+12.5*self.__zoom*(-b), x2, y2, fill=["#ff0", "#0f0"][t])
                if not t: x, y = x2, y2
                del path[0]

    def __create_size_window(self):
        if self.__is_size_window:
            self.__size_window.destroy()
            self.__size_window = None
            self.__is_size_window = False
        else:
            self.__size_window = SizeWindow()
            self.__is_size_window = True

    def __create_new_type_window(self): NewTypeWindow(self, "new")

    def __edit_type_window(self):
        if self.__listbox.get("active") == "": showerror("Erreur", "Aucun type sélectionné.")
        else:
            ide = self.__listbox.get("active").split()[0]
            NewTypeWindow(self, "edit"+ide, self.__types[ide][0], self.__types[ide][1], self.__types[ide][2], self.__types[ide][3], self.__types[ide][4])

    def add_type(self, name, color, n_buttons, can_walk_on, recuperation_time):
        n, change = 0, True
        while change:
            change = False
            for i in self.__types:
                if i[0] == str(n):
                    n += 1
                    change = True
        self.__types[str(n)] = (name, color, str(n_buttons), str(can_walk_on), recuperation_time)
        self.__listbox.insert("end", "{} {} {} {} boutons {} {}s".format(n, name, color, n_buttons, ("Impossible de marcher dessus", "Possible de marcher dessus")[can_walk_on], recuperation_time))
        self.__is_save = False

    def edit_type(self, ide, name, color, n_buttons, can_walk_on, recuperation_time):
        del self.__types[ide]
        self.__types[ide] = (name, color, str(n_buttons), str(can_walk_on), recuperation_time)
        for i in range(len(list(self.__types.keys()))):
            if self.__listbox.get(i).split()[0] == ide:
                self.__listbox.delete(i)
                self.__listbox.insert(i, "{} {} {} {} boutons {} {}s".format(ide, name, color, n_buttons, ("Impossible de marcher dessus", "Possible de marcher dessus")[can_walk_on], recuperation_time))
                break
        self.__is_save = False
        self.__display()

    def __suppr_type(self):
        if self.__listbox.get("active") != "":
            ide = self.__listbox.get("active").split()[0]
            del self.__types[ide]
            for y in range(len(self.__map)):
                for x in range(len(self.__map)):
                    if self.__map[y][x] == ide: self.__map[y][x] = None
            self.__listbox.delete("active")
            self.__clear_map()
            self.__display()
        else: showerror("Erreur", "Aucun type sélectionné.")

    def __ask_save(self):
        resp = True
        if not self.__is_save:
            resp = askyesnocancel("Confirmer l'abandon des modifications", "La carte actuelle n'est pas enregistrée. Voulez-vous l'enregistrer ?")
            if resp != None: resp = not resp
        if resp != None:
            if not resp: resp = self.__save_map()
            return resp
        return False

    def __destroy(self, event=None):
        if self.__bot.is_running(): showerror("Erreur", "Vous ne pouvez pas fermer la fenêtre tant que le bot est actif.")
        elif self.__ask_save():
            if self.__size_window != None: self.__size_window.destroy()
            self.__window.destroy()

    def __clear_memory(self):
        for y in range(len(self.__map)):
            for x in range(len(self.__map[0])):
                del self.__map[0][0]
                del self.__map_height[0][0]
            del self.__map[0]
            del self.__map_height[0]
        keys = [i for i in self.__types]
        for i in keys: del self.__types[i]
        self.__listbox.delete(0, "end")
        self.__path = ""
        self.__is_save = True

    def __new_map(self, event=None):
        if self.__bot.is_running(): showerror("Erreur", "Vous ne pouvez pas changer de carte tant que le bot est actif.")
        elif self.__ask_save():
            self.__clear_memory()
            self.__display()

    def __open_map(self, event=None):
        if self.__bot.is_running(): showerror("Erreur", "Vous ne pouvez pas charger une carte tant que le bot est actif.")
        elif self.__ask_save():
            resp = askopenfilename(title="Ouvrir une carte...", filetypes=[("map files",".map")])
            if resp != "":
                self.__clear_memory()
                self.__path = resp
                file = open(self.__path, "r")
                lines = file.read().split("\n")
                i = 0
                while lines[i] != "":
                    line = lines[i].split()
                    self.__types[line[0]] = (line[1], line[2], line[3], line[4], line[5])
                    self.__listbox.insert("end", "{} {} {} {} boutons {} {}s".format(line[0], line[1], line[2], line[3], ("Impossible de marcher dessus", "Possible de marcher dessus")[int(line[4])], line[5]))
                    i += 1
                i += 1
                while lines[i] != "":
                    self.__map += [lines[i].split()]
                    i += 1
                for y in range(len(self.__map)):
                    self.__map_height += [[int(x) for x in lines[i+y+1].split()]]
                    for x in range(len(self.__map[0])):
                        if self.__map[y][x] == "x": self.__map[y][x] = None
                file.close()
                self.__x, self.__y, self.__bot_x, self.__bot_y = 0, 0, 0, 0
                self.__display()

    def __save_map(self, event=None):
        if self.__bot.is_running():
            showerror("Erreur", "Vous ne pouvez pas sauvegarder une carte tant que le bot est actif.")
            return False
        else:
            if self.__path == "": self.__save_map_as()
            if self.__path == "": return False
            else:
                file = open(self.__path, "w", encoding="utf8")
                file.write("\n".join(["{} {} {} {} {} {}".format(i, self.__types[i][0], self.__types[i][1], self.__types[i][2], self.__types[i][3], self.__types[i][4]) for i in self.__types]))
                file.write("\n\n")
                file.write("\n".join([" ".join(["x" if x == None else x for x in y]) for y in self.__map]))
                file.write("\n\n")
                file.write("\n".join([" ".join([str(x) for x in y]) for y in self.__map_height]))
                file.write("\n")
                file.close()
                self.__is_save = True
                return True

    def __save_map_as(self, event=None):
        if self.__bot.is_running(): showerror("Erreur", "Vous ne pouvez pas sauvegarder une carte tant que le bot est actif.")
        else:
            path = asksaveasfilename(title="Enregistrer la carte sous...", filetypes=[("map files",".map")], defaultextension=".map")
            if path != "":
                self.__is_save, self.__path = True, path
                self.__save_map()

window = MainWindow()
