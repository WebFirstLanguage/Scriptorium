"""Exercise the configured listening port through a disposable Scriptorium site.

Run sequentially with ``python -m unittest discover -s tests/integration -v``.
WFL_EXECUTABLE may select a runtime; otherwise wfl must be on PATH. The default
port cases require loopback port 8080 to be free and never stop other services.
"""

import http.client
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
import time
import unittest


SOURCE = Path(__file__).resolve().parents[2]
STARTUP_SECONDS = 20
BASE_CONFIG = (
    "web_server_bind_address = 127.0.0.1\n"
    "timeout_seconds = 60\n"
    "logging_enabled = false\n"
    "debug_report_enabled = false\n"
)


class ServerPortTests(unittest.TestCase):
    def setUp(self):
        requested = os.environ.get("WFL_EXECUTABLE", "wfl")
        executable = shutil.which(requested)
        self.assertIsNotNone(executable, f"WFL executable not found: {requested}")
        self.executable = str(Path(executable).resolve())
        self.temporary = tempfile.TemporaryDirectory(prefix="scriptorium-port-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name) / "site"
        self.root.mkdir()
        # The runtime searches parent directories for configuration, whereas
        # Scriptorium reads only its own .wflcfg. Keep the absent-file test on
        # loopback too, regardless of the developer's global runtime settings.
        (self.root.parent / ".wflcfg").write_text(BASE_CONFIG, encoding="utf-8")
        runtime_files = [
            Path("main.wfl"),
            Path("lib/scribe/src/scribe.wfl"),
            Path("admin/templates/install.html"),
            *(Path("app") / name for name in
              ("util.wfl", "db.wfl", "auth.wfl", "render.wfl", "site_ext.wfl")),
        ]
        for relative in runtime_files:
            source = SOURCE / relative
            self.assertTrue(source.is_file(), f"Missing runtime source: {source}")
            destination = self.root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        # Never copy a checkout's database, uploads, configuration, or .git.
        (self.root / "static").mkdir()
        self.log_path = self.root.parent / "server.log"
        self.log = self.log_path.open("wb")
        self.addCleanup(self.log.close)
        self.process = None
        self.addCleanup(self.stop_server)

    def stop_server(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=5)

    def server_log(self):
        return self.log_path.read_text(encoding="utf-8", errors="replace")

    def available_port(self, requested=0):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as reservation:
            if os.name == "nt":
                reservation.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            else:
                # Permit a previous test's TIME_WAIT sockets, but not a listener.
                reservation.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                reservation.bind(("127.0.0.1", requested))
            except OSError as exc:
                self.fail(
                    f"Prerequisite: loopback port {requested} must be free; "
                    f"no existing service was stopped ({exc})"
                )
            return reservation.getsockname()[1]

    def assert_installer(self, expected_port, config):
        if config is not None:
            (self.root / ".wflcfg").write_text(
                BASE_CONFIG + "data_dir = runtime-data\n" + config, encoding="utf-8"
            )
        # Also keep the old hardcoded port free when proving the configured
        # case, so a regression can start and explain its actual bind in logs.
        self.available_port(8080)
        self.process = subprocess.Popen(
            [self.executable, "main.wfl"], cwd=self.root,
            stdin=subprocess.DEVNULL, stdout=self.log, stderr=subprocess.STDOUT,
        )
        deadline = time.monotonic() + STARTUP_SECONDS
        last_error = "server has not responded"
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                self.fail(
                    f"Server exited with {self.process.returncode} before serving "
                    f"port {expected_port}:\n{self.server_log()}"
                )
            connection = http.client.HTTPConnection("127.0.0.1", expected_port, timeout=1)
            try:
                connection.request("GET", "/install")
                response = connection.getresponse()
                body = response.read().decode("utf-8")
            except (OSError, http.client.HTTPException) as exc:
                last_error = str(exc)
            else:
                diagnostic = self.server_log()
                self.assertEqual(response.status, 200, diagnostic + "\n" + body)
                self.assertIn("text/html", response.getheader("Content-Type", ""))
                self.assertIn("Set up your site", body)
                self.assertIn('action="/install"', body)
                self.assertIn('name="csrf_token"', body)
                self.assertIn("Scriptorium", body)
                self.assertIn(
                    f"Scriptorium is running at http://127.0.0.1:{expected_port}", diagnostic
                )
                self.assertIn(
                    f"First run — open http://127.0.0.1:{expected_port}/install", diagnostic
                )
                return
            finally:
                connection.close()
            time.sleep(0.1)
        self.fail(
            f"No installer response on configured port {expected_port} within "
            f"{STARTUP_SECONDS}s ({last_error}). Server output:\n{self.server_log()}"
        )

    def test_configured_port_serves_installer_and_updates_startup_urls(self):
        selected = self.available_port()
        self.assertNotEqual(selected, 8080, "OS ephemeral range must exclude default port 8080")
        self.assert_installer(selected, f"web_server_port = {selected}\n")

    def test_missing_port_setting_defaults_to_8080(self):
        self.assert_installer(8080, "# web_server_port intentionally omitted\n")

    def test_missing_config_file_defaults_to_8080(self):
        self.assert_installer(8080, None)


if __name__ == "__main__":
    unittest.main()
