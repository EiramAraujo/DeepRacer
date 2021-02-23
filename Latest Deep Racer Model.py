import math
def reward_function_speed(params,reward):
    speed = params['speed']
    is_offtrack = params['is_offtrack']

    #if all_wheels_on_track:
    #    if speed >= 0.9:
    #        reward += 2
    #    elif speed >= 0.7:
    #        reward += 1
    #    else:
    #        reward = 0.2
    #else:
    #    reward = 1e-3
    if not is_offtrack:
        reward += 50*(speed**6)
    else:
        reward = 1e-3
        
    return float(reward)

def reward_function_center(params, reward):
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']

    # Calculate 3 markers that are at varying distances away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    if distance_from_center <= marker_1:
        reward += 3
    elif distance_from_center <= marker_2:
        reward += 2.75
    elif distance_from_center <= marker_3:
        reward += 2.5
    else:
        reward = 1e-3  # likely crashed/ close to off track

    return float(reward)


import math


def reward_function_waypoint_direction(params, reward, next_direction_diff):
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    heading = params['heading']
    n = closest_waypoints[1] + 1
    if n >= 34:  # 34 seems to be the number of waypoints for this track
        n = 1

    next_point = waypoints[closest_waypoints[1]]
    next2_point = waypoints[n]

    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
    future_track_direction = math.atan2(next2_point[1] - next_point[1], next2_point[0] - next_point[0])
    # Convert to degree
    future_track_direction = math.degrees(future_track_direction)

    # Calculate the difference between the track direction and the heading direction of the car
    direction_diff = abs(future_track_direction - heading)
    if direction_diff > 180:
        direction_diff = 360 - direction_diff

    # Penalize the reward if the difference is too large
    DIRECTION_THRESHOLD_STRAIGHT = 6.0
    DIRECTION_THRESHOLD_CURVE = 10.0
    if abs(next_direction_diff) < 6:
        if direction_diff > DIRECTION_THRESHOLD_STRAIGHT:
            reward *= 0.5
    else:
        if direction_diff > DIRECTION_THRESHOLD_CURVE:
            reward *=0.8

    return float(reward)


# returns a float number indicating direction difference between waypoints. Negative means a right turn.
def next_curve_direction(params):
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    n = closest_waypoints[1] + 1
    if n >= 34:  # 34 seems to be the number of waypoints for this track
        n = 1

    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]
    next2_point = waypoints[n]

    track_direction_current = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
    track_direction_current = math.degrees(track_direction_current)

    track_direction_next = math.atan2(next2_point[1] - next_point[1], next2_point[0] - next_point[0])
    track_direction_next = math.degrees(track_direction_next)

    next_direction_diff = abs(track_direction_next - track_direction_current)

    if next_direction_diff >= 180:
        next_direction_diff - 360
    if next_direction_diff <= -180:
        next_direction_diff + 360

    return next_direction_diff


def reward_function_curve_direction_left(params, reward, next_direction_diff):
    is_left_of_center = params['is_left_of_center']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']

    # Due to the vehicule stearing capabilities being only 30 deegres, the cap for a sharp turn is 30 deegres.
    if abs(next_direction_diff) >= 30:
        curve_sharpness = 30
    else:
        curve_sharpness = abs(next_direction_diff)

    # 0.5 is when the center of the scar is right on the edge of the track
    marker = (curve_sharpness * 0.5 / 30) * track_width

    if not (is_left_of_center ^ (next_direction_diff > 0)):
        if distance_from_center >= marker*0.9:
            reward += 2
        else:
            reward += 1.75
    else:
        reward += 1.5

    return float(reward)


def reward_function(params):
    reward = 1
    next_direction_diff = next_curve_direction(params)

    # counts for error in waypoints angle not being completely straight
    if abs(next_direction_diff) < 6:
        straight = True
    else:
        straight = False

    # rewards position in track
    if not straight:
        reward += reward_function_curve_direction_left(params, reward, next_direction_diff)
    else:
        reward += reward_function_center(params, reward)

    # rewards direction facing
    reward = reward_function_waypoint_direction(params, reward, next_direction_diff)
    
    #rewards speed
    reward = reward_function_speed(params,reward)

    return float(reward)