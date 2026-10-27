from device_repair.tests import test_state as previous
from menu_repair.tests.machine import Machine
from pathlib import Path
previous.Machine=Machine
previous.WORK=Path('/workspace/build_work/menu-1113')
Tests=previous.Tests
