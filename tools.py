def favorite_food(person: str):
    foods = {
        'michelle': 'noodles',
        'james': 'pizza',
        'paul': 'sushi'
    }
    return foods.get(person.lower(), "I don't know.")

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

STOPWORDS = {"the", "a", "an", "what", "which", "table", "has", "have", "with",}

def search_docs(query: str):
    words = [word for word in query.lower().split() if word not in STOPWORDS]
    results = []
    for doc in DOCS:
        searchable_text = f'{doc['name']} {doc['description']}'.lower()
        if any(word in searchable_text for word in words):
            results.append(doc)
    return results