"""
Code to initialise and interact with openai embedding model
"""

import numpy as np
import openai
import tiktoken


def num_tokens_from_string(
    string: str, encoding_name: str = "cl100k_base"
) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens


class OpenAIEmbedder:

    def __init__(self, api_key: str, model_name: str) -> None:
        super().__init__()
        self._client = openai.OpenAI(api_key=api_key)
        self._model_name = model_name

    def preprocess(self, text: str) -> str:
        return text.replace("\n", " ")

    def _embed_long_content(
        self, content: str, max_tokens: int, aggregation: str = "max"
    ) -> list[list[float]]:
        """
        Embeds long content by splitting it into smaller chunks and embedding
        each chunk separately then aggregating the embeddings.

        Default is average.
        """
        embeddings = []
        index = 0
        while index < len(content):
            chunk = content[index : index + max_tokens]
            data = self._client.embeddings.create(
                input=[self.preprocess(chunk)], model=self._model_name
            )
            embeddings.append(data.data[0].embedding)
            index += max_tokens

        if aggregation == "max":
            return np.max(embeddings, axis=0)

        return np.mean(embeddings, axis=0)

    def embed(
        self, content: list[str] | str, max_tokens: int = 8000
    ) -> list[list[float]]:
        if isinstance(content, str):
            content = [content]

        try:
            embeddings = []
            for c in content:
                n_tokens = num_tokens_from_string(c)
                if n_tokens > 8000:
                    embedding = self._embed_long_content(c, max_tokens)
                else:
                    data = self._client.embeddings.create(
                        input=[self.preprocess(c)], model=self._model_name
                    )
                    embedding = data.data[0].embedding
                embeddings.append(embedding)
            return embeddings
        except openai.OpenAIError as e:
            raise ValueError(f"An error occurred: {str(e)}")
