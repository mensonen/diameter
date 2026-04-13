#!/usr/bin/env python3
import os
import sys
import time
import json
import mimetypes
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests
from dotenv import load_dotenv


load_dotenv()


class JiraUploader:
    def __init__(
        self,
        base_url: str,
        email: str,
        api_token: str,
        issue_key: str,
        timeout: int = 60,
        verify_ssl: bool = True,
    ):
        self.base_url = base_url.rstrip("/")
        self.email = email
        self.api_token = api_token
        self.issue_key = issue_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl

        self.session = requests.Session()
        self.session.auth = (self.email, self.api_token)
        self.session.headers.update({"Accept": "application/json"})

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _request(self, method: str, path: str, **kwargs) -> requests.Response:
        kwargs.setdefault("timeout", self.timeout)
        kwargs.setdefault("verify", self.verify_ssl)
        return self.session.request(method, self._url(path), **kwargs)

    def get_issue_attachments(self) -> List[Dict[str, Any]]:
        resp = self._request("GET", f"/rest/api/3/issue/{self.issue_key}?fields=attachment")
        self._raise_for_status(resp, "Failed to fetch issue attachments")
        data = resp.json()
        return data.get("fields", {}).get("attachment", [])

    def attachment_exists(self, filename: str, size: Optional[int] = None) -> bool:
        attachments = self.get_issue_attachments()
        for att in attachments:
            if att.get("filename") == filename:
                if size is None or att.get("size") == size:
                    return True
        return False

    def upload_attachment(self, file_path: Path, retries: int = 3) -> Dict[str, Any]:
        if not file_path.is_file():
            raise FileNotFoundError(f"Attachment file not found: {file_path}")

        mime_type = mimetypes.guess_type(str(file_path))[0] or "application/octet-stream"
        headers = {"X-Atlassian-Token": "no-check"}

        for attempt in range(1, retries + 1):
            with open(file_path, "rb") as f:
                files = {
                    "file": (file_path.name, f, mime_type)
                }
                resp = self._request(
                    "POST",
                    f"/rest/api/3/issue/{self.issue_key}/attachments",
                    headers=headers,
                    files=files,
                )

            if resp.status_code in (200, 201):
                payload = resp.json()
                if isinstance(payload, list) and payload:
                    return payload[0]
                return {"raw": payload}

            if attempt < retries and resp.status_code in (408, 429, 500, 502, 503, 504):
                time.sleep(2 * attempt)
                continue

            self._raise_for_status(resp, "Failed to upload attachment")

        raise RuntimeError("Attachment upload failed after retries")

    def add_comment(self, text: str, visibility: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        body = {
            "body": {
                "type": "doc",
                "version": 1,
                "content": [
                    {
                        "type": "paragraph",
                        "content": [{"type": "text", "text": text}]
                    }
                ],
            }
        }

        if visibility:
            body["visibility"] = visibility

        resp = self._request(
            "POST",
            f"/rest/api/3/issue/{self.issue_key}/comment",
            headers={"Content-Type": "application/json"},
            data=json.dumps(body),
        )
        self._raise_for_status(resp, "Failed to add Jira comment")
        return resp.json()

    @staticmethod
    def _raise_for_status(resp: requests.Response, prefix: str):
        try:
            detail = resp.json()
        except Exception:
            detail = resp.text
        if not resp.ok:
            raise RuntimeError(f"{prefix}: HTTP {resp.status_code} - {detail}")


def parse_bool(value: Optional[str], default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "y", "on")


def build_comment_text(
    issue_key: str,
    file_path: Path,
    attachment_result: Optional[Dict[str, Any]],
    custom_message: Optional[str] = None,
) -> str:
    lines = []

    if custom_message:
        lines.append(custom_message)

    lines.append(f"Evidence report uploaded for issue {issue_key}.")
    lines.append(f"Attachment: {file_path.name}")

    if attachment_result:
        attachment_id = attachment_result.get("id")
        content_url = attachment_result.get("content")
        if attachment_id:
            lines.append(f"Attachment ID: {attachment_id}")
        if content_url:
            lines.append(f"Attachment URL: {content_url}")

    return "\n".join(lines)


def main():
    base_url = os.getenv("JIRA_BASE_URL", "").strip()
    email = os.getenv("JIRA_EMAIL", "").strip()
    api_token = os.getenv("JIRA_API_TOKEN", "").strip()
    issue_key = os.getenv("JIRA_ISSUE_KEY", "").strip()
    file_path_str = os.getenv("JIRA_FILE_PATH", r"C:\project\testcases\diameter_e2e_report.md").strip()
    comment_prefix = os.getenv("JIRA_COMMENT_PREFIX", "Automated E2E evidence upload completed.").strip()
    skip_duplicate = parse_bool(os.getenv("JIRA_SKIP_DUPLICATE", "true"), True)
    verify_ssl = parse_bool(os.getenv("JIRA_VERIFY_SSL", "true"), True)

    if len(sys.argv) > 1:
        issue_key = sys.argv[1]
    if len(sys.argv) > 2:
        file_path_str = sys.argv[2]

    missing = []
    if not base_url:
        missing.append("JIRA_BASE_URL")
    if not email:
        missing.append("JIRA_EMAIL")
    if not api_token:
        missing.append("JIRA_API_TOKEN")
    if not issue_key:
        missing.append("JIRA_ISSUE_KEY")

    if missing:
        raise RuntimeError(f"Missing required configuration in .env: {', '.join(missing)}")

    file_path = Path(file_path_str)
    if not file_path.is_file():
        raise FileNotFoundError(f"Report file not found: {file_path}")

    uploader = JiraUploader(
        base_url=base_url,
        email=email,
        api_token=api_token,
        issue_key=issue_key,
        timeout=60,
        verify_ssl=verify_ssl,
    )

    print(f"Jira issue      : {issue_key}")
    print(f"Attachment path : {file_path}")

    attachment_result = None
    already_exists = False

    if skip_duplicate and uploader.attachment_exists(file_path.name, file_path.stat().st_size):
        already_exists = True
        print("Same attachment already exists in Jira, skipping upload.")
    else:
        attachment_result = uploader.upload_attachment(file_path)
        print("Attachment uploaded successfully.")
        print(json.dumps(attachment_result, indent=2))

    if already_exists:
        comment_text = (
            f"{comment_prefix}\n"
            f"Attachment already present on Jira issue: {file_path.name}"
        )
    else:
        comment_text = build_comment_text(
            issue_key=issue_key,
            file_path=file_path,
            attachment_result=attachment_result,
            custom_message=comment_prefix,
        )

    comment_result = uploader.add_comment(comment_text)
    print("Comment added successfully.")
    print(json.dumps(comment_result, indent=2))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
