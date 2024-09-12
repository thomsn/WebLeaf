import torch
from torch.nn.functional import cosine_similarity


class Leaf(torch.Tensor):
    """
    The Leaf class is a custom subclass of PyTorch's torch.Tensor, designed to represent an HTML element
    with an associated feature embedding. It includes additional methods to calculate similarity and distance
    between elements, as well as a boolean check for the existence of the tensor.

    Methods:
    --------
    similarity(other):
        Calculates the cosine similarity between this Leaf object and another.

    mdist(other):
        Calculates the Manhattan distance (L1 distance) between this Leaf object and another.

    __bool__():
        Returns whether the Leaf tensor is non-empty (contains elements).
    """
    def similarity(self, other):
        """
        Computes the cosine similarity between the current Leaf tensor and another Leaf tensor.

        Cosine similarity measures the cosine of the angle between two vectors, giving a value between -1 and 1,
        where 1 indicates perfect similarity, 0 indicates orthogonality, and -1 indicates perfect dissimilarity.

        Parameters:
        -----------
        other : Leaf
            The other Leaf tensor to compare with.

        Returns:
        --------
        float
            A similarity score between -1 and 1, where 1 indicates high similarity.
        """
        return cosine_similarity(self.unsqueeze(0), other.unsqueeze(0)).detach().item()

    def mdist(self, other):
        """
        Computes the Manhattan distance (L1 distance) between the current Leaf tensor and another Leaf tensor.

        Manhattan distance is the sum of the absolute differences between corresponding elements of two vectors.
        It is a measure of how different two vectors are, with higher values indicating greater dissimilarity.

        Parameters:
        -----------
        other : Leaf
            The other Leaf tensor to compare with.

        Returns:
        --------
        float
            The Manhattan distance between the two tensors.
        """
        return torch.sum(torch.abs(self - other)).detach().item()

    def __bool__(self):
        """
        Checks whether the Leaf tensor is non-empty (i.e., contains elements).

        This method allows Leaf objects to be used in boolean contexts such as conditions.

        Returns:
        --------
        bool
            True if the Leaf tensor has more than zero elements, False otherwise.
        """
        return self.size().numel() > 0
