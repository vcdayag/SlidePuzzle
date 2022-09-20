# UI library GTK
import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

# Constant for the puzzle size
PUZZLE_SIZE = 3


class State:
    __slots__ = ("puzzle", "empty_loc", "action", "parent", "f", "g", "h")

    def __init__(self, _puzzle, _empty_loc, _action, _parent):
        self.puzzle = _puzzle
        self.empty_loc = _empty_loc
        self.action = _action
        self.parent = _parent
        self.g = 0
        if not (self.parent is None):
            self.g = self.parent.g + 1
        self.h = 0
        self.f = 0
        self.computeH()

    def computeH(self) -> int:
        number = 1
        # y coordinate
        for y in range(PUZZLE_SIZE):
            # x coordinate
            for x in range(PUZZLE_SIZE):
                if number == 9:
                    break

                pIndex = self.puzzle.index(number)
                # convert one dimentional index into 2 dimentional index
                pX = pIndex % PUZZLE_SIZE
                pY = pIndex // PUZZLE_SIZE
                self.h = self.h + abs(x - pX) + abs(y - pY)
                number += 1

        self.f = self.g + self.h
        return self.h

    def setParent(self, parent):
        self.parent = parent
        self.g = parent.g + 1
        self.h = self.computeH()

    def values(self):
        print("puzzle: ", self.puzzle)
        print("action: ", self.action)
        print("parent: ", self.parent)
        print("f: ", self.f)
        print("g: ", self.g)
        print("h: ", self.h)
        print("====")


