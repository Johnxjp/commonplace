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
    text: str, n_overlap: int = 0, ngroup: int = 3
) -> list[str]:
    """
    Chunks a piece of text into sentences or cluster of sentences.

    Args:
    text (str): The input text to be tokenized.
    n_overlap (int): Number of sentences to overlap between groups. Must be non-negative and less than ngroup.
    ngroup (int): Number of sentences per group. Must be positive.

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
    idx = 0
    new_sentences = []
    while idx < len(sentences):
        grouped = sentences[idx : idx + ngroup]
        new_sentences.append(" ".join(grouped))
        idx += ngroup - n_overlap

    return new_sentences
