"""
entropia.py
===========
Análise de Entropia de Shannon + visualizações para o pipeline
de criptografia: Arnold (confusão) + Hill/DH (difusão).

Fórmula:
    H(X) = - sum[ P(xi) * log2(P(xi)) ]  para i = 1..n

Entropia máxima teórica para imagens de 8 bits: 8.0 bits/pixel por canal.
"""

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from PIL import Image
import os
import sys
from pathlib import Path

raiz_projeto = Path(__file__).resolve().parent.parent
if str(raiz_projeto) not in sys.path:
    sys.path.append(str(raiz_projeto))


# ─────────────────────────────────────────────────────────────────────────────
# CÁLCULO DE ENTROPIA
# ─────────────────────────────────────────────────────────────────────────────

def entropia_canal(canal: np.ndarray, base: float = 2.0) -> float:
    frequencias    = np.bincount(canal.ravel(), minlength=256)
    probabilidades = frequencias[frequencias > 0] / canal.size
    return -np.sum(probabilidades * np.log(probabilidades) / np.log(base))


def entropia_imagem(img_array: np.ndarray, base: float = 2.0) -> dict:
    img = img_array.astype(np.uint8)
    h_r = entropia_canal(img[:, :, 0], base)
    h_g = entropia_canal(img[:, :, 1], base)
    h_b = entropia_canal(img[:, :, 2], base)
    return {'R': h_r, 'G': h_g, 'B': h_b, 'global': (h_r+h_g+h_b)/3.0, 'base': base}


def analisar_pipeline(img_original:    np.ndarray,
                      img_apos_arnold:  np.ndarray,
                      img_apos_difusao: np.ndarray,
                      base: float = 2.0) -> dict:
    e_orig   = entropia_imagem(img_original,     base)
    e_arnold = entropia_imagem(img_apos_arnold,  base)
    e_difus  = entropia_imagem(img_apos_difusao, base)
    return {
        'original':      e_orig,
        'apos_arnold':   e_arnold,
        'apos_difusao':  e_difus,
        'ganho_arnold':  e_arnold['global'] - e_orig['global'],
        'ganho_difusao': e_difus['global']  - e_arnold['global'],
        'ganho_total':   e_difus['global']  - e_orig['global'],
        'max_teorico':   np.log(256) / np.log(base),
    }


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

_CORES = {'R': '#c0392b', 'G': '#27ae60', 'B': '#2980b9'}


def _estilo_ax_branco(ax):
    """Aplica estilo fundo branco a um eixo."""
    ax.set_facecolor('white')
    ax.tick_params(colors='#333333', labelsize=7)
    ax.xaxis.label.set_color('#333333')
    ax.yaxis.label.set_color('#333333')
    ax.title.set_color('#111111')
    for spine in ax.spines.values():
        spine.set_edgecolor('#cccccc')


def _histograma_canal(ax, canal_array: np.ndarray, canal_nome: str,
                      entropia: float, titulo: str) -> None:
    cor = _CORES[canal_nome]
    contagens, _ = np.histogram(canal_array.ravel(), bins=256, range=(0, 255))
    ax.bar(np.arange(256), contagens, color=cor, alpha=0.80, width=1.0)
    ax.set_xlim(0, 255)
    ax.set_title(f"{titulo} — Canal {canal_nome}\nH = {entropia:.4f} bits",
                 fontsize=8, pad=4)
    ax.set_xlabel("Valor do pixel (0-255)", fontsize=7)
    ax.set_ylabel("Frequência", fontsize=7)
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, _: f"{int(x):,}"))
    _estilo_ax_branco(ax)


def _mostrar_imagem(ax, img_array: np.ndarray, titulo: str) -> None:
    """Exibe a imagem num eixo matplotlib sem eixos visíveis."""
    ax.imshow(img_array.astype(np.uint8))
    ax.set_title(titulo, fontsize=9, fontweight='bold', color='#111111', pad=4)
    ax.axis('off')
    ax.set_facecolor('white')


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO: comparação original vs cifrada
# ─────────────────────────────────────────────────────────────────────────────

