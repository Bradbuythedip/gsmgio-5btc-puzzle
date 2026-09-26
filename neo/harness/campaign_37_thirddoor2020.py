#!/usr/bin/env python3
"""Campaign 37: third door from 2020 poem + genesis grid ONLY (one shot).

Per the 2020 poem (#1710) and Phase-0 grid: yellow/blue numbers on the first image, same spiral
as the URL, "First or zero". sha256(X)+5 fixed encodings -> P2PKH vs 1NULY7 / prize / second.
X scoped to 2020 material only: NO 31/73/42, NO layer-sums (wrong year). One rule, one shot,
then freeze.
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from addr_check import check
X=[
 # poem #1710 lines
 "rosesarewhitebutoftenred","yellowhasanumberandsodoesblue","gobacktothefirstpuzzlepiece",
 "rosesarewhitebutoftenredyellowhasanumberandsodoesblue",
 # "First or zero" -> 1/0
 "firstorzero","first","zero","10","01","1","0",
 # grid / colour 2020 objects
 "gsmg.io/theseedisplanted","theseedisplanted","gsmgiotheseedisplanted",
 "f73d92","F73D92","0xf73d92","08c26d","BBBBYBBBYYBBBBYBBYYBYYBY",
 "111101110011110110010010",
 # yellow/blue counts (2020 image measurement)
 "yellow","blue","yellowblue","blueyellow","159","915","15","9","0F09",
]
print("2020 third-door X:", len(X))
m=check([(x,x.encode()) for x in X])
print("MATCHES:", m if m else "none -> freeze the 2020 third-door rule")
