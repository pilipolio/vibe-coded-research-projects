# Testing Guide

## Quick Start (Local Development)

If you have OpenAI API key and want to test immediately:

```bash
# 1. Install dependencies
pip install -r requirements.txt
python -m playwright install chromium

# 2. Set your API key
export OPENAI_API_KEY='your-key-here'

# 3. Run with local HTML game (no network needed)
python main.py play --url local --no-headless

# 4. Run with remote website
python main.py play --no-headless
```

## Expected Behavior

When running successfully, you should see:

1. Browser window opens (if `--no-headless`)
2. Game loads (either local HTML or remote website)
3. Screenshots are taken at each step
4. AI agent analyzes the board via GPT-4 Vision
5. AI makes moves by clicking cells (positions 1-9)
6. Game continues until win/loss/draw or max moves
7. Final analysis is provided and saved to `game_analysis.txt`

## Example Output

```
🎮 Starting Tic-Tac-Toe AI Agent
📁 Screenshots will be saved to: screenshots/game_20250107_131500
🤖 Max moves: 20
⏱️  Delay between moves: 2.0s
👁️  Headless mode: False

🌐 Starting browser...
✓ Browser started and navigated to file:///path/to/tictactoe_local.html

📸 Taking initial screenshot...
📸 Screenshot saved: screenshots/game_20250107_131500/step_001_initial.png

============================================================
🎯 Move 1
============================================================
🤔 Agent is analyzing the board...

🤖 Agent Response:
ANALYSIS: The board is empty, all 9 cells are available
YOUR_SYMBOL: X
STRATEGY: Taking the center (position 5) is strategically optimal
MOVE: 5

✅ Agent decided to play at position 5
✓ Clicked cell at position 5 (row 2, col 2)
...
```

## Troubleshooting

### "OPENAI_API_KEY not found"
Set the environment variable:
```bash
export OPENAI_API_KEY='sk-...'
```

### Network/Proxy Issues
Use the local HTML game:
```bash
python main.py play --url local
```

### Headless Mode Crashes
Try non-headless mode:
```bash
python main.py play --no-headless
```

### Can't Access Remote Website
This is expected in containerized environments with complex proxy setups. Use `--url local` instead.

## Testing the Components Individually

### Test OpenAI Connection
```python
from tictactoe_agent import TicTacToeAgent
agent = TicTacToeAgent()
# Should not raise any errors if API key is valid
```

### Test Browser Automation
```python
from game_controller import TicTacToeGame
game = TicTacToeGame(game_url="file:///path/to/tictactoe_local.html")
game.start_browser(headless=False)
# Browser should open and load the game
game.close()
```

### Test Screenshot Functionality
```python
from game_controller import TicTacToeGame
game = TicTacToeGame(game_url="file:///path/to/tictactoe_local.html")
game.start_browser(headless=False)
screenshot_path = game.take_screenshot("test")
print(f"Screenshot saved to: {screenshot_path}")
game.close()
```

## Known Limitations

1. **Containerized Environments**: Headless Chromium may crash when taking screenshots in some containerized environments (Docker, Kubernetes, etc.) due to memory/rendering constraints.

2. **Proxy Authentication**: Complex proxy URLs with embedded JWT tokens may not work with Playwright. Use local mode instead.

3. **Rate Limits**: OpenAI API has rate limits. If you make too many requests quickly, you may hit limits.

## Recommended Testing Environment

For best results, test on:
- Mac OS, Windows, or Linux desktop (not containerized)
- Python 3.8 or higher
- Valid OpenAI API key with GPT-4 Vision access
- Internet connection (for remote website testing)

## Sample Game Analysis Output

After a successful game, you'll find `game_analysis.txt`:

```
TIC-TAC-TOE GAME ANALYSIS
============================================================

Game played at: 20250107_131500
Total moves: 9
Screenshots directory: screenshots/game_20250107_131500

FINAL ANALYSIS:
The final board shows a completed game with X winning via
a diagonal line from top-left to bottom-right (positions 1-5-9).

Final board state:
X | O | O
---------
O | X | X
---------
X | O | O

Winner: X (Player)
Winning combination: Diagonal [1, 5, 9]

The game demonstrated effective strategic play with the AI
successfully securing the center position early and maintaining
control of the diagonal.
```
