import csv
import os
import stat
import subprocess
import threading
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable, Optional

from gitops_feedback_app.constants import TIME_FORMAT
from gitops_feedback_app.crypto import Simple3Des
from gitops_feedback_app.ini_file import IniFile


@dataclass
class ServiceConfig:
    settings_path: Path
    host_path: Path
    encryption_key: str = "ct_textbox"
    timer_interval: int = 10


class ColdTurkeyService:
    def __init__(self, config: ServiceConfig) -> None:
        self.config = config
        self.ct_mutex = threading.Lock()
        self.timer_thread = threading.Thread(target=self._timer_loop, daemon=True)
        self.stop_event = threading.Event()
        self.encryption = Simple3Des(self.config.encryption_key)
        self.stream_writer: Optional[object] = None

    def on_start(self) -> None:
        self._ensure_ini()
        ini_file = IniFile.load(self.config.settings_path)
        time_left_date = self._parse_time(ini_file)
        if (time_left_date - datetime.now()).total_seconds() <= 0:
            self.stop_me()
            return

        self._prepare_hosts()
        self.timer_thread.start()

    def on_stop(self) -> None:
        self.stop_event.set()

    def _timer_loop(self) -> None:
        while not self.stop_event.is_set():
            self.timer_elapsed()
            self._handle_add_to_hosts()
            self.stop_event.wait(self.config.timer_interval)

    def timer_elapsed(self) -> None:
        ini_file = IniFile.load(self.config.settings_path)
        time_left_date = self._parse_time(ini_file)
        ini_time_changing = ini_file.get_key_value("Time", "TimeChanging")
        ini_process_list = ini_file.get_key_value("Process", "List")
        if ini_process_list != "null":
            ini_process_list = self.encryption.decrypt_data(ini_process_list)

        self._kill_blocked_processes(ini_process_list)

        time_left = (time_left_date - datetime.now()).total_seconds()
        if ini_time_changing == "no":
            if time_left <= 5:
                self.stop_me()
            else:
                ini_file.set_key_value(
                    "CurrentTime",
                    "Now",
                    self.encryption.encrypt_data(datetime.now().strftime(TIME_FORMAT)),
                )
                ini_file.save()

    def stop_me(self) -> None:
        if self.stream_writer:
            self.stream_writer.close()
        file_reader = ""
        if self.config.host_path.exists():
            self._set_attr_normal(self.config.host_path)
            file_reader = self.config.host_path.read_text(
                encoding="utf-8", errors="ignore"
            )

        if "#### Cold Turkey Entries ####" in file_reader:
            startpos = file_reader.find("#### Cold Turkey Entries ####")
            if startpos <= 1:
                original = ""
            else:
                original = file_reader[: max(0, startpos - 2)]
            self.config.host_path.write_text(original, encoding="utf-8")
            self._set_attr_read_only(self.config.host_path)
            ini_file = IniFile.load(self.config.settings_path)
            ini_file.set_key_value("User", "Done", "yes")
            ini_file.save()
        else:
            self._set_attr_read_only(self.config.host_path)

        self.on_stop()

    def _ensure_ini(self) -> None:
        if self.config.settings_path.exists():
            return
        self._write_default_ini()

    def _write_default_ini(self) -> None:
        ini_file = IniFile.load(self.config.settings_path)
        ini_file.add_section("User")
        ini_file.set_key_value("User", "CustomChecked", "abcdefghijk")
        ini_file.set_key_value("User", "CustomSites", "null")
        ini_file.set_key_value("User", "Done", "no")
        ini_file.set_key_value("User", "NeedsAlerted", "yes")
        ini_file.add_section("Time")
        ini_file.set_key_value(
            "Time",
            "Until",
            self.encryption.encrypt_data(
                (datetime.now() + timedelta(days=7)).strftime(TIME_FORMAT)
            ),
        )
        ini_file.set_key_value("Time", "TimeChanging", "no")
        ini_file.add_section("CurrentTime")
        ini_file.set_key_value(
            "CurrentTime",
            "Now",
            self.encryption.encrypt_data(datetime.now().strftime(TIME_FORMAT)),
        )
        ini_file.add_section("Process")
        ini_file.set_key_value("Process", "List", "null")
        ini_file.save()

    def _parse_time(self, ini_file: IniFile) -> datetime:
        until_value = self.encryption.decrypt_data(ini_file.get_key_value("Time", "Until"))
        return datetime.strptime(until_value, TIME_FORMAT)

    def _prepare_hosts(self) -> None:
        self.config.host_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.config.host_path.exists():
            self.config.host_path.touch()
        self._set_attr_normal(self.config.host_path)
        self.stream_writer = self.config.host_path.open("a", encoding="utf-8")
        self._set_attr_read_only(self.config.host_path)

    def _handle_add_to_hosts(self) -> None:
        add_path = self.config.host_path.parent / "add_to_hosts"
        if add_path.exists():
            to_add = add_path.read_text(encoding="utf-8")
            self._set_attr_normal(self.config.host_path)
            if self.stream_writer:
                self.stream_writer.write(to_add)
                self.stream_writer.flush()
            self._set_attr_read_only(self.config.host_path)
            add_path.unlink(missing_ok=True)

    def _kill_blocked_processes(self, ini_process_list: str) -> None:
        process_names = [name.strip() for name in ini_process_list.split(",") if name.strip()]
        if not process_names:
            return
        processes = self._list_processes()
        for proc_name in processes:
            if proc_name in process_names:
                subprocess.run(
                    ["taskkill", "/F", "/IM", proc_name],
                    check=False,
                    capture_output=True,
                    text=True,
                )

    def _list_processes(self) -> Iterable[str]:
        if os.name != "nt":
            return []
        result = subprocess.run(
            ["tasklist", "/FO", "CSV", "/NH"],
            check=False,
            capture_output=True,
            text=True,
        )
        reader = csv.reader(result.stdout.splitlines())
        return [row[0] for row in reader if row]

    @staticmethod
    def _set_attr_normal(path: Path) -> None:
        if os.name == "nt":
            os.chmod(path, stat.S_IWRITE | stat.S_IREAD)

    @staticmethod
    def _set_attr_read_only(path: Path) -> None:
        if os.name == "nt":
            os.chmod(path, stat.S_IREAD)


def build_default_config(
    settings_path: Optional[Path] = None, host_path: Optional[Path] = None
) -> ServiceConfig:
    if settings_path is None:
        settings_path = Path.cwd() / "ct_settings.ini"
    if host_path is None:
        if os.name == "nt":
            win_dir = os.environ.get("WinDir", r"C:\Windows")
            host_path = Path(win_dir) / "system32" / "drivers" / "etc" / "hosts"
        else:
            host_path = Path.cwd() / "hosts"
    return ServiceConfig(settings_path=settings_path, host_path=host_path)
