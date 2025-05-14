from pathlib import Path

import pytest
from nonebug import App
from pydantic import AnyUrl as Url
from pytest_mock import MockerFixture


async def test_custom_source(app: App, mocker: MockerFixture, tmp_path: Path):
    from nonebot_plugin_wakatime.config import CustomSource

    (tmp_path / "file1.txt").touch()
    (tmp_path / "dir1").mkdir()
    (tmp_path / "dir1" / "file2.txt").write_bytes(b"test")

    mocker.patch("nonebot_plugin_localstore.get_plugin_data_dir", return_value=tmp_path)

    source1 = CustomSource(uri=Url("https://example.com"))
    assert source1.get() == Url("https://example.com")

    source2 = CustomSource(uri=Path("/path/to/file.txt"))
    with pytest.raises(FileNotFoundError):
        assert source2.get()

    source3 = CustomSource(uri=Path(tmp_path.absolute() / "file1.txt"))
    assert source3.get() == (tmp_path / "file1.txt")

    source4 = CustomSource(uri=Path("file1.txt"))
    assert source4.get() == (tmp_path / "file1.txt")

    source5 = CustomSource(uri=Path("dir1"))
    assert source5.get() == (tmp_path / "dir1" / "file2.txt")
