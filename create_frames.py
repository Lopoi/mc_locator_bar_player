import json
import os

with open("output.json", "r") as f:
    data = json.load(f)

frames = data["frames"]

command = "execute if score #global timer matches $tick run waypoint modify @e[tag=pos_$position,limit=1] color hex $color"

rows = data["rows"]
columns = data["columns"]
last = [["" for _ in range(columns)] for _ in range(rows)]

for frame in frames:
    frame_index = frame["frame_index"]
    grid = frame["grid"]
    for i, row in enumerate(grid):
        for j, color in enumerate(row):
            if color == "":
                continue
            final_color = "000"
            if(color == "#FFFFFF"):
                final_color = "FFF"
            if last[i][j] != color:
                command_line = command.replace("$tick", str(frame_index+1)).replace("$position", str(j)).replace("$color", final_color)
                with open(f"movie_player/movie_player/function/lines/line_{i+1}.mcfunction", "a") as f:
                    f.write(command_line + "\n")
                last[i][j] = color

for i in range(rows):
    for j in range(columns):
        command_line = command.replace("$tick", str(frame_index+2)).replace("$position", str(j)).replace("$color", '0F0')
        with open(f"movie_player/movie_player/function/lines/line_{i+1}.mcfunction", "a") as f:
            f.write(command_line + "\n")