import requests


class PublicUploader:
    """
    Uploads an image to a public hosting to obtain an HTTPS URL
    suitable for Instagram Graph API's `image_url`.

    Uses 0x0.st anonymous file hosting, with fallbacks to transfer.sh and catbox.moe.
    """

    HOST_URL = "https://0x0.st"

    def _guess_extension(self, content_type: str) -> str:
        ct = (content_type or "").lower()
        if "jpeg" in ct or "jpg" in ct:
            return "jpg"
        if "png" in ct:
            return "png"
        if "webp" in ct:
            return "webp"
        return "bin"

    def upload_from_url(self, source_image_url: str, timeout: int = 30) -> str:
        # Download image bytes
        r = requests.get(source_image_url, timeout=timeout)
        r.raise_for_status()
        content_type = r.headers.get("Content-Type", "image/jpeg")
        ext = self._guess_extension(content_type)
        filename = f"image.{ext}"
        data = r.content

        # Try 0x0.st first (multipart/form-data)
        try:
            files = {"file": (filename, data, content_type)}
            up = requests.post(self.HOST_URL, files=files, timeout=timeout)
            up.raise_for_status()
            url = up.text.strip()
            if url.startswith("http"):
                return url
            raise RuntimeError(f"Unexpected upload response: {url}")
        except Exception:
            pass

        # Fallback: transfer.sh via PUT
        try:
            headers = {"Content-Type": content_type}
            put = requests.put(f"https://transfer.sh/{filename}", data=data, headers=headers, timeout=timeout)
            put.raise_for_status()
            url = put.text.strip()
            if url.startswith("http"):
                return url
            raise RuntimeError(f"Unexpected transfer.sh response: {url}")
        except Exception:
            pass

        # Fallback: catbox.moe via fileupload
        try:
            files = {"fileToUpload": (filename, data, content_type)}
            resp = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files=files,
                timeout=timeout,
            )
            resp.raise_for_status()
            url = resp.text.strip()
            if url.startswith("http"):
                return url
            raise RuntimeError(f"Unexpected catbox fileupload response: {url}")
        except Exception:
            pass

        # Fallback: catbox.moe via urlupload
        try:
            resp = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "urlupload", "url": source_image_url},
                timeout=timeout,
            )
            resp.raise_for_status()
            url = resp.text.strip()
            if url.startswith("http"):
                return url
            raise RuntimeError(f"Unexpected catbox urlupload response: {url}")
        except Exception as e:
            raise RuntimeError(f"All upload fallbacks failed: {e}")

    def upload_from_file(self, file_path: str, timeout: int = 30) -> str:
        """
        Upload a file from local path to public hosting.
        
        Args:
            file_path: Path to the local file
            timeout: Request timeout in seconds
            
        Returns:
            Public HTTPS URL of the uploaded file
        """
        import os
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Read file content
        with open(file_path, 'rb') as f:
            data = f.read()
            
        # Guess content type from file extension
        ext = os.path.splitext(file_path)[1].lower()
        if ext in ['.jpg', '.jpeg']:
            content_type = 'image/jpeg'
        elif ext == '.png':
            content_type = 'image/png'
        elif ext == '.webp':
            content_type = 'image/webp'
        else:
            content_type = 'application/octet-stream'
            
        filename = os.path.basename(file_path)

        # Try 0x0.st first (multipart/form-data)
        try:
            files = {"file": (filename, data, content_type)}
            up = requests.post(self.HOST_URL, files=files, timeout=timeout)
            up.raise_for_status()
            url = up.text.strip()
            if url.startswith("http"):
                return url
            raise RuntimeError(f"Unexpected upload response: {url}")
        except Exception:
            pass

        # Fallback: transfer.sh via PUT
        try:
            headers = {"Content-Type": content_type}
            put = requests.put(f"https://transfer.sh/{filename}", data=data, headers=headers, timeout=timeout)
            put.raise_for_status()
            url = put.text.strip()
            if url.startswith("http"):
                return url
            raise RuntimeError(f"Unexpected transfer.sh response: {url}")
        except Exception:
            pass

        # Fallback: catbox.moe via fileupload
        try:
            files = {"fileToUpload": (filename, data, content_type)}
            resp = requests.post(
                "https://catbox.moe/user/api.php",
                data={"reqtype": "fileupload"},
                files=files,
                timeout=timeout,
            )
            resp.raise_for_status()
            url = resp.text.strip()
            if url.startswith("http"):
                return url
            raise RuntimeError(f"Unexpected catbox fileupload response: {url}")
        except Exception as e:
            raise RuntimeError(f"All upload fallbacks failed: {e}")