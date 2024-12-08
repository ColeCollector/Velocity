import random, json


WIDTH = 360
HEIGHT = 640

target_rect = [0,0]
obstacle_rect = [0,0]

def reset_target():
    global target_rect
    rnum = (random.randint(150, HEIGHT - 300))

    while abs(rnum - target_rect[1]) <= 50:
        rnum = (random.randint(150, HEIGHT - 300))

    target_rect[1] = rnum
    return [0, rnum]

def reset_obstacle():
    global obstacle_rect
    rnum = (random.randint(150, HEIGHT - 300))
    
    while abs(rnum - obstacle_rect[1]) <= 50:
        rnum = (random.randint(150, HEIGHT - 300))
    
    obstacle_rect[1] = rnum
    return [25, rnum, random.choice(["ghost", "moving"])]

lst = {}

for i in range(1, 16):
    lst[str(i)] = {"target_rect": reset_target()}

for i in range(16, 51):
    if random.randint(16, i) > 28:
        lst[str(i)] = {"target_rect": reset_target(), "obstacle_rect": [reset_obstacle(), reset_obstacle()]}
        print("1")
    else:
        lst[str(i)] = {"target_rect": reset_target(), "obstacle_rect": [reset_obstacle()]}

# Convert dictionary to JSON string
json_string = json.dumps(lst, indent=4)

with open("level_data.json", "w") as f:
    f.write(json_string)