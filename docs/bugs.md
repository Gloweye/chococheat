
Table #2 for B-class items bugs out if Mog was Available, but not found, returning fewer items, and of a subset of the 
C-class, with on D-class item. This can be reproduced with `python -m chococheat mog 11`.

When bugged, Table #2 cuts off at Mog's Amulet, and gives the following instead:

| Bugged B-Class    | Amount |
|-------------------|--------|
| Magic Stone       | 1/64   |
| Ochu Tentacle     | 1/64   |
| Cockatrice Pinion | 1/64   |
| Lightweight       | 1/64   |
| Screw             | 1/64   |
| Mesmerize Blade   | 1/64   |
| Betrayal Sword    | 1/64   |
| Dragon Fang       | 1/64   |
| Curse Spike       | 1/64   |
| Missile           | 1/64   |
| Running Fire      | 1/64   |
| Inferno Fang      | 1/64   |
| Whisper           | 1/64   |
| Barrier           | 1/64   |
| Red Fang          | 1/64   |
| North Wind        | 1/64   |
| MISSING DROPS     | 22/64  |

This doesn't seem very useful yet, but perhaps it could be of use elsewhere. Having MiniMog not found at all doesn't 
trigger this bug, and still properly returns the Mog's Amulet.

The same setup does not trigger bugs in the other item tables. 

Selecting "Do Over" may also result in a similar bugged state if a new save is immediately imported after. The above
table will be seen first, and then continue. 

It grabs the same array that's already populated, and then overwrites items without overwriting their counts. The items
that are provided are stable, but not related to normal Chocobo Loot Tables. 

Then fixing the bug by setting mog to any different value will give items with identical counts on the acceptance pages,
but different items.
Making a save with 64 of each item, using `chocosave run`, and then pressing "Do over" will get you a Solomon Ring 
even if you're otherwise on the wrong loot table. Along with all magazines except Combat King 002 and 004, but you get
5 copies of 003. 

It also requires less resets to get full Thundaga, Holy, Tornado, and Double, because those items overwrite the large
item amounts in the D loot table.
