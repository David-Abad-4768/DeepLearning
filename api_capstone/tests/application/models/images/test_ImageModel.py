# tests/application/models/images/test_ImageModel.py

from pathlib import Path

import pytest
from pydantic import HttpUrl, ValidationError

from app.application.models.images.ImageModel import (GenerateRequest,
                                                      GenerateResponse,
                                                      LoadLoraRequest,
                                                      SimpleMessage,
                                                      TrainLoraResponse)


def test_generate_request_defaults_and_overrides():
    req = GenerateRequest(prompt="foo")
    assert req.prompt == "foo"
    assert req.negative_prompt is None
    assert req.steps == 25
    assert req.guidance_scale == 7.5
    assert req.seed is None

    req2 = GenerateRequest(
        prompt="foo",
        negative_prompt="bar",
        steps=30,
        guidance_scale=2.0,
        seed=123,
    )
    assert req2.negative_prompt == "bar"
    assert req2.steps == 30
    assert req2.guidance_scale == 2.0
    assert req2.seed == 123


@pytest.mark.parametrize("invalid_steps", [0, 51])
def test_generate_request_invalid_steps(invalid_steps):
    with pytest.raises(ValidationError):
        GenerateRequest(prompt="x", steps=invalid_steps)


def test_generate_request_invalid_guidance_scale():
    with pytest.raises(ValidationError):
        GenerateRequest(prompt="x", guidance_scale=0)


def test_generate_response_accepts_path_and_url():
    p = Path("dummy.png")
    resp1 = GenerateResponse(image_path=p)
    assert isinstance(resp1.image_path, Path)

    url = "https://example.com/img.png"
    resp2 = GenerateResponse(image_path=url)
    # Union resolves to Path first, so strings become Path
    assert isinstance(resp2.image_path, Path)


def test_load_lora_request_and_missing():
    lr = LoadLoraRequest(lora_path=Path("/fake/lora.pt"))
    assert isinstance(lr.lora_path, Path)
    with pytest.raises(ValidationError):
        LoadLoraRequest()


def test_simple_message_and_missing():
    sm = SimpleMessage(message="hello")
    assert sm.message == "hello"
    with pytest.raises(ValidationError):
        SimpleMessage()


def test_train_lora_response_valid_and_missing_fields():
    tr = TrainLoraResponse(
        lora_path=Path("/fake/out"),
        huggingface_repo="user/repo",
        message="done",
    )
    assert isinstance(tr.lora_path, Path)
    assert tr.huggingface_repo == "user/repo"
    assert tr.message == "done"

    # missing message should raise
    with pytest.raises(ValidationError):
        TrainLoraResponse(
            lora_path=Path("/fake/out"),
            huggingface_repo="user/repo",
        )
    # missing lora_path should also raise
    with pytest.raises(ValidationError):
        TrainLoraResponse(
            huggingface_repo="user/repo",
            message="done",
        )