class AppWindow(Gtk.Window):
    def __init__(self):
        super().__init__(
            title="Eight Puzzle", default_width=300, default_height=300, border_width=10
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
        dropdownValues.append(["A*Search"])
        self.drpSearch = Gtk.ComboBox.new_with_model_and_entry(dropdownValues)
        self.drpSearch.set_entry_text_column(0)
        self.drpSearch.set_active(0)

        btnSolution = Gtk.Button(label="Solution")
        btnSolution.connect("clicked", self.clicked_solution_button)

        self.lblMoves = Gtk.Label(label="")

        ui_grid.attach(self.lblSolvable, 0, 0, 2, 1)
        ui_grid.attach(puzzle_grid, 0, 2, 2, 1)
        ui_grid.attach(self.drpSearch, 0, 4, 1, 1)
        ui_grid.attach(btnSolution, 1, 4, 1, 1)
        ui_grid.attach(self.lblMoves, 0, 5, 2, 1)

        # holds the goal/final state of the sliding puzzle
        self.final_puzzle = list(range(1, PUZZLE_SIZE**2))
        self.final_puzzle.append(0)
        # holds the value from the puzzle.in file
        self.input_puzzle = []
        # holds current state of the sliding puzzle
        self.current_puzzle = []
        # holds buttons for the sliding puzzle
        self.button_list = []
        # holds the solution for the puzzle
        self.solution_list = []
        self.emptyIndex = 0

        # load the puzzle.in
        self.load_file()

        # y coordinate
        for y in range(PUZZLE_SIZE):
            # x coordinate
            for x in range(PUZZLE_SIZE):
                # convert 2 dimentional index to 1 dimentional
                index = y * PUZZLE_SIZE + x

                txtlabel = ""
                if self.input_puzzle[index] != 0:
                    txtlabel = str(self.input_puzzle[index])

                self.button_list.append(Gtk.Button(label=txtlabel))
                self.button_list[index].set_sensitive(False)
                self.button_list[index].connect("clicked", self.clicked_puzzle_button)
                puzzle_grid.attach(self.button_list[index], x, y, 1, 1)

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

                self.input_puzzle += row

        self.input_puzzle = [int(x) for x in self.input_puzzle]

        if len(self.input_puzzle) != PUZZLE_SIZE**2:
            import random

            self.input_puzzle = list(range(PUZZLE_SIZE**2))
            random.shuffle(self.input_puzzle)

        self.current_puzzle = self.input_puzzle[:]

    def check_solvable(self):
        in_list = self.input_puzzle[:]
        emptyIndex = self.input_puzzle.index(0)
        movestooriginal = (PUZZLE_SIZE**2 - 1) - emptyIndex

        isEven = True if movestooriginal % 2 == 0 else False
        moves = 0

        finalState = self.final_puzzle
        for integer in finalState:
            integerIndex = in_list.index(integer)
            if finalState.index(integer) == integerIndex:
                continue

            for swap in range(integerIndex, integer - 1, -1):
                temp = in_list[swap]
                in_list[swap] = in_list[swap - 1]
                in_list[swap - 1] = temp
                moves += 1

        if isEven == (moves % 2 == 0):
            self.lblSolvable.set_label("Solvable")
            return True
        else:
            self.lblSolvable.set_label("Not Solvable")
            return False

    def clicked_puzzle_button(self, button):
        clickedvalue = int(button.get_label())
        clickedindex = self.current_puzzle.index(clickedvalue)

        self.current_puzzle[self.emptyIndex] = clickedvalue
        self.current_puzzle[clickedindex] = 0

        self.button_list[self.emptyIndex].set_label(str(clickedvalue))
        self.button_list[clickedindex].set_label("")

        self.emptyIndex = clickedindex

        if not self.isWon():
            self.clickable_buttons()

    def isWon(self):
        if self.GoalTest(self.current_puzzle):
            self.lblSolvable.set_label("You Won!")
            for i in range(PUZZLE_SIZE**2):
                self.button_list[i].set_sensitive(False)
            return True

    def clickable_buttons(self):
        # enable button that is beside the blank
        for b in self.button_list:
            b.set_sensitive(False)

        self.emptyIndex = self.current_puzzle.index(0)
        x = self.emptyIndex % PUZZLE_SIZE
        y = self.emptyIndex // PUZZLE_SIZE

        if 0 <= y - 1 < PUZZLE_SIZE:
            self.button_list[self.emptyIndex - PUZZLE_SIZE].set_sensitive(True)
        if 0 <= x + 1 < PUZZLE_SIZE:
            self.button_list[self.emptyIndex + 1].set_sensitive(True)
        if 0 <= y + 1 < PUZZLE_SIZE:
            self.button_list[self.emptyIndex + PUZZLE_SIZE].set_sensitive(True)
        if 0 <= x - 1 < PUZZLE_SIZE:
            self.button_list[self.emptyIndex - 1].set_sensitive(True)

    # EXER 2 Stuff
    def GoalTest(self, inputList):
        return self.final_puzzle == inputList

    def clicked_solution_button(self, button):
        if button.get_label() == "Solution":

            self.current_puzzle = self.input_puzzle[:]
            for index, value in enumerate(self.current_puzzle):
                if value == 0:
                    self.button_list[index].set_label("")
                    self.emptyIndex = index
                else:
                    self.button_list[index].set_label(str(value))
                self.button_list[index].set_sensitive(False)

            index = self.drpSearch.get_active()
            model = self.drpSearch.get_model()
            algorithm = model[index][0]
            lbloutput = ""

            if algorithm == "BFS":
                lbloutput = self.BFSearch()
            elif algorithm == "DFS":
                lbloutput = self.DFSearch()
            else:
                lbloutput = self.AStarSearch()

            self.solution_list = lbloutput.split()
            self.lblMoves.set_label(lbloutput)
            button.set_label("Next")
        else:

            currentEmptyIndex = self.emptyIndex
            clickedButtonIndex = 0

            move = self.solution_list.pop(0)
            if len(self.solution_list) == 0:
                button.set_sensitive(False)

            if move == "U":
                clickedButtonIndex = currentEmptyIndex - PUZZLE_SIZE
            elif move == "R":
                clickedButtonIndex = currentEmptyIndex + 1
            elif move == "D":
                clickedButtonIndex = currentEmptyIndex + PUZZLE_SIZE
            elif move == "L":
                clickedButtonIndex = currentEmptyIndex - 1

            self.current_puzzle[currentEmptyIndex] = self.current_puzzle[
                clickedButtonIndex
            ]
            self.button_list[currentEmptyIndex].set_label(
                str(self.current_puzzle[clickedButtonIndex])
            )

            self.current_puzzle[clickedButtonIndex] = 0
            self.button_list[clickedButtonIndex].set_label("")

            self.emptyIndex = clickedButtonIndex

            self.isWon()

    def Actions(self, inputState):
        fronteir = []
        currentEmptyIndex = inputState.empty_loc
        x = currentEmptyIndex % PUZZLE_SIZE
        y = currentEmptyIndex // PUZZLE_SIZE

        if 0 <= y - 1 < PUZZLE_SIZE:
            temp = inputState.puzzle[:]
            temp[currentEmptyIndex] = temp[currentEmptyIndex - PUZZLE_SIZE]
            temp[currentEmptyIndex - PUZZLE_SIZE] = 0
            fronteir.append(
                State(temp[:], currentEmptyIndex - PUZZLE_SIZE, "U", inputState)
            )
        if 0 <= x + 1 < PUZZLE_SIZE:
            temp = inputState.puzzle[:]
            temp[currentEmptyIndex] = temp[currentEmptyIndex + 1]
            temp[currentEmptyIndex + 1] = 0
            fronteir.append(State(temp[:], currentEmptyIndex + 1, "R", inputState))
        if 0 <= y + 1 < PUZZLE_SIZE:
            temp = inputState.puzzle[:]
            temp[currentEmptyIndex] = temp[currentEmptyIndex + PUZZLE_SIZE]
            temp[currentEmptyIndex + PUZZLE_SIZE] = 0
            fronteir.append(
                State(temp[:], currentEmptyIndex + PUZZLE_SIZE, "D", inputState)
            )
        if 0 <= x - 1 < PUZZLE_SIZE:
            temp = inputState.puzzle[:]
            temp[currentEmptyIndex] = temp[currentEmptyIndex - 1]
            temp[currentEmptyIndex - 1] = 0
            fronteir.append(State(temp[:], currentEmptyIndex - 1, "L", inputState))
        return fronteir

    def BFSearch(self):
        # initial state
        fronteir = [State(self.current_puzzle[:], self.emptyIndex, None, None)]
        explored = []
        while len(fronteir) != 0:
            currentState = fronteir.pop(0)
            explored.append(currentState.puzzle)
            if self.GoalTest(currentState.puzzle):
                outputActions = []
                while currentState.parent != None:
                    outputActions.insert(0, currentState.action)
                    currentState = currentState.parent
                print("explored states: ", len(explored))
                print("path cost states: ", len(outputActions))
                print(outputActions)
                with open("puzzle.out", "w") as puzzleOut:
                    puzzleOut.write(" ".join(outputActions))
                return " ".join(outputActions)
            else:
                for action in self.Actions(currentState):
                    # same logic with test case but slow? because creates a list of the puzzle list from the list of dictionaries
                    if action.puzzle not in explored and action.puzzle not in (
                        x.puzzle for x in fronteir
                    ):
                        fronteir.append(action)

    def DFSearch(self):
        # initial state
        fronteir = [State(self.current_puzzle[:], self.emptyIndex, None, None)]
        explored = []
        while len(fronteir) != 0:
            currentState = fronteir.pop()
            explored.append(currentState.puzzle)
            if self.GoalTest(currentState.puzzle):
                outputActions = []
                while currentState.parent != None:
                    outputActions.insert(0, currentState.action)
                    currentState = currentState.parent
                # print("explored states: ",len(explored))
                # print("path cost states: ",len(outputActions))
                # print(outputActions)
                with open("puzzle.out", "w") as puzzleOut:
                    puzzleOut.write(" ".join(outputActions))
                return " ".join(outputActions)
            else:
                for action in self.Actions(currentState):
                    # same logic with test case but slow? because creates a list of the puzzle list from the list of dictionaries
                    if action.puzzle not in explored and action.puzzle not in (
                        x.puzzle for x in fronteir
                    ):
                        fronteir.append(action)

    # EXER 3 Stuff

    def AStarSearch(self):
        # initial state
        openList = [State(self.current_puzzle[:], self.emptyIndex, None, None)]
        closedList = []
        while len(openList) != 0:
            # get the minimum f
            Flist = [x.f for x in openList]
            MinF = min(Flist)
            MinFIndex = Flist.index(MinF)
            bestNode = openList.pop(MinFIndex)

            closedList.append(bestNode.puzzle)

            if self.GoalTest(bestNode.puzzle):
                outputActions = []
                while bestNode.parent != None:
                    outputActions.insert(0, bestNode.action)
                    bestNode = bestNode.parent
                print("closedList states: ", len(closedList))
                print("path cost states: ", len(outputActions))
                print(outputActions)
                with open("puzzle.out", "w") as puzzleOut:
                    puzzleOut.write(" ".join(outputActions))
                return " ".join(outputActions)
            else:

                for action in self.Actions(bestNode):
                    # same logic with test case but slow? because creates a list of the puzzle list from the list of dictionaries
                    if action.puzzle in closedList:
                        continue

                    try:
                        puzzleList = [x.puzzle for x in openList]
                        pIndex = puzzleList.index(action.puzzle)
                        duplicateState = openList[pIndex]
                        if pIndex >= 0:
                            if action.g < duplicateState.g:
                                openList[pIndex].setParent(bestNode)
                            continue
                    except ValueError as e:
                        pass

                    openList.append(action)


win = AppWindow()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
