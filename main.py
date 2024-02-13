import json
import os
import re
import subprocess
import sys
from typing import Optional

from PySide6 import QtCore, QtGui, QtWidgets

import constants as const
from ui_main import Ui_MainWindow


class BatteryCharging(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.charging_status: str = str()
        self.charge_percentage: int = int()
        self.capacity: Optional[int] = None
        self.until_charged_or_discharged: str = str()
        self.conservation_info: bool = False
        self.warning_icon: bool = False
        self.charging_mode_selected: bool = False

        self.ui.radio_rapid_charge.clicked.connect(
            lambda: self.activate_charging_mode('RAPID'),
        )
        self.ui.radio_slow_charge.clicked.connect(
            lambda: self.activate_charging_mode('SLOW'),
        )
        self.ui.button_conservation.clicked.connect(
            self.check_battery_conservation
        )

        self.battery_status_timer = QtCore.QTimer(self)
        self.battery_status_timer.start(const.Settings.TIMER_INTERVAL_MS.value)
        self.battery_status_timer.timeout.connect(self.battery_status)

        self.setWindowIcon(QtGui.QIcon(const.Resources.ICON_PNG.value))

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(const.Resources.ICON_PNG.value))
        self.tray_icon.setVisible(True)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        show_action = QtGui.QAction(const.MenuAction.SHOW_WINDOW.value, self)
        quit_action = QtGui.QAction(const.MenuAction.QUIT.value, self)
        show_action.triggered.connect(self.show)
        quit_action.triggered.connect(QtWidgets.QApplication.instance().quit)
        self.tray_icon_menu = QtWidgets.QMenu()
        self.tray_icon.setContextMenu(self.tray_icon_menu)
        self.tray_icon_menu.addAction(show_action)
        self.tray_icon_menu.addAction(quit_action)

    def closeEvent(self, event) -> None:
        event.ignore()
        self.hide()

    def tray_icon_activated(self, reason) -> None:
        if reason == self.tray_icon.ActivationReason.Trigger:
            if self.isHidden():
                self.show()
            else:
                self.hide()
        elif reason == self.tray_icon.ActivationReason.DoubleClick:
            self.show()

    def run_shell_command(
            self, command: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*command],
            shell=False,
            text=True,
            capture_output=True,
        )

    def activate_charging_mode(self, mode: str) -> None:
        command = None

        if mode == 'RAPID':
            command = const.Command.RAPID_ON.value
        elif mode == 'SLOW':
            command = const.Command.SLOW_ON.value

        activation = self.run_shell_command(command)
        result = activation.returncode == 0

        if result:
            self.charging_mode_selected = True

        self.setup_ui_charging_mode(mode, activated=result)

    def setup_ui_charging_mode(self, mode: str, activated: bool) -> None:
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

    def warning(self, reason: str) -> None:
        warning_info = const.WarningInfo[reason].value
        status = warning_info.get('status')
        charge = warning_info.get('charge')
        message = warning_info.get('message')

        if status:
            self.charging_status = status
            self.ui.label_current_status.setText(status)
        if charge is not None:
            self.ui.progressbar_battery.setValue(charge)
        if message:
            self.ui.label_message.setText(message)

        self.set_tray_icon('warning')

    def get_battery_data(self) -> Optional[str]:
        try:
            return (
                self.run_shell_command(const.Command.BAT_INFO.value)
            ).stdout.strip()
        except FileNotFoundError:
            self.warning(reason='NO_ACPI')
            return None

    def validate_battery_data(
            self, data: Optional[str]
    ) -> Optional[tuple[str, int, str, Optional[int]]]:
        if data is None:
            return

        data = re.split(r'[\n,]', data)

        try:
            charging_status = data[0][11:]
            charge_percentage = int(data[1][:-1].strip())
            until_charged_or_discharged = data[2]
            capacity_match = re.findall(r'\d+', data[3][-4:])
            capacity = int(''.join(capacity_match)) if capacity_match else None
        except (ValueError, IndexError):
            self.warning(reason='INCORRECT_DATA')
            return None

        return (
            charging_status,
            charge_percentage,
            until_charged_or_discharged,
            capacity,
        )

    def battery_status(self) -> None:
        data = self.get_battery_data()
        validated_data = self.validate_battery_data(data)

        if validated_data is None:
            return

        (
            charging_status,
            charge_percentage,
            until_charged_or_discharged,
            capacity,
        ) = validated_data

        self.charging_status = charging_status
        self.charge_percentage = charge_percentage
        self.until_charged_or_discharged = until_charged_or_discharged
        self.capacity = capacity

        self.update_ui_battery_status()
        self.check_battery_conservation()

    def update_ui_battery_status(self) -> None:
        self.ui.label_current_status.setText(self.charging_status)
        self.ui.progressbar_battery.setValue(self.charge_percentage)

        if (
            'zero' in self.until_charged_or_discharged
            and self.charging_mode_selected
        ):
            self.ui.label_message.setText('. . .')
        elif not self.charging_mode_selected:
            return
        elif self.conservation_info:
            return
        elif self.charging_status in ('Not charging', 'Full'):
            self.ui.label_message.setText(f'Capacity: {self.capacity}%')
        elif self.charging_status in ('Charging', 'Discharging'):
            self.ui.label_message.setText(self.until_charged_or_discharged)

        self.set_tray_icon('normal')

    def check_battery_conservation(self) -> None:
        sys_conservation_mode_is_active = (
            self.sys_conservation_mode_is_active()
        )

        if self.ui.button_conservation.isChecked():
            if sys_conservation_mode_is_active:
                if not self.ui.radio_slow_charge.isChecked():
                    self.setup_ui_charging_mode('SLOW', activated=True)
            else:
                self.ui.button_conservation.setChecked(
                    self.toggle_conservation_mode(
                        activate=True
                    ).returncode == 0
                )
        else:
            if not sys_conservation_mode_is_active:
                self.conservation_info = False
            else:
                deactivation = self.toggle_conservation_mode(activate=False)
                if deactivation.returncode == 0:
                    self.ui.button_conservation.setChecked(False)
                    self.conservation_info = False
                else:
                    self.ui.button_conservation.setChecked(True)
                    self.setup_ui_charging_mode('SLOW', activated=True)

        if self.ui.button_conservation.isChecked():
            self.conservation_info = True
            self.charging_mode_selected = True
            self.update_ui_conservation_info()

    def update_ui_conservation_info(self) -> None:
        if self.charging_status == 'n/a':
            return
        elif self.charging_status == 'Discharging':
            self.conservation_normal_info()
        elif self.charge_percentage > const.Settings.CHARGE_LIMIT.value:
            self.warning(reason='CHARGE_LIMIT')
        else:
            self.conservation_normal_info()

    def conservation_normal_info(self) -> None:
        self.set_tray_icon(mode='normal')

        if self.charging_status == 'Not charging':
            self.ui.label_message.setText(
                f'Conservation is complete. '
                f'Last full capacity: {self.capacity}%'
            )
        elif self.charging_status == 'Charging':
            self.ui.label_message.setText('Conservation in progress.')
        elif self.charging_status == 'Discharging':
            if 'zero' in self.until_charged_or_discharged:
                return
            else:
                self.ui.label_message.setText(
                    self.until_charged_or_discharged
                )

    def toggle_conservation_mode(
            self, activate: bool
    ) -> subprocess.CompletedProcess[str]:
        command = (
            const.Command.CONSERVATION_ON.value if activate
            else const.Command.CONSERVATION_OFF.value
        )

        return self.run_shell_command(command)

    def set_tray_icon(self, mode) -> None:
        modes = {
            'normal': const.Resources.ICON_PNG.value,
            'warning': const.Resources.ICON_WARNING_PNG.value,
        }

        if mode == 'normal' and self.warning_icon:
            self.warning_icon = False
        elif mode == 'warning' and not self.warning_icon:
            self.warning_icon = True

        self.tray_icon.setIcon(QtGui.QIcon(modes[mode]))

    def sys_conservation_mode_is_active(self) -> bool:
        return bool(int(self.run_shell_command(
            const.Command.CHECK_CONSERVATION.value
        ).stdout))

    def save_current_charging_mode(self, mode) -> None:
        with open(
                const.Settings.CHARGING_MODE_JSON.value, 'w+', encoding='utf8',
        ) as write_file:
            json.dump({'charging_mode': mode}, write_file, indent=4)

    def load_last_charging_mode(self) -> None:
        if self.sys_conservation_mode_is_active():
            self.ui.button_conservation.setChecked(True)
            self.setup_ui_charging_mode('SLOW', True)
            self.conservation_info = True
        else:
            if os.path.exists(const.Settings.CHARGING_MODE_JSON.value):
                with open(
                        const.Settings.CHARGING_MODE_JSON.value, 'r'
                ) as read_file:
                    mode = json.load(read_file)
                    charging_mode = mode.get('charging_mode')

                    if charging_mode in ('SLOW', 'RAPID'):
                        self.charging_mode_selected = True
                        self.setup_ui_charging_mode(
                            charging_mode,
                            activated=True,
                        )
                    else:
                        self.warning(reason='CHARGING_MODE')
            else:
                self.warning(reason='CHARGING_MODE')


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = BatteryCharging()
    window.show()
    window.load_last_charging_mode()
    window.battery_status()

    sys.exit(app.exec())
