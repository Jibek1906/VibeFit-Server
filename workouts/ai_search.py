import logging
from django.conf import settings
import openai

logger = logging.getLogger(__name__)

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)

def optimize_query(query, user_details=None):
    user_goal = user_details.goal if user_details else "general fitness"
    training_level = user_details.training_level if user_details else "beginner"

    prompt = (
        f"You're helping improve search queries for YouTube workout videos.\n"
        f"Original user input: '{query}'.\n"
        f"User goal: '{user_goal}', training level: '{training_level}'.\n"
        f"Generate a highly effective YouTube search query (in English) tailored to these preferences. "
        f"Don't use quotes or special symbols — just plain text suitable for YouTube search box."
    )

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=50,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        logger.error(f"AI query optimization failed: {e}")
        return f"{query} workout {training_level} {user_goal}"