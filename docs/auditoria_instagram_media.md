# Auditoria Instagram /{account_id}/media no Railway

Este guia automatiza um teste que chama apenas `/{account_id}/media` com uma imagem pública do Supabase e salva o JSON completo de retorno no container Railway para auditar códigos como `190` e `1` diretamente em produção.

## Pré-requisitos

- Variáveis de ambiente no Railway:
  - `INSTAGRAM_ACCESS_TOKEN`: token válido do Instagram Graph API.
  - `IG_ACCOUNT_ID` (ou `INSTAGRAM_ACCOUNT_ID`): ID do usuário Instagram.
  - `SUPABASE_PUBLIC_IMAGE_URL`: URL pública de uma imagem (bucket público do Supabase).
  - Opcional: `IG_MEDIA_CAPTION` (legenda).

> Observação: Não versionamos segredos. O diretório `audit/` está no `.gitignore` para evitar que artefatos com respostas sejam enviados ao repositório.

## Execução

No container Railway (via shell/exec) ou como comando de start temporário:

```
python tools/audit_instagram_media.py --account-id %IG_ACCOUNT_ID% --image-url %SUPABASE_PUBLIC_IMAGE_URL%
```

Em ambientes Linux, use:

```
python tools/audit_instagram_media.py --account-id $IG_ACCOUNT_ID --image-url $SUPABASE_PUBLIC_IMAGE_URL
```

## Saída e auditoria

- O script grava o arquivo JSON completo em `audit/instagram_media_<timestamp>.json` dentro do container.
- Também imprime um resumo no stdout (logs do Railway), com status HTTP e chaves do corpo.
- O token é mascarado nos logs. Valores reais permanecem apenas no ambiente.

## Interpretação de códigos

- `190`: problemas com token (expirado, inválido, app desautorizado). Valide escopos e renovação.
- `1`: erro genérico do servidor. Tente novamente e verifique parâmetros.

## Boas práticas

- Use URLs de imagem publicamente acessíveis (sem autenticação) para o parâmetro `image_url`.
- Evite incluir backups e arquivos com segredos no repositório; já bloqueamos via `.gitignore` e limpeza de índice.
- Se precisar persistir além do ciclo de vida do container, exporte o conteúdo do `audit/` ou copie para um storage externo.