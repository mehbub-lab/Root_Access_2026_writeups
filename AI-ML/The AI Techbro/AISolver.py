#!/usr/bin/env python3

import math
import random
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

# ---------------- Configuration ---------------- #

ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789"
INPUT_LEN = 16

TARGET = torch.tensor([-8.175837, -1.710289, -0.7002581, 5.3449903])
EPS = 2.5e-4

WEIGHTS = Path(__file__).parent / "ML" / "encoder_weights_updated.npz"

DEVICE = torch.device("cpu")

# ---------------- Model Definition ---------------- #

class SparseLinear(nn.Module):
    def __init__(self, inp, out, blk=16):
        super().__init__()
        self.weight = nn.Parameter(torch.randn(out, inp) * 0.05)
        self.bias = nn.Parameter(torch.zeros(out))
        self.register_buffer("mask", self._build_mask(inp, out, blk))

    def _build_mask(self, i, o, blk):
        if i % blk or o % blk:
            return (torch.rand(o, i) > 0.5).float()

        m = torch.zeros(o, i)
        bi, bo = i // blk, o // blk

        for r in range(bo):
            for c in (r, max(0, r - 1)):
                m[r*blk:(r+1)*blk, c*blk:(c+1)*blk] = 1.0

        return m

    def forward(self, x):
        return F.linear(x, self.weight * self.mask, self.bias)


class Encoder(nn.Module):
    def __init__(self):
        super().__init__()

        self.l1 = nn.Linear(16, 128)
        self.s2 = SparseLinear(128, 128)
        self.l3 = nn.Linear(128, 128)

        self.ga = nn.Linear(128, 128)
        self.gb = nn.Linear(128, 128)

        self.l6 = nn.Linear(128, 64)
        self.s7 = SparseLinear(64, 64, 8)

        self.l8 = nn.Linear(64, 32)
        self.l9 = nn.Linear(32, 16)
        self.out = nn.Linear(16, 4)

    def forward(self, x):
        h = torch.tanh(self.l1(x))
        h = torch.tanh(self.s2(h))
        h = torch.tanh(self.l3(h))

        a = torch.tanh(self.ga(h))
        b = torch.sigmoid(self.gb(h))
        h = a * b

        h = torch.tanh(self.l6(h))
        h = torch.tanh(self.s7(h))
        h = torch.tanh(self.l8(h))
        h = torch.tanh(self.l9(h))

        return self.out(h) * 0.8


# ---------------- Weight Loader ---------------- #

def load_model(path):
    data = np.load(path)

    net = Encoder()

    with torch.no_grad():
        for name in ["l1", "l3", "l6", "l8", "l9", "out", "ga", "gb"]:
            layer = getattr(net, name)
            layer.weight.copy_(torch.from_numpy(data[f"{name}_w"]))
            layer.bias.copy_(torch.from_numpy(data[f"{name}_b"]))

        for tag, key in [("s2", "block2"), ("s7", "block7")]:
            layer = getattr(net, tag)
            layer.weight.copy_(torch.from_numpy(data[f"{key}_w"]))
            layer.bias.copy_(torch.from_numpy(data[f"{key}_b"]))
            layer.mask.copy_(torch.from_numpy(data[f"{key}_mask"]))

    net.eval()
    for p in net.parameters():
        p.requires_grad = False

    return net.to(DEVICE)


MODEL = load_model(WEIGHTS)

# ---------------- Utilities ---------------- #

def encode_batch(strings):
    buf = torch.zeros(len(strings), INPUT_LEN)

    for i, s in enumerate(strings):
        for j, ch in enumerate(s):
            buf[i, j] = ord(ch)

    buf = (buf - 80.0) / 40.0

    with torch.no_grad():
        out = MODEL(buf)

    dist = torch.linalg.norm(out - TARGET, dim=1)

    return dist.numpy(), out.numpy()


def score(s):
    d, z = encode_batch([s])
    return float(d[0]), z[0]


def random_seed():
    return "".join(random.choice(ALPHABET) for _ in range(INPUT_LEN))


# ---------------- Optimization ---------------- #

def hill_climb(start, rounds=50):
    cur = start
    best, _ = score(cur)

    for _ in range(rounds):
        improved = False

        for pos in range(INPUT_LEN):
            trials = [
                cur[:pos] + c + cur[pos+1:]
                for c in ALPHABET
            ]

            ds, _ = encode_batch(trials)
            k = np.argmin(ds)

            if ds[k] < best:
                cur = trials[k]
                best = ds[k]
                improved = True

        if not improved or best < EPS:
            break

    return cur, best


def annealing(start, start_d, steps=100000, t_hi=0.25, t_lo=5e-5):
    cur = start
    cd = start_d

    best = cur
    bd = cd

    for i in range(steps):
        T = t_hi * (t_lo / t_hi) ** (i / steps)

        s = list(cur)
        for _ in range(random.choice([1, 1, 2, 2, 3])):
            idx = random.randrange(INPUT_LEN)
            s[idx] = random.choice(ALPHABET)

        cand = "".join(s)
        nd, _ = score(cand)

        delta = nd - cd

        if delta < 0 or random.random() < math.exp(-delta / T):
            cur = cand
            cd = nd

            if cd < bd:
                best = cur
                bd = cd

        if bd < EPS:
            break

    return best, bd


# ---------------- Driver ---------------- #

def main():
    global_best = ""
    global_dist = float("inf")

    start = time.time()

    for i in range(600):
        seed = random_seed()
        s, d = hill_climb(seed, 40)

        if d < 0.1:
            s, d = annealing(s, d, 80000)
            s, d = hill_climb(s, 40)

        if d < global_dist:
            global_best = s
            global_dist = d
            print(f"[+] {i:03d}  {global_dist:.6f}  {global_best}")

        if global_dist < EPS:
            break

    _, vec = score(global_best)

    print("\n=== Result ===")
    print("Password :", global_best)
    print("Distance :", global_dist)
    print("Vector   :", vec)
    print("Target   :", TARGET.numpy())
    print("Solved   :", global_dist < EPS)
    print("Time     :", f"{time.time() - start:.1f}s")


if __name__ == "__main__":
    main()
