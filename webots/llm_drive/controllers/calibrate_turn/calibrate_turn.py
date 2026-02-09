from controller import Robot
import math

# ────────────────────────────────────────────────
# Robot setup
# ────────────────────────────────────────────────

robot = Robot()
timestep = int(robot.getBasicTimeStep())

# Motors
left_motor = robot.getDevice("left wheel motor")
right_motor = robot.getDevice("right wheel motor")
left_motor.setPosition(float("inf"))
right_motor.setPosition(float("inf"))
left_motor.setVelocity(0.0)
right_motor.setVelocity(0.0)

# Wheel encoders
left_sensor = robot.getDevice("left wheel sensor")
right_sensor = robot.getDevice("right wheel sensor")
left_sensor.enable(timestep)
right_sensor.enable(timestep)

# ────────────────────────────────────────────────
# Constants
# ────────────────────────────────────────────────

MAX_SPEED = 6.28
WHEEL_RADIUS = 0.0205

# Test these axle lengths
TEST_AXLE_LENGTHS1 = [.19]
TEST_AXLE_LENGTHS = [.195, .2, .205]

# ────────────────────────────────────────────────
# Calculate turn parameters
# ────────────────────────────────────────────────

def calculate_turn_params(axle_length, degrees):
    """Calculate wheel rotation needed for a turn"""
    angle_radians = math.radians(degrees)
    arc_length = angle_radians * axle_length
    wheel_rotation = arc_length / WHEEL_RADIUS
    return wheel_rotation, arc_length

# ────────────────────────────────────────────────
# Test 360-degree turn
# ────────────────────────────────────────────────

def test_full_rotation(axle_length):
    """Turn 360 degrees and measure accuracy"""
    
    target_rotation, arc_length = calculate_turn_params(axle_length, 360)
    
    print(f"\n{'='*60}")
    print(f"Testing AXLE_LENGTH = {axle_length:.4f} m")
    print(f"Target rotation: {target_rotation:.4f} rad for 360 degrees")
    
    # Stabilize
    for _ in range(20):
        robot.step(timestep)
    
    left_start = left_sensor.getValue()
    right_start = right_sensor.getValue()
    
    # Turn right (clockwise) 360 degrees
    left_motor.setVelocity(MAX_SPEED)
    right_motor.setVelocity(-MAX_SPEED)
    
    while robot.step(timestep) != -1:
        left_delta = abs(left_sensor.getValue() - left_start)
        right_delta = abs(right_sensor.getValue() - right_start)
        avg_rotation = (left_delta + right_delta) / 2.0
        
        if avg_rotation >= target_rotation:
            break
    
    # Stop
    left_motor.setVelocity(0)
    right_motor.setVelocity(0)
    
    # Measure actual rotation
    left_actual = abs(left_sensor.getValue() - left_start)
    right_actual = abs(right_sensor.getValue() - right_start)
    avg_actual = (left_actual + right_actual) / 2.0
    
    # Calculate actual angle
    actual_arc = avg_actual * WHEEL_RADIUS
    actual_angle = math.degrees(actual_arc / axle_length)
    error = abs(360 - actual_angle)
    
    print(f"Actual angle: {actual_angle:.1f}° (error: {error:.1f}°)")
    
    # Stabilize
    for _ in range(50):
        robot.step(timestep)
    
    return error, actual_angle

# ────────────────────────────────────────────────
# Test four 90-degree turns
# ────────────────────────────────────────────────

