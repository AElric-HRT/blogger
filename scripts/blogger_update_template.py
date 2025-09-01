#!/usr/bin/env python3
"""
Modelo: atualizar posts no Blogger adicionando/atualizando um iframe de player
com o link extraído (m3u8/mp4). Requer uma credencial OAuth 2.0 e o ID do blog.

Passos resumidos:
1) Crie um projeto no Google Cloud, ative Blogger API v3.
2) Crie credenciais OAuth (Desktop App) e baixe client_secret.json.
3) Salve como .env as variáveis: BLOG_ID, POST_ID (opcional), e caminho do client_secret.json.
4) Rode este script para autenticar e atualizar o conteúdo HTML do post.

Observação: este script é apenas um template. Edite a função build_new_content
para combinar com o HTML do seu tema.
"""
import os
import sys
from typing import Optional

from dotenv import load_dotenv

try:
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    from google.oauth2.credentials import Credentials
except Exception:  # noqa: BLE001
    print(
        "Instale dependências Google: pip install google-api-python-client google-auth-oauthlib python-dotenv",
        file=sys.stderr,
    )
    raise


SCOPES = ["https://www.googleapis.com/auth/blogger"]


def build_new_content(current_html: str, direct_link: str) -> str:
    """Retorna o novo conteúdo do post, inserindo/atualizando um iframe do player.

    Adapte esta função ao seu tema. Exemplo abaixo insere um bloco simples.
    """
    iframe = (
        f"<div id=\"player\"><iframe id=\"iframeeps\" allowfullscreen frameborder=\"0\" "
        f"src=\"{direct_link}\" referrerpolicy=\"no-referrer\" style=\"width:100%;height:600px\"></iframe></div>"
    )
    # Estratégia simples: se já houver #player, substitui. Senão, prepend.
    if "id=\"player\"" in current_html:
        start = current_html.find("id=\"player\"")
        # Não fazemos parsing completo para manter template simples;
        # Em produção, use BeautifulSoup.
        return current_html.replace(current_html[start - 12 : start + 2000], iframe)
    return iframe + current_html


def get_service(creds_path: str, token_path: str) -> any:  # type: ignore[no-any-unimported]
    creds: Optional[Credentials] = None
    if os.path.exists(token_path):
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(creds_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token_path, "w", encoding="utf-8") as token:
            token.write(creds.to_json())
    return build("blogger", "v3", credentials=creds)


def main() -> None:
    load_dotenv()
    blog_id = os.getenv("BLOG_ID")
    post_id = os.getenv("POST_ID")
    direct_link = os.getenv("DIRECT_LINK")
    creds_path = os.getenv("GOOGLE_CLIENT_SECRET", "client_secret.json")
    token_path = os.getenv("GOOGLE_TOKEN", "token.json")

    if not blog_id or not direct_link:
        print("Defina BLOG_ID e DIRECT_LINK no .env", file=sys.stderr)
        sys.exit(1)

    service = get_service(creds_path, token_path)

    if not post_id:
        print("Forneça POST_ID no .env para atualizar um post específico.", file=sys.stderr)
        sys.exit(1)

    post = (
        service.posts()
        .get(blogId=blog_id, postId=post_id, view="ADMIN")
        .execute()
    )
    content = post.get("content", "")
    new_content = build_new_content(content, direct_link)

    if new_content == content:
        print("Nenhuma alteração detectada.")
        return

    updated = (
        service.posts()
        .update(blogId=blog_id, postId=post_id, body={"content": new_content})
        .execute()
    )
    print(f"Post atualizado: {updated.get('url')}")


if __name__ == "__main__":
    main()

