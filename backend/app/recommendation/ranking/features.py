from typing import Dict, List


class FeatureEncoder:
    def __init__(self, sparse_dims: Dict[str, int], dense_count: int):
        self.sparse_fields = list(sparse_dims.keys())
        self.sparse_dims = sparse_dims
        self.dense_count = dense_count

    def encode(self, sparse: Dict[str, int], dense: List[float]) -> dict:
        sparse_indices = [sparse[field] for field in self.sparse_fields]
        return {
            "sparse_indices": sparse_indices,
            "dense_values": dense,
        }
