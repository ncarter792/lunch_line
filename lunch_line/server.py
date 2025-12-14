"""
HTTP server entrypoint for Lunch Line.

This module exposes a small FastAPI app intended to run on Google Cloud Run
or locally during development. It provides:

- GET "/": basic health check endpoint.
- POST "/pubsub": receiver for Google Cloud Pub/Sub push messages (e.g.,
  Gmail push notifications). The handler decodes the message and can invoke
  the calendar population pipeline.

Secrets such as the calendar ID and Google auth token (token.json) are
provided via environment variables or (still TODO) pulled from Google Secret Manager.
"""

import base64
import json
import logging
import os

from typing import Any, Dict

from fastapi import FastAPI, Request

from .populate_calendar import run as run_pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()


@app.get("/")
async def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/pubsub")
async def pubsub_push(request: Request) -> None:
    body = await request.json()
    message = body.get("message", {})
    data_b64 = message.get("data")
    if data_b64:
        try:
            decoded = base64.b64decode(data_b64).decode("utf-8")
            payload = json.loads(decoded)
        except Exception:
            payload = {"raw": decoded if 'decoded' in locals() else None}
    else:
        payload = {}

    logger.info(f"Pub/Sub push received: keys={list(payload.keys())}")

    # TODO: Use payload to fetch email/attachment. For now, run the calendar pipeline in a basic mode.
    # This assumes the process can determine the latest menu PDF internally.
    # Will replace this call with more specific behavior once Gmail integration is added.
    try:
        run_pipeline("/tmp/latest_menu.pdf")  # TODO 
    except Exception as e:
        logger.error(f"Pipeline error: {e}")
