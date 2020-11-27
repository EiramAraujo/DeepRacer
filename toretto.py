import math

def reward_function_center(params,reward):
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']

    # Calculate 3 markers that are at varying distances away from the center line
    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    if distance_from_center <= marker_1:
        reward = 1.0
    elif distance_from_center <= marker_2:
        reward = 0.5
    elif distance_from_center <= marker_3:
        reward = 0.1
    else:
        reward = 1e-3  # likely crashed/ close to off track

    return float(reward)

import math

#def reward_function_waypoint_direction(params,reward):
#    waypoints = params['waypoints']
#    closest_waypoints = params['closest_waypoints']
#    heading = params['heading']
#
#
#    next_point = waypoints[closest_waypoints[1]]
#    prev_point = waypoints[closest_waypoints[0]]
#
#    # Calculate the direction in radius, arctan2(dy, dx), the result is (-pi, pi) in radians
#    track_direction = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
#    # Convert to degree
#    track_direction = math.degrees(track_direction)
#
#    # Calculate the difference between the track direction and the heading direction of the car
#    direction_diff = abs(track_direction - heading)
#    if direction_diff > 180:
#        direction_diff = 360 - direction_diff
#
#    # Penalize the reward if the difference is too large
#    DIRECTION_THRESHOLD = 10.0
#    if direction_diff > DIRECTION_THRESHOLD:
#        reward *= 0.5
#
#    return float(reward)

#returns a float number indicating direction difference between waypoints. Negative means a left turn.
def next_curve_direction(params):
    waypoints = params['waypoints']
    closest_waypoints = params['closest_waypoints']
    n = closest_waypoints[1] + 1
    if n >= 34: #34 seems to be the number of waypoints for this track
        n = 1

    next_point = waypoints[closest_waypoints[1]]
    prev_point = waypoints[closest_waypoints[0]]
    next2_point= waypoints[n]

    track_direction_current = math.atan2(next_point[1] - prev_point[1], next_point[0] - prev_point[0])
    track_direction_current = math.degrees(track_direction_current)

    track_direction_next = math.atan2(next2_point[1] - next_point[1], next2_point[0] - next_point[0])
    track_direction_next = math.degrees(track_direction_next)

    next_direction_diff = abs(track_direction_current - track_direction_next)

    if next_direction_diff >= 180:
        next_direction_diff - 360
    if next_direction_diff <= -180:
        next_direction_diff + 360

    return next_direction_diff


def reward_function_curve_direction_left(params,reward,next_direction_diff):
    is_left_of_center = params['is_left_of_center']
    track_width = params['track_width']
    distance_from_center = params['distance_from_center']
    #curve_sharpness = 1 - abs(next_direction_diff) / 180
    #TODO create more markers or find a way to make it so the reward scales with the curve_sharpness

    marker_1 = 0.1 * track_width
    marker_2 = 0.25 * track_width
    marker_3 = 0.5 * track_width

    if not (is_left_of_center ^ (next_direction_diff<0)):
        if distance_from_center <= marker_1:
            reward += 0.5
        elif distance_from_center <= marker_2:
            reward += 1
        elif distance_from_center <= marker_3:
            reward += 1.5
        else:
            reward = 1e-3
    else:
        reward += 0.1

    return float(reward)


def reward_function(params):
    reward=0.0
    next_direction_diff = next_curve_direction(params)
    if next_direction_diff != 0: #TODO cambiarlo para que sea de entre -5 y 5 grados
        reward = reward_function_curve_direction_left(params, reward, next_direction_diff)
    else:
        reward = reward_function_center(params,reward)


    return float(reward)
