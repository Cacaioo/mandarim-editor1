# 🐲 Editor de Estudo de Mandarim

Editor visual em HTML para criar material de estudo de mandarim com letras de
música — tradução em português, pinyin e prática de caligrafia (田字格).

Funciona em conjunto com o script Python `gerador_mandarim.py` que gera o PDF
final, mas também consegue imprimir direto pelo navegador.

## Como usar

### Modo 1 — só pelo navegador (sem Python)

1. Abra `index.html` no navegador (duplo clique ou arraste para a aba).
2. Edite o cabeçalho (título, pinyin, artista).
3. Adicione refrões / linhas / segmentos.
   - Cada **segmento** é um pedaço da frase que aparecerá numa mesma cor.
   - Use **中→PT** para traduzir do chinês ao português, **PT→中** para o
     caminho inverso, e **PY** para gerar o pinyin a partir dos caracteres.
4. Clique em **Pré-visualização** e use **Cmd/Ctrl + P → Salvar como PDF**.

### Modo 2 — gerando PDF pelo script Python (mais bonito, com fonte Kaiti)

1. Use o editor para montar a música.
2. Clique em **Gerar CONFIG Python**, copie o bloco.
3. Cole no `gerador_mandarim.py` substituindo o dicionário `CONFIG = {...}`.
4. Rode:

   ```bash
   pip install weasyprint
   python3 gerador_mandarim.py
   ```

   O PDF sai com o nome em `CONFIG["output"]`.

### Backup do trabalho

- **Salvar / Carregar**: salva no `localStorage` do navegador.
- **Exportar / Importar JSON**: gera um arquivo `.json` que você pode commitar
  ou compartilhar.

## Recursos

- Tradução automática via [MyMemory API](https://mymemory.translated.net) —
  gratuita, sem chave, ~5000 caracteres/dia por IP.
- Pinyin automático com tons via [pinyin-pro](https://github.com/zh-lx/pinyin-pro)
  (carregado por CDN).
- Cores idênticas às do script Python (12 cores, atribuídas em sequência por
  refrão).
- Pré-visualização em HTML que imita o estilo do PDF (mesma fonte Kaiti se o
  sistema tiver, fallback CJK Sans caso contrário).

## Estrutura

```
mandarim-editor/
├── index.html              # editor visual (abrir no navegador)
├── gerador_mandarim.py     # script Python original (gera PDF)
└── README.md
```

## Dependências do script Python (Linux/Mac)

```bash
pip install weasyprint
# fontes para chinês simplificado em estilo Kaiti
sudo apt install fonts-arphic-ukai fonts-arphic-bkai00mp \
                 fonts-noto-cjk fonts-dejavu
```

No macOS o sistema já vem com **STKaiti**, que o script reconhece como
fallback automaticamente.
