import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Any, Dict
from .exceptions import APIClientError

class CourseUploader:
    def __init__(self, base_url: str, api_token: str, timeout: int = 120, max_retries: int = 3):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout

        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=2,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session = requests.Session()
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

        self.session.headers.update({
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/json",
            "User-Agent": "CourseParser/1.0"
        })

    def upload_course(self, course_data: Dict[str, Any]) -> None:
        endpoint = f"{self.base_url}/api/v1/courses/import"

        try:
            print(f"📡 POSTing to {endpoint} (Timeout: {self.timeout}s)...")
            response = self.session.post(
                endpoint,
                json=course_data,
                timeout=self.timeout
            )
            response.raise_for_status()
            print(f"✅ Course uploaded successfully. Server Status: {response.status_code}")

        except Exception as e:
            raise APIClientError(f"Upload failed: {str(e)}")