import numpy as np
import pytest

from app.recommendation.ranking.din import DIN, HAS_TORCH


@pytest.mark.skipif(HAS_TORCH, reason="torch available, test numpy fallback")
def test_din_numpy_forward():
    model = DIN(num_products=200, embed_dim=8, hidden_dims=[32, 16], max_seq_len=20)
    batch_size = 4
    behavior_seq = np.random.randint(0, 200, (batch_size, 20))
    seq_lengths = np.array([10, 15, 5, 20])
    candidate = np.random.randint(0, 200, (batch_size,))

    output = model.predict(behavior_seq, seq_lengths, candidate)
    assert output.shape == (batch_size, 1)
    assert (output >= 0).all() and (output <= 1).all()


@pytest.mark.skipif(HAS_TORCH, reason="torch available, test numpy fallback")
def test_din_numpy_different_inputs():
    model = DIN(num_products=50, embed_dim=4, hidden_dims=[16], max_seq_len=5)
    seq = np.random.randint(0, 50, (2, 5))
    lengths = np.array([3, 5])
    cand = np.random.randint(0, 50, (2,))

    out = model.predict(seq, lengths, cand)
    assert out.shape == (2, 1)
    assert (out >= 0).all() and (out <= 1).all()


@pytest.mark.skipif(not HAS_TORCH, reason="torch not available")
def test_din_torch_forward():
    import torch
    model = DIN(num_products=200, embed_dim=8, hidden_dims=[32, 16], max_seq_len=20)
    batch_size = 4
    behavior_seq = torch.randint(0, 200, (batch_size, 20))
    seq_lengths = torch.tensor([10, 15, 5, 20])
    candidate = torch.randint(0, 200, (batch_size,))

    output = model(behavior_seq, seq_lengths, candidate)
    assert output.shape == (batch_size, 1)
    assert (output >= 0).all() and (output <= 1).all()


@pytest.mark.skipif(not HAS_TORCH, reason="torch not available")
def test_din_torch_backward():
    import torch
    model = DIN(num_products=50, embed_dim=4, hidden_dims=[16], max_seq_len=5)
    seq = torch.randint(0, 50, (2, 5))
    lengths = torch.tensor([3, 5])
    cand = torch.randint(0, 50, (2,))
    labels = torch.tensor([[1.0], [0.0]])

    out = model(seq, lengths, cand)
    loss = torch.nn.BCELoss()(out, labels)
    loss.backward()
    assert any(p.grad is not None for p in model.parameters())
