from unittest.mock import Mock

llm = Mock()

llm.return_value = "fake ai answer"  # Assignment

response = llm("what is python?")

print(response)


