import json
import os
import re
import subprocess
import sys
from enum import Enum

from PySide6 import QtCore, QtGui, QtWidgets

from ui_main import Ui_MainWindow


class BatteryCharging(QtWidgets.QMainWindow):
    ICON_PNG = ':images/scramp_fish.png'
    ICON_WARNING_PNG = ':images/scramp_fish_warning.png'
    TIMER_INTERVAL_MS = 3000
    CHARGE_LIMIT = 65

    class ChargingMode(Enum):
        RAPID = '0x07'
        SLOW = '0x08'
        ACTIVATE_CONSERVATION = '0x03'
        DEACTIVATE_CONSERVATION = '0x05'

    class WarningInfo(Enum):
        NO_ACPI = {
            'status': 'n/a',
            'charge': 0,
            'message': 'Check your ACPI client',
        }
        INCORRECT_DATA = {
            'status': 'n/a',
            'charge': 0,
            'message': 'Data error',
        }
        CHARGE_LIMIT = {
            'message': 'Please, discharge the battery to 60%.',
        }

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.charging_status = None
        self.charge_percentage = None
        self.capacity = None
        self.until_charged_or_discharged = None
        self.conservation_info = False
        self.warning_icon = False

        self.ui.radio_rapid_charge.clicked.connect(
            lambda: self.activate_charging_mode('RAPID'),
        )
        self.ui.radio_slow_charge.clicked.connect(
            lambda: self.activate_charging_mode('SLOW'),
        )
        self.ui.button_conservation.clicked.connect(self.battery_conservation)

        self.battery_status_timer = QtCore.QTimer(self)
        self.battery_status_timer.start(self.TIMER_INTERVAL_MS)
        self.battery_status_timer.timeout.connect(self.battery_status)

        self.conservation_timer = QtCore.QTimer(self)
        self.conservation_timer.start(self.TIMER_INTERVAL_MS)
        self.conservation_timer.timeout.connect(self.battery_conservation)

        self.setWindowIcon(QtGui.QIcon(self.ICON_PNG))

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(self.ICON_PNG))
        self.tray_icon.setVisible(True)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        show_action = QtGui.QAction('Open Scramp-fish', self)
        exit_action = QtGui.QAction('Quit', self)
        show_action.triggered.connect(self.show)
        exit_action.triggered.connect(QtWidgets.QApplication.instance().quit)
        self.tray_icon_menu = QtWidgets.QMenu()
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon_menu.addAction(show_action)
        self.tray_icon_menu.addAction(exit_action)

    def closeEvent(self, event):
        event.ignore()
        self.hide()

    def tray_icon_activated(self, reason):
        if reason == self.tray_icon.ActivationReason.Trigger:
            if self.isHidden():
                self.show()
            else:
                self.hide()
        elif reason == self.tray_icon.ActivationReason.DoubleClick:
            self.show()

    def run_shell_command(self, command):
        return subprocess.run(
            ['pkexec', 'sh', '-c', command],
            shell=False,
            text=True,
            capture_output=True,
        )

    def activate_charging_mode(self, mode):
        activation = self.run_shell_command(
            f'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC '
            f'{self.ChargingMode[mode].value}" '
            '| tee /proc/acpi/call'
        )

        result = activation.returncode == 0
        self.setup_ui_charging_mode(mode, activated=result)

    def setup_ui_charging_mode(self, mode, activated: bool):
        if not activated:
            if mode == 'RAPID':
                self.ui.radio_rapid_charge.setChecked(False)
            elif mode == 'SLOW':
                self.ui.radio_slow_charge.setChecked(False)
        else:
            if mode == 'RAPID':
                self.ui.radio_rapid_charge.setEnabled(False)
                self.ui.radio_rapid_charge.setChecked(True)
                self.ui.radio_slow_charge.setChecked(False)
                self.ui.radio_slow_charge.setEnabled(True)
                self.ui.button_conservation.setChecked(False)
                self.save_current_charging_mode('RAPID')
            elif mode == 'SLOW':
                self.ui.radio_slow_charge.setEnabled(False)
                self.ui.radio_slow_charge.setChecked(True)
                self.ui.radio_rapid_charge.setChecked(False)
                self.ui.radio_rapid_charge.setEnabled(True)
                self.save_current_charging_mode('SLOW')

    def warning(self, reason):
        warning_info = self.WarningInfo[reason].value
        status = warning_info.get('status')
        charge = warning_info.get('charge')
        message = warning_info.get('message')

        if status:
            self.charging_status = status
            self.ui.label_current_status.setText(status)
        if charge is not None:
            self.ui.progressbar_battery.setValue(charge)
        if message:
            self.ui.label_remaining.setText(message)

        self.set_tray_icon('warning')

    def get_battery_data(self):
        try:
            return subprocess.run(
                ['acpi', '-i'],
                capture_output=True,
                check=True,
                text=True,
                shell=False,
            ).stdout.strip()
        except FileNotFoundError:
            self.warning(reason='NO_ACPI')
            return None

    def validate_battery_data(self, data):
        data = re.split(r'\n|,', data)

        try:
            charging_status = data[0][11:]
            charge_percentage = int(data[1][:-1].strip())
            until_charged_or_discharged = data[2]
            capacity = ' '.join(re.findall(r'\d+', data[3][-4:]))
        except (ValueError, IndexError):
            self.warning(reason='INCORRECT_DATA')
            return None

        return (
            charging_status,
            charge_percentage,
            until_charged_or_discharged,
            capacity,
        )

    def battery_status(self):
        data = self.get_battery_data()

        if data is None:
            return

        validated_data = self.validate_battery_data(data)

        if validated_data is None:
            return

        (
            charging_status,
            charge_percentage,
            until_charged_or_discharged,
            capacity,
        ) = validated_data

        self.update_ui_battery_status(
            charging_status,
            charge_percentage,
            until_charged_or_discharged,
            capacity
        )

    def update_ui_battery_status(
            self,
            charging_status,
            charge_percentage,
            until_charged_or_discharged,
            capacity
    ):
        self.ui.label_current_status.setText(charging_status)
        self.ui.progressbar_battery.setValue(charge_percentage)

        if 'zero' in until_charged_or_discharged:
            self.ui.label_remaining.setText('. . .')
        elif self.conservation_info:
            self.charging_status = charging_status
            self.charge_percentage = charge_percentage
            self.until_charged_or_discharged = until_charged_or_discharged
            self.capacity = capacity
            return
        elif self.charging_status == 'Not charging':
            self.ui.label_remaining.setText(f'Capacity: {capacity}%')
        elif self.charging_status in ('Charging', 'Discharging'):
            self.ui.label_remaining.setText(until_charged_or_discharged)

        self.set_tray_icon('normal')

    def battery_conservation(self):
        sys_conservation_mode_is_active = (
            self.sys_conservation_mode_is_active()
        )

        if self.ui.button_conservation.isChecked():
            if sys_conservation_mode_is_active:
                if not self.ui.radio_slow_charge.isChecked():
                    self.setup_ui_charging_mode('SLOW', activated=True)
            else:
                self.ui.button_conservation.setChecked(
                    self.activate_conservation_mode().returncode == 0
                )
        else:
            if not sys_conservation_mode_is_active:
                self.conservation_info = False
            else:
                deactivation = self.deactivate_conservation_mode()
                if deactivation.returncode == 0:
                    self.ui.button_conservation.setChecked(False)
                    self.conservation_info = False
                else:
                    self.ui.button_conservation.setChecked(True)
                    self.setup_ui_charging_mode('SLOW', activated=True)

        if self.ui.button_conservation.isChecked():
            self.conservation_info = True
            self.update_ui_conservation_info()

    def activate_conservation_mode(self):
        command = (
            f'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC '
            f'{self.ChargingMode.ACTIVATE_CONSERVATION.value}" '
            f'| tee /proc/acpi/call '
            f'&& echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x08" '
            f'| tee /proc/acpi/call'
        )

        return self.run_shell_command(command)

    def deactivate_conservation_mode(self):
        command = (
            f'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC '
            f'{self.ChargingMode.DEACTIVATE_CONSERVATION.value}" '
            f'| tee /proc/acpi/call'
        )

        return self.run_shell_command(command)

    def update_ui_conservation_info(self):
        if self.charging_status == 'n/a':
            return
        elif self.charging_status == 'Discharging':
            self.update_normal_info()
        elif self.charge_percentage > self.CHARGE_LIMIT:
            self.warning(reason='CHARGE_LIMIT')
        else:
            self.update_normal_info()

    def update_normal_info(self):
        self.set_tray_icon(mode='normal')

        if self.charging_status == 'Not charging':
            self.ui.label_remaining.setText(
                f'Conservation is complete. '
                f'Last full capacity: {self.capacity}%'
            )
        elif self.charging_status == 'Charging':
            self.ui.label_remaining.setText('Conservation in progress.')
        elif self.charging_status == 'Discharging':
            self.ui.label_remaining.setText(self.until_charged_or_discharged)

    def set_tray_icon(self, mode):
        modes = {
            'normal': self.ICON_PNG,
            'warning': self.ICON_WARNING_PNG,
        }

        if mode == 'normal' and self.warning_icon:
            self.warning_icon = False
            self.tray_icon.setIcon(QtGui.QIcon(modes[mode]))
        elif mode == 'warning' and not self.warning_icon:
            self.warning_icon = True
            self.tray_icon.setIcon(QtGui.QIcon(modes[mode]))

    def sys_conservation_mode_is_active(self):
        check_conservation_mode = subprocess.run(
            [
                'cat',
                '/sys/bus/platform/drivers'
                '/ideapad_acpi/VPC2004:00/conservation_mode'
            ],
            text=True,
            capture_output=True
        ).stdout

        return bool(int(check_conservation_mode))

    def save_current_charging_mode(self, mode):
        with open('charging_mode.json', 'w+', encoding='utf8') as write_file:
            json.dump({'charging_mode': mode}, write_file)

    def load_last_charging_mode(self):
        if self.sys_conservation_mode_is_active():
            self.ui.button_conservation.setChecked(True)
            self.setup_ui_charging_mode('SLOW', True)
            self.conservation_info = True
        else:
            charging_mode_warning = 'Select the charging mode.'
            if os.path.exists('charging_mode.json'):
                with open('charging_mode.json', 'r') as read_file:
                    mode = json.load(read_file)
                    charging_mode = mode.get(
                        'charging_mode'
                    )
                    if charging_mode == ('SLOW' or 'RAPID'):
                        self.setup_ui_charging_mode(
                            charging_mode, activated=True,
                        )
                    else:
                        self.ui.label_remaining.setText(charging_mode_warning)
            else:
                self.ui.label_remaining.setText(charging_mode_warning)


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = BatteryCharging()
    # window.show()
    window.load_last_charging_mode()
    window.battery_status()

    sys.exit(app.exec())
