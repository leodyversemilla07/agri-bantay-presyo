import httpx
from pathlib import Path
from typing import Optional
import os

class PDFDownloader:
    def __init__(self, download_dir: str = "downloads"):
        self.download_dir = Path(download_dir)
        self.download_dir.mkdir(parents=True, exist_ok=True)

    def download_pdf_sync(self, url: str, filename: Optional[str] = None) -> Path:
        if not filename:
            filename = url.split("/")[-1]
        
        target_path = self.download_dir / filename
        
        with httpx.Client() as client:
            response = client.get(url)
            response.raise_for_status()
            
            with open(target_path, "wb") as f:
                f.write(response.content)
        
        return target_path

    async def download_pdf_async(self, url: str, filename: Optional[str] = None) -> Path:
        if not filename:
            filename = url.split("/")[-1]
        
        target_path = self.download_dir / filename
        
        async with httpx.AsyncClient(follow_redirects=True) as client:
            response = await client.get(url)
            response.raise_for_status()
            
            with open(target_path, "wb") as f:
                f.write(response.content)
        
        return target_path

    def list_downloaded_pdfs(self) -> list[Path]:
        return list(self.download_dir.glob("*.pdf"))
