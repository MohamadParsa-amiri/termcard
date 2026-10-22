import os
import sys
import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from termcard.models import Card, Deck
from termcard.scheduler import review_card, AGAIN, HARD, GOOD, EASY
from termcard.storage import Storage
from termcard.match import match_answer, normalize


class TestCard(unittest.TestCase):
    def test_new_card_is_due_and_new(self):
        c = Card.new("Q", "A")
        self.assertTrue(c.is_due())
        self.assertTrue(c.is_new())
        self.assertEqual(c.ease_factor, 2.5)
        self.assertEqual(c.repetitions, 0)

    def test_card_roundtrip(self):
        c = Card.new("Q", "A")
        c2 = Card.from_dict(c.to_dict())
        self.assertEqual(c2.front, "Q")
        self.assertEqual(c2.back, "A")
        self.assertEqual(c2.id, c.id)

    def test_not_due_future(self):
        c = Card.new("Q", "A")
        c.due = (date.today() + timedelta(days=3)).isoformat()
        self.assertFalse(c.is_due())


class TestScheduler(unittest.TestCase):
    def test_again_resets(self):
        c = Card.new("Q", "A")
        c.repetitions = 5
        c.interval = 30
        review_card(c, AGAIN)
        self.assertEqual(c.repetitions, 0)
        self.assertEqual(c.interval, 1)
        self.assertEqual(c.total_reviews, 1)

    def test_good_progression(self):
        c = Card.new("Q", "A")
        review_card(c, GOOD)
        self.assertEqual((c.interval, c.repetitions), (1, 1))
        review_card(c, GOOD)
        self.assertEqual((c.interval, c.repetitions), (6, 2))
        prev = c.interval
        review_card(c, GOOD)
        self.assertEqual(c.repetitions, 3)
        self.assertGreaterEqual(c.interval, prev)

    def test_easy_increases_ef(self):
        c = Card.new("Q", "A")
        initial = c.ease_factor
        review_card(c, EASY)
        self.assertGreater(c.ease_factor, initial)

    def test_hard_decreases_ef(self):
        c = Card.new("Q", "A")
        initial = c.ease_factor
        review_card(c, HARD)
        self.assertLess(c.ease_factor, initial)

    def test_hard_keeps_streak(self):
        c = Card.new("Q", "A")
        review_card(c, GOOD)
        review_card(c, GOOD)
        reps = c.repetitions
        review_card(c, HARD)
        self.assertEqual(c.repetitions, reps + 1)

    def test_ef_floor(self):
        c = Card.new("Q", "A")
        c.ease_factor = 1.3
        for _ in range(20):
            review_card(c, AGAIN)
        self.assertGreaterEqual(c.ease_factor, 1.3)

    def test_due_is_set_in_future(self):
        c = Card.new("Q", "A")
        review_card(c, GOOD)
        due = date.fromisoformat(c.due)
        self.assertGreaterEqual(due, date.today())


class TestStorage(unittest.TestCase):
    def test_save_and_load(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "test.json")
            s = Storage(path)
            s.save({"decks": [{"id": "1", "name": "Test"}]})
            data = s.load()
            self.assertEqual(len(data["decks"]), 1)
            self.assertEqual(data["decks"][0]["name"], "Test")

    def test_load_missing_returns_empty(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Storage(os.path.join(tmp, "nonexistent.json"))
            self.assertEqual(s.load(), {"decks": []})

    def test_atomic_save_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "t.json")
            s = Storage(path)
            s.save({"decks": [{"id": "1"}]})
            s.save({"decks": [{"id": "2"}]})
            self.assertEqual(s.load()["decks"][0]["id"], "2")


class TestDeck(unittest.TestCase):
    def test_due_cards_filter(self):
        d = Deck.new("Test")
        c1 = Card.new("Q1", "A1")
        c2 = Card.new("Q2", "A2")
        c2.due = (date.today() + timedelta(days=5)).isoformat()
        d.cards.extend([c1, c2])
        due = d.due_cards()
        self.assertEqual(len(due), 1)
        self.assertEqual(due[0].front, "Q1")

    def test_deck_roundtrip(self):
        d = Deck.new("Test", "desc")
        d.cards.append(Card.new("Q", "A"))
        d2 = Deck.from_dict(d.to_dict())
        self.assertEqual(d2.name, "Test")
        self.assertEqual(d2.description, "desc")
        self.assertEqual(len(d2.cards), 1)
        self.assertEqual(d2.cards[0].front, "Q")


class TestNormalize(unittest.TestCase):
    def test_arabic_yeh_and_kaf_map_to_persian(self):
        self.assertEqual(normalize("سلام عليكم"), normalize("سلام علیکم"))

    def test_arabic_digits_map_to_ascii(self):
        self.assertEqual(normalize("۱۲۳"), "123")

    def test_accents_stripped(self):
        self.assertEqual(normalize("Adiós"), "adios")

    def test_whitespace_and_punctuation_collapsed(self):
        self.assertEqual(normalize("  Hola,   mundo!  "), "hola mundo")


class TestMatchAnswer(unittest.TestCase):
    def test_exact_match(self):
        self.assertEqual(match_answer("Hola", "Hola")[0], "correct")

    def test_case_insensitive(self):
        self.assertEqual(match_answer("hola", "Hola")[0], "correct")

    def test_accent_insensitive(self):
        self.assertEqual(match_answer("adios", "Adiós")[0], "correct")

    def test_persian_normalization(self):
        self.assertEqual(match_answer("como estas", "¿Cómo estás?")[0], "correct")

    def test_close_match(self):
        self.assertEqual(match_answer("hla", "hola")[0], "close")

    def test_wrong_match(self):
        self.assertEqual(match_answer("xyz", "hola")[0], "wrong")

    def test_empty_reveals(self):
        self.assertEqual(match_answer("", "hola")[0], "reveal")


if __name__ == "__main__":
    unittest.main()
