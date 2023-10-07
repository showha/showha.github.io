let sudokuBoard = [];
let length = 0;
let sudoku_slove = [];

function fetchSudoku() {
  // const response = fetch('http://localhost:5000/sudoku').then(response => response.json());
  const data = fetch('http://localhost:5000/sudoku').then(response => response.json());
  // const data = response.json();
  return data.sudokuBoard;
}

function generateSudoku() {
  length = 1;
  // AJAX request to Python backend to generate a Sudoku puzzle
  // Here, we'll use a predefined Sudoku for simplicity
  fetch('http://localhost:5000/sudoku').then(response => response.json())
    .then(data => {
      sudoku_slove = data.sudoku_solve;
      sudokuBoard = data.sudoku_problems;
      const predefinedSudoku = data.sudoku_problems;
      // length = data.length;
      // sudokuBoard = data.sudokuBoard;
      const container = document.getElementById('sudokuContainer');
      container.innerHTML = '';  // Clear the container
      // const table = document.getElementById('sudokuBoard');
      // table.innerHTML = '';  // Clear the table
      const table = document.createElement('table');
      table.id = 'sudoku';
      container.appendChild(table);

      for (let i = 0; i < 9; i++) {
        const row = table.insertRow(i);
        // sudokuBoard.push([]);
        for (let j = 0; j < 9; j++) {
          const cell = row.insertCell(j);
          if (predefinedSudoku[i][j] !== 0) {
            cell.innerHTML = predefinedSudoku[i][j];
            cell.classList.add('predefined');
          } else {
            // cell.innerHTML = '<input type="text" maxlength="1" oninput="onInput(this)" />';
            cell.innerHTML = '<input type="text" oninput="onInput(this)" />';
            cell.classList.add('inputable');
          }
          // sudokuBoard[i].push(predefinedSudoku[i][j]);
        }
      }
    });
}

function generateSudoku_more() {
  length = 9;
  // sudokuBoard = [];
  // sudoku_slove = [];
  fetch('http://localhost:5000/sudoku_nine')
    .then(response => response.json())
    .then(data => {
      sudokuBoard = data.sudoku_problems;
      sudoku_slove = data.sudoku_solve;
      const sudokus = data.sudoku_problems;
      const container = document.getElementById('sudokuContainer');
      container.innerHTML = '';  // Clear the container

      for (let i = 0; i < sudokus.length; i++) {
        const table = document.createElement('table');
        table.id = `${i}`
        container.appendChild(table);

        for (let j = 0; j < 9; j++) {
          const row = table.insertRow(j);
          for (let k = 0; k < 9; k++) {
            const cell = row.insertCell(k);
            if (sudokus[i][j][k] !== 0) {
              cell.innerHTML = sudokus[i][j][k];
              cell.classList.add('predefined');
            } else {
              cell.innerHTML = '<input type="text" oninput="onInputS(this)"/>';
              cell.classList.add('inputable');
              // cell.innerHTML = '<input type="text" maxlength="1" oninput="onInput(this)" />';
            }
          }
        }
      }
    });
}

function solveSudoku() {
  if (length==1) {
    sudokuBoard = sudoku_slove;
    // const table = document.getElementById('sudoku');
    const container = document.getElementById('sudokuContainer');
    container.innerHTML = '';  // Clear the container
    // const table = document.getElementById('sudokuBoard');
    // table.innerHTML = '';  // Clear the table
    const table = document.createElement('table');
    table.id = 'sudoku';
    container.appendChild(table);

    for (let i = 0; i < 9; i++) {
      const row = table.insertRow(i);
      // sudokuBoard.push([]);
      for (let j = 0; j < 9; j++) {
        const cell = row.insertCell(j);
        cell.innerHTML = sudokuBoard[i][j];
        cell.classList.add('predefined');
      }
    }
  } else {
    const container = document.getElementById('sudokuContainer');
    container.innerHTML = '';  // Clear the container
    for (let i = 0; i < 9; i++) {
      sudokuBoard[i] = sudoku_slove[i];
      // const table = document.getElementById(`${i}`);
      const table = document.createElement('table');
      table.id = `${i}`
      container.appendChild(table);
      for (let j = 0; j < 9; j++) {
        const row = table.insertRow(j);
        for (let k = 0; k < 9; k++) {
          const cell = row.insertCell(k);
          cell.innerHTML = sudokuBoard[i][j][k];
          cell.classList.add('predefined');
        }
      }
    }
  }
}

function onInput(input) {
  const row = input.parentElement.parentElement.rowIndex;
  const col = input.parentElement.cellIndex;
  sudokuBoard[row][col] = Number(input.value);
}

function onInputS(input) {
  const table = input.parentElement.parentElement.parentElement.parentElement;
  const row = input.parentElement.parentElement.rowIndex;
  const col = input.parentElement.cellIndex;
  const tableIndex = Number(table.id);
  sudokuBoard[tableIndex][row][col] = Number(input.value);
}

function validateSudoku() {
  // TODO: Implement Sudoku validation logic
  console.log('Validating Sudoku...');
  console.log(sudokuBoard);
}

function prove() {
  // const tableContainer = document.getElementById("sudokuContainer");
  if (length==1) {
    // console.log(true);
    const data = {sudoku: sudokuBoard, "length": 1}
    console.log(JSON.stringify(data))
    // 将数组传入到后端检查
    fetch('http://localhost:5000/provesudoku', {
      method: 'POST',  // You can use 'GET' or other HTTP methods as needed
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({"sudokuBoard": sudokuBoard, "length": 1}),
      // mode: 'cors'  // 设置CORS选项
    })
    .then(response => response.json())
    .then(data => {
      console.log('Response from backend:', data);
      result = data.sudoku_status;
      if (result) {
        alert("正确！");
      } else {
        alert("错误！");
      }
    })
    .catch(error => console.error('Error:', error));
  } else {
    // alert("9!");
    console.log("9!");
    // 将数组们传入到后端检查
    const data = {"sudokuBoard": sudokuBoard, "length": 9}
    console.log(JSON.stringify(data))
    fetch('http://localhost:5000/provesudoku', {
      method: 'POST',  // You can use 'GET' or other HTTP methods as needed
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(data),
      // mode: 'cors'  // 设置CORS选项
    })
    .then(response => response.json())
    .then(data => {
      console.log('Response from backend:', data);
      result = data.sudoku_status;
      result_str = "";
      for (let i = 0; i < 9; i++) {
        result_str += `${i+1}` + "th: ";
        result_str += result[i] ? "正确！\n" : "错误！\n";
      }
      alert(result_str);
    })
  }
}

