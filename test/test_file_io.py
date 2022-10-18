import textwrap
import os
from reoner.core.pather import Pather


def test_pather_relative_paths():
    path = Pather()
    assert path().endswith("test")

    path = Pather('.')
    assert path().endswith("test")

    path = Pather("./")
    assert path().endswith("test")

    path = Pather("")
    assert path().endswith("test")

    path = Pather("../", "test", "test_data")
    assert path().endswith("test_data")

    path = Pather("../../", "reoner", "test", "test_data")
    assert path().endswith("test_data")


def test_pather_movement():
    path = Pather("test_data")
    assert os.getcwd() != path()

    path.cd()
    assert os.getcwd() == path()

    path = Pather("test_data")
    path.cd('.')
    assert os.getcwd() == path()

    path = Pather("test_data")
    path.cd("audio")
    assert path().endswith("audio")

    path.cd("../../")
    assert path().endswith("test")


def test_pather_get_files():
    path = Pather("test_data/audio")
    expected = textwrap.dedent("""\
        1 - username - Rock Pop - 128BPM - 2022-04-20-04-35.aiff
        4 - username - Orbit - 128BPM - 2022-04-20-04-02.aiff
        5 - username - Approach - 128BPM - 2022-04-20-04-28.aiff
        5 - username - Buuo - 128BPM - 2022-04-20-04-10.aiff
        5 - username - Spiral - 128BPM - 2022-04-20-04-00.aiff
        6 - username - Audio In - 128BPM - 2022-04-18-23-01.aiff
        6 - username - Channel - 128BPM - 2022-04-20-03-57.aiff
        8 - username - Highpass - 128BPM - 2022-04-19-00-17.aiff
        8 - username - Third Space - 128BPM - 2022-04-20-03-59.aiff""")
    assert expected == "\n".join(path.get_files('aiff'))


def test_pather_get_full_path_files():
    expected_base = textwrap.dedent("""\
        1 - username - Rock Pop - 128BPM - 2022-04-20-04-35.aiff
        4 - username - Orbit - 128BPM - 2022-04-20-04-02.aiff
        5 - username - Approach - 128BPM - 2022-04-20-04-28.aiff
        5 - username - Buuo - 128BPM - 2022-04-20-04-10.aiff
        5 - username - Spiral - 128BPM - 2022-04-20-04-00.aiff
        6 - username - Audio In - 128BPM - 2022-04-18-23-01.aiff
        6 - username - Channel - 128BPM - 2022-04-20-03-57.aiff
        8 - username - Highpass - 128BPM - 2022-04-19-00-17.aiff
        8 - username - Third Space - 128BPM - 2022-04-20-03-59.aiff""").split("\n")

    prefix = f"{os.getcwd()}/test_data/audio"
    expected = [f"{prefix}/{i}" for i in expected_base]
    path = Pather('test_data/audio')
    assert expected == path.get_files_full_paths('aiff')


def test_pather_get_full_path_files_with_dot_in_ext():
    expected_base = textwrap.dedent("""\
        1 - username - Rock Pop - 128BPM - 2022-04-20-04-35.aiff
        4 - username - Orbit - 128BPM - 2022-04-20-04-02.aiff
        5 - username - Approach - 128BPM - 2022-04-20-04-28.aiff
        5 - username - Buuo - 128BPM - 2022-04-20-04-10.aiff
        5 - username - Spiral - 128BPM - 2022-04-20-04-00.aiff
        6 - username - Audio In - 128BPM - 2022-04-18-23-01.aiff
        6 - username - Channel - 128BPM - 2022-04-20-03-57.aiff
        8 - username - Highpass - 128BPM - 2022-04-19-00-17.aiff
        8 - username - Third Space - 128BPM - 2022-04-20-03-59.aiff""").split("\n")

    prefix = f"{os.getcwd()}/test_data/audio"
    expected = [f"{prefix}/{i}" for i in expected_base]
    path = Pather('test_data/audio')
    assert expected == path.get_files_full_paths('.aiff')
