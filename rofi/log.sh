#!/bin/bash

# drop ansi colors
timl log | sed 's/\x1b\[[0-9;]*m//g' | rofi -dmenu -p "log: "
