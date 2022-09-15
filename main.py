import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

PUZZLE_SIZE = 3

class AppWindow(Gtk.Window):
    def __init__(self):
        super().__init__(
            title="Puzzle",
            default_width=300,
            default_height=300,
            border_width=10
        )
        
        ui_grid = Gtk.Grid(
            column_spacing=1,
            row_spacing=3,
            row_homogeneous=False,
            column_homogeneous=True,
        )
        self.add(ui_grid)
        
        PUZZLE_GRID_SPACING = 2
        puzzle_grid = Gtk.Grid(
            column_spacing=PUZZLE_GRID_SPACING,
            row_spacing=PUZZLE_GRID_SPACING,
            row_homogeneous=True,
            column_homogeneous=True,
        )
        
        lbltitle = Gtk.Label(label="3x3 Slide Puzzle")
        self.lblSolvable = Gtk.Label()
        
        ui_grid.attach(lbltitle, 0, 0, 1, 1)
        ui_grid.attach(self.lblSolvable, 0, 1, 1, 1)
        ui_grid.attach(puzzle_grid, 0, 2, 1, 1)
        
        self.input_list = []
        if not self.load_file():
            import random
            self.input_list = list(range(PUZZLE_SIZE**2))
            random.shuffle(self.input_list)
        
        self.button_list = []
        self.blankindex = 0
        
        for x in range(PUZZLE_SIZE):
            for y in range(PUZZLE_SIZE):
                index = x * PUZZLE_SIZE + y

                txtlabel = ""
                if self.input_list[index] != 0:
                    txtlabel = str(self.input_list[index])

                self.button_list.append(Gtk.Button(label=txtlabel))
                self.button_list[index].set_sensitive(False)
                self.button_list[index].connect("clicked", self.button_clicked)
                puzzle_grid.attach(self.button_list[index], y, x, 1, 1)
        
        if self.check_solvable():
            self.lblSolvable.set_label("Solvable")
            self.clickable_buttons()
        else:
            self.lblSolvable.set_label("Not Solvable")
    
    def load_file(self):
        with open("puzzle.in","r") as file:
            lines = file.readlines()
            for x in lines:
                row = x.split()
                if len(row) != PUZZLE_SIZE:
                    return False

                self.input_list += row
        self.input_list = [int(x) for x in self.input_list]
        if len(self.input_list) != PUZZLE_SIZE**2:
            return False
        return True
        
    
    def check_solvable(self):
        in_list = self.input_list[:]
        blnkindex = self.input_list.index(0)
        x = blnkindex % PUZZLE_SIZE
        y = blnkindex // PUZZLE_SIZE
        movestooriginal = (PUZZLE_SIZE**2)-1-(x+y)
        
        iseven = True if movestooriginal%2 == 0 else False
        moves = 0
        for integer in range(1,PUZZLE_SIZE**2):
            integerindex = in_list.index(integer)
            if integer-1 == integerindex:
                continue
            
            for swap in range(integerindex,integer-1,-1):
                temp = in_list[swap]
                in_list[swap] = in_list[swap-1]
                in_list[swap-1] = temp
                moves += 1
                # print(in_list)
        
        # print(moves)
        if iseven == (moves%2 == 0):
            self.lblSolvable.set_label("Solvable")
            return True
        else:
            self.lblSolvable.set_label("Not Solvable")
            return False
            

    def clickable_buttons(self):
        # enable button that is beside the blank
        for b in self.button_list:
            b.set_sensitive(False)

        for x in range(PUZZLE_SIZE):
            for y in range(PUZZLE_SIZE):
                index = x * PUZZLE_SIZE + y
                if self.button_list[index].get_label() == "":
                    self.blankindex = index
                    if x - 1 >= 0 and x - 1 < PUZZLE_SIZE:
                        self.button_list[index - PUZZLE_SIZE].set_sensitive(True)
                    if y - 1 >= 0 and y - 1 < PUZZLE_SIZE:
                        self.button_list[index - 1].set_sensitive(True)
                    if y + 1 >= 0 and y + 1 < PUZZLE_SIZE:
                        self.button_list[index + 1].set_sensitive(True)
                    if x + 1 >= 0 and x + 1 < PUZZLE_SIZE:
                        self.button_list[index + PUZZLE_SIZE].set_sensitive(True)
                    break

    def get_button_index(self, button):
        for i, btn in enumerate(self.button_list):
            if button == btn:
                return i

    def button_clicked(self, button):
        clickedindex = self.get_button_index(button)
        clickedlabel = self.button_list[clickedindex].get_label()
        self.button_list[self.blankindex].set_label(clickedlabel)
        self.button_list[clickedindex].set_label("")
        if self.check_puzzle():
            self.lblSolvable.set_label("You Won!")
            for b in self.button_list:
                b.set_sensitive(False)
        else:
            self.clickable_buttons()

    def check_puzzle(self):
        final = [1, 2, 3, 4, 5, 6, 7, 8, ""]
        for i in range(9):
            if self.button_list[i].get_label() != str(final[i]):
                return False
        return True
    
    # EXER 2 Stuff
    
    # EXER 3 Stuff

win = AppWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
