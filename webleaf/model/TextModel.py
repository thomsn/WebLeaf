from sentence_transformers import SentenceTransformer
import nltk
from nltk.tokenize import sent_tokenize

# The dimensionality of the text embeddings produced by the model
TEXT_DIMS = 384

class TextEmbeddingModel:
    """
    A class to handle text embeddings for sentences using a pre-trained transformer model.

    This class uses the SentenceTransformer model from the HuggingFace 'sentence-transformers/multi-qa-MiniLM-L6-cos-v1'
    to encode text into dense embeddings. The embeddings are designed to capture the semantic meaning of the text.

    Attributes:
    -----------
    model : SentenceTransformer
        The pre-trained SentenceTransformer model used to generate text embeddings.

    Methods:
    --------
    get_text_embeddings(text):
        Generates embeddings for the input text data.
    """
    def __init__(self):
        """
        Initializes the TextEmbeddingModel by downloading necessary NLTK data and loading the pre-trained model.

        NLTK's 'punkt' tokenizer is downloaded to tokenize input text into sentences, and the SentenceTransformer model
        'multi-qa-MiniLM-L6-cos-v1' is loaded to generate embeddings.
        """
        for resource in ["punkt", "punkt_tab"]:
            nltk.download(resource)
        self.model = SentenceTransformer('sentence-transformers/multi-qa-MiniLM-L6-cos-v1')

    def get_text_embeddings(self, text):
        """
        Generates embeddings for a list of text strings. Each text string is tokenized into its first sentence,
        and that sentence is encoded into a dense embedding using the pre-trained SentenceTransformer model.

        Parameters:
        -----------
        text : list of str
            A list of text strings for which embeddings are to be generated.

        Returns:
        --------
        numpy.ndarray
            A 2D array of embeddings where each row represents the embedding of a sentence from the input text.
        """
        sentences = []
        for t in text:
            sentence = sent_tokenize(t)
            if sentence:
                sentences.append(sentence[0])
            else:
                sentences.append("")
        return self.model.encode(sentences)
