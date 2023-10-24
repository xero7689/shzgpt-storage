def formate_chats_to_gpt_request_messages(chats):
    """
    Formats a list of Chat object from models into a request list
    to be used for querying Open AI's Chat GPT completion API endpoint.

    Args:
        chats (list): A list of chat objects containing conversation data.

    Returns:
        list: A request list formatted to be sent to the Chat GPT completion API endpoint.
    """
    # Format Recent Chat Messages
    gpt_request_messages = []
    for message in chats:
        gpt_request_messages.append({
            "role": message.role,
            "content": message.content
        })
    return gpt_request_messages
