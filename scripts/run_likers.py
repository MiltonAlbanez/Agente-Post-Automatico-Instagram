import argparse
import json
import os
from pathlib import Path
from src.config import load_config
from src.services.rapidapi_client import RapidAPIClient


def main():
    parser = argparse.ArgumentParser(description="Testar get_post_likers via RapidAPI")
    parser.add_argument("--post_id", type=str, default=None, help="ID do post (opcional)")
    parser.add_argument("--shortcode", type=str, default=None, help="Shortcode do post (opcional)")
    parser.add_argument("--monitor", action="store_true", help="Modo monitor contínuo (24/7)")
    args = parser.parse_args()

    cfg = load_config()
    api_key = cfg.get("RAPIDAPI_KEY") or os.getenv("RAPIDAPI_KEY")
    host = cfg.get("RAPIDAPI_HOST") or os.getenv("RAPIDAPI_HOST")
    if not api_key or not host:
        raise RuntimeError("RAPIDAPI_KEY e RAPIDAPI_HOST devem estar configurados")

    client = RapidAPIClient(api_key=api_key, host=host)

    def once():
        data = client.get_post_likers(post_id=args.post_id, shortcode=args.shortcode)
        # salvar saída para inspeção
        out_dir = Path("logs")
        out_dir.mkdir(exist_ok=True)
        out_path = out_dir / "last_likers_result.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # imprimir resumo
        keys = list(data.keys())[:6]
        print(f"Resultado OK. Chaves: {keys}. Saída em {out_path}")

    if args.monitor:
        import time
        print("Iniciando monitor de RapidAPI (get_post_likers) 24/7...")
        while True:
            try:
                once()
            except Exception as e:
                print(f"Falha no monitor: {e}")
            # intervalos suaves para não abusar; 10 minutos
            time.sleep(600)
    else:
        once()


if __name__ == "__main__":
    main()