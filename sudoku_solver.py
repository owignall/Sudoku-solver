import numpy as np
import copy
import time

class SudokuSolver():
    class SudokuState:
        def __init__(self, initial_state):
            self.width = 9
            self.height = 9
            self.possible_values = np.array([[range(1,10) for c in range(self.width)] for r in range(self.height)])
            self.final_values = copy.deepcopy(initial_state)
            self.initialise_possible_values()
            self.update_possible_values()

        def most_constrained_cell(self):
            """Find the most constrained cell and return its row and col"""
            minimum = float('inf')
            row = -1
            col = -1
            for row_index in range(self.height):
                for col_index in range(self.width):
                    if self.final_values[row_index, col_index] == 0:
                        remaining = len(self.options_remaining(row_index, col_index))
                        if remaining < minimum:
                            minimum = remaining
                            row = row_index
                            col = col_index
            return row, col

        def options_remaining(self, row, col):
            """Returns list of remaining options for a given cell"""
            return [x for x in self.possible_values[row, col] if x != -1]
        
        def options_remaining_ordered(self, row, col):
            """Returns list of remaining options for a given cell in order of least constraining values"""
            # Obtain remaining values
            remaining = self.options_remaining(row, col)
            # Creates a list for value counts amongst all cells groups
            counts = [0 if (i + 1) in remaining else -1 for i in range(9)]
            # Find count values
            # Position alternatives in row
            for col_index in [x for x in range(self.width) if x != col]:
                for val in self.possible_values[row, col_index]:
                    if val in remaining and val != -1:
                        counts[val-1] += 1
            # Position alternatives in col
            for row_index in [x for x in range(self.height) if x != row]:
                for val in self.possible_values[row_index, col]:
                    if val in remaining and val != -1:
                        counts[val-1] += 1
            # Position alternatives in box
            box_row_start_index = (row // 3) * 3
            box_col_start_index = (col // 3) * 3
            for ri in range(box_row_start_index, box_row_start_index + 3):
                for ci in range(box_col_start_index, box_col_start_index + 3):
                    if ri != row or ci != col:
                        for val in self.possible_values[ri, ci]:
                            if val in remaining and val != -1:
                                counts[val-1] += 1
            pairs = []
            for i in range(9):
                if counts[i] != -1:
                    pairs.append([i+1, counts[i]])
            ordered_pairs = sorted(pairs, key=lambda pair: pair[1])
            ordered_remaining = list(map((lambda pair: pair[0]), ordered_pairs))
            return ordered_remaining
        
        def is_goal(self):
            """Checks if the Sudoku state is the goal state"""
            for row_index in range(self.height):
                for col_index in range(self.width):
                    if self.final_values[row_index, col_index] == 0: return False
            return True
        
        def final_values_valid(self):
            """Checks is there are condition conflicts in the final values array"""
            # Check for row conflics
            for row_index in range(self.height):
                seen = set()
                for col_index in range(self.width):
                    value = self.final_values[row_index, col_index]
                    if value in seen and value != 0:
                        return False
                    seen.add(value)
            # Check for col conflics
            for col_index in range(self.width):
                seen = set()
                for row_index in range(self.height):
                    value = self.final_values[row_index, col_index]
                    if value in seen and value != 0:
                        return False
                    seen.add(value)
            # Check for box conflics
            for box_r in range(3):
                for box_c in range(3):
                    seen = set()
                    for ri in range((3*box_r), (3*box_r) + 3):
                        for ci in range((3*box_c), (3*box_c) + 3):
                            value = self.final_values[ri, ci]
                            if value in seen and value != 0:
                                return False
                            seen.add(value)
            return True
        
        def is_invalid(self):
            """Checks if the Sudoku state is invalid"""
            def cell_invalid(values):
                for v in values:
                    if v != -1: return False
                return True
            for row_index in range(self.height):
                for col_index in range(self.width):
                    if cell_invalid(self.possible_values[row_index, col_index]): return True
            return False
        
        def initialise_possible_values(self):
            """Populates the possible values array based on current final values"""
            for row_index in range(self.height):
                for col_index in range(self.width):
                    final_val = self.final_values[row_index, col_index]
                    if final_val != 0:
                        self.possible_values[row_index, col_index] = \
                            [x if x == final_val else -1 for x in self.possible_values[row_index, col_index]]
                        
        def update_possible_values(self):
            """Updates the possible values for each cell"""
            # Remove items from possible values that conflict with conditions
            for row_index in range(self.height):
                for col_index in range(self.width):
                    final_val = self.final_values[row_index, col_index]
                    if final_val == 0:
                        # Remove any values that aren't possible with current final vals
                        # Check row
                        for i in [x for x in range(self.width) if x != col_index]:
                            if self.final_values[row_index, i] in self.possible_values[row_index, col_index]:
                                self.possible_values[row_index, col_index, self.final_values[row_index, i] - 1] = -1
                        # Check col
                        for i in [x for x in range(self.height) if x != row_index]:
                            if self.final_values[i, col_index] in self.possible_values[row_index, col_index]:
                                self.possible_values[row_index, col_index, self.final_values[i, col_index] - 1] = -1
                        # Check box
                        box_row_start_index = (row_index // 3) * 3
                        box_col_start_index = (col_index // 3) * 3
                        for ri in range(box_row_start_index, box_row_start_index + 3):
                            for ci in range(box_col_start_index, box_col_start_index + 3):
                                if (self.final_values[ri,ci] in self.possible_values[row_index, col_index]) \
                                    and (ri != row_index or ci != col_index):
                                    self.possible_values[row_index, col_index, self.final_values[ri,ci] - 1] = -1
            # Determine last remaining options for number in any row, col, or box.
            # Last rows options
            for row_index in range(self.height):
                counts = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
                for col_index in range(self.width):
                    for val in self.possible_values[row_index, col_index]:
                        if val != -1:
                            counts[val] += 1
                for col_index in range(self.width):
                    if len(self.options_remaining(row_index, col_index)) > 1:
                        for i in range(9):
                            v = self.possible_values[row_index, col_index, i]
                            if v != -1 and counts[v] == 1:
                                self.possible_values[row_index, col_index] = \
                                    [x if x == v else -1 for x in self.possible_values[row_index, col_index]]
            # Last cols options
            for col_index in range(self.width):
                counts = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
                for row_index in range(self.height):
                    for val in self.possible_values[row_index, col_index]:
                        if val != -1:
                            counts[val] += 1
                for row_index in range(self.height):
                    if len(self.options_remaining(row_index, col_index)) > 1:
                        for i in range(9):
                            v = self.possible_values[row_index, col_index, i]
                            if v != -1 and counts[v] == 1:
                                self.possible_values[row_index, col_index] = \
                                    [x if x == v else -1 for x in self.possible_values[row_index, col_index]]
            # Last boxs options
            for box_r in range(3):
                for box_c in range(3):
                    # Add counts
                    counts = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
                    for ri in range((3*box_r), (3*box_r) + 3):
                        for ci in range((3*box_c), (3*box_c) + 3):
                            for val in self.possible_values[ri, ci]:
                                if val != -1:
                                    counts[val] += 1
                    # Make determinations
                    for ri in range((3*box_r), (3*box_r) + 3):
                        for ci in range((3*box_c), (3*box_c) + 3):
                            if len(self.options_remaining(ri, ci)) > 1:
                                for i in range(9):
                                    v = self.possible_values[ri, ci, i]
                                    if v != -1 and counts[v] == 1:
                                        self.possible_values[ri, ci] = \
                                            [x if x == v else -1 for x in self.possible_values[ri, ci]]   
            # Determinations from numbers restricted to row or col in a box
            for box_r in range(3):
                for box_c in range(3):
                    # Add counts
                    box_counts = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
                    for ri in range((3*box_r), (3*box_r) + 3):
                        for ci in range((3*box_c), (3*box_c) + 3):
                            for val in self.possible_values[ri, ci]:
                                if val != -1:
                                    box_counts[val] += 1             
                    # Make determinations
                    # Box's row determinations
                    for bow_row in range((3*box_r), (3*box_r) + 3):
                        row_counts = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
                        for bci in range((3*box_c), (3*box_c) + 3):
                            for val in self.possible_values[bow_row, bci]:
                                if val != -1:
                                    row_counts[val] += 1
                        for n in range(1,10):
                            if box_counts[n] == row_counts[n]:
                                # Remove possiblilty in row in other boxes
                                for col_index in [i for i in range(self.width) if i not in range((3*box_c), (3*box_c) + 3)]:
                                    self.possible_values[bow_row, col_index, n - 1] = -1
                    # Box's col determinations
                    for bow_col in range((3*box_c), (3*box_c) + 3):
                        col_counts = {1:0, 2:0, 3:0, 4:0, 5:0, 6:0, 7:0, 8:0, 9:0}
                        for bri in range((3*box_r), (3*box_r) + 3):
                            for val in self.possible_values[bri, bow_col]:
                                if val != -1:
                                    col_counts[val] += 1
                        for n in range(1,10):
                            if box_counts[n] == col_counts[n]:
                                # Remove possiblilty in row in other boxes
                                for row_index in [i for i in range(self.height) if i not in range((3*box_r), (3*box_r) + 3)]:
                                    self.possible_values[row_index, bow_col, n - 1] = -1
            
        def set_value(self, row, col, value):
            """Returns a copy of the current Sudoku state with the provided value set"""
            if self.final_values[row, col] != 0:
                raise ValueError(f"The cell in row {row} and col {col} is already filled")
            if not (row in range(9) and col in range(9)):
                raise ValueError("Cell out of range")
            if not value in self.possible_values[row, col]:
                raise ValueError("Given value is not possible for this cell") 
            state = copy.deepcopy(self)
            state.final_values[row, col] = value
            state.update_possible_values()        
            return state

    def sudoku_csv_to_array(self, filepath):
        return np.genfromtxt(f"{filepath}",delimiter=',',dtype="int32")
    
    def solve_from_array(self, sudoku):
        """
        Solves a Sudoku puzzle and returns its unique solution.
        Input: 9x9 numpy array with empty cells are designated by 0.
        Output: 9x9 numpy array of integers. Contains the solution, if there is one. If there is no solution, all array entries should be -1.
        """  
        def depth_first_search(state):
            """Searches for a solution to state returning either the solution array or None if there is no solution"""
            # Select a cell
            row, col = state.most_constrained_cell()
            # Iterate through all possible options for this cell
            options = state.options_remaining_ordered(row,col)
            for value in options:
                new_state = state.set_value(row, col, value)
                if new_state.is_goal():
                    return new_state
                if not new_state.is_invalid():
                    deep_state = depth_first_search(new_state)
                    if deep_state != None and deep_state.is_goal():
                        return deep_state
            # If no solutions are found for this state then return None
            return None
        state = self.SudokuState(sudoku)
        # Check given if Sudoku is already breaching conditions
        if not state.final_values_valid():
            return np.array([[-1 for c in range(9)] for r in range(9)])
        # Execute depth first search
        response = depth_first_search(state)
        # Return solution or grid of -1 if it is not possible
        if response: 
            solved_sudoku = response.final_values
        else: 
            solved_sudoku = np.array([[-1 for c in range(9)] for r in range(9)])
        return solved_sudoku

    def solve(self, filepath):
        "Returns array solution of a csv sudoku at a given filepath"
        return self.solve_from_array(self.sudoku_csv_to_array(filepath))

    def run_tests(self, verbose=False):
        """
        Test data generated from https://qqwing.com/generate.html
        """
        difficulties = ["intermediate","expert"]
        for difficulty in difficulties:
            for i in range(1,11):
                sudoku = self.sudoku_csv_to_array(f"test_sudokus/{difficulty}{i}.csv")
                print(f"{difficulty} {i}")
                if verbose: print(sudoku)
                start_time = time.process_time()
                my_solution = self.solve_from_array(sudoku)
                end_time = time.process_time()
                if verbose: print("solution\n", my_solution)
                print(f"runtime: {end_time-start_time}\n")

    def check_same(self, array1, array2):
        for row_index in range(9):
                for col_index in range(9):
                    if array1[row_index,col_index] != array2[row_index,col_index]:
                        return False
        return True

if __name__ == "__main__":
    solver = SudokuSolver()

    # Example of how to solve sudoku
    solution = solver.solve("test_sudokus/expert1.csv")
    # print(solution)

    # Solving test sudokus
    solver.run_tests(verbose=True)