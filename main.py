import json
import re
import subprocess
import sys
from json import JSONDecodeError
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
        self.charge_percent: int = int()
        self.capacity: Optional[int] = None
        self.until_charged_or_discharged: str = str()
        self.show_conservation_info: bool = False
        self.conservation: Optional[bool] = False
        self.warning_icon: bool = False
        self.charging_mode_selected: bool = False

        self.ui.radio_rapid_charge.clicked.connect(
            lambda: self.switch_charging_mode(rapid=True),
        )
        self.ui.radio_regular_charge.clicked.connect(
            lambda: self.switch_charging_mode(rapid=False),
        )
        self.ui.checkbox_conservation.clicked.connect(
            lambda: self.switch_conservation_mode(
                activate=self.ui.checkbox_conservation.isChecked()
            )
        )

        self.battery_status_timer = QtCore.QTimer(self)
        self.battery_status_timer.start(const.Settings.TIMER_INTERVAL_MS.value)
        self.battery_status_timer.timeout.connect(self.update_battery_status)

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

    def switch_charging_mode(self, rapid: bool) -> None:
        result = self.toggle_charging_mode(rapid=rapid)

        if result:
            self.save_current_charging_mode(
                rapid_selected=rapid,
                conservation=False,
            )
            self.charging_mode_selected = True
            self.conservation = False

        self.setup_ui_charging_mode(rapid_selected=rapid, activated=result)

    def toggle_charging_mode(self, rapid: bool) -> bool:
        command = (
            const.Command.RAPID_ON.value if rapid
            else const.Command.RAPID_OFF.value
        )

        return self.run_shell_command(command=command).returncode == 0

    def setup_ui_charging_mode(
            self, rapid_selected: bool, activated: bool,
    ) -> None:
        if not activated:
            if rapid_selected:
                self.ui.radio_rapid_charge.setChecked(False)
                self.ui.radio_rapid_charge.setEnabled(True)
            else:
                self.ui.radio_regular_charge.setChecked(False)
                self.ui.radio_regular_charge.setEnabled(True)
        else:
            if rapid_selected:
                self.ui.radio_rapid_charge.setEnabled(False)
                self.ui.radio_rapid_charge.setChecked(True)
                self.ui.radio_regular_charge.setChecked(False)
                self.ui.radio_regular_charge.setEnabled(True)
                self.ui.checkbox_conservation.setChecked(False)
            else:
                self.ui.radio_regular_charge.setEnabled(False)
                self.ui.radio_regular_charge.setChecked(True)
                self.ui.radio_rapid_charge.setChecked(False)
                self.ui.radio_rapid_charge.setEnabled(True)

    def warning(self, reason: str) -> None:
        warning_info = const.WarningInfo[reason].value
        charging_status = warning_info.get('charging_status')
        charge_percent = warning_info.get('charge_percent')
        message = warning_info.get('message')

        if charging_status:
            self.charging_status = charging_status
            self.ui.label_charging_status.setText(charging_status)
        if charge_percent is not None:
            self.ui.progressbar_battery.setValue(charge_percent)
        if message:
            self.ui.label_message.setText(message)

        self.set_tray_icon(warning=True)

    def reset_ui_checkboxes(self):
        self.ui.radio_rapid_charge.setChecked(False)
        self.ui.radio_rapid_charge.setEnabled(True)
        self.ui.radio_regular_charge.setChecked(False)
        self.ui.radio_regular_charge.setEnabled(True)
        self.ui.checkbox_conservation.setChecked(False)

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
            return None

        data = re.split(r'[\n,]', data)

        try:
            charging_status = data[0][11:]
            charge_percent = int(data[1][:-1].strip())
            until_charged_or_discharged = data[2]
            capacity_match = re.findall(r'\d+', data[3][-4:])
            capacity = int(''.join(capacity_match)) if capacity_match else None
        except (ValueError, IndexError):
            self.warning(reason='INCORRECT_DATA')
            return None

        return (
            charging_status,
            charge_percent,
            until_charged_or_discharged,
            capacity,
        )

    def update_battery_status(self) -> None:
        data = self.get_battery_data()
        validated_data = self.validate_battery_data(data)

        if validated_data is None:
            return

        (
            charging_status,
            charge_percent,
            until_charged_or_discharged,
            capacity,
        ) = validated_data

        self.charging_status = charging_status
        self.charge_percent = charge_percent
        self.until_charged_or_discharged = until_charged_or_discharged
        self.capacity = capacity

        self.update_ui_battery_status()

        if self.charging_mode_selected:
            self.check_battery_conservation()

    def update_ui_battery_status(self) -> None:
        self.ui.label_charging_status.setText(self.charging_status)
        self.ui.progressbar_battery.setValue(self.charge_percent)

        if not self.charging_mode_selected:
            return
        elif (
                'zero' in self.until_charged_or_discharged
                and self.charging_mode_selected
        ):
            self.ui.label_message.setText(const.Message.DOTS.value)
        elif self.conservation:
            return
        elif self.charging_status in ('Not charging', 'Full'):
            self.ui.label_message.setText(f'Capacity: {self.capacity}%')
        elif self.charging_status in ('Charging', 'Discharging'):
            self.ui.label_message.setText(self.until_charged_or_discharged)

        self.set_tray_icon(warning=False)

    def switch_conservation_mode(self, activate: bool) -> None:
        desired_button_status = activate
        run_command = self.toggle_conservation_mode(activate=activate)

        if not run_command:
            self.ui.checkbox_conservation.setChecked(
                not desired_button_status
            )

        if self.ui.checkbox_conservation.isChecked():
            self.setup_ui_charging_mode(rapid_selected=False, activated=True)
            self.check_battery_conservation()

    def toggle_conservation_mode(self, activate: bool) -> bool:
        command = (
            const.Command.CONSERVATION_ON.value if activate
            else const.Command.CONSERVATION_OFF.value
        )

        return self.run_shell_command(command).returncode == 0

    def check_battery_conservation(self) -> None:
        result = self.sys_conservation_mode_is_active()
        self.show_conservation_info = result

        if result:
            self.handle_active_conservation_mode()
        else:
            self.handle_inactive_conservation_mode()

        if self.charging_mode_selected:
            self.update_ui_conservation(conservation_is_active=result)

    def handle_active_conservation_mode(self) -> None:
        if (
            self.ui.radio_rapid_charge.isChecked()
            or not self.ui.radio_regular_charge.isChecked()
            or not self.ui.checkbox_conservation.isChecked()
        ):
            self.warning(reason='INVALID_CHARGING_MODE_VALUE')
            self.charging_mode_selected = False
            self.reset_ui_checkboxes()
            self.save_current_charging_mode(
                rapid_selected=None,
                conservation=None,
            )

        else:
            if not self.charging_mode_selected or not self.conservation:
                self.charging_mode_selected = True
                self.conservation = True
                self.save_current_charging_mode(
                    rapid_selected=False,
                    conservation=True,
                )

    def handle_inactive_conservation_mode(self) -> None:
        if self.ui.checkbox_conservation.isChecked():
            self.warning(reason='INVALID_CHARGING_MODE_VALUE')
            self.charging_mode_selected = False
            self.reset_ui_checkboxes()
            self.save_current_charging_mode(
                rapid_selected=None,
                conservation=None,
            )

        else:
            if not self.charging_mode_selected or self.conservation:
                self.charging_mode_selected = True
                self.conservation = False

                self.save_current_charging_mode(
                    rapid_selected=(
                        self.ui.radio_rapid_charge.isChecked() if True
                        else self.ui.radio_regular_charge.isChecked()
                    ),
                    conservation=False,
                )

    def update_ui_conservation(self, conservation_is_active: bool) -> None:
        if not conservation_is_active:
            return

        if self.charging_status == 'n/a':
            return
        elif self.charging_status == 'Discharging':
            self.conservation_normal_info()
        elif self.charge_percent > const.Settings.CHARGE_LIMIT_WARNING.value:
            self.warning(reason='CHARGE_LIMIT')
        else:
            self.conservation_normal_info()

    def conservation_normal_info(self) -> None:
        self.set_tray_icon(warning=False)

        if self.charging_status == 'Not charging':
            self.ui.label_message.setText(
                'Conservation is complete. '
                f'Last full capacity: {self.capacity}%'
            )
        elif self.charging_status == 'Charging':
            self.ui.label_message.setText(
                const.Message.CONSERVATION.value
            )
        elif self.charging_status == 'Discharging':
            if 'zero' in self.until_charged_or_discharged:
                self.ui.label_message.setText(const.Message.DOTS.value)
            else:
                self.ui.label_message.setText(
                    self.until_charged_or_discharged
                )

    def set_tray_icon(self, warning: bool) -> None:
        icon = (
            const.Resources.ICON_PNG.value if not warning
            else const.Resources.ICON_WARNING_PNG.value
        )

        if warning != self.warning_icon:
            self.warning_icon = warning
            self.tray_icon.setIcon(QtGui.QIcon(icon))

    def sys_conservation_mode_is_active(self) -> bool:
        return bool(int(self.run_shell_command(
            const.Command.CHECK_CONSERVATION.value
        ).stdout))

    def save_current_charging_mode(
            self,
            rapid_selected: Optional[bool],
            conservation: Optional[bool] = False
    ) -> None:
        print('current charging mode saved')
        with open(
                const.Settings.CHARGING_MODE_JSON.value, 'w+', encoding='utf8',
        ) as write_file:
            json.dump({
                'rapid_selected': rapid_selected,
                'conservation': conservation,
            }, write_file, indent=4)

    def load_last_charging_mode(self) -> None:
        charging_mode_path = const.Settings.CHARGING_MODE_JSON.value

        try:
            with open(charging_mode_path, 'r') as read_file:
                mode = json.load(read_file)
                rapid_is_active = mode.get('rapid_selected')
                conservation = mode.get('conservation')

            if not isinstance(rapid_is_active, bool) or not isinstance(
                    conservation, bool):
                raise ValueError('Invalid charging mode value')

            self.setup_ui_charging_mode(
                rapid_selected=rapid_is_active,
                activated=True,
            )
            self.ui.checkbox_conservation.setChecked(conservation)
            self.charging_mode_selected = True
            self.conservation = conservation

        except (FileNotFoundError, JSONDecodeError, ValueError):
            self.warning(reason='INVALID_CHARGING_MODE_VALUE')
        except PermissionError:
            self.warning(reason='PERMISSION_DENIED')

        self.update_battery_status()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = BatteryCharging()
    window.show()

    window.load_last_charging_mode()

    sys.exit(app.exec())
