#!/usr/bin/env python3
"""
CLI for running an LLM agent to play tic-tac-toe.
"""
import os
import sys
import time
from datetime import datetime
from pathlib import Path
import click
from dotenv import load_dotenv

from game_controller import TicTacToeGame
from tictactoe_agent import TicTacToeAgent


@click.group()
def cli():
    """LLM Agent Tic-Tac-Toe Player"""
    pass


@cli.command()
@click.option('--headless/--no-headless', default=False, help='Run browser in headless mode')
@click.option('--max-moves', default=20, help='Maximum number of moves before stopping')
@click.option('--screenshots-dir', default='screenshots', help='Directory to save screenshots')
@click.option('--delay', default=2.0, help='Delay between moves in seconds')
def play(headless: bool, max_moves: int, screenshots_dir: str, delay: float):
    """Start a new game and let the AI agent play."""

    # Load environment variables
    load_dotenv()

    # Check for OpenAI API key
    if not os.getenv('OPENAI_API_KEY'):
        click.echo("❌ Error: OPENAI_API_KEY not found in environment variables.", err=True)
        click.echo("Please set your OpenAI API key:", err=True)
        click.echo("  export OPENAI_API_KEY='your-api-key-here'", err=True)
        sys.exit(1)

    # Create timestamped screenshots directory
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    game_screenshots_dir = Path(screenshots_dir) / f"game_{timestamp}"
    game_screenshots_dir.mkdir(parents=True, exist_ok=True)

    click.echo("🎮 Starting Tic-Tac-Toe AI Agent")
    click.echo(f"📁 Screenshots will be saved to: {game_screenshots_dir}")
    click.echo(f"🤖 Max moves: {max_moves}")
    click.echo(f"⏱️  Delay between moves: {delay}s")
    click.echo(f"👁️  Headless mode: {headless}")
    click.echo()

    # Initialize game controller and agent
    game = TicTacToeGame(screenshots_dir=str(game_screenshots_dir))
    agent = TicTacToeAgent()

    try:
        # Start browser
        click.echo("🌐 Starting browser...")
        game.start_browser(headless=headless)

        # Take initial screenshot
        click.echo("\n📸 Taking initial screenshot...")
        initial_screenshot = game.take_screenshot("initial")

        # Game loop
        move_count = 0
        game_over = False

        while move_count < max_moves and not game_over:
            move_count += 1
            click.echo(f"\n{'=' * 60}")
            click.echo(f"🎯 Move {move_count}")
            click.echo(f"{'=' * 60}")

            # Take screenshot of current state
            current_screenshot = game.take_screenshot(f"before_move_{move_count}")

            # Let agent analyze and decide move
            click.echo("🤔 Agent is analyzing the board...")
            move, reasoning = agent.analyze_board_and_decide_move(current_screenshot, move_count)

            if move is None:
                click.echo("🏁 Agent detected game is over or couldn't determine a move.")
                game_over = True
                break

            click.echo(f"✅ Agent decided to play at position {move}")

            # Execute the move
            success = game.click_cell(move)

            if not success:
                click.echo("⚠️  Move failed, taking screenshot of current state...")
                game.take_screenshot(f"failed_move_{move_count}")
                click.echo("🔄 Continuing to next iteration...")

            # Wait for computer's move (if it's a player vs computer game)
            time.sleep(delay)

            # Take screenshot after move
            game.take_screenshot(f"after_move_{move_count}")

            # Check game state
            state = game.get_game_state()
            if state["status"] == "finished":
                click.echo(f"\n🏁 Game Over! Winner: {state['winner']}")
                game_over = True

        # Take final screenshot
        click.echo("\n📸 Taking final screenshot...")
        final_screenshot = game.take_screenshot("final")

        # Get agent's analysis of final state
        click.echo("\n🔍 Agent analyzing final game state...")
        final_analysis = agent.analyze_final_state(final_screenshot)
        click.echo("\n" + "=" * 60)
        click.echo("📊 FINAL GAME ANALYSIS")
        click.echo("=" * 60)
        click.echo(final_analysis)
        click.echo("=" * 60)

        # Save analysis to file
        analysis_file = game_screenshots_dir / "game_analysis.txt"
        with open(analysis_file, 'w') as f:
            f.write("TIC-TAC-TOE GAME ANALYSIS\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Game played at: {timestamp}\n")
            f.write(f"Total moves: {move_count}\n")
            f.write(f"Screenshots directory: {game_screenshots_dir}\n\n")
            f.write("FINAL ANALYSIS:\n")
            f.write(final_analysis)

        click.echo(f"\n✅ Game completed! Analysis saved to: {analysis_file}")

    except KeyboardInterrupt:
        click.echo("\n\n⚠️  Game interrupted by user")
    except Exception as e:
        click.echo(f"\n❌ Error: {e}", err=True)
        import traceback
        traceback.print_exc()
    finally:
        # Cleanup
        click.echo("\n🧹 Cleaning up...")
        game.close()
        click.echo("✅ Done!")


@cli.command()
@click.argument('screenshots_dir', type=click.Path(exists=True))
def analyze(screenshots_dir: str):
    """Analyze screenshots from a previous game."""
    load_dotenv()

    if not os.getenv('OPENAI_API_KEY'):
        click.echo("❌ Error: OPENAI_API_KEY not found in environment variables.", err=True)
        sys.exit(1)

    agent = TicTacToeAgent()
    screenshots_path = Path(screenshots_dir)

    # Find final screenshot
    final_screenshots = list(screenshots_path.glob("*final*.png"))
    if not final_screenshots:
        click.echo("❌ No final screenshot found in directory.", err=True)
        sys.exit(1)

    final_screenshot = final_screenshots[0]
    click.echo(f"🔍 Analyzing: {final_screenshot}")

    analysis = agent.analyze_final_state(str(final_screenshot))
    click.echo("\n" + "=" * 60)
    click.echo("📊 GAME ANALYSIS")
    click.echo("=" * 60)
    click.echo(analysis)
    click.echo("=" * 60)


if __name__ == '__main__':
    cli()
