import os
import json
import requests
from dotenv import load_dotenv
from groq import Groq

load_dotenv()

groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

MODEL = "llama-3.3-70b-versatile"


def fetch_tech_news(query: str = "artificial intelligence India") -> list[dict]:
    url = "https://newsapi.org/v2/everything"

    params = {
        "q": query,
        "language": "en",
        "pageSize": 5,
        "sortBy": "publishedAt",
        "apiKey": NEWS_API_KEY,
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()

        data = response.json()
        articles = data.get("articles", [])

        cleaned_articles = []

        for article in articles:
            cleaned_articles.append(
                {
                    "title": article.get("title", "No title"),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "description": article.get("description", "No description"),
                    "url": article.get("url", ""),
                }
            )

        return cleaned_articles

    except Exception as e:
        print(f"News fetch error: {e}")
        return []


def summarize_news(articles: list[dict]) -> str:
    if not articles:
        return "No articles available for summarization."

    articles_text = json.dumps(articles, indent=2)

    prompt = f"""
Here are {len(articles)} recent AI news articles from India:

{articles_text}

Please provide:
1. A 3-sentence summary.
2. The most important development and why it matters.
3. How this impacts AI job opportunities in India.
"""

    try:
        response = groq_client.chat.completions.create(
            model=MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an AI industry analyst specializing in the Indian technology ecosystem."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            max_tokens=800,
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"Summarization error: {e}"


def save_results(articles: list[dict], summary: str):
    output = {
        "articles": articles,
        "summary": summary,
    }

    with open("news_summary.json", "w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)


def main():
    print("Fetching latest AI news...\n")

    articles = fetch_tech_news(
        "artificial intelligence India 2026"
    )

    if not articles:
        print("Unable to fetch news. Check your NEWS_API_KEY.")
        return

    print(f"Found {len(articles)} articles.\n")
    print("Generating AI summary...\n")

    summary = summarize_news(articles)

    print("=" * 60)
    print("AI NEWS SUMMARY")
    print("=" * 60)
    print(summary)

    save_results(articles, summary)

    print("\nResults saved to news_summary.json")


if __name__ == "__main__":
    main()