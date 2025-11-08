# LLM Agent Tic-Tac-Toe Player

An AI agent that uses OpenAI's vision API and Playwright to autonomously play tic-tac-toe in a web browser.

## Features

- 🤖 Uses OpenAI's GPT-4 with vision to analyze game boards
- 🎮 Automated browser control with Playwright
- 📸 Takes screenshots at each step of gameplay
- 📊 Provides detailed analysis of game outcomes
- 🖥️ Simple CLI interface

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

3. **Set up your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```

   Or create a `.env` file:
   ```
   OPENAI_API_KEY=your-api-key-here
   ```

## Usage

### Play a game

Start a new game with the AI agent:

```bash
python main.py play
```

**Options:**
- `--headless` / `--no-headless` - Run browser in headless mode (default: visible)
- `--max-moves N` - Maximum number of moves (default: 20)
- `--screenshots-dir DIR` - Directory for screenshots (default: screenshots)
- `--delay SECONDS` - Delay between moves (default: 2.0)
- `--url URL` - Custom game URL (use "local" for bundled HTML game)

**Examples:**

Play with remote website (default):
```bash
python main.py play --no-headless --max-moves 15 --delay 3
```

Play with local HTML game (useful for testing):
```bash
python main.py play --url local
```

Play with custom URL:
```bash
python main.py play --url https://example.com/tictactoe
```

### Analyze a previous game

Analyze screenshots from a previous game:

```bash
python main.py analyze screenshots/game_20250107_120000/
```

## How it Works

1. **Browser Automation**: Playwright controls a Chromium browser and navigates to the tic-tac-toe game
2. **Vision Analysis**: Takes screenshots and sends them to OpenAI's GPT-4 with vision
3. **Decision Making**: The AI analyzes the board state and decides on the best move
4. **Action Execution**: Clicks the chosen cell on the game board
5. **Iteration**: Repeats until game is complete or max moves reached
6. **Final Analysis**: Provides a comprehensive analysis of the game outcome

## Visual Demo

### Game Flow Example

Here's what a typical game looks like:

**Initial State:**
```
┌───────┬───────┬───────┐
│       │       │       │
│   1   │   2   │   3   │
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
│   4   │   5   │   6   │
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
│   7   │   8   │   9   │
│       │       │       │
└───────┴───────┴───────┘
```
**AI Decision**: "Empty board - taking center for maximum strategic advantage"
**Move**: X → Position 5

**After Move 1:**
```
┌───────┬───────┬───────┐
│       │       │       │
│   1   │   2   │   3   │
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
│   4   │  [X]  │   6   │
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
│   7   │   8   │   9   │
│       │       │       │
└───────┴───────┴───────┘
```

**After Move 2:**
```
┌───────┬───────┬───────┐
│       │       │       │
│  [O]  │   2   │   3   │
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
│   4   │  [X]  │   6   │
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
│   7   │   8   │  [X]  │
│       │       │       │
└───────┴───────┴───────┘
```
**AI Decision**: "Establishing diagonal threat [1-5-9]"
**Move**: X → Position 9

**Final State (X Wins!):**
```
┌───────┬───────┬───────┐
│       │       │       │
│  [O]  │  [O]  │  ✓X   │
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
│   X   │  ✓X   │  [O]  │
│       │       │       │
├───────┼───────┼───────┤
│       │       │       │
│  ✓X   │   8   │  [O]  │
│       │       │       │
└───────┴───────┴───────┘
```
**Result**: X wins via diagonal [3-5-7]! 🎉

### Example AI Analysis

When analyzing the board, GPT-4 Vision provides detailed reasoning:

```
ANALYSIS: Current board shows X at center (5) and bottom-right (9).
O occupies top-left (1) and top-middle (2). O is building a threat
on the top row.

YOUR_SYMBOL: X

STRATEGY: Must block position 3 to prevent O victory on top row.
This move also maintains our diagonal threat through positions 3-5-7,
creating a dual-purpose defensive and offensive play.

MOVE: 3
```

### Terminal Output Preview

```bash
🎮 Starting Tic-Tac-Toe AI Agent
📁 Screenshots will be saved to: screenshots/game_20250107_143022

============================================================
🎯 Move 1
============================================================
🤔 Agent is analyzing the board...

🤖 Agent Response:
ANALYSIS: The board is completely empty...
YOUR_SYMBOL: X
STRATEGY: Taking center position for maximum winning opportunities
MOVE: 5

✅ Agent decided to play at position 5
✓ Clicked cell at position 5 (row 2, col 2)
📸 Screenshot saved: screenshots/.../step_003_after_move_1.png
```

For more detailed examples, see [docs/DEMO.md](docs/DEMO.md) and [docs/example_game_flow.md](docs/example_game_flow.md).

## Project Structure

```
.
├── main.py                # CLI interface
├── game_controller.py     # Playwright automation for game control
├── tictactoe_agent.py     # OpenAI agent for decision making
├── tictactoe_local.html   # Local HTML tic-tac-toe game for testing
├── requirements.txt       # Python dependencies
└── screenshots/           # Generated screenshots (timestamped by game)
```

## Network & Environment Notes

**Proxy Support**: The tool automatically detects and uses `HTTPS_PROXY` environment variables for accessing remote websites.

**Local Testing**: A bundled HTML tic-tac-toe game (`tictactoe_local.html`) is included for testing in environments with network restrictions. Use `--url local` to play with it.

**Containerized Environments**: In some containerized or restricted environments, Playwright may have limitations with:
- Complex proxy authentication
- Headless mode screenshot capabilities
- External website access

For these scenarios, use the local HTML game option or run in a standard desktop environment.

## Screenshot Organization

Each game creates a timestamped directory with screenshots:
- `step_001_initial.png` - Initial game state
- `step_002_before_move_1.png` - Before AI's first move
- `step_003_after_move_1.png` - After AI's first move
- ...
- `step_XXX_final.png` - Final game state
- `game_analysis.txt` - Complete game analysis

## Requirements

- Python 3.8+
- OpenAI API key with GPT-4 vision access
- Internet connection

## Additional Resources

This repository also contains:

### Lc0 ONNX Conversion Guide

Comprehensive documentation and tools for converting Leela Chess Zero (Lc0) neural network weights to ONNX format:

- **Documentation**: [docs/LC0_ONNX_CONVERSION.md](docs/LC0_ONNX_CONVERSION.md)
- **Tools & Models**: [lc0_models/](lc0_models/)
- **Network Inspector**: Python tool for analyzing Lc0 network files and getting conversion guidance

## License

See LICENSE file.
