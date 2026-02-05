"""Python translation of the VB.NET Windows Service installer logic.

Requires: pywin32 (win32service, win32serviceutil, etc.)
"""

import sys

import servicemanager
import win32event
import win32service
import win32serviceutil

SERVICE_NAME = "KCTRP"
SERVICE_DISPLAY_NAME = "KCTRP"
SERVICE_DESCRIPTION = "Cold Turkey background service (translated installer example)."


class KCTRPService(win32serviceutil.ServiceFramework):
    """Minimal Windows Service class to mirror VB.NET ServiceBase usage."""

    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION

    def __init__(self, args):
        super().__init__(args)
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)

    def SvcDoRun(self):
        servicemanager.LogInfoMsg(f"{SERVICE_NAME} service started.")
        win32event.WaitForSingleObject(self.stop_event, win32event.INFINITE)
        servicemanager.LogInfoMsg(f"{SERVICE_NAME} service stopped.")


def install_service():
    """Install the service as LocalSystem and set it to start automatically."""
    win32serviceutil.InstallService(
        pythonClassString=f"{__name__}.KCTRPService",
        serviceName=SERVICE_NAME,
        displayName=SERVICE_DISPLAY_NAME,
        description=SERVICE_DESCRIPTION,
        startType=win32service.SERVICE_AUTO_START,
    )
    win32serviceutil.SetServiceCustomOption(
        SERVICE_NAME,
        "RunAs",
        "LocalSystem",
    )


def main():
    if len(sys.argv) > 1:
        win32serviceutil.HandleCommandLine(KCTRPService)
    else:
        print("Usage: python -m gitops_feedback_app.windows_service [install|remove|start|stop]")


if __name__ == "__main__":
    main()
