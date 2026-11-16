"""
Preparação dos dados.

- Loader da base REAL: espera DATA_DIR/Positive e DATA_DIR/Negative (igual à base
  "Concrete Crack Images for Classification" e SDNET2018).
- Gerador SINTÉTICO (fallback): cria texturas de concreto com e sem fissura, incluindo
  SOMBRAS em alguns negativos (distratores) para possibilitar a análise de erros exigida.
- Split treino/val/teste no nível da IMAGEM, estratificado, evitando vazamento (não
  distribui recortes da mesma imagem original entre conjuntos diferentes).
"""
import random

import numpy as np
import torch
from PIL import Image
from torch.utils.data import DataLoader, Dataset
from torchvision import transforms

import config


# --------------------------------------------------------------------------- #
# Geração sintética
# --------------------------------------------------------------------------- #
def _textura_concreto(size, rng):
    base = rng.normal(150, 18, (size, size))
    base += rng.normal(0, 7, (size, size))          # granulação fina
    # algumas manchas claras/escuras (porosidade do concreto)
    for _ in range(rng.integers(4, 10)):
        cx, cy = rng.integers(0, size, 2)
        r = rng.integers(5, 25)
        yy, xx = np.ogrid[:size, :size]
        mask = (xx - cx) ** 2 + (yy - cy) ** 2 <= r * r
        base[mask] += rng.normal(0, 12)
    return np.clip(base, 55, 215)


def _adicionar_sombra(img, rng):
    """Gradiente escuro numa faixa — simula sombra/iluminação desigual (distrator)."""
    size = img.shape[0]
    grad = np.linspace(0, rng.uniform(40, 80), size)
    if rng.random() < 0.5:
        grad = grad[::-1]
    if rng.random() < 0.5:
        img = img - grad[:, None]
    else:
        img = img - grad[None, :]
    return np.clip(img, 20, 230)


def _adicionar_fissura(img, rng):
    """Desenha 1-2 fissuras: caminhada aleatória fina e escura, com ramificações."""
    size = img.shape[0]
    for _ in range(rng.integers(1, 3)):
        x, y = rng.integers(0, size), rng.integers(0, size // 4)
        ang = rng.uniform(np.pi / 4, 3 * np.pi / 4)  # tende a descer
        comprimento = rng.integers(size, size * 2)
        escuro = rng.integers(25, 65)
        largura = rng.integers(1, 3)
        for _ in range(comprimento):
            ang += rng.normal(0, 0.35)
            x += np.cos(ang)
            y += np.sin(ang)
            xi, yi = int(x), int(y)
            if not (0 <= xi < size and 0 <= yi < size):
                break
            for dx in range(-largura, largura + 1):
                for dy in range(-largura, largura + 1):
                    px, py = xi + dx, yi + dy
                    if 0 <= px < size and 0 <= py < size:
                        img[py, px] = min(img[py, px], escuro + rng.normal(0, 5))
            if rng.random() < 0.02:  # ramificação
                ang += rng.choice([-1, 1]) * rng.uniform(0.3, 0.8)
    return img


def gerar_sinteticos():
    """Gera a amostra sintética em DATA_DIR/{Positive,Negative}. Retorna contagem."""
    rng = np.random.default_rng(config.SEED)
    total = 0
    for classe in config.CLASSES:
        destino = config.DATA_DIR / classe
        destino.mkdir(parents=True, exist_ok=True)
        for i in range(config.N_POR_CLASSE):
            img = _textura_concreto(config.IMG_SIZE, rng)
            # ~35% dos negativos recebem sombra (distrator p/ análise de erro)
            if classe == "Negative" and rng.random() < 0.35:
                img = _adicionar_sombra(img, rng)
            if classe == "Positive":
                if rng.random() < 0.3:
                    img = _adicionar_sombra(img, rng)
                img = _adicionar_fissura(img, rng)
            arr = np.clip(img, 0, 255).astype(np.uint8)
            Image.fromarray(arr).convert("RGB").save(destino / f"{classe}_{i:04d}.jpg")
            total += 1
    return total


# --------------------------------------------------------------------------- #
# Dataset / splits
# --------------------------------------------------------------------------- #
def _listar_amostras():
    amostras = []
    for rotulo, classe in enumerate(config.CLASSES):
        pasta = config.DATA_DIR / classe
        for p in sorted(pasta.glob("*")):
            if p.suffix.lower() in (".jpg", ".jpeg", ".png", ".bmp"):
                amostras.append((p, rotulo))
    return amostras


def _transforms(treino):
    etapas = [transforms.Resize((config.IMG_SIZE, config.IMG_SIZE))]
    if treino:
        etapas += [transforms.RandomHorizontalFlip(), transforms.RandomVerticalFlip()]
    etapas += [
        transforms.ToTensor(),
        transforms.Normalize(config.NORM_MEAN, config.NORM_STD),
    ]
    return transforms.Compose(etapas)


class CrackDataset(Dataset):
    def __init__(self, amostras, treino=False):
        self.amostras = amostras
        self.tf = _transforms(treino)

    def __len__(self):
        return len(self.amostras)

    def __getitem__(self, i):
        caminho, rotulo = self.amostras[i]
        img = Image.open(caminho).convert("RGB")
        return self.tf(img), rotulo


def split_estratificado():
    """Divide por imagem, estratificado por classe (sem vazamento). Retorna 3 listas."""
    amostras = _listar_amostras()
    random.Random(config.SEED).shuffle(amostras)
    por_classe = {0: [], 1: []}
    for a in amostras:
        por_classe[a[1]].append(a)

    treino, val, teste = [], [], []
    for rotulo, lista in por_classe.items():
        n = len(lista)
        n_teste = int(n * config.TEST_FRAC)
        n_val = int(n * config.VAL_FRAC)
        teste += lista[:n_teste]
        val += lista[n_teste:n_teste + n_val]
        treino += lista[n_teste + n_val:]
    return treino, val, teste


def dataloaders():
    treino, val, teste = split_estratificado()
    dl = lambda amostras, tr, shuf: DataLoader(
        CrackDataset(amostras, treino=tr), batch_size=config.BATCH, shuffle=shuf
    )
    return (
        dl(treino, True, True),
        dl(val, False, False),
        dl(teste, False, False),
        {"treino": len(treino), "val": len(val), "teste": len(teste)},
    )
