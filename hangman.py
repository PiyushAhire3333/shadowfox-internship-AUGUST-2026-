
from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Set

# Data

class Difficulty(Enum):
    """Difficulty levels, each mapped to an allowed number of wrong guesses."""
    EASY = 8
    MEDIUM = 6
    HARD = 4


WORD_BANK: Dict[str, List[str]] = {
    "Programming": ["python", "variable", "function", "algorithm", "compiler"],
    "Cybersecurity": ["firewall", "encryption", "malware", "phishing", "exploit"],
    "Geography": ["mountain", "peninsula", "continent", "archipelago", "plateau"],
    "Animals": ["elephant", "kangaroo", "dolphin", "penguin", "cheetah"],
}

HANGMAN_STAGES: List[str] = [
    r"""
       -----
       |   |
       |
       |
       |
       |
    ---------
    """,
    r"""
       -----
       |   |
       |   O
       |
       |
       |
    ---------
    """,
    r"""
       -----
       |   |
       |   O
       |   |
       |
       |
    ---------
    """,
    r"""
       -----
       |   |
       |   O
       |  /|
       |
       |
    ---------
    """,
    r"""
       -----
       |   |
       |   O
       |  /|\
       |
       |
    ---------
    """,
    r"""
       -----
       |   |
       |   O
       |  /|\
       |  /
       |
    ---------
    """,
    r"""
       -----
       |   |
       |   O
       |  /|\
       |  / \
       |
    ---------
    """,
    r"""
       -----
       |   |
       |   O
       |  /|\
       |  / \
       |  DEAD
    ---------
    """,
]



# Core Game map

@dataclass
class HangmanGame:
    """
    Encapsulates all game state and rules for a single round of Hangman.

    The engine is presentation-agnostic: it exposes plain data (properties
    and methods) that any front-end — console, GUI, or web — can render.
    """

    secret_word: str
    max_wrong_guesses: int = Difficulty.MEDIUM.value
    guessed_letters: Set[str] = field(default_factory=set)
    wrong_guesses: int = field(default=0, init=False)

    def __post_init__(self) -> None:
        self.secret_word = self.secret_word.lower()


    def guess(self, letter: str) -> bool:
        """
        Register a single-letter guess.

        Returns:
            True if the letter is in the secret word, False otherwise.

        Raises:
            ValueError: if the input is not exactly one alphabetic character.
        """
        letter = letter.lower().strip()

        if len(letter) != 1 or not letter.isalpha():
            raise ValueError("Please enter exactly one letter (A-Z).")

        if letter in self.guessed_letters:
            raise ValueError(f"You've already guessed '{letter}'.")

        self.guessed_letters.add(letter)

        if letter in self.secret_word:
            return True

        self.wrong_guesses += 1
        return False

    @property
    def display_word(self) -> str:
        """The secret word with unguessed letters masked as underscores."""
        return " ".join(
            char if char in self.guessed_letters else "_"
            for char in self.secret_word
        )

    @property
    def remaining_guesses(self) -> int:
        return self.max_wrong_guesses - self.wrong_guesses

    @property
    def is_won(self) -> bool:
        return all(char in self.guessed_letters for char in self.secret_word)

    @property
    def is_lost(self) -> bool:
        return self.wrong_guesses >= self.max_wrong_guesses

    @property
    def is_over(self) -> bool:
        return self.is_won or self.is_lost

    @property
    def wrong_letters(self) -> List[str]:
        return sorted(l for l in self.guessed_letters if l not in self.secret_word)


class ConsoleView:
    """Renders game state to the terminal. Swap this out for a GUI/web view
    without touching HangmanGame."""

    @staticmethod
    def render(game: HangmanGame) -> None:
        stage_index = min(game.wrong_guesses, len(HANGMAN_STAGES) - 1)
        print(HANGMAN_STAGES[stage_index])
        print(f"Word:      {game.display_word}")
        print(f"Wrong:     {', '.join(game.wrong_letters) or '(none)'}")
        print(f"Attempts left: {game.remaining_guesses}")
        print("-" * 40)

    @staticmethod
    def render_result(game: HangmanGame) -> None:
        if game.is_won:
            print(f"\nYou win! The word was '{game.secret_word.upper()}'.\n")
        else:
            print(HANGMAN_STAGES[-1])
            print(f"\nGame over. The word was '{game.secret_word.upper()}'.\n")

class HangmanApp:
    """Orchestrates category/difficulty selection, the game loop, and
    replay flow. This is the only class that talks to the user."""

    def __init__(self) -> None:
        self.view = ConsoleView()
        self.wins = 0
        self.losses = 0

    def run(self) -> None:
        self._print_banner()
        while True:
            category, word = self._choose_word()
            difficulty = self._choose_difficulty()
            game = HangmanGame(secret_word=word, max_wrong_guesses=difficulty.value)

            print(f"\nCategory: {category}  |  Difficulty: {difficulty.name}\n")
            self._play_round(game)

            if not self._play_again():
                break

        self._print_summary()


    def _print_banner(self) -> None:
        print("=" * 40)
        print("            H A N G M A N")
        print("=" * 40)

    def _choose_word(self) -> tuple[str, str]:
        categories = list(WORD_BANK.keys())
        print("Choose a category:")
        for idx, name in enumerate(categories, start=1):
            print(f"  {idx}. {name}")

        choice = self._read_int_in_range("> ", 1, len(categories))
        category = categories[choice - 1]
        word = random.choice(WORD_BANK[category])
        return category, word

    def _choose_difficulty(self) -> Difficulty:
        options = list(Difficulty)
        print("\nChoose difficulty:")
        for idx, level in enumerate(options, start=1):
            print(f"  {idx}. {level.name} ({level.value} wrong guesses allowed)")

        choice = self._read_int_in_range("> ", 1, len(options))
        return options[choice - 1]

    def _play_round(self, game: HangmanGame) -> None:
        while not game.is_over:
            self.view.render(game)
            letter = input("Guess a letter: ")

            try:
                correct = game.guess(letter)
            except ValueError as err:
                print(f"Invalid input: {err}\n")
                continue

            print("Correct!\n" if correct else "Wrong!\n")

        self.view.render_result(game)
        self.wins += int(game.is_won)
        self.losses += int(game.is_lost)

    def _play_again(self) -> bool:
        answer = input("Play again? (y/n): ").strip().lower()
        return answer.startswith("y")

    def _print_summary(self) -> None:
        print("=" * 40)
        print(f"Session summary — Wins: {self.wins}  Losses: {self.losses}")
        print("Thanks for playing!")
        print("=" * 40)

    @staticmethod
    def _read_int_in_range(prompt: str, low: int, high: int) -> int:
        """Repeatedly prompts until the user enters a valid integer in range."""
        while True:
            raw = input(prompt).strip()
            if raw.isdigit() and low <= int(raw) <= high:
                return int(raw)
            print(f"Please enter a number between {low} and {high}.")




def main() -> None:
    app = HangmanApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!")


if __name__ == "__main__":
    main()