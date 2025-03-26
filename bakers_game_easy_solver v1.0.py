import sys
import copy
sys.setrecursionlimit(20000)

# Initial State

# Rules
# Move all card to the foundation in order to win
# Card only move onto cards of the same suit (2H goes onto 3H)
suits = ["H", "D", "C", "S"]
ranks = ["0", "A", "2", "3", "4", "5", "6", "7", "8", "9", "T", "J", "Q", "K"]
deck = [rank + suit for suit in suits for rank in ranks]
values = {rank: i for i, rank in enumerate(ranks)}
num_of_cols = 8
num_of_reserves = 4

# Board
board = [
    ["4C", "4H", "8D", "2C", "2D", "AH", "KC"],
    ["JS", "9H", "3C", "7C", "6D", "QC", "5S"],
    ["8C", "2H", "5C", "QD", "JH", "4S", "TC"],
    ["TS", "7S", "3H", "8H", "9D", "KD", "AD"],
    ["5D", "JD", "AS", "QH", "6H", "2S"],
    ["3S", "JC", "6S", "6C", "9S", "TH"],
    ["9C", "3D", "5H", "7H", "4D", "AC"],
    ["KS", "TD", "QS", "7D", "KH", "8S"]
    ]
foundations = ["0H", "0D", "0C", "0S"]
reserve = []

script = []
state = [foundations, reserve, board]
win = ["KH", "KD", "KC", "KS"]
say_rank = {"A": "Ace", "2": "2", "3": "3", "4": "4", "5": "5", "6": "6", "7": "7", "8": "8", "9": "9", "T": "10", "J": "Jack", "Q": "Queen", "K": "King"}
say_suit = {"H": "Hearts", "D": "Diamonds", "C": "Cloves", "S": "Spades"}

# Helpers 
def check_board(board):
    deck = [rank + suit for suit in suits for rank in ranks]
    if len(board) != num_of_cols:
        print("Too many columns")
        return False
    num_of_cards = 0
    for col in board:
        num_of_cards += len(col)
        if num_of_cards > 52:
            print("Too many cards on the board")
            return False
        for card in col:
            if card in deck:
                deck.remove(card)
            else:
                print(f"Card {card} is duplicated")
                return False
    for card in foundations:
        deck.remove(card)
    if len(deck) > 0:
        print(f"There are missing cards on the board: {deck}")
        return False
    print("The board is valid")
    return True

def print_board(state): 
    longest_col = max(len(col) for col in state[2])
    print("----------------------------------------------------")
    print("------ Foundations ------------- Reserve -----------")
    print(f"{state[0]}----{state[1]}")
    print("----------------------------------------------------")

    for i in range(longest_col):
        row = []
        for col in state[2]:
            if i < len(col):
                row.append(f"[{col[i]}]")
        else:
            row.append("   ")
        print(" ".join(row))
    print("----------------------------------------------------")
    print("")

def read_move(move):
    if move[0] == "BtR":
        return f"Move the {say_rank[move[1][0]]} of {say_suit[move[1][1]]} from column {move[2]} to the reserve."
    if move[0] == "RtB":
        return f"Move the {say_rank[move[1][0]]} of {say_suit[move[1][1]]} from the reserve to column {move[2]}."
    if move[0] == "BtB":
        if len(move[1]) > 1:
            return f"Move the cards beggining wwith the {say_rank[move[1][0][0]]} of {say_suit[move[1][0][1]]} from column {move[2]} to column {move[3]}. "
        else:
            return f"Move the {say_rank[move[1][0][0]]} of {say_suit[move[1][0][1]]} from column {move[2]} to column {move[3]}"
    if move[0] == "BtF":
        return f"Move the {say_rank[move[1][0]]} of {say_suit[move[1][1]]} from column {move[2]} to the foundations"
    if move[0] == "RtF":
        return f"Move the {say_rank[move[1][0]]} of {say_suit[move[1][1]]} from the reserve to the foundations"

def print_winning_script(process):
    print("\nWinning Script:")
    for step, move in enumerate(process, start=1):
        print(f"{step}: {read_move(move[0])}")
        # print(f"{step}: {move[0]}") #For Debugging
    print("Congrats! The baord is done!")

def card_is_higher_and_same_suit(card_to_move, destination_card):
    c1_rank, c1_suit = card_to_move
    c2_rank, c2_suit = destination_card
    return values[c1_rank] - 1 == values[c2_rank] and c1_suit == c2_suit
    
