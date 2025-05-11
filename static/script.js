const cells = document.querySelectorAll('.cell');
const messageDiv = document.getElementById('message');
const resetButton = document.getElementById('reset');
const playerScoreSpan = document.getElementById('player-score');
const aiScoreSpan = document.getElementById('ai-score');
const playerSymbolSelect = document.getElementById('player-symbol');
const difficultySelect = document.getElementById('difficulty');
const applyOptionsButton = document.getElementById('apply-options');

const btnTicTacToe = document.getElementById('btn-tictactoe');
const btnWumpus = document.getElementById('btn-wumpus');
const tictactoeSection = document.getElementById('tictactoe-section');
const wumpusSection = document.getElementById('wumpus-section');

const wumpusStatusDiv = document.getElementById('wumpus-status');
const wumpusGridDiv = document.getElementById('wumpus-grid');
const wumpusResetButton = document.getElementById('wumpus-reset');
const wumpusMoveButtons = document.querySelectorAll('.wumpus-move');
const wumpusShootButtons = document.querySelectorAll('.wumpus-shoot');

let board = [
    [null, null, null],
    [null, null, null],
    [null, null, null]
];

// Navigation between games
btnTicTacToe.addEventListener('click', () => {
    tictactoeSection.style.display = 'block';
    wumpusSection.style.display = 'none';
});

btnWumpus.addEventListener('click', () => {
    tictactoeSection.style.display = 'none';
    wumpusSection.style.display = 'block';
    startWumpusGame();
});

// Tic Tac Toe game logic
cells.forEach(cell => {
    cell.addEventListener('click', () => {
        const index = cell.getAttribute('data-index');
        const x = Math.floor(index / 3);
        const y = index % 3;

        if (board[x][y] === null) {
            cell.textContent = playerSymbolSelect.value;
            board[x][y] = playerSymbolSelect.value;
            checkGameStatus(x, y);
        }
    });
});

resetButton.addEventListener('click', resetGame);

applyOptionsButton.addEventListener('click', () => {
    const options = {
        player_symbol: playerSymbolSelect.value,
        difficulty: difficultySelect.value
    };
    fetch('/set_options', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(options)
    }).then(() => {
        resetGame();
    });
});

function checkGameStatus(x, y) {
    fetch('/move', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ move: [x, y] })
    })
    .then(response => response.json())
    .then(data => {
        setTimeout(() => {
            if (data.status === 'win') {
                messageDiv.textContent = 'You win!';
                updateBoard(data.board);
            } else if (data.status === 'lose') {
                messageDiv.textContent = 'AI wins!';
                updateBoard(data.board);
            } else if (data.status === 'draw') {
                messageDiv.textContent = 'It\'s a draw!';
                updateBoard(data.board);
            } else {
                updateBoard(data.board);
                messageDiv.textContent = '';
            }
            playerScoreSpan.textContent = data.player_score;
            aiScoreSpan.textContent = data.ai_score;
        }, 500);
    });
}

function updateBoard(newBoard) {
    board = newBoard;
    cells.forEach((cell, index) => {
        const x = Math.floor(index / 3);
        const y = index % 3;
        cell.textContent = board[x][y] === null ? '' : board[x][y];
    });
}

function resetGame() {
    board = [
        [null, null, null],
        [null, null, null],
        [null, null, null]
    ];
    cells.forEach(cell => {
        cell.textContent = '';
    });
    messageDiv.textContent = '';
    playerScoreSpan.textContent = '0';
    aiScoreSpan.textContent = '0';

    // Reset the game on the server as well
    fetch('/reset', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        }
    });
}

// Wumpus game logic

function startWumpusGame() {
    fetch('/wumpus/start', {
        method: 'POST'
    })
    .then(response => response.json())
    .then(data => {
        updateWumpusUI(data.game);
    });
}

function updateWumpusUI(game) {
    wumpusStatusDiv.textContent = `Player Position: (${game.player_pos[0]}, ${game.player_pos[1]}) | Arrows: ${game.arrows} | Alive: ${game.is_alive} | Wumpus Alive: ${game.is_wumpus_alive} | Has Gold: ${game.has_gold} | Breeze: ${game.breeze ? 'Yes' : 'No'} | Stinky: ${game.stinky ? 'Yes' : 'No'}`;
    renderWumpusGrid(game);
}

function renderWumpusGrid(game) {
    wumpusGridDiv.innerHTML = '';
    const size = 8;
    for (let i = 0; i < size; i++) {
        const rowDiv = document.createElement('div');
        rowDiv.classList.add('wumpus-row');
        for (let j = 0; j < size; j++) {
            const cellDiv = document.createElement('div');
            cellDiv.classList.add('wumpus-cell');
            if (game.player_pos[0] === i && game.player_pos[1] === j) {
                cellDiv.textContent = 'P';
                cellDiv.classList.add('player');
            } else if (game.wumpus_pos && game.wumpus_pos[0] === i && game.wumpus_pos[1] === j) {
                cellDiv.textContent = 'W';
                cellDiv.classList.add('wumpus');
            } else if (game.gold_pos && game.gold_pos[0] === i && game.gold_pos[1] === j) {
                cellDiv.textContent = 'Gold';
                cellDiv.classList.add('gold');
            } else {
                // Show breeze or stinky smell indicators if adjacent
                let indicator = '';
                if (game.breeze && isAdjacent(game.player_pos, [i, j])) {
                    indicator += 'B';
                }
                if (game.stinky && isAdjacent(game.player_pos, [i, j])) {
                    indicator += 'S';
                }
                cellDiv.textContent = indicator;
            }
            rowDiv.appendChild(cellDiv);
        }
        wumpusGridDiv.appendChild(rowDiv);
    }
}

function isAdjacent(pos1, pos2) {
    const dx = Math.abs(pos1[0] - pos2[0]);
    const dy = Math.abs(pos1[1] - pos2[1]);
    return (dx + dy) === 1;
}

wumpusMoveButtons.forEach(button => {
    button.addEventListener('click', () => {
        const direction = button.getAttribute('data-direction');
        fetch('/wumpus/move', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction })
        })
        .then(response => response.json())
        .then(data => {
            updateWumpusUI(data.game);
        });
    });
});

wumpusShootButtons.forEach(button => {
    button.addEventListener('click', () => {
        const direction = button.getAttribute('data-direction');
        fetch('/wumpus/shoot', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ direction })
        })
        .then(response => response.json())
        .then(data => {
            updateWumpusUI(data.game);
            if (data.hit) {
                alert('You hit the Wumpus!');
            } else {
                alert('You missed!');
            }
        });
    });
});

wumpusResetButton.addEventListener('click', () => {
    startWumpusGame();
});
