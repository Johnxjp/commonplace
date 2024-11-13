"""
Text preprocessing

My content is going to be either:

1. Annotations from a book. I'd say that the average annotation
is probably a paragraph long which is at most 2-3 sentences. I could
probably embed the whole thing without chunking. There's a risk if breaking
down to lose semantic meaning and valuable info in that case.

The most convenient but less optimal could be just sentence.

For videos will have entire transcript if whole video. Clip maybe
shorter but not sure.

Having chunks of like 2-3 sentences could probably work well.
"""

import nltk

nltk.download("punkt")


def multisentence_tokeniser(
    text: str,
    n_overlap: int = 1,
    ngroup: int = 3,
    min_chunk_size: int = 20,
    max_chunk_size: int = 10000,
) -> list[str]:
    """
    Chunks a piece of text into sentences or cluster of sentences.

    Need to clean up any short or non-informative chunks created. Ignore
    anything with no words or numbers. If shorter than X then combine with
    previous.

    TODO: Sentence tokenisation ignores complexity of a document. Luckily
    with annotations and transcripts likely to be very simple document
    formatting without tables and images.

    Args:
    text (str): The input text to be tokenized.
    n_overlap (int): Number of sentences to overlap between groups. Must be non-negative and less than ngroup.
    ngroup (int): Number of sentences per group. Must be positive.
    max_chunk_size (int): Maximum number of characters in a chunk. Limited by embedding model, max tokens
    Most are quite generous but how to handle

    Returns:
    List[str]: List of sentence groups.
    """
    if ngroup <= 0:
        raise ValueError("Group size must be positive.")
    if n_overlap < 0 or n_overlap >= ngroup:
        raise ValueError(
            "Overlap must be non-negative and less than the group size."
        )

    if not text:
        return []

    sentences = nltk.sent_tokenize(text)
    sentences = _combine_short_strings(sentences, min_chunk_size)
    idx = 0
    new_sentences = []
    while idx < len(sentences):
        grouped = sentences[idx : idx + ngroup]
        new_sentences.append(" ".join(grouped))
        idx += ngroup - n_overlap

    return new_sentences


def _combine_short_strings(strings, min_length):
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
