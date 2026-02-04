from controller import Robot
import ollama

robot = Robot()
timestep = int(robot.getBasicTimeStep())

left = robot.getDevice("left wheel motor")
right = robot.getDevice("right wheel motor")

left.setPosition(float("inf"))
right.setPosition(float("inf"))

left.setVelocity(0.0)
right.setVelocity(0.0)

SPEED = 6.0

action = "STOP"
steps_since_llm = 0
LLM_INTERVAL = 20

def query_llm():
    response = ollama.chat(
        model="qwen2.5:3b",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a robot controller.\n"
                    "Your policy:\n"
                    "- Move FORWARD by default\n"
                    "- Occasionally turn LEFT or RIGHT\n"
                    "Valid actions (one word only):\n"
                    "FORWARD, LEFT, RIGHT, BACK"
                )
            },
            {
                "role": "user",
                "content": (
                    "Continue controlling the robot.\n"
                    "Choose the next action."
                )
            }
        ]
    )
    return response["message"]["content"].strip().upper()


while robot.step(timestep) != -1:
    steps_since_llm += 1

    if steps_since_llm >= LLM_INTERVAL:
        action = query_llm()
        print("LLM action:", action)
        steps_since_llm = 0

    if action == "FORWARD":
        left.setVelocity(SPEED)
        right.setVelocity(SPEED)

    elif action == "BACK":
        left.setVelocity(-SPEED)
        right.setVelocity(-SPEED)

    elif action == "LEFT":
        left.setVelocity(-SPEED)
        right.setVelocity(SPEED)

    elif action == "RIGHT":
        left.setVelocity(SPEED)
