import numpy as np
import pytest

from app.recommendation.ranking.deepfm import DeepFM, HAS_TORCH
from app.recommendation.ranking.features import FeatureEncoder


def test_feature_encoder():
    encoder = FeatureEncoder(
        sparse_dims={"user_id": 100, "product_id": 200, "category_id": 20},
        dense_count=5,
    )
    sparse = {"user_id": 1, "product_id": 50, "category_id": 3}
    dense = [0.5, 0.3, 10.0, 0.8, 1.0]
    result = encoder.encode(sparse, dense)
    assert "sparse_indices" in result
    assert "dense_values" in result
    assert len(result["sparse_indices"]) == 3
    assert len(result["dense_values"]) == 5


@pytest.mark.skipif(HAS_TORCH, reason="torch available, test numpy fallback")
def test_deepfm_numpy_forward():
    model = DeepFM(
        sparse_field_dims=[100, 200, 20],
        embed_dim=8,
        dense_dim=5,
        hidden_dims=[64, 32],
    )
    batch_size = 4
    sparse_input = np.array([[1, 50, 3], [2, 60, 5], [3, 70, 1], [4, 80, 2]])
    dense_input = np.random.randn(batch_size, 5).astype(np.float32)
    output = model.predict(sparse_input, dense_input)
    assert output.shape == (batch_size, 1)
    assert (output >= 0).all() and (output <= 1).all()


@pytest.mark.skipif(not HAS_TORCH, reason="torch not available")
def test_deepfm_torch_forward():
    import torch
    model = DeepFM(
        sparse_field_dims=[100, 200, 20],
        embed_dim=8,
        dense_dim=5,
        hidden_dims=[64, 32],
    )
    batch_size = 4
    sparse_input = torch.tensor([[1, 50, 3], [2, 60, 5], [3, 70, 1], [4, 80, 2]])
    dense_input = torch.randn(batch_size, 5)
    output = model(sparse_input, dense_input)
    assert output.shape == (batch_size, 1)
    assert (output >= 0).all() and (output <= 1).all()


@pytest.mark.skipif(not HAS_TORCH, reason="torch not available")
def test_deepfm_torch_backward():
    import torch
    model = DeepFM(sparse_field_dims=[10, 20], embed_dim=4, dense_dim=2, hidden_dims=[16])
    sparse = torch.tensor([[1, 5], [2, 10]])
    dense = torch.randn(2, 2)
    labels = torch.tensor([[1.0], [0.0]])

    output = model(sparse, dense)
    loss = torch.nn.BCELoss()(output, labels)
    loss.backward()

    has_grad = any(p.grad is not None for p in model.parameters())
    assert has_grad
