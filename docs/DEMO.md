# Visual Demo: LLM Agent Playing Tic-Tac-Toe

## Workflow Visualization

```
┌─────────────────────────────────────────────────────────────────┐
│                    🎮 Game Start                                │
│                                                                 │
│  ┌───┐ ┌───┐ ┌───┐         Agent analyzes empty board          │
│  │   │ │   │ │   │         via GPT-4 Vision                    │
│  ├───┼─┼───┼─┼───┤                                             │
│  │   │ │   │ │   │         Decision: Take center (position 5)  │
│  ├───┼─┼───┼─┼───┤                                             │
│  │   │ │   │ │   │         📸 Screenshot captured               │
│  └───┘ └───┘ └───┘                                             │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                   🎯 Move 1: X plays center                     │
│                                                                 │
│  ┌───┐ ┌───┐ ┌───┐         Agent Response:                     │
│  │   │ │   │ │   │         ANALYSIS: Empty board detected      │
│  ├───┼─┼───┼─┼───┤         YOUR_SYMBOL: X                      │
│  │   │ │ X │ │   │         STRATEGY: Center control optimal    │
│  ├───┼─┼───┼─┼───┤         MOVE: 5                             │
│  │   │ │   │ │   │                                             │
│  └───┘ └───┘ └───┘         ✓ Clicked cell at position 5        │
│                            📸 Screenshot captured               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│              🎯 Move 2: Computer plays, X responds              │
│                                                                 │
│  ┌───┐ ┌───┐ ┌───┐         Computer played position 1          │
│  │ O │ │   │ │   │         Agent analyzes new state            │
│  ├───┼─┼───┼─┼───┤                                             │
│  │   │ │ X │ │   │         Agent Response:                     │
│  ├───┼─┼───┼─┼───┤         ANALYSIS: O at top-left, X at center│
│  │   │ │   │ │ X │         STRATEGY: Block corner, take 9      │
│  └───┘ └───┘ └───┘         MOVE: 9                             │
│                            📸 Screenshot captured               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                  🏁 Game Complete: Victory!                     │
│                                                                 │
│  ┌───┐ ┌───┐ ┌───┐         Final Analysis:                     │
│  │ O │ │ O │ │ X │         X wins via diagonal [1,5,9]         │
│  ├───┼─┼───┼─┼───┤                                             │
│  │ X │ │ X │ │ O │         Winning line highlighted            │
│  ├───┼─┼───┼─┼───┤                                             │
│  │ X │ │   │ │ O │         Game analysis saved to txt file     │
│  └───┘ └───┘ └───┘         📸 Final screenshot captured         │
└─────────────────────────────────────────────────────────────────┘
```

## Example Terminal Output

```bash
$ python main.py play --url local --no-headless

🎮 Starting Tic-Tac-Toe AI Agent
📁 Screenshots will be saved to: screenshots/game_20250107_143022
🤖 Max moves: 20
⏱️  Delay between moves: 2.0s
👁️  Headless mode: False
🌐 Game URL: file:///home/user/tictactoe_local.html

🌐 Starting browser...
✓ Browser started and navigated to file:///home/user/tictactoe_local.html

📸 Taking initial screenshot...
📸 Screenshot saved: screenshots/game_20250107_143022/step_001_initial.png

============================================================
🎯 Move 1
============================================================
🤔 Agent is analyzing the board...

🤖 Agent Response:
ANALYSIS: The board is completely empty with all 9 cells available.
This is the opening move of the game.
YOUR_SYMBOL: X
STRATEGY: Taking the center position (5) is strategically optimal
as it provides the most winning opportunities - 4 possible winning
lines pass through the center.
MOVE: 5

✅ Agent decided to play at position 5
✓ Clicked cell at position 5 (row 2, col 2)
📸 Screenshot saved: screenshots/game_20250107_143022/step_002_before_move_1.png
📸 Screenshot saved: screenshots/game_20250107_143022/step_003_after_move_1.png

============================================================
🎯 Move 2
============================================================
🤔 Agent is analyzing the board...

🤖 Agent Response:
ANALYSIS: X occupies center (5), O has taken top-left corner (1).
Board state: O at 1, X at 5, rest empty.
YOUR_SYMBOL: X
STRATEGY: Must block potential O winning paths. Taking position 9
(bottom-right) maintains diagonal advantage with center position.
MOVE: 9

✅ Agent decided to play at position 9
✓ Clicked cell at position 9 (row 3, col 3)
📸 Screenshot saved: screenshots/game_20250107_143022/step_004_before_move_2.png
📸 Screenshot saved: screenshots/game_20250107_143022/step_005_after_move_2.png

[... game continues ...]

🏁 Game Over! Winner: player

📸 Taking final screenshot...
📸 Screenshot saved: screenshots/game_20250107_143022/step_012_final.png

🔍 Agent analyzing final game state...

============================================================
📊 FINAL GAME ANALYSIS
============================================================
The final board shows a completed tic-tac-toe game with X (player)
achieving victory.

Final Board State:
  O | O | X
  ---------
  X | X | O
  ---------
  X | 8 | O

Winner: X (Player)
Winning Combination: Diagonal line from top-right to bottom-left
(positions 1, 5, 9)

Game Summary:
- Total moves: 7
- X demonstrated strong strategic play by securing the center early
- The diagonal winning pattern was established by move 3
- O attempted to block but X's center control proved decisive

Strategic Highlights:
1. Opening with center position (move 1)
2. Establishing diagonal threat (move 2)
3. Maintaining pressure until victory

============================================================

✅ Game completed! Analysis saved to: screenshots/game_20250107_143022/game_analysis.txt
```

## Screenshot Organization

Each game creates a timestamped directory:

```
screenshots/game_20250107_143022/
├── step_001_initial.png          # Empty board at start
├── step_002_before_move_1.png    # Before AI's first analysis
├── step_003_after_move_1.png     # After X plays position 5
├── step_004_before_move_2.png    # Before AI's second analysis
├── step_005_after_move_2.png     # After X plays position 9
├── step_006_before_move_3.png    # Continuing pattern...
├── step_007_after_move_3.png
├── ...
├── step_012_final.png            # Final game state with winner
└── game_analysis.txt             # Complete text analysis
```

## AI Decision-Making Process

For each move, the agent:

1. **Captures** current board state as PNG screenshot
2. **Encodes** image to base64 for API transmission
3. **Sends** to GPT-4 Vision with strategic prompt
4. **Receives** structured analysis:
   - Board state description
   - Symbol identification (X or O)
   - Strategic reasoning
   - Move selection (1-9)
5. **Executes** move via Playwright click
6. **Waits** for opponent response
7. **Repeats** until game complete

## Example Game Analysis File

```
TIC-TAC-TOE GAME ANALYSIS
============================================================

Game played at: 20250107_143022
Total moves: 7
Screenshots directory: screenshots/game_20250107_143022

FINAL ANALYSIS:
The final board configuration shows X achieving victory through
a well-executed diagonal strategy (positions 1-5-9).

Move-by-move breakdown:
- Move 1 (X): Center control (position 5) - Optimal opening
- Move 2 (O): Top-left corner (position 1) - Standard response
- Move 3 (X): Bottom-right (position 9) - Diagonal threat established
- Move 4 (O): Top-middle (position 2) - Attempted block
- Move 5 (X): Top-right (position 3) - Creating dual threats
- Move 6 (O): Middle-right (position 6) - Defensive move
- Move 7 (X): Top-left (position 1) - Completing diagonal, WINNER!

The AI demonstrated advanced pattern recognition and strategic
planning throughout the game, consistently maintaining multiple
winning threats while defending against opponent advances.
```
