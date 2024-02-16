import json
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
        self.charge_percent: int = int()
        self.capacity: Optional[int] = None
        self.until_charged_or_discharged: str = str()
        self.conservation_info: bool = False
        self.warning_icon: bool = False
        self.charging_mode_selected: bool = False

        self.ui.radio_rapid_charge.clicked.connect(
            lambda: self.switch_charging_mode(rapid=True),
        )
        self.ui.radio_regular_charge.clicked.connect(
            lambda: self.switch_charging_mode(rapid=False),
        )
        self.ui.checkbox_conservation.clicked.connect(
            self.switch_conservation_mode
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
            self.charging_mode_selected = True
            self.save_current_charging_mode(rapid=rapid)

        self.setup_ui_charging_mode(clicked_rapid=rapid, activated=result)

    def toggle_charging_mode(self, rapid: bool) -> bool:
        command = (
            const.Command.RAPID_ON.value if rapid
            else const.Command.RAPID_OFF.value
        )

        return self.run_shell_command(command=command).returncode == 0

    def setup_ui_charging_mode(self, clicked_rapid: bool, activated: bool) -> None:
        if not activated:
            if clicked_rapid:
                self.update_rapid_charge_radio(is_checked=False)
                self.ui.radio_rapid_charge.setEnabled(True)
            else:
                self.ui.radio_regular_charge.setChecked(False)
                self.ui.radio_regular_charge.setEnabled(True)
        else:
            if clicked_rapid:
                self.ui.radio_rapid_charge.setEnabled(False)
                self.ui.radio_rapid_charge.setChecked(True)
                self.ui.radio_regular_charge.setChecked(False)
                self.ui.radio_regular_charge.setEnabled(True)
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
            self.update_charging_status_label(charging_status=charging_status)
        if charge_percent is not None:
            self.update_battery_progressbar(charge_percent=charge_percent)
        if message:
            self.update_message_label(message=message)

        self.set_tray_icon(warning=True)

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
        self.update_charging_status_label(self.charging_status)
        self.update_battery_progressbar(self.charge_percent)

        if not self.charging_mode_selected:
            return
        elif (
            'zero' in self.until_charged_or_discharged
            and self.charging_mode_selected
        ):
            self.update_message_label(const.Message.DOTS.value)
        elif self.conservation_info:
            return
        elif self.charging_status in ('Not charging', 'Full'):
            self.update_message_label(f'Capacity: {self.capacity}%')
        elif self.charging_status in ('Charging', 'Discharging'):
            self.update_message_label(self.until_charged_or_discharged)

        self.set_tray_icon(warning=False)

    def update_rapid_charge_radio(self, is_checked: bool) -> None:
        self.ui.radio_rapid_charge.setChecked(is_checked)

    def update_slow_charge_radio(self, is_checked: bool) -> None:
        self.ui.radio_regular_charge.setChecked(is_checked)

    def update_charging_status_label(self, charging_status: str) -> None:
        self.ui.label_charging_status.setText(charging_status)

    def update_battery_progressbar(self, charge_percent: int) -> None:
        self.ui.progressbar_battery.setValue(charge_percent)

    def update_message_label(self, message: str) -> None:
        self.ui.label_message.setText(message)

    def update_conservation_checkbox(self, is_checked: bool) -> None:
        self.ui.checkbox_conservation.setChecked(is_checked)

    def switch_conservation_mode(self) -> None:
        desired_button_status = self.ui.checkbox_conservation.isChecked()
        result = self.toggle_conservation_mode(
            activate=desired_button_status
        )

        if not result:
            self.update_conservation_checkbox(
                is_checked=not desired_button_status
            )

        if self.ui.checkbox_conservation.isChecked():
            self.check_battery_conservation()

    def toggle_conservation_mode(self, activate: bool) -> bool:
        command = (
            const.Command.CONSERVATION_ON.value if activate
            else const.Command.CONSERVATION_OFF.value
        )

        return self.run_shell_command(command).returncode == 0

    def check_battery_conservation(self) -> None:
        result = self.sys_conservation_mode_is_active()
        self.conservation_info = result

        if result:
            self.handle_active_conservation_mode()
        else:
            self.handle_inactive_conservation_mode()

        self.update_ui_conservation(conservation_is_active=result)

    def handle_active_conservation_mode(self) -> None:
        if (
            self.ui.radio_rapid_charge.isChecked()
            # or not self.charging_mode_selected
            or not self.ui.radio_regular_charge.isChecked()
        ):
            self.warning(reason='INVALID_CHARGING_MODE_VALUE')
            self.charging_mode_selected = False
            self.setup_ui_charging_mode(clicked_rapid=True, activated=False)
            if not self.ui.radio_rapid_charge.isChecked():
                self.save_current_charging_mode(rapid=False)
        else:
            self.charging_mode_selected = True

    def handle_inactive_conservation_mode(self) -> None:
        if (
            self.ui.radio_regular_charge.isChecked()
            and self.ui.checkbox_conservation.isChecked()
        ):
            self.warning(reason='INVALID_CHARGING_MODE_VALUE')
            self.charging_mode_selected = False
            self.setup_ui_charging_mode(clicked_rapid=False, activated=False)

    def update_ui_conservation(self, conservation_is_active: bool) -> None:
        if not conservation_is_active:
            self.update_conservation_checkbox(is_checked=False)
            return

        if not self.ui.checkbox_conservation.isChecked():
            self.update_conservation_checkbox(is_checked=True)

        if not self.ui.radio_regular_charge.isChecked():
            self.setup_ui_charging_mode(clicked_rapid=False, activated=True)

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
            self.update_message_label(
                message='Conservation is complete. '
                        f'Last full capacity: {self.capacity}%'
            )
        elif self.charging_status == 'Charging':
            self.update_message_label(
                message=const.Message.CONSERVATION.value
            )
        elif self.charging_status == 'Discharging':
            if 'zero' in self.until_charged_or_discharged:
                return
            else:
                self.update_message_label(
                    message=self.until_charged_or_discharged
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

    def save_current_charging_mode(self, rapid: bool) -> None:
        with open(
                const.Settings.CHARGING_MODE_JSON.value, 'w+', encoding='utf8',
        ) as write_file:
            json.dump({'clicked_rapid': rapid}, write_file, indent=4)

    def load_last_charging_mode(self) -> None:
        charging_mode_path = const.Settings.CHARGING_MODE_JSON.value

        try:
            with open(charging_mode_path, 'r') as read_file:
                mode = json.load(read_file)
                rapid_is_active = mode.get('clicked_rapid')
        except FileNotFoundError:
            self.warning(reason='INVALID_CHARGING_MODE_VALUE')
            return self.update_battery_status()
        except PermissionError:
            self.warning(reason='PERMISSION_DENIED')
            return self.update_battery_status()

        if isinstance(rapid_is_active, bool):
            self.setup_ui_charging_mode(
                clicked_rapid=rapid_is_active, activated=True
            )
            self.charging_mode_selected = True
        else:
            self.warning(reason='INVALID_CHARGING_MODE_VALUE')

        self.update_battery_status()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = BatteryCharging()
    window.show()

    window.load_last_charging_mode()

    sys.exit(app.exec())
