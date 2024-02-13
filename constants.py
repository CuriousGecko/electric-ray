from enum import Enum
from typing import Union


class Settings(Enum):
    CHARGING_MODE_JSON: str = 'charging_mode.json'
    TIMER_INTERVAL_MS: int = 3000
    CHARGE_LIMIT: int = 65


class Resources(Enum):
    ICON_PNG: str = ':images/scramp_fish.png'
    ICON_WARNING_PNG: str = ':images/scramp_fish_warning.png'


class WarningInfo(Enum):
    NO_ACPI: dict[str, Union[str, int]] = {
        'status': 'n/a',
        'charge': 0,
        'message': 'Check your ACPI client',
    }
    INCORRECT_DATA: dict[str, Union[str, int]] = {
        'status': 'n/a',
        'charge': 0,
        'message': 'Data error',
    }
    CHARGE_LIMIT: dict[str, Union[str, int]] = {
        'message': 'Please discharge the battery to 60%.',
    }
    CHARGING_MODE: dict[str, Union[str, int]] = {
        'message': 'Please select the charging mode.',
    }


class Command(Enum):
    RAPID_ON: str = [
        'pkexec', 'sh', '-c',
        'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x07" '
        '| tee /proc/acpi/call'
    ]
    SLOW_ON: str = [
        'pkexec', 'sh', '-c',
        'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x08" '
        '| tee /proc/acpi/call'
    ]
    BAT_INFO: str = [
        'acpi', '-i'
    ]
    CONSERVATION_ON: str = [
        'pkexec', 'sh', '-c',
        'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x03" '
        '| tee /proc/acpi/call '
        '&& echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x08" '
        '| tee /proc/acpi/call'
    ]
    CONSERVATION_OFF: str = [
        'pkexec', 'sh', '-c',
        'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x05" '
        '| tee /proc/acpi/call'
    ]
    CHECK_CONSERVATION: str = [
        'cat',
        '/sys/bus/platform/drivers'
        '/ideapad_acpi/VPC2004:00/conservation_mode'
    ]


class MenuAction(Enum):
    SHOW_WINDOW = 'Open Scramp-fish'
    QUIT = 'Quit'
