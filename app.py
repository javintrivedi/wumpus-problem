from flask import Flask, jsonify, request, render_template
import numpy as np
import random

app = Flask(__name__)

# Tic Tac Toe game state
board = np.full((3, 3), None)
player_symbol = 'X'
ai_symbol = 'O'
player_score = 0
ai_score = 0
difficulty = 'hard'  # can be 'easy' or 'hard'

def evaluate_board(board):
    # Check rows, columns, and diagonals for a win
    for i in range(3):
        if board[i, 0] == board[i, 1] == board[i, 2] and board[i, 0] is not None:
            return 10 if board[i, 0] == ai_symbol else -10
        if board[0, i] == board[1, i] == board[2, i] and board[0, i] is not None:
            return 10 if board[0, i] == ai_symbol else -10
    if board[0, 0] == board[1, 1] == board[2, 2] and board[0, 0] is not None:
        return 10 if board[0, 0] == ai_symbol else -10
    if board[0, 2] == board[1, 1] == board[2, 0] and board[0, 2] is not None:
        return 10 if board[0, 2] == ai_symbol else -10
    return 0

def is_board_full(board):
    return np.all(board != None)

def minimax(board, depth, is_maximizing):
    score = evaluate_board(board)
    
    if score == 10 or score == -10:
        return score
    
    if is_board_full(board):
        return 0

    if is_maximizing:
        best_score = -float('inf')
        for i in range(3):
            for j in range(3):
                if board[i, j] is None:
                    board[i, j] = ai_symbol
                    best_score = max(best_score, minimax(board, depth + 1, False))
                    board[i, j] = None
        return best_score
    else:
        best_score = float('inf')
        for i in range(3):
            for j in range(3):
                if board[i, j] is None:
                    board[i, j] = player_symbol
                    best_score = min(best_score, minimax(board, depth + 1, True))
                    board[i, j] = None
        return best_score

def best_move(board):
    if difficulty == 'easy':
        # Easy difficulty: choose random available move
        available_moves = [(i, j) for i in range(3) for j in range(3) if board[i, j] is None]
        if available_moves:
            return random.choice(available_moves)
        else:
            return (-1, -1)
    else:
        # Hard difficulty: minimax
        best_score = -float('inf')
        move = (-1, -1)
        for i in range(3):
            for j in range(3):
                if board[i, j] is None:
                    board[i, j] = ai_symbol
                    score = minimax(board, 0, False)
                    board[i, j] = None
                    if score > best_score:
                        best_score = score
                        move = (i, j)
        return move

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def make_move():
    global player_score, ai_score
    data = request.json
    x, y = data['move']
    global board
    board[x, y] = player_symbol  # Player move

    if evaluate_board(board) == -10:
        player_score += 1
        return jsonify({'status': 'win', 'board': board.tolist(), 'player_score': player_score, 'ai_score': ai_score})

    if is_board_full(board):
        return jsonify({'status': 'draw', 'board': board.tolist(), 'player_score': player_score, 'ai_score': ai_score})

    ai_move = best_move(board)
    if ai_move != (-1, -1):
        board[ai_move[0], ai_move[1]] = ai_symbol  # AI move

    if evaluate_board(board) == 10:
        ai_score += 1
        return jsonify({'status': 'lose', 'board': board.tolist(), 'player_score': player_score, 'ai_score': ai_score})

    if is_board_full(board):
        return jsonify({'status': 'draw', 'board': board.tolist(), 'player_score': player_score, 'ai_score': ai_score})

    return jsonify({'status': 'continue', 'board': board.tolist(), 'player_score': player_score, 'ai_score': ai_score})

@app.route('/reset', methods=['POST'])
def reset_game():
    global board, player_score, ai_score
    board = np.full((3, 3), None)
    player_score = 0
    ai_score = 0
    return jsonify({'status': 'reset', 'player_score': player_score, 'ai_score': ai_score})

@app.route('/set_options', methods=['POST'])
def set_options():
    global player_symbol, ai_symbol, difficulty
    data = request.json
    player_symbol = data.get('player_symbol', 'X')
    ai_symbol = 'O' if player_symbol == 'X' else 'X'
    difficulty = data.get('difficulty', 'hard')
    # Reset board on options change
    global board
    board = np.full((3, 3), None)
    return jsonify({'status': 'options_set'})

# Wumpus game backend implementation

WUMPUS_SIZE = 8

