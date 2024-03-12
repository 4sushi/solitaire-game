# Author: 4sushi
from __future__ import annotations
import curses
import re
from solitaire_game.game import GameSolitaire, Card
from typing import List, Optional, Dict, Tuple
import sys
from datetime import datetime, timedelta
from solitaire_game import BACK_CARD, TOP_PART_CARD, CARD_TEMPLATE, PART_CARD_TEMPLATE, TOP_PART_CARD_TEMPLATE


class GameUI:

    def __init__(self):
        self.cursor_area: None | int = None
        self.game: None | GameSolitaire = None
        self.selected_cursor_area: None | int = None
        self.selected_quantity: int = 1
        self.quantity: int = 1
        self.dt_start_game: datetime = datetime.now()
        self.KEY_QUIT: int = ord('!')
        self.KEY_RESTART: int = ord('?')
        self.KEY_ENTER: int = 10
        self.HORIZONTAL_MARGIN_BETWEEN_CARDS = 1
        self.VERTICAL_MARGIN_BETWEEN_CARDS = 1
        self.MARGIN_TOP = 1
        self.MARGIN_LEFT = 1
        self.COLOR_RED: None | int = None
        self.COLOR_DEFAULT: None | int = None
        self.COLOR_CURSOR: None | int = None
        self.COLOR_CURSOR_SELECTED: None | int = None
        self.height: None | int = None
        self.width: None | int = None
        self.x_center: None | int = None
        self.y_center: None | int = None
        self.stdscr = None
        self.init_game()
        curses.wrapper(self.init_screen)

    def init_game(self):
        self.game = GameSolitaire()
        self.cursor_area = 0
        self.selected_cursor_area = None
        self.selected_quantity = 1
        self.quantity = 1
        self.dt_start_game: datetime = datetime.now()

    def init_screen(self, stdscr):
        self.stdscr = stdscr
        print(type(stdscr))
        curses.curs_set(0)
        self.stdscr.keypad(True)
        # Init colors
        curses.use_default_colors()
        curses.start_color()
        curses.init_pair(1, curses.COLOR_RED, -1)
        curses.init_pair(2, -1, -1)
        if sys.platform == 'win32':
            curses.init_pair(3, curses.COLOR_RED, -1)
        else:
            curses.init_pair(3, curses.COLOR_MAGENTA, -1)
        curses.init_pair(4, curses.COLOR_GREEN, -1)
        self.COLOR_RED = curses.color_pair(1)
        self.COLOR_DEFAULT = curses.color_pair(2)
        self.COLOR_CURSOR = curses.color_pair(3)
        self.COLOR_CURSOR_SELECTED = curses.color_pair(4)
        self.controller()

    def controller(self):
        k = 0
        while k != self.KEY_QUIT:
            try:
                if k in (curses.KEY_RIGHT, curses.KEY_LEFT, curses.KEY_DOWN, curses.KEY_UP):
                    self.controller_direction_keys(k)
                elif k == self.KEY_ENTER:
                    self.controller_enter_key()
                elif k == self.KEY_RESTART:
                    self.init_game()
                self.refresh_screen()
                if self.game.is_game_won():
                    self.popup_game_won()
            except curses.error as e:
                if str(e) == 'addwstr() returned ERR':
                    self.popup_error()
                else:
                    raise e
            k = self.stdscr.getch()

    def controller_direction_keys(self, k: int):
        if k == curses.KEY_RIGHT:
            self.quantity = 1
            if self.cursor_area >= 12:
                self.cursor_area = 0
            else:
                self.cursor_area += 1
        elif k == curses.KEY_LEFT:
            self.quantity = 1
            if self.cursor_area <= 0:
                self.cursor_area = 12
            else:
                self.cursor_area -= 1
        elif k == curses.KEY_UP:
            if self.selected_cursor_area:
                return
            if self.cursor_area < 6:
                return
            i_stack: int = self.game.areas[str(self.cursor_area)]['i_stack']
            if self.game.initial_stacks.get_stack(i_stack).count_visible_cards() > self.quantity:
                self.quantity += 1
        elif k == curses.KEY_DOWN:
            if self.selected_cursor_area:
                return
            self.quantity = max(self.quantity - 1, 1)

    def controller_enter_key(self):
        if not self.selected_cursor_area:
            if self.cursor_area == 0:
                self.game.action_switch_deck_cards()
            else:
                self.selected_cursor_area = self.cursor_area
                self.selected_quantity = self.quantity
        else:
            if self.cursor_area != 0:
                self.game.handle_action_move_cards(str(self.selected_cursor_area), str(self.cursor_area),
                                                   self.selected_quantity)
            self.selected_cursor_area = None
            self.quantity = 1
            self.selected_quantity = self.quantity

    def popup_game_won(self):
        self.stdscr.clear()
        dt_now: datetime = datetime.now()
        delta: timedelta = dt_now - self.dt_start_game
        message: str = f'Victory! You have won in {delta.seconds // 60} minutes and {delta.seconds % 60} seconds.'
        self.stdscr.addstr(self.y_center - 1, self.x_center - int(len(message) / 2), message)
        message = f'Press [?] to replay or [!] to quit.'
        self.stdscr.addstr(self.y_center, self.x_center - int(len(message) / 2), message)
        while True:
            k = self.stdscr.getch()
            c = chr(k)
            if c == '!':
                sys.exit(0)
            elif c == '?':
                self.init_game()
                break

    def popup_error(self):
        self.stdscr.clear()
        error_message: str = 'Screen is to small, enlarge the window to play.'
        self.stdscr.addstr(self.y_center - 1, self.x_center - int(len(error_message) / 2), error_message,
                           self.COLOR_RED)

    def refresh_screen(self):
        self.stdscr.clear()
        self.height, self.width = self.stdscr.getmaxyx()
        self.x_center = int(self.width / 2)
        self.y_center = int(self.height / 2)

        self.draw_deck()
        self.draw_initial_stacks()
        self.draw_final_stacks()

        info_menu: str = f'[Enter↵]select [Left←][Right→][Up↑][Down↓]navigate [?]new game [!]quit'
        self.stdscr.addstr(self.height - 1, 0, info_menu + ' ' * (self.width - len(info_menu) - 1), curses.A_STANDOUT)
        self.stdscr.refresh()

    def draw_deck(self):
        area_id: int = 1
        x: int = self.MARGIN_LEFT
        y: int = self.MARGIN_TOP

        self.draw_card(y, x, BACK_CARD, cursor_area=0)
        x += self.get_shape_card_str(BACK_CARD)['nb_cols'] + self.HORIZONTAL_MARGIN_BETWEEN_CARDS
        cards: List[Card] = self.game.deck.get_visible_cards()
        for i, card in enumerate(cards):
            if i == len(cards) - 1:
                card_str: str = self.eval_card_template(CARD_TEMPLATE, card)
                self.draw_card(y, x, card_str, cursor_area=area_id)
            else:
                card_str: str = self.eval_card_template(PART_CARD_TEMPLATE, card)
                self.draw_card(y, x, card_str)
                x += self.get_shape_card_str(PART_CARD_TEMPLATE)['nb_cols']
        if len(cards) == 0:
            card_str: str = self.eval_card_template(CARD_TEMPLATE)
            self.draw_card(y, x, card_str, cursor_area=area_id)

    def draw_initial_stacks(self):
        x: int = self.MARGIN_LEFT
        for i_stack, stack in enumerate(self.game.initial_stacks.stacks):
            area_id: int = 6 + i_stack
            y: int = self.MARGIN_TOP + self.get_shape_card_str(CARD_TEMPLATE)[
                'nb_lines'] + self.VERTICAL_MARGIN_BETWEEN_CARDS
            for _ in stack.hidden_cards:
                self.draw_card(y, x, TOP_PART_CARD)
                y += self.get_shape_card_str(TOP_PART_CARD)['nb_lines']
            for i_card, card in enumerate(stack.visible_cards):
                if i_card == stack.count_visible_cards() - 1:
                    card_str: str = self.eval_card_template(CARD_TEMPLATE, card)
                    self.draw_card(y, x, card_str, cursor_area=area_id)
                else:
                    card_str: str = self.eval_card_template(TOP_PART_CARD_TEMPLATE, card)
                    self.draw_card(y, x, card_str, cursor_area=area_id, quantity=stack.count_visible_cards() - i_card)
                    y += self.get_shape_card_str(card_str)['nb_lines']
            if stack.count_cards() == 0:
                card_str: str = self.eval_card_template(CARD_TEMPLATE)
                self.draw_card(y, x, card_str, cursor_area=area_id)
            x += self.get_shape_card_str(CARD_TEMPLATE)['nb_cols'] + self.HORIZONTAL_MARGIN_BETWEEN_CARDS

    def draw_final_stacks(self):
        x: int = self.MARGIN_LEFT + (self.get_shape_card_str(CARD_TEMPLATE)['nb_cols'] +
                                     self.HORIZONTAL_MARGIN_BETWEEN_CARDS) * 3
        y: int = self.MARGIN_TOP
        for i_stack, stack in enumerate(self.game.final_stacks.stacks):
            area_id: int = 2 + i_stack
            if stack.count_cards() > 0:
                card: Card = stack.get_pickable_card()
                card_str: str = self.eval_card_template(CARD_TEMPLATE, card)
                self.draw_card(y, x, card_str, cursor_area=area_id)
            else:
                card_str: str = self.eval_card_template(CARD_TEMPLATE)
                self.draw_card(y, x, card_str, cursor_area=area_id)
            x += self.get_shape_card_str(CARD_TEMPLATE)['nb_cols'] + self.HORIZONTAL_MARGIN_BETWEEN_CARDS

    def draw_card(self, x: int, y: int, card_str: str, cursor_area=None, quantity=None):
        stdscr_attr: int = 0
        is_bold_card: bool = False
        if cursor_area and cursor_area == self.selected_cursor_area:
            if not quantity or quantity <= self.selected_quantity:
                stdscr_attr = self.COLOR_CURSOR_SELECTED
                is_bold_card = True

        if cursor_area == self.cursor_area:
            if not quantity or quantity <= self.quantity:
                stdscr_attr = self.COLOR_CURSOR
                is_bold_card = True

        lines = card_str.split('\n')
        for i, line in enumerate(lines):
            line = self.render_card_bold(is_bold_card, line)
            self.stdscr.addstr(x + i, y, line, stdscr_attr)
            match = re.search(r'[0-9AJQK]+[♥♦]+|[♥♦]+\s?[0-9AJQK]+', line)
            if match:
                self.stdscr.addstr(x + i, y + match.start(), match.group(), self.COLOR_RED)
            match = re.search(r'[0-9AJQK]+[♠♣]+|[♠♣]+\s?[0-9AJQK]+', line)
            if match:
                self.stdscr.addstr(x + i, y + match.start(), match.group(), self.COLOR_DEFAULT)

    def render_card_bold(self, bold_card: bool, line: str) -> str:
        if not bold_card:
            return line
        replace_chars: List[Tuple[str, str]] = [('╭', '┏'), ('╮', '┓'), ('╯', '┛'), ('╰', '┗'), ('─', '━'), ('│', '┃')]
        for c in replace_chars:
            line = line.replace(c[0], c[1])
        return line

    def eval_card_template(self, card_template: str, card: Optional[Card] = None) -> str:
        left_value: str = '  '
        right_value: str = '  '
        icon: str = ' '
        if card:
            left_value = card.get_str_value().ljust(2)
            right_value = card.get_str_value().rjust(2)
            icon = card.icon
        return card_template.replace('xx', left_value).replace('yy', right_value).replace('S', icon)

    def get_shape_card_str(self, card_str: str) -> Dict:
        lines: List[str] = card_str.split('\n')
        nb_lines: int = len(lines)
        nb_cols: int = max([len(line) for line in lines])
        return {'nb_lines': nb_lines, 'nb_cols': nb_cols}
