# Author: 4sushi
from __future__ import annotations
from typing import Optional, List, Dict
import random


class Card:

    def __init__(self, value: int, symbol: str, color: str, icon: str):
        self.value = value
        self.symbol: str = symbol
        self.color: str = color
        self.icon: str = icon

    def get_str_value(self) -> str:
        mapping_values: Dict = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}
        if self.value in mapping_values:
            return mapping_values[self.value]
        else:
            return str(self.value)

    def __repr__(self) -> str:
        return f'{self.get_str_value()}{self.icon}'


class GameCards:

    SYMBOLS = {
        'hearts': {'name': 'hearts', 'color': 'red', 'icon': '♥'},
        'diamonds': {'name': 'diamonds', 'color': 'red', 'icon': '♦'},
        'spades': {'name': 'spades', 'color': 'black', 'icon': '♠'},
        'clubs': {'name': 'clubs', 'color': 'black', 'icon': '♣'},
    }

    def __init__(self, min_value: int = 1, max_value: int = 13):
        self.cards: List[Card] = []
        for symbol in self.SYMBOLS.values():
            for value in range(min_value, max_value+1):
                card = Card(value=value, symbol=symbol['name'], color=symbol['color'], icon=symbol['icon'])
                self.cards.append(card)
        self.NB_CARDS = len(self.cards)

    def mix_cards(self):
        random.shuffle(self.cards)

    def withdraw_cards(self, quantity: int = 1) -> List[Card]:
        if quantity > len(self.cards):
            raise ValueError('Error withdraw cards - Not enough cards in the game')
        cards: List[Card] = self.cards[0:quantity]
        self.cards = self.cards[quantity:]
        return cards
    

class GameSolitaire:

    def __init__(self):
        game_cards = GameCards()
        game_cards.mix_cards()
        self.NB_CARDS = game_cards.NB_CARDS

        self.deck: Deck = Deck(game_cards)

        self.initial_stacks: InitialStacks = InitialStacks(game_cards)

        self.final_stacks: FinalStacks = FinalStacks()

        self.areas = {  # area id => area params
            '1': {'name': 'deck'},
            '2': {'name': 'final_stacks', 'i_stack': 0},
            '3': {'name': 'final_stacks', 'i_stack': 1},
            '4': {'name': 'final_stacks', 'i_stack': 2},
            '5': {'name': 'final_stacks', 'i_stack': 3},
            '6': {'name': 'initial_stacks', 'i_stack': 0},
            '7': {'name': 'initial_stacks', 'i_stack': 1},
            '8': {'name': 'initial_stacks', 'i_stack': 2},
            '9': {'name': 'initial_stacks', 'i_stack': 3},
            '10': {'name': 'initial_stacks', 'i_stack': 4},
            '11': {'name': 'initial_stacks', 'i_stack': 5},
            '12': {'name': 'initial_stacks', 'i_stack': 6},
        }

    def action_switch_deck_cards(self):
        self.deck.switch_cards()

    def handle_action_move_cards(self, src_area_id: str,  dest_area_id: str,  quantity: int = 1):
        src_params: Dict = self.areas[src_area_id]
        dest_params: Dict = self.areas[dest_area_id]

        id_deck = [k for k, v in self.areas.items() if v['name'] == 'deck']
        id_final_stacks = [k for k, v in self.areas.items() if v['name'] == 'final_stacks']
        id_initial_stacks = [k for k, v in self.areas.items() if v['name'] == 'initial_stacks']

        if src_area_id in id_deck and dest_area_id in id_final_stacks:
            self.action_deck_to_finalstacks(dest_params['i_stack'])
        elif src_area_id in id_deck and dest_area_id in id_initial_stacks:
            self.action_deck_to_initialstacks(dest_params['i_stack'])
        elif src_area_id in id_final_stacks and dest_area_id in id_initial_stacks:
            self.action_finalstacks_to_initialstacks(src_params['i_stack'], dest_params['i_stack'])
        elif src_area_id in id_initial_stacks and dest_area_id in id_initial_stacks:
            self.action_initialstacks_to_initialstacks(src_params['i_stack'], dest_params['i_stack'], quantity)
        elif src_area_id in id_initial_stacks and dest_area_id in id_final_stacks:
            self.action_initialstacks_to_finalstacks(src_params['i_stack'], dest_params['i_stack'], quantity)
        else:
            return

    def action_deck_to_finalstacks(self, dest_i_stack: int):
        if not self.deck.can_pick_card():
            return
        source_card: Card = self.deck.get_pickable_card()
        final_stack: FinalStack = self.final_stacks.get_stack(dest_i_stack)
        if not final_stack.can_put_card(source_card):
            return
        final_stack.put_card(source_card)
        self.deck.pick_card()

    def action_deck_to_initialstacks(self, dest_i_stack: int):
        if not self.deck.can_pick_card():
            return
        source_card: Card = self.deck.get_pickable_card()
        initial_stack: InitialStack = self.initial_stacks.get_stack(dest_i_stack)
        if not initial_stack.can_put_cards([source_card]):
            return
        initial_stack.put_cards([source_card])
        self.deck.pick_card()

    def action_finalstacks_to_initialstacks(self, src_i_stack: int, dest_i_stack: int):
        final_stack: FinalStack = self.final_stacks.get_stack(src_i_stack)
        if not final_stack.can_pick_card():
            return
        source_card: Card = final_stack.get_pickable_card()
        initial_stack: InitialStack = self.initial_stacks.get_stack(dest_i_stack)
        if not initial_stack.can_put_cards([source_card]):
            return
        initial_stack.put_cards([source_card])
        final_stack.pick_card()

    def action_initialstacks_to_initialstacks(self, src_i_stack: int, dest_i_stack: int, quantity: int):
        initial_stack_src: InitialStack = self.initial_stacks.get_stack(src_i_stack)
        if not initial_stack_src.can_pick_cards(quantity):
            return
        source_cards: List[Card] = initial_stack_src.get_pickable_cards(quantity)
        initial_stack_dest: InitialStack = self.initial_stacks.get_stack(dest_i_stack)
        if not initial_stack_dest.can_put_cards(source_cards):
            return
        initial_stack_dest.put_cards(source_cards)
        initial_stack_src.pick_cards(quantity)

    def action_initialstacks_to_finalstacks(self, src_i_stack: int, dest_i_stack: int, quantity: int):
        initial_stack: InitialStack = self.initial_stacks.get_stack(src_i_stack)
        if not initial_stack.can_pick_cards(quantity):
            return
        source_cards: List[Card] = initial_stack.get_pickable_cards(quantity)
        if len(source_cards) != 1:
            return
        final_stack: FinalStack = self.final_stacks.get_stack(dest_i_stack)
        if not final_stack.can_put_card(source_cards[0]):
            return
        final_stack.put_card(source_cards[0])
        initial_stack.pick_cards(quantity)
    
    def is_game_won(self) -> bool:
        return sum([len(stack.cards) for stack in self.final_stacks.stacks]) == self.NB_CARDS
    

