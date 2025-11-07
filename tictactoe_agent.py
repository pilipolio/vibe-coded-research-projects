"""
OpenAI-powered agent for playing tic-tac-toe using vision analysis.
"""
import base64
import os
from pathlib import Path
from typing import Optional, Tuple
from openai import OpenAI


class TicTacToeAgent:
    """LLM agent that uses OpenAI's vision capabilities to play tic-tac-toe."""

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the agent.

        Args:
            api_key: OpenAI API key. If not provided, will try to get from environment.
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable.")

        self.client = OpenAI(api_key=self.api_key)
        self.conversation_history = []

    def encode_image(self, image_path: str) -> str:
        """Encode image to base64 string."""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode("utf-8")

    def analyze_board_and_decide_move(self, screenshot_path: str, move_number: int) -> Tuple[Optional[int], str]:
        """
        Analyze the current board state from a screenshot and decide the next move.

        Args:
            screenshot_path: Path to the screenshot of the current game state
            move_number: Current move number

        Returns:
            Tuple of (cell_position, reasoning) where cell_position is 1-9 or None if game is over
        """
        # Encode the image
        base64_image = self.encode_image(screenshot_path)

        # Create the prompt for the LLM
        prompt = f"""You are playing tic-tac-toe. This is move number {move_number}.

Analyze the screenshot of the tic-tac-toe game board and:
1. Identify which cells are empty, which have X, and which have O
2. Determine which symbol you are playing as (X or O)
3. Decide the best move

The cells are numbered 1-9 like this:
1 2 3
4 5 6
7 8 9

Respond in EXACTLY this format:
ANALYSIS: [Describe what you see on the board - which cells are filled with X or O]
YOUR_SYMBOL: [X or O]
STRATEGY: [Explain your reasoning for the next move]
MOVE: [Just the number 1-9 of the cell you want to play, or NONE if the game is over]

Be very careful to identify the correct positions and symbols. Look closely at the screenshot."""

        try:
            # Call OpenAI API with vision
            response = self.client.chat.completions.create(
                model="gpt-4o",  # Using GPT-4 with vision
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=500
            )

            # Extract the response
            response_text = response.choices[0].message.content
            print(f"\n🤖 Agent Response:\n{response_text}\n")

            # Parse the move from the response
            move = self._parse_move_from_response(response_text)

            return move, response_text

        except Exception as e:
            print(f"❌ Error calling OpenAI API: {e}")
            return None, f"Error: {e}"

    def _parse_move_from_response(self, response: str) -> Optional[int]:
        """Parse the move number from the agent's response."""
        try:
            # Look for MOVE: line
            for line in response.split('\n'):
                if line.strip().startswith('MOVE:'):
                    move_str = line.split('MOVE:')[1].strip()
                    if move_str.upper() == 'NONE':
                        return None
                    # Extract just the number
                    import re
                    match = re.search(r'\d+', move_str)
                    if match:
                        move = int(match.group())
                        if 1 <= move <= 9:
                            return move
            return None
        except Exception as e:
            print(f"⚠ Error parsing move: {e}")
            return None

    def analyze_final_state(self, screenshot_path: str) -> str:
        """
        Analyze the final state of the game.

        Args:
            screenshot_path: Path to the final screenshot

        Returns:
            Analysis of the game outcome
        """
        base64_image = self.encode_image(screenshot_path)

        prompt = """Analyze this final tic-tac-toe game state.

Describe:
1. The final board configuration
2. Who won (X, O, or draw)
3. The winning combination if applicable
4. Brief analysis of the game

Be concise but thorough."""

        try:
            response = self.client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=300
            )

            return response.choices[0].message.content

        except Exception as e:
            print(f"❌ Error analyzing final state: {e}")
            return f"Error: {e}"
