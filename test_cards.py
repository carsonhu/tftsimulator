"""Hover cards (sim_entry.get_cards): the client's tooltip without the placeholders only the game fills in, and the
simulator's own notes (CARD_NOTE)."""
import re

import pytest

import sim_entry

PLACEHOLDER = re.compile(sim_entry._PLACEHOLDER)


@pytest.mark.parametrize("raw, clean", [
    ("The holder gains 1% per Hat.\n\nCurrent Hats: ⟨live⟩", "The holder gains 1% per Hat."),
    ("Execute.\n\nGold collected: ⟨live⟩Coin\n\nUnique", "Execute.\n\nUnique"),
    ("(4) AND they drop 1 Gold! (Total: ⟨live⟩)", "(4) AND they drop 1 Gold!"),
    ("Heal 20%.\n\nAlly Healing: ⟨HealthCalc1⟩", "Heal 20%."),
    ("Gain an Augment and [Gold ?] gold.", "Gain an Augment and gold."),
    ("No placeholders (except uniques).", "No placeholders (except uniques)."),
])
def test_placeholders_are_cleaned(raw, clean):
    assert sim_entry._clean_card_text(raw) == clean


def test_no_card_shows_a_placeholder():
    for name, card in sim_entry.get_cards({}).items():
        for text in [card["text"]] + [t["text"] for t in card["tiers"]]:
            assert not PLACEHOLDER.search(text), (name, text)