def test_90_degree_turns(axle_length):
    """Test four 90-degree turns"""
    
    target_rotation, _ = calculate_turn_params(axle_length, 90)
    
    print(f"Testing 4x 90° turns...")
    
    angles = []
    
    for i in range(4):
        # Stabilize
        for _ in range(20):
            robot.step(timestep)
        
        left_start = left_sensor.getValue()
        right_start = right_sensor.getValue()
        
        # Turn right 90°
        left_motor.setVelocity(MAX_SPEED)
        right_motor.setVelocity(-MAX_SPEED)
        
        while robot.step(timestep) != -1:
            left_delta = abs(left_sensor.getValue() - left_start)
            right_delta = abs(right_sensor.getValue() - right_start)
            avg_rotation = (left_delta + right_delta) / 2.0
            
            if avg_rotation >= target_rotation:
                break
        
        # Stop
        left_motor.setVelocity(0)
        right_motor.setVelocity(0)
        
        # Measure
        left_actual = abs(left_sensor.getValue() - left_start)
        right_actual = abs(right_sensor.getValue() - right_start)
        avg_actual = (left_actual + right_actual) / 2.0
        
        actual_arc = avg_actual * WHEEL_RADIUS
        actual_angle = math.degrees(actual_arc / axle_length)
        angles.append(actual_angle)
        
        print(f"  Turn {i+1}: {actual_angle:.1f}°")
    
    total_angle = sum(angles)
    avg_angle = total_angle / 4
    error = abs(360 - total_angle)
    
    print(f"Total: {total_angle:.1f}° (error: {error:.1f}°)")
    
    for _ in range(50):
        robot.step(timestep)
    
    return error, avg_angle

# ────────────────────────────────────────────────
# Main calibration - STARTS AUTOMATICALLY
# ────────────────────────────────────────────────

print("\n" + "="*60)
print("E-PUCK AXLE LENGTH CALIBRATION - AUTO START")
print("="*60)
print(f"Wheel radius: {WHEEL_RADIUS} m")
print(f"Max speed: {MAX_SPEED} rad/s")
print(f"Testing {len(TEST_AXLE_LENGTHS)} different axle lengths...")
print("="*60)

# Wait a moment for simulation to stabilize
for _ in range(100):
    robot.step(timestep)

results = []

for axle_length in TEST_AXLE_LENGTHS:
    # Test 360° turn
    error_360, actual_360 = test_full_rotation(axle_length)
    
    # Wait between tests
    for _ in range(100):
        robot.step(timestep)
    
    # Test 4x 90° turns
    error_90s, avg_90 = test_90_degree_turns(axle_length)
    
    # Combined error
    total_error = error_360 + error_90s
    
    results.append({
        'axle': axle_length,
        'error_360': error_360,
        'error_90s': error_90s,
        'total_error': total_error,
        'actual_360': actual_360,
        'avg_90': avg_90
    })
    
    print(f"Total error: {total_error:.1f}°\n")
    
    # Wait before next test
    for _ in range(200):
        robot.step(timestep)

# ────────────────────────────────────────────────
# Final results
# ────────────────────────────────────────────────

print("\n" + "="*60)
print("CALIBRATION COMPLETE - RESULTS")
print("="*60)
print(f"{'Axle (m)':<12} {'360° Err':<12} {'4x90° Err':<12} {'Total Err':<12}")
print("-"*60)

best = min(results, key=lambda x: x['total_error'])

for r in results:
    marker = " ← BEST" if r == best else ""
    print(f"{r['axle']:<12.4f} {r['error_360']:<12.1f} {r['error_90s']:<12.1f} {r['total_error']:<12.1f}{marker}")

print("="*60)
print(f"\n*** USE THIS VALUE IN YOUR CONTROLLER ***")
print(f"AXLE_LENGTH = {best['axle']:.4f}")
print(f"*** COPY THIS LINE EXACTLY ***\n")

# Calculate 90° turn parameters
target_90, arc_90 = calculate_turn_params(best['axle'], 90)
time_90 = target_90 / MAX_SPEED

print(f"For 90° turns with this axle length:")
print(f"  Wheel rotation: {target_90:.4f} rad")
print(f"  Arc length: {arc_90:.4f} m")
print(f"  Time: {time_90:.3f} seconds")
print(f"\nIf you want time-based instead of encoder-based:")
print(f"  TURN_90_DURATION = {time_90:.3f}")
print("="*60)

print("\nCalibration done! Robot stopping.")

# Stop the robot after calibration
left_motor.setVelocity(0)
right_motor.setVelocity(0)

# Keep running so results stay visible
while robot.step(timestep) != -1:
    pass