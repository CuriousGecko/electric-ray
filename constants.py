from enum import Enum
from typing import Union


class Settings(Enum):
    CHARGING_MODE_JSON: str = 'charging_mode.json'
    TIMER_INTERVAL_MS: int = 3000
    CHARGE_LIMIT_WARNING: int = 65


class Resources(Enum):
    ICON_PNG: str = ':img/icon.png'
    ICON_WARNING_PNG: str = ':img/icon_warning.png'


class WarningInfo(Enum):
    NO_ACPI: dict[str, Union[str, int]] = {
        'charging_status': 'n/a',
        'charge_percent': 0,
        'message': 'Check your ACPI client',
    }
    INCORRECT_DATA: dict[str, Union[str, int]] = {
        'charging_status': 'n/a',
        'charge_percent': 0,
        'message': 'Data error',
    }
    CHARGE_LIMIT: dict[str, Union[str, int]] = {
        'message': 'Please discharge the battery to 60%.',
    }
    INVALID_CHARGING_MODE_VALUE: dict[str, Union[str, int]] = {
        'message': 'Please select the charging mode or conservation.',
    }
    PERMISSION_DENIED: dict[str, Union[str, int]] = {
        'message': "Check permissions of 'charging_mode.json'."
    }


class Command(Enum):
    RAPID_ON: str = [
        'pkexec', 'sh', '-c',
        'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x07" '
        '| tee /proc/acpi/call'
    ]
    RAPID_OFF: str = [
        'pkexec', 'sh', '-c',
        'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x05" '
        '| tee /proc/acpi/call '
        '&& echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x08" '
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


class Menu(Enum):
    SHOW_WINDOW: str = 'Open Electric ray'
    QUIT: str = 'Quit'
    TOOLTIP: str = 'Electric ray'


class Message(Enum):
    DOTS: str = '. . .'
    CONSERVATION: str = 'Conservation in progress.'


class BatteryData(Enum):
    CHARGING_STATUS: int = 0
    CHARGE_PERCENT: int = 1
    UNTIL_CHARGED_OR_DISCHARGED: int = 2
    CAPACITY: int = 3
