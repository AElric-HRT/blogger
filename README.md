## Automação para coletar links de vídeo e atualizar posts (Blogger)

### Visão geral
- **scripts/scrape_videos.py**: CLI que usa `yt-dlp` para extrair links diretos (m3u8/mp4) de páginas de episódio ou players.
- **scripts/blogger_update_template.py**: Template para atualizar o conteúdo de um post no Blogger inserindo um iframe com o link extraído.

### Requisitos
1) Python 3.10+
2) Criar venv e instalar dependências:

```bash
cd /workspace
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Uso: extrair links de vídeo

```bash
source .venv/bin/activate
python scripts/scrape_videos.py "https://url-da-pagina-do-episodio" --json
```

Opcional: alguns hosts exigem `Referer`/`Origin`:

```bash
python scripts/scrape_videos.py "https://url" --header "Referer:https://site-alvo" --header "Origin:https://site-alvo"
```

Saída inclui `preferred.url` com o melhor palpite (m3u8/MP4).

### Atualizar post no Blogger (template)
1) Ative Blogger API v3 no Google Cloud e gere credenciais OAuth (Desktop App).
2) Baixe `client_secret.json` para `/workspace`.
3) Crie `.env` com:

```
BLOG_ID=SEU_BLOG_ID
POST_ID=ID_DO_POST
DIRECT_LINK=https://link-direto-m3u8-ou-mp4
GOOGLE_CLIENT_SECRET=client_secret.json
GOOGLE_TOKEN=token.json
```

4) Instale dependências Google e rode:

```bash
pip install google-api-python-client google-auth-oauthlib python-dotenv
python scripts/blogger_update_template.py
```

Adapte a função `build_new_content()` no template para combinar com o seu tema (ex.: usar `#player` / `#iframeeps`).

### Lote (batch) de episódios
Para vários episódios, gere as URLs e extraia em sequência.

```bash
source .venv/bin/activate
python scripts/generate_episode_urls.py \
  --template 'https://site/temporada-01/episodio-{num}/' \
  --start 1 --end 12 --zfill 2 \
| xargs -I {} python scripts/scrape_videos.py '{}' --header 'Referer:https://site' --json > resultados.json
```

Depois, consuma `resultados.json` para atualizar posts específicos com `scripts/blogger_update_template.py`.

### Observações legais
Respeite os termos de uso e direitos autorais das fontes que você automatizar. Use cabeçalhos apenas quando permitido e evite sobrecarregar serviços.

