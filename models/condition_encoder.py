
import torch
import torch.nn as nn


class ConditionEncoder(nn.Module):
    """Encodes assay conditions and fuses them with the interaction fingerprint.
    Modes: 'off' (no-op, reproduces baseline), 'concat', 'film'."""

    def __init__(self, feat_dim, num_std, num_assay, mode='off',
                 emb_dim=32, cond_hidden=64, dropout=0.1):
        super().__init__()
        assert mode in ('off', 'concat', 'film'), f"bad mode: {mode}"
        self.mode = mode
        self.feat_dim = feat_dim
        if mode == 'off':
            return
        self.emb_std = nn.Embedding(num_std, emb_dim)
        self.emb_assay = nn.Embedding(num_assay, emb_dim)
        self.cond_mlp = nn.Sequential(
            nn.Linear(emb_dim * 2, cond_hidden), nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(cond_hidden, cond_hidden), nn.ReLU())
        if mode == 'concat':
            self.fuse = nn.Sequential(
                nn.Linear(feat_dim + cond_hidden, feat_dim), nn.ReLU(),
                nn.LayerNorm(feat_dim))
        elif mode == 'film':
            self.to_gamma = nn.Linear(cond_hidden, feat_dim)
            self.to_beta = nn.Linear(cond_hidden, feat_dim)
            nn.init.zeros_(self.to_gamma.weight); nn.init.zeros_(self.to_gamma.bias)
            nn.init.zeros_(self.to_beta.weight); nn.init.zeros_(self.to_beta.bias)

    def reset_parameters(self):
        if self.mode == 'off':
            return
        self.emb_std.reset_parameters(); self.emb_assay.reset_parameters()
        for m in self.cond_mlp:
            if hasattr(m, 'reset_parameters'): m.reset_parameters()
        if self.mode == 'concat':
            for m in self.fuse:
                if hasattr(m, 'reset_parameters'): m.reset_parameters()
        elif self.mode == 'film':
            nn.init.zeros_(self.to_gamma.weight); nn.init.zeros_(self.to_gamma.bias)
            nn.init.zeros_(self.to_beta.weight); nn.init.zeros_(self.to_beta.bias)

    def forward(self, feat, cond_std, cond_assay):
        if self.mode == 'off':
            return feat
        e = torch.cat([self.emb_std(cond_std), self.emb_assay(cond_assay)], dim=-1)
        c = self.cond_mlp(e)
        if self.mode == 'concat':
            return self.fuse(torch.cat([feat, c], dim=-1))
        gamma = 1.0 + self.to_gamma(c)
        beta = self.to_beta(c)
        return gamma * feat + beta