class WumpusGame:
    def __init__(self):
        self.size = WUMPUS_SIZE
        self.player_pos = (0, 0)
        self.wumpus_pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
        while self.wumpus_pos == self.player_pos:
            self.wumpus_pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
        self.pits = set()
        while len(self.pits) < 3:
            pit = (random.randint(0, self.size-1), random.randint(0, self.size-1))
            if pit != self.player_pos and pit != self.wumpus_pos:
                self.pits.add(pit)
        self.gold_pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
        while self.gold_pos == self.player_pos or self.gold_pos == self.wumpus_pos or self.gold_pos in self.pits:
            self.gold_pos = (random.randint(0, self.size-1), random.randint(0, self.size-1))
        self.has_gold = False
        self.is_alive = True
        self.is_wumpus_alive = True
        self.arrows = 1
        self.game_over = False

    def move_player(self, direction):
        if not self.is_alive or self.game_over:
            return
        x, y = self.player_pos
        if direction == 'up' and x > 0:
            x -= 1
        elif direction == 'down' and x < self.size - 1:
            x += 1
        elif direction == 'left' and y > 0:
            y -= 1
        elif direction == 'right' and y < self.size - 1:
            y += 1
        self.player_pos = (x, y)
        self.check_current_position()

    def check_current_position(self):
        if self.player_pos == self.wumpus_pos and self.is_wumpus_alive:
            self.is_alive = False
            self.game_over = True
        elif self.player_pos in self.pits:
            self.is_alive = False
            self.game_over = True
        elif self.player_pos == self.gold_pos:
            self.has_gold = True
            self.game_over = True

    def shoot_arrow(self, direction):
        if self.arrows <= 0 or not self.is_alive or self.game_over:
            return False
        self.arrows -= 1
        x, y = self.player_pos
        if direction == 'up':
            for i in range(x-1, -1, -1):
                if (i, y) == self.wumpus_pos:
                    self.is_wumpus_alive = False
                    self.game_over = True
                    return True
        elif direction == 'down':
            for i in range(x+1, self.size):
                if (i, y) == self.wumpus_pos:
                    self.is_wumpus_alive = False
                    self.game_over = True
                    return True
        elif direction == 'left':
            for j in range(y-1, -1, -1):
                if (x, j) == self.wumpus_pos:
                    self.is_wumpus_alive = False
                    self.game_over = True
                    return True
        elif direction == 'right':
            for j in range(y+1, self.size):
                if (x, j) == self.wumpus_pos:
                    self.is_wumpus_alive = False
                    self.game_over = True
                    return True
        return False

    def get_status(self):
        # When game is over, reveal all pits and wumpus and gold
        reveal_all = self.game_over
        pits_list = list(self.pits) if reveal_all else []
        wumpus_pos = None if (self.is_wumpus_alive and not reveal_all) else self.wumpus_pos
        gold_pos = None if (not self.has_gold and not reveal_all) else self.gold_pos
        # Breeze and stinky smell detection
        breeze = self.is_adjacent_to_pit(self.player_pos)
        stinky = self.is_adjacent_to_wumpus(self.player_pos) and self.is_wumpus_alive
        return {
            'player_pos': self.player_pos,
            'wumpus_pos': wumpus_pos,
            'pits': pits_list,
            'gold_pos': gold_pos,
            'has_gold': self.has_gold,
            'is_alive': self.is_alive,
            'is_wumpus_alive': self.is_wumpus_alive,
            'arrows': self.arrows,
            'breeze': breeze,
            'stinky': stinky,
            'game_over': self.game_over
        }

    def is_adjacent_to_pit(self, pos):
        x, y = pos
        for pit in self.pits:
            if abs(pit[0] - x) + abs(pit[1] - y) == 1:
                return True
        return False

    def is_adjacent_to_wumpus(self, pos):
        x, y = pos
        wx, wy = self.wumpus_pos
        return abs(wx - x) + abs(wy - y) == 1

wumpus_game = WumpusGame()

@app.route('/wumpus/start', methods=['POST'])
def wumpus_start():
    global wumpus_game
    wumpus_game = WumpusGame()
    return jsonify({'status': 'started', 'game': wumpus_game.get_status()})

@app.route('/wumpus/move', methods=['POST'])
def wumpus_move():
    data = request.json
    direction = data.get('direction')
    wumpus_game.move_player(direction)
    return jsonify({'status': 'moved', 'game': wumpus_game.get_status()})

@app.route('/wumpus/shoot', methods=['POST'])
def wumpus_shoot():
    data = request.json
    direction = data.get('direction')
    result = wumpus_game.shoot_arrow(direction)
    return jsonify({'status': 'shot', 'hit': result, 'game': wumpus_game.get_status()})

if __name__ == '__main__':
    app.run(debug=True)
