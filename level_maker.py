import random, json

WIDTH = 360
HEIGHT = 640

target_rect = [0,0]
default_max_height = HEIGHT - 300

def reset_target(max_height = default_max_height):
    global target_rect
    rnum = (random.randint(150, max_height))

    while abs(rnum - target_rect[1]) <= 50 and max_height != default_max_height:
        rnum = (random.randint(150, max_height))

    target_rect[1] = rnum
    return [0, rnum]

def not_far_enough(obstacle_rects, rnum):
    results = []
    for obstacle_rect in obstacle_rects:
        results.append(abs(obstacle_rect - rnum) > 50)

    return False in results

def reset_obstacle(obstacle_type):
    global obstacle_rects
    rnum = (random.randint(150, default_max_height))
    attempts = 0
    while not_far_enough(obstacle_rects, rnum):
        attempts +=1
        rnum = (random.randint(150, default_max_height))

    obstacle_rects.append(rnum)
    return [25, rnum, obstacle_type, random.choice([3,2,-3,-2])]

levels = {}

for i in range(1, 16):
    levels[str(i)] = {"target_rect": reset_target()}

for i in range(16, 76):
    obstacle_rects = []
    obstacle_type = random.choice(["ghost", "moving", "bouncy"])
    obstacle_1 = reset_obstacle(obstacle_type)
    max_height = min(obstacle_rects[0] + 70, default_max_height) if obstacle_type == "ghost" else default_max_height

    if i > 28:
        levels[str(i)] = {"obstacle_rect": [obstacle_1, reset_obstacle(random.choice(["moving", "bouncy"]))], "target_rect": reset_target(max_height)}
    elif i > 50:
        levels[str(i)] = {"obstacle_rect": [obstacle_1, reset_obstacle(random.choice(["moving", "bouncy"])), reset_obstacle(random.choice(["moving", "bouncy"]))], "target_rect": reset_target(max_height)}
    else:
        levels[str(i)] = {"obstacle_rect": [obstacle_1], "target_rect": reset_target(max_height)}

# Convert dictionary to JSON string
json_string = json.dumps(levels, indent=4)

with open("level_data1.json", "w") as f:
    f.write(json_string)