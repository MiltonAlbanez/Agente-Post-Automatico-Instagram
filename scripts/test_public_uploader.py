import sys, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
sys.path.append(str(root))
from src.services.public_uploader import PublicUploader

def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/test_public_uploader.py <image_url>")
        return
    url = sys.argv[1]
    try:
        hosted = PublicUploader().upload_from_url(url)
        print("Hosted URL:", hosted)
    except Exception as e:
        print("Upload error:", e)

if __name__ == "__main__":
    main()