def grafico_comparacao(img_original: np.ndarray,
                       img_cifrada:  np.ndarray,
                       titulo_original: str = "Original",
                       titulo_cifrada:  str = "Cifrada",
                       salvar_em: str = None,
                       mostrar:   bool = True) -> plt.Figure:
    """
    Layout (fundo branco):
      Linha 0 : imagem original  |  imagem cifrada
      Linhas 1-3 : histogramas R, G, B para cada coluna
      Linha 4 : barras de entropia comparativas
    """
    e_orig = entropia_imagem(img_original)
    e_cifr = entropia_imagem(img_cifrada)
    canais = ['R', 'G', 'B']

    fig = plt.figure(figsize=(14, 13), facecolor='white')
    fig.suptitle("Análise de Entropia — Original vs Cifrada",
                 color='#111111', fontsize=13, fontweight='bold', y=0.99)

    # 5 linhas: 1 imagem + 3 histogramas + 1 barra | 2 colunas
    gs = gridspec.GridSpec(5, 2, figure=fig,
                           hspace=0.60, wspace=0.35,
                           top=0.95, bottom=0.06, left=0.08, right=0.97,
                           height_ratios=[1.4, 1, 1, 1, 1.2])

    # ── Linha 0: imagens ────────────────────────────────────────────────────
    ax_img_o = fig.add_subplot(gs[0, 0])
    _mostrar_imagem(ax_img_o, img_original, titulo_original)

    ax_img_c = fig.add_subplot(gs[0, 1])
    _mostrar_imagem(ax_img_c, img_cifrada, titulo_cifrada)

    # ── Linhas 1-3: histogramas por canal ───────────────────────────────────
    for i, c in enumerate(canais):
        ax_o = fig.add_subplot(gs[i + 1, 0])
        _histograma_canal(ax_o, img_original[:, :, i], c, e_orig[c], titulo_original)

        ax_c = fig.add_subplot(gs[i + 1, 1])
        _histograma_canal(ax_c, img_cifrada[:, :, i],  c, e_cifr[c], titulo_cifrada)

    # ── Linha 4: barras de entropia ─────────────────────────────────────────
    ax_bar = fig.add_subplot(gs[4, :])
    ax_bar.set_facecolor('white')

    x      = np.arange(len(canais))
    width  = 0.30
    vals_o = [e_orig[c] for c in canais]
    vals_c = [e_cifr[c] for c in canais]
    cores  = [_CORES[c]  for c in canais]

    bars_o = ax_bar.bar(x - width/2, vals_o, width, color=cores, alpha=0.45,
                        label=titulo_original, edgecolor='#555555', linewidth=0.6)
    bars_c = ax_bar.bar(x + width/2, vals_c, width, color=cores, alpha=0.95,
                        label=titulo_cifrada,  edgecolor='#555555', linewidth=0.6)

    ax_bar.axhline(8.0, color='#e67e22', linestyle='--', linewidth=1.3,
                   label='Máximo teórico (8.0 bits)')

    for bar in list(bars_o) + list(bars_c):
        h = bar.get_height()
        ax_bar.text(bar.get_x() + bar.get_width()/2, h + 0.04,
                    f"{h:.3f}", ha='center', va='bottom',
                    fontsize=7, color='#222222')

    ax_bar.set_xticks(x)
    ax_bar.set_xticklabels([f"Canal {c}" for c in canais], color='#333333')
    ax_bar.set_ylim(0, 8.8)
    ax_bar.set_ylabel("Entropia (bits)", color='#333333', fontsize=8)
    ax_bar.set_title(
        f"Entropia Global — {titulo_original}: {e_orig['global']:.4f} bits  |  "
        f"{titulo_cifrada}: {e_cifr['global']:.4f} bits",
        color='#111111', fontsize=9
    )
    ax_bar.tick_params(colors='#333333', labelsize=8)
    ax_bar.legend(fontsize=8, facecolor='white', edgecolor='#cccccc')
    ax_bar.grid(axis='y', color='#eeeeee', linewidth=0.7)
    for spine in ax_bar.spines.values():
        spine.set_edgecolor('#cccccc')

    if salvar_em:
        fig.savefig(salvar_em, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"[✓] Gráfico salvo em: {salvar_em}")

    if mostrar:
        plt.show()

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# GRÁFICO: pipeline completo (3 etapas)
# ─────────────────────────────────────────────────────────────────────────────

