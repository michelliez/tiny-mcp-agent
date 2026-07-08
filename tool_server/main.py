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
def get_table_info(table_name: str) -> dict:
    """Return metadata about a mock hospital table"""
    tables = {
        "encounters": {
            "table": "encounters",
            "primary_key": "encounter_id",
            "description": "Contains admission, discharge, department, and encounter date information.",
        },
        "diagnoses": {
            "table": "diagnoses",
            "primary_key": "diagnosis_id",
            "description": "Contains diagnosis codes and diagnosis descriptions.",
        },
        "departments": {
            "table": "departments",
            "primary_key": "department_id",
            "description": "Contains department names and department metadata.",
        },
    }
    return tables.get(
        table_name.lower(),
        {
            "error": f"Unknown table: {table_name}"
        }
    )

def favorite_food(person: str) -> str:
    foods = {
        'michelle': 'noodles',
        'james': 'pizza',
        'paul': 'sushi'
    }
    return foods.get(person.lower(), "I don't know.")

if __name__ == '__main__':
    mcp.run(transport='http', host='127.0.0.1', port=8001)

