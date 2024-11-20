def prepare_text_e5(text: str, is_passage: bool = False) -> str:
    """
    intfloat/e5-large-v2 embedding model has been trained with text
    that is prefixed with "query: " for queries and "passage: " for passages.

    See https://huggingface.co/intfloat/e5-large-v2
    """
    prefix = "passage: " if is_passage else "query: "
    return prefix + text
