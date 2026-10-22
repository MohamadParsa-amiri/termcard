from .match import match_answer
from .models import Card, Deck
from .scheduler import review_card, AGAIN, HARD, GOOD, EASY
from .storage import Storage
from . import ui


class FlashcardApp:
    def __init__(self, data_path):
        self.storage = Storage(data_path)
        self.data = self.storage.load()
        self.decks = [Deck.from_dict(d) for d in self.data.get("decks", [])]

    def save(self):
        self.data["decks"] = [d.to_dict() for d in self.decks]
        self.storage.save(self.data)

    def run(self):
        try:
            while True:
                self.main_menu()
        except (KeyboardInterrupt, EOFError):
            print()
            ui.info("Bye!")

    def main_menu(self):
        ui.clear()
        ui.banner()
        total_due = sum(len(d.due_cards()) for d in self.decks)
        total_new = sum(1 for d in self.decks for c in d.cards if c.is_new())
        total_cards = sum(len(d.cards) for d in self.decks)
        print(
            f"  Decks: {len(self.decks)}   Cards: {total_cards}   "
            f"{ui.color('Due: ' + str(total_due), ui.C.YELLOW)}   "
            f"{ui.color('New: ' + str(total_new), ui.C.GREEN)}"
        )
        print()
        for key, label in [
            ("D", "Decks"),
            ("R", "Review all due cards"),
            ("S", "Statistics"),
            ("Q", "Quit"),
        ]:
            print(f"  {ui.color('[' + key + ']', ui.C.CYAN)} {label}")
        print()
        choice = ui.prompt("> ").strip().lower()
        if choice == "d":
            self.decks_menu()
        elif choice == "r":
            self.review_all()
        elif choice == "s":
            self.show_stats()
        elif choice == "q":
            raise SystemExit

    def decks_menu(self):
        while True:
            ui.clear()
            ui.header("DECKS")
            if not self.decks:
                ui.warn("No decks yet.")
            for i, d in enumerate(self.decks, 1):
                due = len(d.due_cards())
                print(
                    f"  {ui.color(str(i) + '.', ui.C.CYAN)} {d.name}  "
                    f"{ui.color('(' + str(len(d.cards)) + ' cards, ' + str(due) + ' due)', ui.C.GRAY)}"
                )
            print()
            print(f"  {ui.color('[N]', ui.C.CYAN)} New deck   {ui.color('[B]', ui.C.CYAN)} Back")
            print()
            choice = ui.prompt("Deck # or command: ").strip().lower()
            if choice in ("b", ""):
                return
            if choice == "n":
                self.create_deck()
                continue
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(self.decks):
                    self.deck_menu(self.decks[idx])
            except ValueError:
                ui.error("Invalid choice")
                ui.pause()

    def create_deck(self):
        ui.clear()
        ui.header("NEW DECK")
        name = ui.prompt("Deck name: ").strip()
        if not name:
            ui.error("Name is required")
            ui.pause()
            return
        desc = ui.prompt("Description (optional): ").strip()
        self.decks.append(Deck.new(name, desc))
        self.save()
        ui.success(f"Deck '{name}' created")
        ui.pause()

    def deck_menu(self, deck):
        while True:
            ui.clear()
            ui.header(f"DECK: {deck.name}")
            if deck.description:
                print(f"  {ui.color(deck.description, ui.C.GRAY)}")
                print()
            due = len(deck.due_cards())
            print(f"  Cards: {len(deck.cards)}   Due: {ui.color(str(due), ui.C.YELLOW)}")
            print()
            for key, label in [
                ("A", "Add card"),
                ("L", "List cards"),
                ("R", "Review"),
                ("E", "Edit deck"),
                ("X", "Delete deck"),
                ("B", "Back"),
            ]:
                print(f"  {ui.color('[' + key + ']', ui.C.CYAN)} {label}")
            print()
            choice = ui.prompt("> ").strip().lower()
            if choice == "b":
                return
            if choice == "a":
                self.add_card(deck)
            elif choice == "l":
                self.list_cards(deck)
            elif choice == "r":
                self.review_deck(deck)
            elif choice == "e":
                new = ui.prompt(f"New name [{deck.name}]: ").strip()
                if new:
                    deck.name = new
                new_desc = ui.prompt(f"New description [{deck.description}]: ").strip()
                if new_desc:
                    deck.description = new_desc
                self.save()
                ui.success("Deck updated")
                ui.pause()
            elif choice == "x":
                confirm = ui.prompt(f"Delete deck '{deck.name}'? (y/N): ").strip().lower()
                if confirm == "y":
                    self.decks.remove(deck)
                    self.save()
                    ui.success("Deck deleted")
                    ui.pause()
                    return

    def add_card(self, deck):
        ui.clear()
        ui.header(f"ADD CARD -> {deck.name}")
        front = ui.prompt("Front: ").strip()
        if not front:
            ui.error("Front is required")
            ui.pause()
            return
        back = ui.prompt("Back: ").strip()
        if not back:
            ui.error("Back is required")
            ui.pause()
            return
        deck.cards.append(Card.new(front, back))
        self.save()
        ui.success("Card added")
        ui.pause()

    def list_cards(self, deck):
        ui.clear()
        ui.header(f"CARDS IN '{deck.name}'")
        if not deck.cards:
            ui.warn("No cards.")
            ui.pause()
            return
        for i, c in enumerate(deck.cards, 1):
            if c.is_due():
                tag = ui.color("due", ui.C.YELLOW)
            else:
                tag = ui.color(f"in {c.interval}d", ui.C.GRAY)
            print(
                f"  {ui.color(str(i) + '.', ui.C.CYAN)} {c.front}  "
                f"{ui.color('->', ui.C.GRAY)}  {c.back}  {ui.color('[' + tag + ']', ui.C.GRAY)}"
            )
        print()
        ui.pause()

    def review_all(self):
        items = [(d, c) for d in self.decks for c in d.due_cards()]
        if not items:
            ui.clear()
            ui.banner()
            ui.success("No cards due!")
            ui.pause()
            return
        self._run_review_session(items, "ALL DECKS")

    def review_deck(self, deck):
        items = [(deck, c) for c in deck.due_cards()]
        if not items:
            ui.clear()
            ui.header(f"REVIEW: {deck.name}")
            ui.success("No cards due in this deck!")
            ui.pause()
            return
        self._run_review_session(items, deck.name)

    @staticmethod
    def _show_verdict(result, ratio):
        if result == "correct":
            ui.success("Correct!")
        elif result == "close":
            ui.warn(f"So close! ({ratio:.0%} match)")
        elif result == "wrong":
            ui.error("Wrong answer")

    def _run_review_session(self, items, title):
        queue = list(items)
        reviewed = 0
        while queue:
            deck, card = queue.pop(0)
            ui.clear()
            ui.header(f"REVIEW: {title}")
            print(
                f"  {ui.color('Reviewed:', ui.C.BOLD)} {reviewed}   "
                f"{ui.color('Remaining:', ui.C.BOLD)} {len(queue) + 1}"
            )
            print()
            ui.box([card.front], title="FRONT", border_color=ui.C.CYAN)
            print()
            try:
                answer = ui.prompt("Your answer (Enter to reveal): ")
            except (KeyboardInterrupt, EOFError):
                return

            result, ratio = match_answer(answer, card.back)
            if result != "reveal":
                try:
                    self._show_verdict(result, ratio)
                    ui.pause("Press Enter to reveal the back...")
                except (KeyboardInterrupt, EOFError):
                    return

            ui.clear()
            ui.header(f"REVIEW: {title}")
            ui.box([card.front], title="FRONT", border_color=ui.C.CYAN)
            print()
            ui.box([card.back], title="BACK", border_color=ui.C.GREEN)
            print()
            print(
                f"  {ui.color('[1]', ui.C.RED)} Again    "
                f"{ui.color('[2]', ui.C.YELLOW)} Hard    "
                f"{ui.color('[3]', ui.C.GREEN)} Good    "
                f"{ui.color('[4]', ui.C.BLUE)} Easy"
            )
            rating = ui.prompt("> ").strip()
            quality_map = {"1": AGAIN, "2": HARD, "3": GOOD, "4": EASY}
            q = quality_map.get(rating)
            if q is None:
                queue.insert(0, (deck, card))
                continue

            review_card(card, q)
            if q == AGAIN:
                queue.append((deck, card))
            else:
                reviewed += 1
            self.save()

        ui.clear()
        ui.banner()
        ui.success(f"Session complete! {reviewed} card(s) reviewed.")
        ui.pause()

    def show_stats(self):
        ui.clear()
        ui.header("STATISTICS")
        total_cards = sum(len(d.cards) for d in self.decks)
        total_reviews = sum(c.total_reviews for d in self.decks for c in d.cards)
        avg_ef = 0.0
        if total_cards:
            avg_ef = sum(c.ease_factor for d in self.decks for c in d.cards) / total_cards

        print(f"  Decks:           {len(self.decks)}")
        print(f"  Total cards:     {total_cards}")
        print(f"  Total reviews:   {total_reviews}")
        print(f"  Average EF:      {avg_ef:.2f}")
        print()
        for d in self.decks:
            due = len(d.due_cards())
            new = sum(1 for c in d.cards if c.is_new())
            print(f"  - {d.name}: {len(d.cards)} cards, {due} due, {new} new")
        print()
        ui.pause()