def grafico_pipeline(img_original:    np.ndarray,
                     img_apos_arnold:  np.ndarray,
                     img_apos_difusao: np.ndarray,
                     salvar_em: str = None,
                     mostrar:   bool = True) -> plt.Figure:
    """
    Layout (fundo branco):
      Linha 0 : imagem original | imagem arnold | imagem difusão
      Linhas 1-3 : histogramas R, G, B para cada coluna
      Linha 4 : gráfico de linha com evolução da entropia
    """
    etapas = [
        ("Original",     img_original),
        ("Após Arnold",  img_apos_arnold),
        ("Após Hill/DH", img_apos_difusao),
    ]
    entropias = [entropia_imagem(img) for _, img in etapas]
    canais    = ['R', 'G', 'B']

    fig = plt.figure(figsize=(17, 13), facecolor='white')
    fig.suptitle("Evolução da Entropia no Pipeline de Criptografia",
                 color='#111111', fontsize=13, fontweight='bold', y=0.99)

    # 5 linhas: 1 imagem + 3 histogramas + 1 evolução | 3 colunas
    gs = gridspec.GridSpec(5, 3, figure=fig,
                           hspace=0.60, wspace=0.35,
                           top=0.95, bottom=0.06, left=0.07, right=0.97,
                           height_ratios=[1.4, 1, 1, 1, 1.3])

    # ── Linha 0: imagens de cada etapa ──────────────────────────────────────
    for col, (titulo, img_arr) in enumerate(etapas):
        ax_img = fig.add_subplot(gs[0, col])
        _mostrar_imagem(ax_img, img_arr, titulo)

    # ── Linhas 1-3: histogramas por canal e etapa ────────────────────────────
    for col, (titulo, img_arr) in enumerate(etapas):
        for row, c in enumerate(canais):
            ax = fig.add_subplot(gs[row + 1, col])
            _histograma_canal(ax, img_arr[:, :, canais.index(c)],
                              c, entropias[col][c], titulo)

    # ── Linha 4: evolução da entropia ────────────────────────────────────────
    ax_line = fig.add_subplot(gs[4, :])
    ax_line.set_facecolor('white')

    x_pos       = [0, 1, 2]
    nomes_etapa = [t for t, _ in etapas]

    for c in canais:
        vals = [e[c] for e in entropias]
        ax_line.plot(x_pos, vals, 'o-', color=_CORES[c], linewidth=2,
                     markersize=7, label=f"Canal {c}", zorder=3)
        for xi, vi in zip(x_pos, vals):
            ax_line.text(xi, vi + 0.05, f"{vi:.3f}", ha='center',
                         fontsize=7.5, color=_CORES[c], fontweight='bold')

    vals_glob = [e['global'] for e in entropias]
    ax_line.plot(x_pos, vals_glob, 's--', color='#e67e22', linewidth=2,
                 markersize=8, label="Global (média)", zorder=4)
    for xi, vi in zip(x_pos, vals_glob):
        ax_line.text(xi, vi - 0.20, f"{vi:.3f}", ha='center',
                     fontsize=8, color='#e67e22', fontweight='bold')

    ax_line.axhline(8.0, color='#95a5a6', linestyle=':', linewidth=1.3,
                    label='Máximo teórico (8.0 bits)')

    ax_line.set_xticks(x_pos)
    ax_line.set_xticklabels(nomes_etapa, color='#333333', fontsize=9)
    ax_line.set_ylim(max(0, min(vals_glob) - 0.6), 8.6)
    ax_line.set_ylabel("Entropia (bits)", color='#333333', fontsize=8)
    ax_line.set_title("Evolução da Entropia por Etapa do Pipeline",
                      color='#111111', fontsize=9)
    ax_line.tick_params(colors='#333333', labelsize=8)
    ax_line.legend(fontsize=8, ncol=5, facecolor='white', edgecolor='#cccccc')
    ax_line.grid(axis='y', color='#eeeeee', linewidth=0.8)
    for spine in ax_line.spines.values():
        spine.set_edgecolor('#cccccc')

    if salvar_em:
        fig.savefig(salvar_em, dpi=150, bbox_inches='tight', facecolor='white')
        print(f"[✓] Gráfico salvo em: {salvar_em}")

    if mostrar:
        plt.show()

    return fig


