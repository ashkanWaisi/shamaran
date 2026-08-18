"""Validate the model's public JSON action protocol."""

import json

from pydantic import ValidationError

from shamaran.exceptions import ProviderError

from .models import AgentEnvelope


def parse_envelope(content: str) -> AgentEnvelope:
    try:
        payload = json.loads(content)
        return AgentEnvelope.model_validate(payload)
    except (json.JSONDecodeError, ValidationError) as exc:
        raise ProviderError(
            "The model returned an invalid agent response. Try again or choose a model with reliable JSON support."
        ) from exc