# Move Logic
def try_move(state, wrong_moves, process):
    # Make note of the state upon which to perform a move
    foundations, reserve, board = state

    # Try moving cards to the foundations

    # Check every exposed (last) card on the board
    for col in board:
        if col:
            card = col[-1]
            foundation_card = foundations[suits.index(card[1])]
            # If the card is one higher than its foundation card (of the same suit)
            if card_is_higher_and_same_suit(card, foundation_card):
                # Determine what move will be attempted, make a copy of the state at which it was made
                move = [["BtF", card, board.index(col)], copy.deepcopy(state)]
                # Check if move is permitted (doesn't lead to a locked game)
                if move in wrong_moves:
                    continue
                # Avoid repeating patterns
                if move in process:
                    continue
                # Make the move
                foundations[suits.index(card[1])] = card
                col.pop()
                # Track the process
                process.append(move)
                state = [copy.deepcopy(foundations), copy.deepcopy(reserve), copy.deepcopy(board)]
                return True
    for card in reserve:
        foundation_card = foundations[suits.index(card[1])]
        if card_is_higher_and_same_suit(card, foundation_card):
            move = [["RtF", card], copy.deepcopy(state)]
            if move in wrong_moves:
                continue
            if move in process:
                    continue
            foundations[suits.index(card[1])] = card
            reserve.remove(card)
            process.append(move)
            state = [copy.deepcopy(foundations), copy.deepcopy(reserve), copy.deepcopy(board)]
            return True
        
    # Try moving cards around
    for col in board:
        if col:
            card = col[-1]
            movable_group = [card]
            if len(col) > 1:
                for i in range(len(col) - 2, -1, -1): #Check back from the exposed card
                    card = col[i]
                    next_card = movable_group[-1]
                    if card_is_higher_and_same_suit(card, next_card):
                        movable_group.append(card)
                    else:
                        break
                movable_group.reverse()
                for dest_col in board:
                    if dest_col == col:
                        continue
                    if not dest_col:
                        move = [["BtB", movable_group, board.index(col), board.index(dest_col)], copy.deepcopy(state)]
                        if move in wrong_moves:
                            continue
                        if move in process:
                            continue
                        if len(col) == len(movable_group):
                            continue
                        dest_col.extend(movable_group)
                        del col[-len(movable_group):]
                        process.append(move)
                        state = [copy.deepcopy(foundations), copy.deepcopy(reserve), copy.deepcopy(board)]
                        return True
                    else:
                        dest_card = dest_col[-1]
                        high_card = movable_group[0]
                        if card_is_higher_and_same_suit(dest_card, high_card):
                            move = [["BtB", movable_group, board.index(col), board.index(dest_col)], copy.deepcopy(state)]
                            if move in wrong_moves:
                                continue
                            if move in process:
                                continue
                            dest_col.extend(movable_group)
                            del col[-len(movable_group):]
                            process.append(move)
                            state = [copy.deepcopy(foundations), copy.deepcopy(reserve), copy.deepcopy(board)]
                            return True

    # Try moving cards from the reserve
    if reserve:
        for card in reserve:
            for col in board:
                if not col:
                    move = [["RtB", card, board.index(col)], copy.deepcopy(state)]
                    if move in wrong_moves:
                        continue
                    if move in process:
                        continue
                    col.append(card)
                    reserve.remove(card)
                    process.append(move)
                    state = [copy.deepcopy(foundations), copy.deepcopy(reserve), copy.deepcopy(board)]
                    return True
                else:
                    dest_card = col[-1]
                    if card_is_higher_and_same_suit(dest_card, card):
                        move = [["RtB", card, board.index(col)], copy.deepcopy(state)]
                        if move in wrong_moves:
                            continue
                        if move in process:
                            continue
                        col.append(card)
                        reserve.remove(card)
                        process.append(move)
                        state = [copy.deepcopy(foundations), copy.deepcopy(reserve), copy.deepcopy(board)]
                        return True

    # Try moving cards into the reserve
    if len(reserve) < num_of_reserves:
        for col in board:
            if col:
                card = col[-1]
                move = [["BtR", card, board.index(col)], copy.deepcopy(state)]
                if move in wrong_moves:
                    continue
                if move in process:
                    continue
                reserve.append(card)
                col.pop()
                process.append(move)
                state = [copy.deepcopy(foundations), copy.deepcopy(reserve), copy.deepcopy(board)]
                return True
    
    return False

def solver(state):
    global script
    state_stack = [copy.deepcopy(state)]
    process = []
    wrong_moves = []

    while state_stack:
        current_state = copy.deepcopy(state_stack[-1])

        if current_state[0] == win:
            script = process
            return True

        if try_move(current_state, wrong_moves, process): #Try a move
            state_stack.append(copy.deepcopy(current_state)) #Add state

        else:
            last_move = process.pop() # Remove the last move
            wrong_moves.append(copy.deepcopy(last_move))
            state_stack.pop() #Remove current state

            if not state_stack:
                print("Could not solve board")
                return False
            
    
    print("Could not solve baord")
    return False

def main():
    print("Let's try to solve your board:")
    print_board(state)
    if not check_board(board):
        return
    print("Finding solution...")
    if not solver(state):
        print("There's no solution!")
    else:
        print("The solution has been found!")
        print_winning_script(script)
        return
    
main()
