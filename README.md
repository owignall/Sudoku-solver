# Sudoku-solver

## Overview
The `solve_from_array` method of the `SudokuSolver` class takes in a sudoku as a two-dimensional NumPy array and returns the solution of this sudoku as a new two-dimensional NumPy array. If there is no possible solution to the input sudoku then the values in the array returned will all be set to -1.

## Sudokus
A Sudoku board consists of a 9 by 9 grid split into 9 equally sized boxes of 3 by 3. The objective is to fill this grid such that each row, column, and box contains all the digits from 1 to 9. As a consequence of this the same digit cannot be repeated more than once in any of these groups as they all have exactly 9 cells.

## Basic Approach

The approach used here is depth first search backtracking with constraint satisfaction. In the case of a sudoku solver the set of variables (X) is the set of remaining empty cells. The set of domains (D) will be a set of sets of 1 to 9 for each variable. The set of constraints (C) is that no row, column, or box can contain any number more than once. A Sudoku state can be considered consistent if it does not breach any of the constraints and complete if all of the cells have been assigned a value.

The basic implementation of this involves picking a cell at random and entering a number that does not breach the constraints. You continue to do this until there are no numbers that can be entered into the cell without breaching the constraints. When this happens, you backtrack and try another number in the previous cell.

I implemented this in the `solve_from_array` method using a recursive `depth_first_search` function which takes in a `SudokuState` object and returns either a solution if one is found or `None` if no solution exists.

In order to try possible options, the `set_value` method is used. This is called on a `SudokuState` object, with the row and column of a cell as arguments, and returns a copy of the state with this new value added. If this new state `is_goal` then it can be returned as the solution. Otherwise, providing the state is valid we can recursively call `depth_first_search` on it and return the result if it `is_goal`.

## Optimisations
I also added a number of backtracking heuristics to improve the speed at which this algorithm solves sudokus:
- Selecting the most constrained cells first.
- Ordering options for cell numbers by those which least constrain other cells.
- Reducing the list of possible numbers for each cell.
- Removing possible numbers that are the same as finalised numbers in the same row, column, or box.
- Removing all other options for cells that are the only remaining possible position for a number in a row, column, or box.
- If it is known that a number is constrained to a certain row or column in a box then removing this number from the possible numbers in this row or column of other boxes.

For my first optimisation, I changed the selection of cells. Instead of random selection the most constrained cells were selected. Selecting the most constrained cells first means that cells with only one possible value will always be filled first and in the case that the algorithm cannot determine any values it will first select the cell which it is most likely to pick the correct value for. I implemented this using a `most_constrained_cell` method for `SudokuState` objects which returned the row and column of the most constrained cell.

My next optimisation involved the order in which numbers were entered into the cells. The possible values for the chosen cell were ordered from those which least constrain other cells to those which most constrain other cells. If entering a value into a cell constrains lots of other cells this is an indication that this number had lots of alternative positions. However, if entering the value does not constrain many other cells this indicates that the likelihood of it being the correct cell for the value is higher. We can therefore improve the algorithms probability of making the correct selection by ordering value options in this way. I implemented this with the `options_remaining_ordered` method which takes a row and column and returns an ordered list of value options for that cell.

To keep track of which numbers could possibly be in a given cell the `SudokuState` class includes an attribute called `possible_values` which contains a three dimentional NumPy array, which states for each cell the numbers that it could still possibly be. To further optimise the selection of numbers I added a method to update this array called `update_possible_values`. This method goes through the `possible_values` array, and for all cells removes the numbers that are no longer possible. Identifying the numbers that are no longer possible however can be done in a number of ways. The more numbers that can be removed at each stage the more efficient the algorithm is going to be because the probability of selecting the right number is higher. I included three approaches to this in my `update_possible_values` method.

Firstly, if a number is present in the `final_values` for any row, column, or box then this number will be removed from the possible values for all other cells in that group. This is the simplest way of reducing the possible options and is essentially just a way of implementing the basic constraints.

Secondly, if in any row, column, or box there is only one remaining cell that a number can go in then we can remove all other numbers from the possible options for this cell as it is already determined.

Thirdly, if we know that in a box a number has to be in a specific row or column then we can remove this number from the possible values for all cells in this row or column of that are not in the box.

## Results

I found that depth first search backtracking with constraint satisfaction was an effective approach to this problem. Utilising the heuristics that I have mentioned also significantly improved the speed at which the `solve_from_array` method was able to solve harder sudokus.