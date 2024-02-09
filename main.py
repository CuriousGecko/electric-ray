import json
import os
import re
import subprocess
import sys
import time

from PySide6 import QtCore, QtGui, QtWidgets

from ui_main import Ui_MainWindow


class BatteryCharging(QtWidgets.QMainWindow):
    MODES = {
        'rapid': '0x07',
        'slow': '0x08',
        'activate_conservation': '0x03',
        'deactivate_conservation': '0x05',
    }

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.current_charge = None
        self.charging_status = None
        self.capacity = None
        self.conservation_info = False
        self.warning_icon = False

        self.ui.radio_rapid_charge.clicked.connect(
            lambda: self.charging_mode_changed('rapid'),
        )
        self.ui.radio_slow_charge.clicked.connect(
            lambda: self.charging_mode_changed('slow'),
        )
        self.ui.button_conservation.clicked.connect(self.battery_conservation)

        self.battery_timer = QtCore.QTimer(self)
        self.battery_timer.start(3000)
        self.battery_timer.timeout.connect(self.battery_status)

        self.conservation_timer = QtCore.QTimer(self)
        self.conservation_timer.start(3000)
        self.conservation_timer.timeout.connect(self.battery_conservation)

        self.setWindowIcon(QtGui.QIcon(':images/scramp_fish.png'))

        self.tray_icon = QtWidgets.QSystemTrayIcon(self)
        self.tray_icon.setIcon(QtGui.QIcon(':images/scramp_fish.png'))
        self.tray_icon.setVisible(True)
        self.tray_icon.activated.connect(self.tray_icon_activated)

        show_action = QtGui.QAction("Open Scramp-fish", self)
        exit_action = QtGui.QAction("Quit", self)
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

    def charging_mode_changed(self, mode):
        activation = self.run_sh_command(
            f'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC {self.MODES[mode]}" '
            '| tee /proc/acpi/call'
        )
        result = activation.returncode == 0
        self.setup_ui_charging_mode(mode, activated=result)

    def run_sh_command(self, command):
        return subprocess.run(
            ['pkexec', 'sh', '-c', command],
            shell=False,
            text=True,
            capture_output=True,
        )

    def setup_ui_charging_mode(self, mode, activated: bool):
        if not activated:
            if mode == 'rapid':
                self.ui.radio_rapid_charge.setChecked(False)
            elif mode == 'slow':
                self.ui.radio_slow_charge.setChecked(False)
        else:
            if mode == 'rapid':
                self.ui.radio_rapid_charge.setEnabled(False)
                self.ui.radio_rapid_charge.setChecked(True)
                self.ui.radio_slow_charge.setChecked(False)
                self.ui.radio_slow_charge.setEnabled(True)
                self.ui.button_conservation.setChecked(False)
                self.save_current_charging_mode('rapid')
            elif mode == 'slow':
                self.ui.radio_slow_charge.setEnabled(False)
                self.ui.radio_slow_charge.setChecked(True)
                self.ui.radio_rapid_charge.setChecked(False)
                self.ui.radio_rapid_charge.setEnabled(True)
                self.save_current_charging_mode('slow')

    def battery_status(self):
        try:
            check_status = subprocess.run(
                ['acpi', '-i'],
                capture_output=True,
                text=True,
                shell=False,
            ).stdout.strip()
        except FileNotFoundError:
            self.ui.label_current_status.setText('n/a')
            self.ui.progressbar_battery.setValue(0)
            self.ui.label_remaining.setText('Check your ACPI client')
            time.sleep(3)

        data = re.split(r'\n|,', check_status)
        current_charge = data[1][:-1].strip()
        charging_status = data[0][11:]

        if not current_charge.isdigit():
            self.ui.label_current_status.setText('n/a')
            self.ui.progressbar_battery.setValue(0)
            self.ui.label_remaining.setText('Data error')
        else:
            self.ui.progressbar_battery.setValue(int(current_charge))
            self.ui.label_current_status.setText(charging_status)
            self.current_charge = int(current_charge)
            self.charging_status = charging_status
            self.capacity = ' '.join(re.findall(r'\d+', data[3][-4:]))
            until_charged_or_discharged = data[2]
            if 'zero' in until_charged_or_discharged:
                self.ui.label_remaining.setText('. . .')
            elif self.conservation_info:
                pass
            elif self.charging_status == 'Not charging':
                self.ui.label_remaining.setText(f'Capacity: {self.capacity}%')
            elif self.charging_status in ('Charging', 'Discharging'):
                self.ui.label_remaining.setText(until_charged_or_discharged)

    def battery_conservation(self):
        sys_conservation_mode_is_active = (
            self.sys_conservation_mode_is_active()
        )
        if self.ui.button_conservation.isChecked():
            if sys_conservation_mode_is_active:
                if not self.ui.radio_slow_charge.isChecked():
                    self.setup_ui_charging_mode('slow', activated=True)
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
                    self.setup_ui_charging_mode('slow', activated=True)

        if self.ui.button_conservation.isChecked():
            self.conservation_info = True
            self.update_ui_conservation_info()

    def activate_conservation_mode(self):
        command = (
            f'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC '
            f'{self.MODES["activate_conservation"]}" '
            f'| tee /proc/acpi/call '
            f'&& echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC 0x08" '
            f'| tee /proc/acpi/call'
        )
        return self.run_sh_command(command)

    def deactivate_conservation_mode(self):
        command = (
            f'echo "\_SB.PCI0.LPC0.EC0.VPC0.SBMC '
            f'{self.MODES["deactivate_conservation"]}" '
            f'| tee /proc/acpi/call'
        )
        return self.run_sh_command(command)

    def update_ui_conservation_info(self):
        if self.charging_status == 'Discharging':
            self._update_discharging_info()
        elif self.current_charge > 65:
            self._update_warning_info()
        elif self.current_charge <= 65:
            self._update_normal_info()

    def _update_discharging_info(self):
        self.conservation_info = False
        if self.warning_icon:
            self._set_tray_icon(':images/scramp_fish.png')
            self.warning_icon = False

    def _update_warning_info(self):
        self.ui.label_remaining.setText(
            'Please, discharge the battery to 60%'
        )
        if not self.warning_icon:
            self._set_tray_icon(':images/scramp_fish_warning.png')
            self.warning_icon = True

    def _update_normal_info(self):
        if self.warning_icon:
            self._set_tray_icon(':images/scramp_fish.png')
            self.warning_icon = False
        if self.charging_status == 'Not charging':
            self.ui.label_remaining.setText(
                f'Conservation is complete. '
                f'Last full capacity: {self.capacity}%'
            )
        elif self.charging_status == 'Charging':
            self.ui.label_remaining.setText('Conservation')

    def _set_tray_icon(self, icon_path):
        self.tray_icon.setIcon(QtGui.QIcon(icon_path))

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
            self.setup_ui_charging_mode('slow', True)
        else:
            charging_mode_warning = 'Select the charging mode.'
            if os.path.exists('charging_mode.json'):
                with open('charging_mode.json', 'r') as read_file:
                    mode = json.load(read_file)
                    charging_mode = mode.get(
                        'charging_mode'
                    )
                    if charging_mode == ('slow' or 'rapid'):
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
