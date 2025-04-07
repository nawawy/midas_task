import openai

# Set OpenAI API key
openai.api_key = "your-openai-api-key"

# Predefined categories 
CATEGORIES = {
    "Financial Reports": ["annual report", "quarterly report", "earnings"],
    "Investor Presentations": ["presentation", "conference", "slides"],
    "Corporate Governance Documents": ["policy", "charter", "governance"],
    "Press Releases": ["announcement", "merger", "leadership"],
    "Stock Market Information": ["stock price", "dividend", "shareholder"],
    "Corporate Social Responsibility (CSR) Reports": ["sustainability", "ESG", "community"]
}

def classify_document(text: str) -> str:

    result_category = "Unknown"

    prompt = f"""
    You are a document classifier. Classify the following document into one of these categories:
    {', '.join(CATEGORIES)}

    Document:
    {text}

    Respond with only the category name, exactly as listed above.
        """.strip()

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # or "gpt-4"
            messages=[{"role": "user", "content": prompt}],
            temperature=0
        )
        result_category = response['choices'][0]['message']['content'].strip()

    except openai.error.OpenAIError as e:
        print(f"Error communicating with OpenAI API: {e}")
        # Rule-based classification using keyword matching
        for category, keywords in CATEGORIES.items():
            if any(keyword.lower() in text.lower() for keyword in keywords):
                result_category = category
                break

    return result_category