class Deck:

    NB_VISIBLE_CARDS: int = 3

    def __init__(self, game_cards: GameCards):
        self.cards: List[Card] = game_cards.withdraw_cards(quantity=24)
        self.i_deck_min: int = 0
        self.i_deck_max: int = 0

    def get_visible_cards(self) -> List[Card]:
        return self.cards[self.i_deck_min:self.i_deck_max]
    
    def can_pick_card(self) -> bool:
        return len(self.get_visible_cards()) > 0
    
    def get_pickable_card(self) -> Card:
        cards: List[Card] = self.get_visible_cards()
        return cards[-1]
        
    def pick_card(self):
        self.cards.pop(self.i_deck_max-1)
        self.i_deck_max -= 1

    def switch_cards(self):
        if self.i_deck_max == 0:
            self.i_deck_max = min(self.NB_VISIBLE_CARDS, len(self.cards))
        else:
            if self.i_deck_max == len(self.cards):
                self.i_deck_min = 0
                self.i_deck_max = 0
            else:
                self.i_deck_min = self.i_deck_max
                self.i_deck_max = min(len(self.cards), self.i_deck_max+self.NB_VISIBLE_CARDS)

    
class InitialStack:

    def __init__(self, hidden_cards: List[Card], visible_cards: List[Card]):
        self.hidden_cards: List[Card] = hidden_cards
        self.visible_cards: List[Card] = visible_cards

    def can_pick_cards(self, quantity) -> bool:
        return len(self.visible_cards) >= quantity

    def get_pickable_cards(self, quantity: int) -> List[Card]:
        return self.visible_cards[-quantity:]
        
    def count_visible_cards(self) -> int:
        return len(self.visible_cards)
    
    def count_hidden_cards(self) -> int:
        return len(self.hidden_cards)
    
    def count_cards(self) -> int:
        return self.count_visible_cards() + self.count_hidden_cards()

    def can_put_cards(self, cards: List[Card]) -> bool:
        top_card: Card = cards[0]
        if self.count_visible_cards() == 0:
            return top_card.get_str_value() == 'K'
        else:
            bottom_card: Card = self.get_pickable_cards(quantity=1)[0]
            return bottom_card.color != top_card.color and bottom_card.value == (top_card.value+1)

    def put_cards(self, cards: List[Card]):
        self.visible_cards += cards

    def pick_cards(self, quantity: int):
        self.visible_cards = self.visible_cards[:-quantity]
        if self.count_visible_cards() == 0 and self.count_hidden_cards() > 0:
            self.turn_hidden_card_face_up()

    def turn_hidden_card_face_up(self):
        card: Card = self.hidden_cards.pop()
        self.visible_cards = [card]


class InitialStacks:

    NB_STACKS = 7

    def __init__(self, game_cards: GameCards):
        self.stacks: List[InitialStack] = []
        for i in range(0, self.NB_STACKS):
            stack: InitialStack = InitialStack(
                hidden_cards=game_cards.withdraw_cards(quantity=i), 
                visible_cards=game_cards.withdraw_cards(quantity=1)
            )
            self.stacks.append(stack)

    def get_stack(self, i_stack: int) -> InitialStack:
        return self.stacks[i_stack]


class FinalStack:

    def __init__(self):
        self.cards: List[Card] = []

    def count_cards(self) -> int:
        return len(self.cards)

    def can_pick_card(self) -> bool:
        return len(self.cards) > 0

    def get_pickable_card(self) -> Card:
        return self.cards[-1]

    def can_put_card(self, card: Card) -> bool:
        if self.count_cards() == 0:
            return card.get_str_value() == 'A'
        else:
            top_card: Optional[Card] = self.get_pickable_card()
            return top_card.value == (card.value-1) and top_card.symbol == card.symbol

    def put_card(self, card: Card):
        self.cards.append(card)

    def pick_card(self):
        self.cards.pop()


class FinalStacks:

    NB_STACKS = 4

    def __init__(self):
        self.stacks: List[FinalStack] = []
        for _ in range(self.NB_STACKS):
            final_stack: FinalStack = FinalStack()
            self.stacks.append(final_stack)

    def get_stack(self, i_stack: int) -> FinalStack:
        return self.stacks[i_stack]
