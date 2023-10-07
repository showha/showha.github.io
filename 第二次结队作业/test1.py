import random
import copy
import flask
from flask_cors import CORS
import concurrent.futures

app = flask.Flask(__name__)
CORS(app)
num_sudokus = 9

def generate_sudoku():
    # 创建一个已解数独格局
    solved_grid = [[0 for _ in range(9)] for _ in range(9)]
    fill(solved_grid)
    
    # 复制已解数独格局以创建谜题
    sudoku_puzzle = [row[:] for row in solved_grid]
    
    # 从谜题中移除一些数字以创建难度
    remove_numbers(sudoku_puzzle)
    
    return sudoku_puzzle, solved_grid

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
    # Check if 'num' is a valid move at grid[row][col]
    for i in range(9):
        if grid[row][i] == num or grid[i][col] == num:
            return False

    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(start_row, start_row + 3):
        for j in range(start_col, start_col + 3):
            if grid[i][j] == num:
                return False

    return True

def remove_numbers(grid):
    # 从数独格局中移除一些数字以创建谜题
    # 确保谜题仍有唯一解
    for _ in range(40):  # 调整迭代次数以控制难度
        while True:
            i, j = random.randint(0, 8), random.randint(0, 8)
            if grid[i][j] != 0:
                temp = grid[i][j]
                grid[i][j] = 0
                
                # 检查谜题是否仍有唯一解
                num_solutions = count_solutions(grid)
                if num_solutions == 1:
                    break
                else:
                    grid[i][j] = temp

def count_solutions(grid):
    # 初始化一个计数器
    global solution_count
    solution_count = 0
    
    # 调用解数独函数，同时计算解的数量
    solve_with_count(grid)
    
    return solution_count

def solve_with_count(grid):
    global solution_count
    
    # 找到一个空格
    ind = find_empty_cell(grid)
    
    # 如果没有空格，表示已经找到一个解
    if ind is None:
        solution_count += 1
        return
    
    row, col = ind
    
    # 尝试填入数字
    for num in range(1, 10):
        if is_valid_move(grid, row, col, num):
            grid[row][col] = num
            solve_with_count(grid)
            grid[row][col] = 0  # 回溯

def solve(grid):
    # Solve the Sudoku using backtracking (similar to the 'solve' function in your code)
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
    # Find the first empty cell in the Sudoku grid
    for i in range(9):
        for j in range(9):
            if grid[i][j] == 0:
                return (i, j)
                # return i, j
    return None

def is_valid_sudoku(board):
    nums = list(range(1, 10))
    # print(nums)
    # nums.append(None)
    def is_valid(arr):
        # Exclude 0 and check if the array has unique non-zero elements
        arr1 = arr
        arr = [num for num in arr if num in nums]
        return len(arr1) == len(set(arr))

    # Check rows
    for row in board:
        if not is_valid(row):
            return False

    # Check columns
    for col in range(9):
        if not is_valid([board[row][col] for row in range(9)]):
            return False

    # Check 3x3 subgrids
    for i in range(0, 9, 3):
        for j in range(0, 9, 3):
            if not is_valid([board[row][col] for row in range(i, i + 3) for col in range(j, j + 3)]):
                return False

    return True

@app.route('/sudoku')
def generate():
    sudoku_problem, sudoku_solve = generate_sudoku()
    return flask.jsonify({"sudoku_problems": sudoku_problem, "sudoku_solve": sudoku_solve})


# @app.route('/sudoku/<int:difficulty>')
@app.route('/sudoku_nine')
def generateSS():
    with concurrent.futures.ThreadPoolExecutor() as executor:
        sudoku_pAs = list(executor.map(lambda _: generate_sudoku(), range(num_sudokus)))
    
    sudoku_pAs_T = [*zip(*sudoku_pAs)]
    return flask.jsonify({"sudoku_problems": sudoku_pAs_T[0], "sudoku_solve": sudoku_pAs_T[1]})


@app.route('/provesudoku', methods=['POST'])
def proveSudoku():
    data = flask.request.get_json()
    sudokuu = data['sudokuBoard']
    length = data["length"]
    if length==1:
        result = is_valid_sudoku(tuple(tuple(row) for row in sudokuu))
    else:
        # result_list = []
        with concurrent.futures.ThreadPoolExecutor() as excutor:
            result = list(excutor.map(lambda _: is_valid_sudoku(tuple(tuple(row) for row in sudokuu[_])), range(num_sudokus)))
    return flask.jsonify({"sudoku_status": result})

if __name__ == '__main__':
    app.run(debug=True)
