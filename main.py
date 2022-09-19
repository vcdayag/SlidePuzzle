import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

PUZZLE_SIZE = 3

class AppWindow(Gtk.Window):
    def __init__(self):
        super().__init__(
            title="Eight Puzzle",
            default_width=300,
            default_height=300,
            border_width=10
        )

        ui_grid = Gtk.Grid(
            column_spacing=2,
            row_spacing=4,
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

        self.lblSolvable = Gtk.Label()
        
        dropdownValues = Gtk.ListStore(str)
        dropdownValues.append(["BFS"])
        dropdownValues.append(["DFS"])
        self.drpSearch = Gtk.ComboBox.new_with_model_and_entry(dropdownValues)
        self.drpSearch.set_entry_text_column(0)
        self.drpSearch.set_active(0)
        
        btnSolution = Gtk.Button(label="Solution")
        btnSolution.connect("clicked", self.buttonSearchAlgo)
        
        self.lblMoves = Gtk.Label(label="")

        ui_grid.attach(self.lblSolvable, 0, 0, 2, 1)
        ui_grid.attach(puzzle_grid,      0, 2, 2, 1)        
        ui_grid.attach(self.drpSearch,   0, 4, 1, 1)
        ui_grid.attach(btnSolution,      1, 4, 1, 1)
        ui_grid.attach(self.lblMoves,    0, 5, 2, 1)

        self.input_list = []
        if not self.load_file():
            import random

            self.input_list = list(range(PUZZLE_SIZE**2))
            random.shuffle(self.input_list)

        self.current_tile_arrangement = self.input_list[:]
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
            self.lblSolvable.set_label("Solvable. You can do this!")
            self.clickable_buttons()
        else:
            self.lblSolvable.set_label("Not Solvable")

    def load_file(self):
        with open("puzzle.in", "r") as file:
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
        movestooriginal = (PUZZLE_SIZE**2) - 1 - (x + y)

        iseven = True if movestooriginal % 2 == 0 else False
        moves = 0
        for integer in range(1, PUZZLE_SIZE**2):
            integerindex = in_list.index(integer)
            if integer - 1 == integerindex:
                continue

            for swap in range(integerindex, integer - 1, -1):
                temp = in_list[swap]
                in_list[swap] = in_list[swap - 1]
                in_list[swap - 1] = temp
                moves += 1

        if iseven == (moves % 2 == 0):
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

        self.current_tile_arrangement[self.blankindex] = int(clickedlabel)
        self.current_tile_arrangement[clickedindex] = 0
        self.blankindex = clickedindex

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
    
    def buttonSearchAlgo(self, button):
        index = self.drpSearch.get_active()
        model = self.drpSearch.get_model()
        algorithm = model[index][0]
        lbloutput = ""
        if algorithm == "BFS":
            lbloutput = self.BFSearch()
        else:
            lbloutput = self.DFSearch()
        self.lblMoves.set_label(lbloutput)
    
    def GoalTest(self, inputList):
        final = list(range(1, PUZZLE_SIZE**2))
        final.append(0)
        return inputList == final

    def Actions(self, inputState):
        fronteir = []
        currentBlankIndex = inputState["empty_loc"]
        x = currentBlankIndex % PUZZLE_SIZE
        y = currentBlankIndex // PUZZLE_SIZE
        if y - 1 >= 0 and y - 1 < PUZZLE_SIZE:
            temp = inputState["puzzle"][:]
            temp[currentBlankIndex] = temp[currentBlankIndex - PUZZLE_SIZE]
            temp[currentBlankIndex - PUZZLE_SIZE] = 0
            state_record = {
                "puzzle": temp[:],
                "empty_loc": currentBlankIndex - PUZZLE_SIZE,
                "action": "U",
                "parent": inputState,
            }
            fronteir.append(state_record)
        if x + 1 >= 0 and x + 1 < PUZZLE_SIZE:
            temp = inputState["puzzle"][:]
            temp[currentBlankIndex] = temp[currentBlankIndex + 1]
            temp[currentBlankIndex + 1] = 0
            state_record = {
                "puzzle": temp[:],
                "empty_loc": currentBlankIndex + 1,
                "action": "R",
                "parent": inputState,
            }
            fronteir.append(state_record)
        if y + 1 >= 0 and y + 1 < PUZZLE_SIZE:
            temp = inputState["puzzle"][:]
            temp[currentBlankIndex] = temp[currentBlankIndex + PUZZLE_SIZE]
            temp[currentBlankIndex + PUZZLE_SIZE] = 0
            state_record = {
                "puzzle": temp[:],
                "empty_loc": currentBlankIndex + PUZZLE_SIZE,
                "action": "D",
                "parent": inputState,
            }
            fronteir.append(state_record)
        if x - 1 >= 0 and x - 1 < PUZZLE_SIZE:
            temp = inputState["puzzle"][:]
            temp[currentBlankIndex] = temp[currentBlankIndex - 1]
            temp[currentBlankIndex - 1] = 0
            state_record = {
                "puzzle": temp[:],
                "empty_loc": currentBlankIndex - 1,
                "action": "L",
                "parent": inputState,
            }
            fronteir.append(state_record)
        return fronteir

    def BFSearch(self):
        # initial state
        fronteir = [
            {
                "puzzle": self.current_tile_arrangement[:],
                "empty_loc": self.blankindex,
                "action": None,
                "parent": None,
            }
        ]
        explored = []
        turns = 0
        while len(fronteir) != 0:
            currentState = fronteir.pop(0)
            explored.append(currentState["puzzle"])
            turns += 1
            if self.GoalTest(currentState["puzzle"]):
                outputActions = []
                while currentState["parent"] != None:
                    outputActions.insert(0, currentState["action"])
                    currentState = currentState["parent"]
                # print("explored states: ",len(explored))
                # print("path cost states: ",len(outputActions))
                # print(outputActions)
                with open("puzzle.out", "w") as puzzleOut:
                    puzzleOut.write(" ".join(outputActions))
                return " ".join(outputActions)
            else:
                for action in self.Actions(currentState):
                    # same logic with test case but slow? because creates a list of the puzzle list from the list of dictionaries
                    if action["puzzle"] not in explored and action["puzzle"] not in [
                        x["puzzle"] for x in fronteir
                    ]:
                        fronteir.append(action)

    def DFSearch(self):
        # initial state
        fronteir = [
            {
                "puzzle": self.current_tile_arrangement[:],
                "empty_loc": self.blankindex,
                "action": None,
                "parent": None,
            }
        ]
        explored = []
        turns = 0
        while len(fronteir) != 0:
            currentState = fronteir.pop()
            explored.append(currentState["puzzle"])
            turns += 1
            if self.GoalTest(currentState["puzzle"]):
                outputActions = []
                while currentState["parent"] != None:
                    outputActions.insert(0, currentState["action"])
                    currentState = currentState["parent"]
                # print("explored states: ",len(explored))
                # print("path cost states: ",len(outputActions))
                # print(outputActions)
                with open("puzzle.out", "w") as puzzleOut:
                    puzzleOut.write(" ".join(outputActions))
                return " ".join(outputActions)
            else:
                for action in self.Actions(currentState):
                    # same logic with test case but slow? because creates a list of the puzzle list from the list of dictionaries
                    if action["puzzle"] not in explored and action["puzzle"] not in [
                        x["puzzle"] for x in fronteir
                    ]:
                        fronteir.append(action)

    # EXER 3 Stuff


win = AppWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
