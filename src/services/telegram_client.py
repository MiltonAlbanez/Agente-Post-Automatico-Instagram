import requests


class TelegramClient:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id

    def send_message(self, text: str) -> bool:
        """
        Envia mensagem via Telegram e retorna True se bem-sucedido
        """
        try:
            url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": text}
            response = requests.post(url, data=payload, timeout=30)
            return response.status_code == 200
        except Exception as e:
            print(f"Erro ao enviar mensagem Telegram: {e}")
            return False