# ─────────────────────────────────────────────────────────────────────────────
# RELATÓRIO TEXTO
# ─────────────────────────────────────────────────────────────────────────────

def imprimir_relatorio(resultado: dict) -> None:
    max_t   = resultado.get('max_teorico', 8.0)
    base    = resultado['original']['base'] if 'original' in resultado else resultado.get('base', 2)
    unidade = 'bits' if base == 2 else f'log_{base}'
    sep     = "─" * 60

    def _linha(nome, dados):
        pct = (dados['global'] / max_t) * 100
        print(f"\n  {nome}")
        print(f"  {sep}")
        print(f"  R: {dados['R']:.6f}   G: {dados['G']:.6f}   B: {dados['B']:.6f}")
        print(f"  Global: {dados['global']:.6f} {unidade}  ({pct:.2f}% do máximo)")

    print(f"\n{'═'*60}")
    print(f"  ANÁLISE DE ENTROPIA DE SHANNON  (base={base}, unidade={unidade})")
    print(f"  Máximo teórico: {max_t:.4f} {unidade}/pixel")
    print(f"{'═'*60}")

    if 'original' in resultado:
        _linha("📷 ORIGINAL",     resultado['original'])
        _linha("🌀 APÓS ARNOLD",  resultado['apos_arnold'])
        _linha("🔒 APÓS DIFUSÃO", resultado['apos_difusao'])
        print(f"\n  {sep}")
        print(f"  Ganho c/ Arnold   : {resultado['ganho_arnold']:+.6f} {unidade}")
        print(f"  Ganho c/ Difusão  : {resultado['ganho_difusao']:+.6f} {unidade}")
        print(f"  Ganho Total       : {resultado['ganho_total']:+.6f} {unidade}")
        e_f   = resultado['apos_difusao']['global']
        icone = '✅' if e_f >= 7.9 else '⚠️ '
        print(f"\n  {icone} Entropia final: {e_f:.6f} bits")
        msg = ("Imagem altamente aleatória (próxima do ideal)."
               if e_f >= 7.9 else "Aleatoriedade pode ser melhorada.")
        print(f"  {msg}")
    else:
        _linha("IMAGEM", resultado)

    print(f"{'═'*60}\n")


# ─────────────────────────────────────────────────────────────────────────────
# STANDALONE
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    """
    Modos de uso:

    1) Analisar imagem única:
       python3 entropia.py imagem.png

    2) Comparar original vs cifrada:
       python3 entropia.py original.png cifrada.png

    3) Analisar pipeline completo (original, arnold, hill):
       python3 entropia.py original.png arnold.png difundida.png
    """
    n = len(sys.argv) - 1

    if n == 0:
        print(__doc__)
        sys.exit(0)

    imgs = []
    for path in sys.argv[1:]:
        arr = np.array(Image.open(path).convert('RGB'))
        imgs.append(arr)
        print(f"[✓] Carregada: {path}  {arr.shape}")

    if n == 1:
        e = entropia_imagem(imgs[0])
        print(f"\nEntropia  R:{e['R']:.4f}  G:{e['G']:.4f}  "
              f"B:{e['B']:.4f}  Global:{e['global']:.4f} bits\n")

    elif n == 2:
        grafico_comparacao(
            imgs[0], imgs[1],
            titulo_original=Path(sys.argv[1]).stem,
            titulo_cifrada =Path(sys.argv[2]).stem,
            salvar_em="comparacao_entropia.png",
            mostrar=True
        )

    elif n == 3:
        resultado = analisar_pipeline(imgs[0], imgs[1], imgs[2])
        imprimir_relatorio(resultado)
        grafico_pipeline(
            imgs[0], imgs[1], imgs[2],
            salvar_em="pipeline_entropia.png",
            mostrar=True
        )

    else:
        print("Máximo 3 imagens aceitas. Veja o docstring para instruções.")
        sys.exit(1)
