import random

# 색깔별 오브젝트 타입
OBJECT_TYPES = {
    "red": "box",
    "blue": "can",
    "yellow": "bottle",
    "green": "box",
}

# 다양한 instruction 템플릿
INSTRUCTION_TEMPLATES = [
    "pick up the {color} trash and place it on the {color} pad",
    "grab the {color} {object} and put it on the {color} pad",
    "collect the {color} {object} and move it to the {color} area",
    "place the {color} {object} onto the {color} pad",
    "sort the {color} {object} into the {color} zone",
    "clean up the {color} {object} by placing it on the {color} pad",
]

def get_instruction(color, randomize=True):
    """
    Returns a language instruction for the given color.
    If randomize=True, randomly selects from templates.
    """
    obj = OBJECT_TYPES.get(color, "object")
    if randomize:
        template = random.choice(INSTRUCTION_TEMPLATES)
    else:
        template = INSTRUCTION_TEMPLATES[0]
    return template.format(color=color, object=obj)

if __name__ == "__main__":
    # Test
    print("=== Diverse Instruction Examples ===")
    for color in ["red", "blue", "yellow", "green"]:
        for _ in range(3):
            print(f"[{color}] {get_instruction(color)}")
        print()
