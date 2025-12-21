from __future__ import annotations

import torch
import torch.nn as nn


class PositionalEncoding(nn.Module):
    def __init__(self, d_model: int, max_len: int = 5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-torch.log(torch.tensor(10000.0)) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        pe = pe.unsqueeze(0)
        self.register_buffer("pe", pe)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (batch, seq_len, d_model)
        seq_len = x.size(1)
        return x + self.pe[:, :seq_len]


class TemporalAttention(nn.Module):
    def __init__(self, hidden_dim: int):
        super().__init__()
        self.attention = nn.MultiheadAttention(hidden_dim, num_heads=4, batch_first=True)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        seq_len = x.size(1)
        mask = torch.triu(torch.ones(seq_len, seq_len, device=x.device), diagonal=1).bool()
        attended, _ = self.attention(x, x, x, attn_mask=mask)
        return attended


class TokenMovementTransformer(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.num_features = config.get("num_features", 16)
        self.hidden_dim = config.get("hidden_dim", 256)
        self.num_heads = config.get("num_heads", 4)
        self.num_layers = config.get("num_layers", 4)
        self.dropout = config.get("dropout", 0.1)
        self.max_seq_len = config.get("max_seq_len", 256)
        self.num_addresses = config.get("num_addresses", 1000)

        self.feature_embedding = nn.Linear(self.num_features, self.hidden_dim)
        self.positional_encoding = PositionalEncoding(self.hidden_dim, self.max_seq_len)

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=self.hidden_dim,
            nhead=self.num_heads,
            dim_feedforward=self.hidden_dim * 4,
            dropout=self.dropout,
            batch_first=True,
        )
        self.transformer_encoder = nn.TransformerEncoder(encoder_layer, num_layers=self.num_layers)
        self.temporal_attention = TemporalAttention(self.hidden_dim)

        self.next_amount_head = nn.Sequential(
            nn.Linear(self.hidden_dim, self.hidden_dim // 2), nn.ReLU(), nn.Dropout(self.dropout), nn.Linear(self.hidden_dim // 2, 1)
        )
        self.next_address_head = nn.Sequential(
            nn.Linear(self.hidden_dim, self.hidden_dim // 2), nn.ReLU(), nn.Dropout(self.dropout), nn.Linear(self.hidden_dim // 2, self.num_addresses)
        )
        self.next_time_head = nn.Sequential(
            nn.Linear(self.hidden_dim, self.hidden_dim // 2), nn.ReLU(), nn.Dropout(self.dropout), nn.Linear(self.hidden_dim // 2, 1)
        )

    def forward(self, x: torch.Tensor, attention_mask: torch.Tensor | None = None):
        embedded = self.feature_embedding(x)
        embedded = self.positional_encoding(embedded)
        transformer_out = self.transformer_encoder(embedded, src_key_padding_mask=attention_mask)
        temporal_weighted = self.temporal_attention(transformer_out)
        context_vector = torch.mean(temporal_weighted, dim=1)
        amount_pred = self.next_amount_head(context_vector)
        address_pred = self.next_address_head(context_vector)
        time_pred = self.next_time_head(context_vector)
        return {"amount": amount_pred, "address": address_pred, "time": time_pred}
