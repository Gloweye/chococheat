
Save game editor for FF8 chocoworld.
Based on [this Gamespot guide](https://gamefaqs.gamespot.com/boards/197343-final-fantasy-viii/68239394), 
but modified since PC save format has minor differences compared to pocketstation chocoworld saves. 
Tested it on non-remastered FF8, since I bought it before the remaster was a thing and I don't feel like 
spending money twice.

00-03: Big-endian 32-bit integer file-length
04-005:
07: Mog Event Control. bit 7 is SET when event wait is OFF. (value of 80)
08: Level, 01-99, 00 == 100 (max)
09: Current HP
0a: max hp
0b: First two weapon numbers (00-99, no abcdef)
0c: Last two weapon numbers (00-99, no abcdef)
0d: Not on PocketStation. f7 for me -> that's 11101111. (big-endian)
0e: Probably RANK. It was 006, but doesn't match PocketStation, since RANK 006 shouldn't allow A-class items.
0f: Probably movement rate. Don't mess with it.
10: Save Counter. Don't know overflow regions.
11-12: Likely overflow region, but no clue why it'd be a 24-bit integer. Like, really?
13: Lower part of ID (last two digits)
14: Higher part of ID (zero and first digit)
15: Home/out status. 01 == walking, 00 means at home.

Note: Only if 2 categories of items are owned.
1c: A-class Items
1d: B-class Items
1e: C-class Items
1f: D-class Items
