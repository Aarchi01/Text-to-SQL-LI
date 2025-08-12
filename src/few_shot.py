import json

def load_few_shot_examples(path="data/few_shot_examples.json"):
    with open(path, "r") as f:
        return json.load(f)
    
def format_few_shot_prompt(examples):
    prompt = ""
    for ex in examples:
        prompt += f"Q: {ex['question']}\nA: {ex['sql']}\n\n"
    return prompt

"""
this format function will convert this loaded
python list into a text block to be used in the prompt.
"""