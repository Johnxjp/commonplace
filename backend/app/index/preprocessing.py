"""
Text preprocessing

My content is going to be either:

1. Annotations from a book. I'd say that the average annotation
is probably a paragraph long which is at most 2-3 sentences. I could
probably embed the whole thing without chunking. There's a risk if breaking
down to lose semantic meaning and valuable info in that case.

The most convenient but less optimal could be just sentence.

Having chunks of like 2-3 sentences could probably work well.
"""

import nltk
nltk.download("punkt")


def multisentence_tokeniser(
    text: str,
    max_sentences: int = 3,
    group_overlap: int = 1,
    min_characters: int = 20,
) -> list[str]:
    """
    Chunks a piece of text into sentences or cluster of sentences.

    Need to clean up any short or non-informative chunks created. Ignore
    anything with no words or numbers. If shorter than X then combine with
    previous.

    Args:
    - text (str): The input text to be tokenized.
    - max_sentences (int): Number of sentences per group. Must be positive.
    - group_overlap (int): Number of sentences to overlap between groups.
    Must be non-negative and less than ngroup.
    - min_characters (int): Minimum number of characters in a chunk.

    Returns:
    List[str]: List of sentence groups.
    """
    if max_sentences < 0:
        raise ValueError("Group size must be positive.")
    if group_overlap < 0 or group_overlap >= max_sentences:
        raise ValueError(
            "Overlap must be non-negative and less than the group size."
        )

    if not text:
        return []

    sentences = nltk.sent_tokenize(text)
    sentences = _combine_short_strings(sentences, min_characters)
    idx = 0
    new_sentences = []
    while idx < len(sentences):
        grouped = sentences[idx : idx + max_sentences]
        new_sentences.append(" ".join(grouped))
        idx += max_sentences - group_overlap

    return new_sentences


def _combine_short_strings(strings: list[str], min_length: int) -> list[str]:
    """
    Combines adjacent strings in a list if current string is shorter than
    min_length.
    Continues combining until the resulting string meets the minimum length or
    no more strings are available.

    Args:
        strings (list): List of strings to process
        min_length (int): Minimum length threshold for combining strings

    Returns:
        list: New list with appropriate strings combined
    """
    result = []
    i = 0

    while i < len(strings):
        current = strings[i]

        # Keep combining strings while current is too short and there are
        # more strings
        while len(current) < min_length and i + 1 < len(strings):
            current = f"{current} {strings[i + 1]}"
            i += 1

        # Last string is too short, combine with previous
        if (
            i + 1 >= len(strings)
            and len(current) < min_length
            and len(result) > 0
        ):
            result[-1] = result[-1] + " " + current
        else:
            result.append(current)
        i += 1

    return result
