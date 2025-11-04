import os
import json
import argparse
import datetime
import pathlib
import sys

try:
    import requests
except Exception:
    requests = None


def mask_secret(value: str, keep: int = 4) -> str:
    if not value:
        return ""
    if len(value) <= keep:
        return "*" * len(value)
    return value[:keep] + "..." + "*" * max(0, len(value) - keep)


def write_audit_json(data: dict, directory: str = "audit") -> str:
    ts = datetime.datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    pathlib.Path(directory).mkdir(parents=True, exist_ok=True)
    out_path = pathlib.Path(directory) / f"instagram_media_{ts}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(out_path)


def call_instagram_media(account_id: str, access_token: str, image_url: str, caption: str = None):
    if requests is None:
        raise RuntimeError("The 'requests' library is required to run this script.")

    url = f"https://graph.facebook.com/v19.0/{account_id}/media"
    params = {"access_token": access_token}
    payload = {"image_url": image_url}
    if caption:
        payload["caption"] = caption

    resp = requests.post(url, params=params, data=payload, timeout=30)
    try:
        body = resp.json()
    except Exception:
        body = {"raw": resp.text}

    result = {
        "request": {
            "url": url,
            "params": {"access_token": mask_secret(access_token)},
            "data": {"image_url": image_url, **({"caption": caption} if caption else {})},
        },
        "response": {
            "status_code": resp.status_code,
            "json": body,
        },
        "meta": {
            "timestamp_utc": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
        },
    }
    return result


def main():
    parser = argparse.ArgumentParser(description="Audit Instagram /{account_id}/media call with a public image URL.")
    parser.add_argument("--account-id", default=os.getenv("IG_ACCOUNT_ID") or os.getenv("INSTAGRAM_ACCOUNT_ID"), help="Instagram account (user) ID")
    parser.add_argument("--image-url", default=os.getenv("SUPABASE_PUBLIC_IMAGE_URL"), help="Public image URL (e.g., from Supabase public bucket)")
    parser.add_argument("--caption", default=os.getenv("IG_MEDIA_CAPTION"), help="Optional caption")
    args = parser.parse_args()

    access_token = os.getenv("INSTAGRAM_ACCESS_TOKEN") or os.getenv("IG_ACCESS_TOKEN")

    missing = []
    if not args.account_id:
        missing.append("--account-id or env IG_ACCOUNT_ID/INSTAGRAM_ACCOUNT_ID")
    if not args.image_url:
        missing.append("--image-url or env SUPABASE_PUBLIC_IMAGE_URL")
    if not access_token:
        missing.append("env INSTAGRAM_ACCESS_TOKEN or IG_ACCESS_TOKEN")
    if missing:
        print("Missing required inputs:")
        for m in missing:
            print(f" - {m}")
        sys.exit(2)

    print(f"Calling /{args.account_id}/media with image_url={args.image_url}")
    print(f"Access token: {mask_secret(access_token)}")

    try:
        audit = call_instagram_media(args.account_id, access_token, args.image_url, args.caption)
    except Exception as e:
        audit = {
            "error": str(e),
            "meta": {
                "timestamp_utc": datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z",
            },
        }

    out_file = write_audit_json(audit)
    print(f"Audit saved to {out_file}")
    # Also print condensed summary for quick log inspection
    if isinstance(audit, dict) and "response" in audit:
        status = audit["response"].get("status_code")
        json_body = audit["response"].get("json")
        print(f"HTTP {status}; body keys: {list(json_body.keys()) if isinstance(json_body, dict) else 'raw'}")


if __name__ == "__main__":
    main()