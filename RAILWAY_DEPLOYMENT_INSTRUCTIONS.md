# Instruções para Implementação no Railway

## Arquivos a serem atualizados

1. **railway_scheduler.py**
   - Alteração na função `create_scheduled_post`: substituir `mode='feed'` por `publish_to_stories=False`
   - A função `create_scheduled_stories` já está correta com `publish_to_stories=True`

## Passos para Implementação

1. Acesse o dashboard do Railway em https://railway.app/dashboard
2. Navegue até o projeto "Agente Post Automático Instagram"
3. Selecione o serviço que contém o agendador
4. Vá para a aba "Files" e edite o arquivo `railway_scheduler.py`
5. Localize a função `create_scheduled_post` (aproximadamente linha 70-90)
6. Substitua a chamada de `generate_and_publish` que usa `mode='feed'` por `publish_to_stories=False`
7. Salve as alterações
8. Reinicie o serviço para aplicar as mudanças

## Monitoramento

1. Após a implementação, monitore os logs de execução para cada horário agendado
2. Verifique se os stories estão sendo publicados nos horários: 9h, 15h e 21h BRT
3. Verifique se os posts de feed estão sendo publicados nos horários configurados

## Validação

1. Execute o script de teste `test_scheduler_verification.py` após cada execução agendada
2. Confirme que as publicações estão aparecendo corretamente no Instagram
3. Verifique as notificações no Telegram para confirmar o sucesso das publicações