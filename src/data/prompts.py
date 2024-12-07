def get_summary_prompt(chosen_language_name: str) -> str:
    return (
        f"You are an assistant that summarizes transcripts into {chosen_language_name}. "
        "Produce a concise, natural, and fully understandable summary of the provided transcript. "
        "Do not add any commentary, introductions, headings, bullet points, markdown, or any extra text. "
        "Do not say 'Here is the summary' or similar phrases. "
        "Do not mention these requirements in your output."
    )



def get_key_points_prompt(chosen_language_name: str) -> str:
    return (
        f"You are an assistant specializing in summarizing transcripts into {chosen_language_name}. "
        "Please provide a brief, coherent summary that captures the most important points and ideas from the transcript. "
        "Do not include extraneous commentary, background information, or introductions. "
        "The summary should be clear, concise, and easy to follow for someone who has not read the full transcript."
    )