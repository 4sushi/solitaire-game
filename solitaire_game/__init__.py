from sys import platform

BACK_CARD = """\
╭───────╮
│///////│
│///4///│
│/sushi/│
│///////│
╰───────╯\
"""

TOP_PART_CARD = """\
╭───────╮\
"""

CARD_TEMPLATE_LINUX = """\
╭───────╮
│S xx   │
│       │
│       │
│    yyS│
╰───────╯\
"""

PART_CARD_TEMPLATE_LINUX = """\
╭────
│S xx
│   
│   
│   
╰────\
"""

TOP_PART_CARD_TEMPLATE_LINUX = """\
╭───────╮
│S xx   │\
"""

CARD_TEMPLATE_OSX = """\
╭───────╮
│Sxx    │
│       │
│       │
│    yyS│
╰───────╯\
"""

PART_CARD_TEMPLATE_OSX = """\
╭───
│Sxx
│   
│   
│   
╰───\
"""

TOP_PART_CARD_TEMPLATE_OSX = """\
╭───────╮
│Sxx    │\
"""

if 'linux' in platform:
    CARD_TEMPLATE = CARD_TEMPLATE_LINUX
    PART_CARD_TEMPLATE = PART_CARD_TEMPLATE_LINUX
    TOP_PART_CARD_TEMPLATE = TOP_PART_CARD_TEMPLATE_LINUX
else:
    CARD_TEMPLATE = CARD_TEMPLATE_OSX
    PART_CARD_TEMPLATE = PART_CARD_TEMPLATE_OSX
    TOP_PART_CARD_TEMPLATE = TOP_PART_CARD_TEMPLATE_OSX