"""
Playwright-based controller for the tic-tac-toe web game.
"""
import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright, Page, Browser
from typing import Optional, Tuple


class TicTacToeGame:
    """Controls the tic-tac-toe game using Playwright."""

    def __init__(self, screenshots_dir: str = "screenshots"):
        self.screenshots_dir = Path(screenshots_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.screenshot_count = 0
        self.game_url = "https://memorymatching.com/tic-tac-toe"

    def start_browser(self, headless: bool = False):
        """Start the browser and navigate to the game."""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(headless=headless)
        self.page = self.browser.new_page()
        self.page.goto(self.game_url)

        # Wait for page to load
        time.sleep(2)

        print(f"✓ Browser started and navigated to {self.game_url}")

    def take_screenshot(self, label: str = "") -> str:
        """Take a screenshot of the current game state."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")

        self.screenshot_count += 1
        filename = f"step_{self.screenshot_count:03d}"
        if label:
            filename += f"_{label}"
        filename += ".png"

        filepath = self.screenshots_dir / filename
        self.page.screenshot(path=str(filepath))
        print(f"📸 Screenshot saved: {filepath}")
        return str(filepath)

    def click_cell(self, position: int) -> bool:
        """
        Click a cell on the tic-tac-toe board.

        Args:
            position: Cell position (1-9), numbered left to right, top to bottom:
                1 2 3
                4 5 6
                7 8 9

        Returns:
            True if click was successful, False otherwise
        """
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")

        if position < 1 or position > 9:
            print(f"❌ Invalid position: {position}. Must be between 1 and 9.")
            return False

        try:
            # The game uses a table structure with cells
            # We need to find the right cell selector
            # Let's try different common selectors
            selectors_to_try = [
                f"td:nth-child({((position - 1) % 3) + 1})",  # Generic table cell
                f".cell:nth-child({position})",
                f"[data-cell='{position}']",
                f"#cell-{position}",
            ]

            # First, let's try to click by calculating row and column
            row = (position - 1) // 3
            col = (position - 1) % 3

            # Try to find table rows and cells
            rows = self.page.query_selector_all("tr")
            if len(rows) >= 3:
                cells = rows[row].query_selector_all("td")
                if len(cells) > col:
                    cells[col].click()
                    print(f"✓ Clicked cell at position {position} (row {row + 1}, col {col + 1})")
                    time.sleep(0.5)  # Wait for animation
                    return True

            # Fallback: try clicking by position if we can find all cells
            all_cells = self.page.query_selector_all("td")
            if len(all_cells) >= 9:
                all_cells[position - 1].click()
                print(f"✓ Clicked cell at position {position}")
                time.sleep(0.5)
                return True

            print(f"⚠ Could not find cell at position {position}")
            return False

        except Exception as e:
            print(f"❌ Error clicking cell {position}: {e}")
            return False

    def reset_game(self) -> bool:
        """Reset the game by clicking the reset/new game button."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")

        try:
            # Try common reset button selectors
            reset_selectors = [
                "button:has-text('New Game')",
                "button:has-text('Reset')",
                "button:has-text('Play Again')",
                ".reset",
                "#reset",
                "input[type='button'][value*='New']",
            ]

            for selector in reset_selectors:
                try:
                    button = self.page.query_selector(selector)
                    if button:
                        button.click()
                        print("✓ Game reset")
                        time.sleep(1)
                        return True
                except:
                    continue

            # If no reset button found, reload the page
            print("⚠ Reset button not found, reloading page...")
            self.page.reload()
            time.sleep(2)
            return True

        except Exception as e:
            print(f"❌ Error resetting game: {e}")
            return False

    def get_game_state(self) -> dict:
        """Get the current state of the game from the page."""
        if not self.page:
            raise RuntimeError("Browser not started. Call start_browser() first.")

        try:
            # Try to extract game state from the page
            state = {
                "board": [],
                "status": "playing",
                "winner": None
            }

            # Check for game over messages
            game_over_selectors = [
                "text='You win!'",
                "text='You lose!'",
                "text='Draw!'",
                "text='Tie!'",
                ".game-over",
                ".winner"
            ]

            for selector in game_over_selectors:
                try:
                    element = self.page.query_selector(selector)
                    if element:
                        text = element.text_content().lower()
                        if 'win' in text:
                            state["status"] = "finished"
                            state["winner"] = "player"
                        elif 'lose' in text:
                            state["status"] = "finished"
                            state["winner"] = "computer"
                        elif 'draw' in text or 'tie' in text:
                            state["status"] = "finished"
                            state["winner"] = "draw"
                        break
                except:
                    continue

            return state

        except Exception as e:
            print(f"⚠ Error getting game state: {e}")
            return {"board": [], "status": "unknown", "winner": None}

    def close(self):
        """Close the browser and cleanup."""
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        print("✓ Browser closed")
