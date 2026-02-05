import argparse
import time
from pathlib import Path

from gitops_feedback_app.service import ColdTurkeyService, build_default_config


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Cold Turkey service loop.")
    parser.add_argument(
        "--settings-path",
        type=Path,
        help="Path to ct_settings.ini (default: ./ct_settings.ini)",
    )
    parser.add_argument(
        "--hosts-path",
        type=Path,
        help="Path to hosts file (default: platform-specific)",
    )
    parser.add_argument(
        "--timer-interval",
        type=int,
        default=None,
        help="Override the polling interval in seconds.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = build_default_config(
        settings_path=args.settings_path,
        host_path=args.hosts_path,
    )
    if args.timer_interval is not None:
        config.timer_interval = args.timer_interval
    service = ColdTurkeyService(config)
    service.on_start()
    try:
        while not service.stop_event.is_set():
            time.sleep(1)
    except KeyboardInterrupt:
        service.on_stop()


if __name__ == "__main__":
    main()
