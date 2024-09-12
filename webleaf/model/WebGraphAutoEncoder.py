from torch_geometric.nn import GAE, GCN2Conv
import torch.nn.functional as F
from .TagModel import TagEmbeddingModel, html_tags, TAG_DIMS
from .TextModel import TextEmbeddingModel, TEXT_DIMS
from torch_geometric.utils import subgraph
from torch.nn import Linear
import os
from lxml import etree
from pathlib import Path
import torch
import re

MODEL_PATH = os.path.join(Path(__file__).parent.absolute(), f"product_page_model_4_80.torch")
EMBEDDING_DIMENSIONS = 32

tag_embedding_model = None
text_embedding_model = None


class GCNEncoder(torch.nn.Module):
    def __init__(self, input_channels, hidden_channels, output_channels, num_layers, alpha, theta, shared_weights=True, dropout=0.0):
        super().__init__()

        self.lins = torch.nn.ModuleList()
        self.lins.append(Linear(input_channels, hidden_channels))
        self.lins.append(Linear(hidden_channels, output_channels))

        self.convs = torch.nn.ModuleList()
        for layer in range(num_layers):
            self.convs.append(
                GCN2Conv(hidden_channels, alpha, theta, layer + 1,
                         shared_weights, normalize=False))

        self.dropout = dropout

    def forward(self, x, edge_index):
        x = F.dropout(x, self.dropout, training=self.training)
        x = x_0 = self.lins[0](x).relu()

        for conv in self.convs:
            x = F.dropout(x, self.dropout, training=self.training)
            x = conv(x, x_0, edge_index)
            x = x.relu()

        x = F.dropout(x, self.dropout, training=self.training)
        x = self.lins[1](x)

        return x


class WebGraphAutoEncoder:
    def __init__(self):
        global tag_embedding_model
        if not tag_embedding_model:
            tag_embedding_model = TagEmbeddingModel()

        global text_embedding_model
        if not text_embedding_model:
            text_embedding_model = TextEmbeddingModel()

        num_features = TAG_DIMS + TEXT_DIMS
        hidden = 128
        out_channels = EMBEDDING_DIMENSIONS
        encoder = GCNEncoder(input_channels=num_features, hidden_channels=hidden, output_channels=out_channels, num_layers=6, alpha=0.1, theta=0.5, shared_weights=True, dropout=0.1)
        self.model = GAE(encoder)

        assert os.path.exists(MODEL_PATH), f"Could not find WebLeaf model at [{MODEL_PATH}]"
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.load_state_dict(torch.load(MODEL_PATH, map_location=self.device))
        self.model.eval()
        self.model = self.model.to(self.device)

    def extract(self, tree):
        root = tree.getroot()

        # List of formatting tags we want to remove
        formatting_tags = ['b', 'i', 'u', 'strong', 'em', 'mark', 'small', 'del', 'ins']

        etree.strip_tags(root, *formatting_tags)

        stack = [(root, 0)]
        tag_lookup = set(html_tags)
        assert tree, "Could not create tree"

        i = 0
        texts = [""]
        tags = [root.tag]
        edge_index = []
        masks = [False]
        paths = [tree.getpath(root)]
        while stack:
            element, parent_id = stack.pop(0)

            for index, child in enumerate(element):
                if isinstance(child, etree._Comment):
                    continue

                while child.tag == "div" and len(child) == 1:
                    child = child[0]

                if child.tag in tag_lookup:
                    tags.append(child.tag)
                    text = self.extract_text(child)[:256]
                    texts.append(text)
                    masks.append(bool(text))
                    paths.append(tree.getpath(child))
                    i += 1
                    edge_index.append([parent_id, i])
                    stack.append((child, i))

        text_embeddings = text_embedding_model.get_text_embeddings(texts)
        tag_embeddings = tag_embedding_model.get_tag_embedding(tags)
        x = []
        for i in range(len(text_embeddings)):
            x.append(torch.concatenate((torch.from_numpy(text_embeddings[i]), tag_embeddings[i])))

        input_masks = torch.tensor(masks, dtype=torch.bool)
        input_features = torch.stack(x).to(self.device)
        input_edge_index = torch.tensor(edge_index, dtype=torch.int64).permute(1, 0)
        subset_edge_index, _ = subgraph(input_masks, input_edge_index)
        subset_edge_index = subset_edge_index.to(self.device)

        features = self.model.encode(input_features, edge_index=subset_edge_index)

        return features, paths

    def clean_text(self, text):
        if not text:
            return
        cleaned_text = ' '.join(re.sub(r'[^a-zA-Z\s.,!?\'\";:]', '', text).split())
        return cleaned_text

    def extract_text(self, element) -> str:
        text = self.clean_text(element.text)
        if text:
            return text

        for label in ["alt", "tite", "aria-label"]:
            text = self.clean_text(element.get(label))
            if text:
                return text
        return ""
