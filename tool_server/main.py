from fastmcp import FastMCP

mcp = FastMCP('tiny-docs')


DOCS = [
    {
        "name": "encounters",
        "description": "Contains admissions, discharges, departments, encounter dates, and encounter types.",
    },
    {
        "name": "diagnoses",
        "description": "Contains diagnosis codes, diagnosis descriptions, and encounter diagnosis information.",
    },
    {
        "name": "departments",
        "description": "Contains hospital department metadata, department names, and department IDs.",
    },
]

@mcp.tool
def search_docs(query: str) -> list[dict]:
    """Search tiny hospital documentation for relevant tables."""
    q = query.lower()
    return [
        doc for doc in DOCS if q in f"{doc['name']} {doc['description']}".lower()
    ]

@mcp.tool
def favorite_food(person: str) -> str:
    foods = {
        'michelle': 'noodles',
        'james': 'pizza',
        'paul': 'sushi'
    }
    return foods.get(person.lower(), "I don't know.")

if __name__ == '__main__':
    mcp.run(transport='http', host='127.0.0.1', port=8001)

