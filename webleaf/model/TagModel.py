import torch
import torch.nn as nn
import os
from pathlib import Path

# Define the path where tag embeddings are stored
TAG_PATH = os.path.join(Path(__file__).parent.absolute(), f"tag_embeddings.torch")
# The dimensionality of the tag embeddings
TAG_DIMS = 8

# List of HTML tags that will be embedded
html_tags = [
    'a', 'abbr', 'address', 'area', 'article', 'aside', 'audio', 'b', 'base', 'bdi', 'bdo', 'blockquote',
    'body', 'br', 'button', 'canvas', 'caption', 'cite', 'code', 'col', 'colgroup', 'data', 'datalist', 'dd',
    'del', 'details', 'dfn', 'dialog', 'div', 'dl', 'dt', 'em', 'embed', 'fieldset', 'figcaption', 'figure',
    'footer', 'form', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'head', 'header', 'hr', 'html', 'i', 'iframe', 'img',
    'input', 'ins', 'kbd', 'label', 'legend', 'li', 'link', 'main', 'map', 'mark', 'meter', 'nav', 'noscript',
    'object', 'ol', 'optgroup', 'option', 'output', 'p', 'param', 'picture', 'pre', 'progress', 'q', 'rp', 'rt', 'ruby',
    's', 'samp', 'section', 'select', 'small', 'source', 'span', 'strong', 'sub', 'summary', 'sup',
    'table', 'tbody', 'td', 'template', 'textarea', 'tfoot', 'th', 'thead', 'time', 'title', 'tr', 'track', 'u', 'ul',
    'var', 'video', 'wbr'
]


class NormalizedEmbedding(nn.Module):
    """
    A PyTorch module that creates an embedding layer and normalizes the output.

    Attributes:
    -----------
    embedding : torch.nn.Embedding
        The embedding layer that learns to map each HTML tag to a vector in a fixed-dimensional space.

    Methods:
    --------
    forward(x):
        Performs the forward pass by computing embeddings for the input and normalizing them.
    """
    def __init__(self, n_classes, m_dimensions):
        """
        Initializes the NormalizedEmbedding class.

        Parameters:
        -----------
        n_classes : int
            The number of classes (i.e., HTML tags) to embed.
        m_dimensions : int
            The number of dimensions in the embedding space.
        """
        super(NormalizedEmbedding, self).__init__()
        # Create the embedding layer
        self.embedding = nn.Embedding(n_classes, m_dimensions)

        # Initialize the embedding weights randomly
        nn.init.xavier_uniform_(self.embedding.weight)

    def forward(self, x):
        """
        Forward pass of the embedding layer with normalization.

        Parameters:
        -----------
        x : torch.Tensor
            A tensor containing indices of HTML tags to be embedded.

        Returns:
        --------
        torch.Tensor
            A tensor of normalized embeddings for the input tags.
        """
        # Get the embeddings
        embed = self.embedding(x)

        # Normalize the embeddings to have unit length
        normalized_embed = embed / embed.norm(dim=1, keepdim=True)
        return normalized_embed


class TagEmbeddingModel:
    """
    A class for managing tag embeddings for HTML tags. It loads a pre-trained embedding model and
    provides a method to retrieve embeddings for specific HTML tags.

    Attributes:
    -----------
    embedding_model : NormalizedEmbedding
        The model that handles tag embeddings and their normalization.

    Methods:
    --------
    get_tag_embedding(tags):
        Retrieves the embeddings for a list of HTML tags.
    """
    def __init__(self):
        """
         Initializes the TagEmbeddingModel class by loading a pre-trained embedding model.

         Raises:
         -------
         AssertionError if the pre-trained model cannot be found at the specified path.
         """
        self.embedding_model = NormalizedEmbedding(len(html_tags), TAG_DIMS)
        assert os.path.exists(TAG_PATH), f"Could not find tag model at [{TAG_PATH}]"
        self.embedding_model.load_state_dict(torch.load(TAG_PATH))

    def get_tag_embedding(self, tags):
        """
         Retrieves the embeddings for the provided HTML tags.

         Parameters:
         -----------
         tags : list of str
             A list of HTML tags for which to retrieve the embeddings.

         Returns:
         --------
         torch.Tensor
             A tensor containing the embeddings for the specified HTML tags.
         """
        return self.embedding_model(torch.tensor([html_tags.index(tag) for tag in tags]))
