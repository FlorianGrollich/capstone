import httpx
import json

from fastapi import HTTPException


class VideoService:

    async def upload_video(self, account_id: str, api_key: str, request_body: bytes, metadata: dict | None = None,
                           querystring: dict | None = None):
        base_url = "https://api.bytescale.com"
        path = f"/v2/accounts/{account_id}/uploads/binary"
        url = f"{base_url}{path}"

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/octet-stream"
        }
        if metadata:
            try:
                headers["X-Upload-Metadata"] = json.dumps(metadata)
            except TypeError as e:
                raise ValueError(f"Metadata could not be serialized to JSON: {metadata}") from e

        params_to_send = querystring if querystring is not None else {}

        async with httpx.AsyncClient(timeout=60.0) as client:
            try:
                response = await client.post(
                    url,
                    headers=headers,
                    params=params_to_send,
                    content=request_body
                )
                response.raise_for_status()
                return response.json()
            except httpx.RequestError as exc:
                raise HTTPException(status_code=503, detail=f"Error connecting to upload service: {type(exc).__name__}")
            except httpx.HTTPStatusError as exc:
                error_detail = f"Upload service error ({exc.response.status_code})"
                try:
                    api_error = exc.response.json()
                    if isinstance(api_error, dict) and 'error' in api_error and isinstance(api_error['error'], dict):
                        error_detail = api_error['error'].get('message', error_detail)
                    else:
                        error_detail = f"{error_detail}: {exc.response.text[:200]}"
                except (json.JSONDecodeError, AttributeError, TypeError):
                    error_detail = f"{error_detail}: {exc.response.text[:200]}"
                raise HTTPException(status_code=exc.response.status_code, detail=error_detail)
            except ValueError as ve:
                raise HTTPException(status_code=400, detail=str(ve))
