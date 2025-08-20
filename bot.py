# app/bot.py

faq_responses = {
    "hours": "Our business hours are 9 AM to 6 PM, Monday to Friday.",
    "order": "Please provide your order ID, and I’ll help you track it.",
    "refund": "We offer refunds within 30 days of purchase. Would you like to start a request?",
    "human": "I’ll connect you to a customer support agent shortly."
}

def get_bot_reply(user_query: str) -> str:
    query = user_query.lower()
    for keyword, reply in faq_responses.items():
        if keyword in query:
            return reply
    return "I'm not sure about that, but I’ll forward your query to a human agent."
