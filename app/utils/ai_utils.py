import random

EASY_QUESTIONS = [
    "What is JSX in React?",
    "Explain difference between var, let, and const in JS."
]
MEDIUM_QUESTIONS = [
    "How does useEffect work in React?",
    "Explain how Node.js handles async operations."
]
HARD_QUESTIONS = [
    "How would you optimize performance in a React app?",
    "Explain the event loop in depth with Node.js."
]

def generate_question(index: int):
    if index < 2:
        difficulty = "Easy"
        question = random.choice(EASY_QUESTIONS)
    elif index < 4:
        difficulty = "Medium"
        question = random.choice(MEDIUM_QUESTIONS)
    else:
        difficulty = "Hard"
        question = random.choice(HARD_QUESTIONS)
    return {"question": question, "difficulty": difficulty}

def evaluate_answer(answer: str, difficulty: str):
    if not answer:
        return 0
    base = {"Easy": 10, "Medium": 20, "Hard": 30}[difficulty]
    return random.randint(base - 5, base)
