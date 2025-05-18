"""
Collection of prompts for testing Bedrock models.
Each function returns a prompt string with the input text inserted.
"""

def get_default_summary_prompt(text: str) -> str:
    """
    Default prompt for summarizing text content.
    Generates a concise, accurate summary in 3-5 sentences.
    """
    return f"""Summarize the following text in plain English. Focus ONLY on the main idea and key points.
Write a concise summary of 2-3 short sentences. Be extremely brief and direct.
Avoid all unnecessary words, explanations, and details.

Text:
{text}

Summary:"""


# Dictionary mapping prompt names to their respective functions
# This allows for easy lookup of prompts by name in the main script
PROMPTS = {
    "default_summary": get_default_summary_prompt,
    # Add more prompts here as you create them
}
