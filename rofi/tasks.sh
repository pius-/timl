#!/bin/bash

selected=$((echo "stop"; timl tasks) | rofi -dmenu -p "task: ")

if [ "$selected" == "stop" ]; then
    output=$(timl stop)
elif [ ! -z "$selected" ]; then
    output=$(timl start $(echo $selected | cut -d':' -f1))
fi

notify-send --urgency low "$output"

