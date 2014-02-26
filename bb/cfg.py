#!/usr/bin/env python3
items = {
    1: {
        "multi": 99,
        "buy": 10,
        "sell": 5,
    },
    2: {
        "multi": 99,
        "buy": 88,
        "sell": 44,
    },
    # ...
    3: {
        "multi": 6,
        "buy": 88,
        "sell": 44,
        "output": (  # for apply
                   (("hp", "lv * 3"), 1.0),
                   ((("mp", 1), ("mp", 5)), (9, 1)),
                  ),
    },

    1001: {
        "buy": 2000,
        "sell": 1000,
        #"attributes": [
        #    ["strength", 2],
        #    ["dexterity", 3],
        #    ["strength", 1],
        #],
    },
    # ...
}
