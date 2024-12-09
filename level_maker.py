import random, json


WIDTH = 360
HEIGHT = 640

target_rect = [0,0]
obstacle_rect = [0,0]

def reset_target(max_height=HEIGHT - 300):
    global target_rect
    rnum = (random.randint(150, max_height))
    attempts = 0

    while abs(rnum - target_rect[1]) <= 50 and attempts < 50:
        attempts += 1
        rnum = (random.randint(150, max_height))

    target_rect[1] = rnum
    return [0, rnum]

def reset_obstacle(obstacle_type):
    global obstacle_rect
    rnum = (random.randint(150, HEIGHT - 300))
    attempts = 0
    
    while abs(rnum - obstacle_rect[1]) <= 50 and attempts < 50:
        attempts += 1
        rnum = (random.randint(150, HEIGHT - 300))
    
    obstacle_rect[1] = rnum
    return [25, rnum, obstacle_type]

levels = {}

for i in range(1, 16):
    levels[str(i)] = {"target_rect": reset_target()}

for i in range(16, 51):
    obstacle_type = random.choice(["ghost", "moving"])
    obstacle_1 = reset_obstacle(obstacle_type)
    max_height = min(obstacle_rect[1] + 70, HEIGHT - 300) if obstacle_type == "ghost" else HEIGHT - 300

    if random.randint(16, i + 5) > 28:
        levels[str(i)] = {"obstacle_rect": [obstacle_1, reset_obstacle("moving")], "target_rect": reset_target(max_height)}
        print("1")
    else:
        levels[str(i)] = {"obstacle_rect": [obstacle_1], "target_rect": reset_target(max_height)}

# Convert dictionary to JSON string
json_string = json.dumps(levels, indent=4)

with open("level_data1.json", "w") as f:
    f.write(json_string)