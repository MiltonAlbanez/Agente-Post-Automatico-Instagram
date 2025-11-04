import requests


class TelegramClient:
    def __init__(self, bot_token: str, chat_id: str):
        # Sanitiza entradas para evitar espaços acidentais
        self.bot_token = (bot_token or "").strip()
        self.chat_id = (chat_id or "").strip()

    def send_message(self, text: str) -> bool:
        """
        Envia mensagem via Telegram e retorna True se bem-sucedido
        """
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": text}
            response = requests.post(url, data=payload, timeout=30)
            if response.status_code != 200:
                try:
                    body = response.text
                except Exception:
                    body = "<sem corpo>"
                print(
                    f"Telegram falhou: status={response.status_code} body={body} url={url} payload={payload}"
                )
                return False
            return True
        except Exception as e:
            print(f"Erro ao enviar mensagem Telegram: {e}")
            return False