from unittest.mock import Mock

fake_llm = Mock(return_value="Python is a programming language.")

def get_answer(question, llm):
    prompt = f"Answer this question: {question}"
    response = llm(prompt)
    return response


result = get_answer("What is Python?", fake_llm)

print(result)

