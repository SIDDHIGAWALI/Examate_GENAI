import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

from database import askQuestion

load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
client = genai.Client(api_key=API_KEY)

MODEL = "gemini-3.8-flash"


def rag_search(query: str):
    chunks = askQuestion(query)

    if not chunks:
        return "No relevant information was found in the knowledge base."

    return "\n\n".join(
        chunk.page_content for chunk in chunks
    )


def calculate_purchase_total(items: list):
    line_items = []
    grand_total = 0

    for item in items:
        name = item["name"]
        quantity = float(item["quantity"])
        unit_price = float(item["unit_price"])

        amount = quantity * unit_price
        grand_total += amount

        line_items.append({
            "item": name,
            "quantity": quantity,
            "unit_price": round(unit_price, 2),
            "amount": round(amount, 2)
        })

    return {
        "items": line_items,
        "grand_total": round(grand_total, 2),
        "currency": "INR"
    }


rag_search_declaration = types.FunctionDeclaration(
    name="rag_search",
    description="Search the user's uploaded documents and knowledge base. Use this when the user asks questions about information in their documents.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "query": types.Schema(
                type=types.Type.STRING,
                description="The search query to find relevant information in the knowledge base."
            )
        },
        required=["query"]
    )
)

calculator_declaration = types.FunctionDeclaration(
    name="calculate_purchase_total",
    description="Calculate the total cost of purchased goods. Use this whenever the user provides item names, quantities, and unit prices and asks for a total or bill.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "items": types.Schema(
                type=types.Type.ARRAY,
                description="The purchased items and their quantities and unit prices.",
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "name": types.Schema(
                            type=types.Type.STRING,
                            description="Name of the purchased item."
                        ),
                        "quantity": types.Schema(
                            type=types.Type.NUMBER,
                            description="Number of units purchased."
                        ),
                        "unit_price": types.Schema(
                            type=types.Type.NUMBER,
                            description="Price for one unit in Indian rupees."
                        )
                    },
                    required=["name", "quantity", "unit_price"]
                )
            )
        },
        required=["items"]
    )
)

tools = [
    types.Tool(
        function_declarations=[
            rag_search_declaration,
            calculator_declaration
        ]
    )
]

tool_registry = {
    "rag_search": rag_search,
    "calculate_purchase_total": calculate_purchase_total
}


def _call_gemini(contents, config):
    models = [MODEL, "gemini-2.0-flash", "gemini-1.5-flash"]
    for m in models:
        for attempt in range(3):
            try:
                return client.models.generate_content(
                    model=m,
                    contents=contents,
                    config=config
                )
            except Exception as e:
                err_str = str(e)
                if "503" in err_str or "UNAVAILABLE" in err_str:
                    time.sleep(2)
                    continue
                elif "404" in err_str:
                    break
                raise e
    raise RuntimeError("Gemini models currently unavailable due to high demand. Please try again.")


def findResponse(question: str):
    contents = [
        types.Content(
            role="user",
            parts=[types.Part.from_text(text=question)]
        )
    ]

    tools_used = []

    while True:
        cfg = types.GenerateContentConfig(
            tools=tools,
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
            system_instruction="""
            You are an assistant with access to two tools.

            1. rag_search:
               Use this to answer questions about the user's uploaded
               documents and knowledge base.

            2. calculate_purchase_total:
               Use this to calculate bills and totals for purchased goods.
               Use the exact quantities and unit prices provided by the user.
               Do not invent missing prices or quantities. Ask the user
               for missing information when necessary.

            Use the appropriate tool when the user's request needs it.
            If the user asks a question about documents, use rag_search
            instead of answering from general knowledge.
            If the user asks for a purchase total, use the calculator.
            You may use both tools when a request needs both.
            Explain the tool result clearly to the user.
            """
        )
        response = _call_gemini(contents, cfg)

        function_calls = response.function_calls

        if not function_calls:
            return {
                "answer": response.text or "I could not generate a response.",
                "tools_used": tools_used
            }

        contents.append(response.candidates[0].content)

        function_responses = []

        for call in function_calls:
            function = tool_registry[call.name]
            result = function(**call.args)

            tools_used.append(call.name)

            function_responses.append(
                types.Part.from_function_response(
                    name=call.name,
                    response={"result": result}
                )
            )

        contents.append(
            types.Content(
                role="tool",
                parts=function_responses
            )
        )