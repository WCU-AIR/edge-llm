from controller import Robot
import ollama
import json
import math


# Robot setup
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

# Constants
TILE_SIZE = 0.20          # meters
WHEEL_RADIUS = 0.0205     # meters
MAX_SPEED = 6.28          # rad/s


# 1D World - Just a line!
robot_position = 0  # Current position on the line

# World
world_map = {
    "green": 2,    # 2 tiles forward
    "blue": -2     # 2 tiles backward
}

goal_name = "green" 
goal_position = world_map[goal_name]


# Simple motion - forward or backward
def move_one_tile(direction):
    """
    Move one tile forward or backward
    direction: "FORWARD" or "BACKWARD"
    """
    global robot_position
    
    target_rotation = TILE_SIZE / WHEEL_RADIUS
    
    left_start = left_sensor.getValue()
    right_start = right_sensor.getValue()
    
    # Set motor direction
    if direction == "FORWARD":
        left_motor.setVelocity(MAX_SPEED)
        right_motor.setVelocity(MAX_SPEED)
        robot_position += 1
    else:  # BACKWARD
        left_motor.setVelocity(-MAX_SPEED)
        right_motor.setVelocity(-MAX_SPEED)
        robot_position -= 1
    
    # Move until we've traveled one tile
    while robot.step(timestep) != -1:
        left_delta = abs(left_sensor.getValue() - left_start)
        right_delta = abs(right_sensor.getValue() - right_start)
        avg_rotation = (left_delta + right_delta) / 2.0
        
        if avg_rotation >= target_rotation:
            break
    
    # Stop
    left_motor.setVelocity(0)
    right_motor.setVelocity(0)
    
    # Stabilize
    for _ in range(10):
        robot.step(timestep)
    
    print(f"    → Moved {direction}, now at position {robot_position}")


# LLM 
def get_path_from_llm():
    """Ask LLM for a sequence of forward/backward moves"""
    
    system_prompt = """You control a robot on a 1D line (just forward and backward).

Robot state:
- Current position: an integer (0 = start)
- Goal position: an integer

Available actions:
- "F": move forward 1 tile (position increases by 1)
- "B": move backward 1 tile (position decreases by 1)

Task: Generate the SHORTEST sequence to reach the goal.

Logic:
- If goal > current: move forward (goal - current) times
- If goal < current: move backward (current - goal) times
- If goal == current: no moves needed

Output ONLY JSON with array of actions:
{"path": ["F", "F"]}
{"path": ["B", "B", "B"]}
{"path": []}

Example 1: position=0, goal=3
Answer: {"path": ["F", "F", "F"]}

Example 2: position=0, goal=-2
Answer: {"path": ["B", "B"]}

Example 3: position=2, goal=0
Answer: {"path": ["B", "B"]}"""

    user_prompt = f"""Plan the path:

Current position: {robot_position}
Goal position: {goal_position}

Distance to goal: {goal_position - robot_position}

What actions are needed?"""

    print(f"\n{'='*60}")
    print(f"LLM Planning:")
    print(f"  Current: {robot_position}")
    print(f"  Goal: {goal_position}")
    print(f"  Distance: {goal_position - robot_position}")
    
    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    try:
        content = response["message"]["content"]
        
        # Extract JSON from response - try multiple methods
        # Method 1: Look for JSON in code blocks
        if "```" in content:
            parts = content.split("```")
            for part in parts:
                if part.startswith("json"):
                    content = part[4:].strip()
                    break
                elif "{" in part:
                    content = part.strip()
                    break
        
        # Method 2: Find JSON object directly (look for {...})
        if "{" in content and "}" in content:
            start = content.index("{")
            end = content.rindex("}") + 1
            content = content[start:end]
        
        result = json.loads(content.strip())
        path = result.get("path", [])
        print(f"  LLM path: {' '.join(path) if path else 'No moves needed'}")
        return path
    except Exception as e:
        print(f"  ✗ LLM error: {e}")
        print(f"  Raw response: {response['message']['content']}")
        
        # Fallback: try to extract path manually
        content = response["message"]["content"]
        if '["B", "B"]' in content:
            print("  Manual extraction: found ['B', 'B']")
            return ["B", "B"]
        elif '["F", "F"]' in content:
            print("  Manual extraction: found ['F', 'F']")
            return ["F", "F"]
        
        return []

# Execute path
def execute_path(path):
    """Execute sequence of F/B actions"""
    
    if not path:
        print("Already at goal!")
        return
    
    for i, action in enumerate(path):
        print(f"\n[Step {i+1}/{len(path)}] Action: {action}, Position: {robot_position}")
        
        if action == "F":
            move_one_tile("FORWARD")
        elif action == "B":
            move_one_tile("BACKWARD")
        else:
            print(f"    ✗ Unknown action: {action}")

# Main
print("\n" + "="*60)
print("1D ROBOT NAVIGATION - SUPER SIMPLE")
print("="*60)
print(f"The robot is on a line and can only move forward or backward")
print(f"\nWorld:")
print(f"  Blue: position {world_map['blue']} (2 tiles backward)")
print(f"  Start: position 0")
print(f"  Green: position {world_map['green']} (2 tiles forward)")
print(f"\nMission:")
print(f"  Current position: {robot_position}")
print(f"  Goal: {goal_name} at position {goal_position}")
print("="*60)

# Stabilize
for _ in range(50):
    robot.step(timestep)

# Get path from LLM
path = get_path_from_llm()

if path is not None:
    print(f"\n{'='*60}")
    print(f"Executing {len(path)} actions...")
    print("="*60)
    
    execute_path(path)
    
    print("\n" + "="*60)
    print("MISSION RESULT")
    print("="*60)
    print(f"Final position: {robot_position}")
    print(f"Goal position: {goal_position}")
    
    if robot_position == goal_position:
        print(f"\n✓✓✓ SUCCESS! Robot reached the goal! ✓✓✓")
    else:
        diff = goal_position - robot_position
        print(f"\n✗ FAILED. Off by {diff} tiles")
    print("="*60)

# Keep robot alive
print("\nMaintaining position...")
while robot.step(timestep) != -1:
    pass