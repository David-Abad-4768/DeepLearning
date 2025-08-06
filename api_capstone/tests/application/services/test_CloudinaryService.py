import io
from pathlib import Path

import cloudinary
import cloudinary.uploader
import pytest
from fastapi import UploadFile

from app.application.services.CloudinaryService import CloudinaryService
from app.infrastructure.Settings import settings


def test_init_calls_cloudinary_config(monkeypatch):
    called = {}

    def fake_config(**kwargs):
        called.update(kwargs)

    monkeypatch.setattr(cloudinary, "config", fake_config)
    monkeypatch.setattr(settings, "cloudinary_cloud_name", "cn")
    monkeypatch.setattr(settings, "cloudinary_api_key", "key")
    monkeypatch.setattr(settings, "cloudinary_api_secret", "secret")

    CloudinaryService()
    assert called == {
        "cloud_name": "cn",
        "api_key": "key",
        "api_secret": "secret",
        "secure": True,
    }


@pytest.fixture(autouse=True)
def stub_config(monkeypatch):
    monkeypatch.setattr(cloudinary, "config", lambda **kwargs: None)
    yield


@pytest.mark.parametrize("input_file", ["/tmp/img.png", Path("/tmp/img.png")])
def test_upload_image_with_path(monkeypatch, tmp_path, input_file):
    fake_url = "https://example.com/foo.png"
    calls = []

    def fake_upload(source, **kwargs):
        calls.append((source, kwargs))
        return {"secure_url": fake_url}

    monkeypatch.setattr(cloudinary.uploader, "upload", fake_upload)

    svc = CloudinaryService()
    if isinstance(input_file, Path):
        p = tmp_path / "img.png"
        p.write_bytes(b"data")
        input_file = p

    result = svc.upload_image(
        input_file,
        folder="f",
        public_id="id",
        overwrite=True,
        resource_type="res",
        opt1="v1",
    )
    assert result == fake_url

    src, opts = calls[0]
    assert src == str(input_file)
    assert opts["folder"] == "f"
    assert opts["public_id"] == "id"
    assert opts["overwrite"] is True
    assert opts["resource_type"] == "res"
    assert opts["opt1"] == "v1"
