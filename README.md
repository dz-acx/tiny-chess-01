# Tiny Chess — a 4 KB Python chess engine

[![make.fun tiny-chess-01](https://make.fun/badge/tiny-chess-01.svg)](https://make.fun/bounty/tiny-chess-01)
[![rank](https://make.fun/badge/tiny-chess-01/dz-acx/tiny-chess-01/rank.svg)](https://make.fun/bounty/tiny-chess-01)
[![reward](https://make.fun/badge/tiny-chess-01/dz-acx/tiny-chess-01/reward.svg)](https://make.fun/bounty/tiny-chess-01)

A complete chess engine in a single `main.py` of at most 4,096 bytes:
negamax alpha-beta search with quiescence, piece-square tables and
MVV-LVA move ordering, driven by a fixed node budget (no clock, no
randomness), playing through the make.fun environment API.

Run: the make.fun harness runs `main.py` (Python 3.13, standard library
only) against the competition environment.
