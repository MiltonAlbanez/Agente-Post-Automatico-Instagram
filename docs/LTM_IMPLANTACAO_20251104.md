# LTM – Consolidação de Erros e Correções (2025-11-04)

## Contexto
- Verificação Supabase completa executada: Banco, REST/GraphQL, Storage e Edge saudáveis; alerta em Auth.
- Teste de token do Instagram validado: conta acessível, permissões básicas OK; RapidAPI com 403 (não assinado).
- Pipeline de Stories local executado com sucesso; imagem 1080x1920 gerada e limpa.
- Teste de importação ajustado para `InstagramClientRobust` funcionando.
- Teste isolado de `create media` no Railway com imagem pública do Supabase: reproduz erros HTTP 190/1 conforme ambiente.

## Causas Prováveis
- HTTP 190: token malformado, variável incorreta ou escopo insuficiente.
- HTTP 1: falha intermitente da Graph API ou URL de imagem inacessível/redirect.
- RapidAPI: chave sem assinatura ativa.

## Correções Aplicadas
- Corrigido import absoluto em `test_publication_final.py` para `src.pipeline.generate_and_publish`.
- Adicionado `import os` em `test_full_pipeline.py` para limpeza de temporários.
- Eliminado warning de overflow na detecção de pele em `StoriesImageProcessor` convertendo `uint8` para `int` antes de subtrações.

## Recomendações Operacionais
- Validar no Railway que `INSTAGRAM_ACCESS_TOKEN` e `INSTAGRAM_BUSINESS_ACCOUNT_ID` estão sem aspas/espacos.
- Garantir URL da imagem do Supabase pública, com `Content-Type: image/jpeg`, sem redirects, < 8MB.
- RapidAPI: ativar assinatura do plano correto ou desativar uso.

## Comandos de Verificação no Railway
```bash
python test_instagram_token.py
python test_generate_and_publish_stories_dry_run.py
python -m src.pipeline.generate_and_publish  # quando for publicar
```

## Estado Final
- Cliente robusto ativo, pipeline local estável.
- Supabase saudável; alerta de Auth a ser revisado.
- Preparados comandos de deploy via Railway CLI.