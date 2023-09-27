import random
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import concurrent.futures

app = Flask(__name__)
CORS(app)
num_sudokus = 9

def generate_sudoku():
    base  = [[0 for _ in range(9)] for _ in range(9)]
    fill(base)
    return base

def generate_sudoku_more():
    global num_sudokus
    with concurrent.futures.ThreadPoolExecutor() as executor:
        sudokus = list(executor.map(lambda _: generate_sudoku(), range(num_sudokus)))
    return sudokus

def fill(grid):
    for i in range(9):
        for j in range(9):
            nums = list(range(1, 10))
            random.shuffle(nums)
            for num in nums:
                if is_valid_move(grid, i, j, num):
                    grid[i][j] = num
                    if solve(grid):
                        return True
                    grid[i][j] = 0
            return False

def is_valid_move(grid, row, col, num):
    for i in range(9):
        if grid[row][i] == num or grid[i][col] == num:
            return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if grid[i][j] == num:
                return False

    return True

def solve(grid):
    empty_cell = find_empty_cell(grid)
    if not empty_cell:
        return True

    row, col = empty_cell
    for num in range(1, 10):
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num

            if solve(grid):
                return True

            grid[row][col] = 0

    return False

def find_empty_cell(grid):
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)
    return None

def print_sudoku(grid):
    for i in range(9):
        for j in range(9):
            if random.random() < 0.6:  # Adjust the fraction of masked cells as needed
                grid[i][j] = 0
            print(grid[i][j], end=' ')
        print()

@app.route('/sudoku')
def index():
    sudoku = generate_sudoku()
    print("Generated Sudoku:")
    print_sudoku(sudoku)
    return jsonify({'sudoku': sudoku})

# @app.route('/sudoku/<int:difficulty>')
@app.route('/sudoku_more')
def index_more():
    sudokus = generate_sudoku_more()
    print("Generated Sudoku_more:")
    # print_sudoku(sudokus)
    for sudoku in sudokus:
        print_sudoku(sudoku)
    return jsonify({'sudokus': sudokus})

if __name__ == '__main__':
    app.run(debug=True)
    # sudoku = generate_sudoku()
    # print("Generated Sudoku:")
    # print_sudoku(sudoku)
