
Table #2 for B-class items bugs out if Mog was Available, but not found, returning fewer items, and of
a subset of the C-class. This can be reproduced with `python -m chococheat mog 11`.

When bugged, Table #2 cuts off at Mog's Amulet, and gives the following instead:

| Bugged B-Class    ||
|-------------------|----------|
| Magic Stone       | 1/64     |
| Ochu Tentacle     | 1/64     |
| Cockatrice Pinion | 1/64     |
| Lightweight       | 1/64     |
| Screw             | 1/64     |
| Mesmerize Blade   | 1/64     |
| Betrayal Sword    | 1/64     |
| Dragon Fang       | 1/64     |
| Curse Spike       | 1/64     |
| Missile           | 1/64     |
| Running Fire      | 1/64     |
| Inferno Fang      | 1/64     |
| Whisper           | 1/64     |
| Barrier           | 1/64     |
| Red Fang          | 1/64     |
| North Wind        | 1/64     |
| MISSING DROPS     | 22/64    |

This doesn't seem very useful yet, but perhaps it could be of use elsewhere. Having MiniMog not found at
all doesn't trigger this bug, and still properly returns the Mog's Amulet.

The same setup does not trigger bugs in the other item tables. 
