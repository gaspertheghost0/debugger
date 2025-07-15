import os
import time
import traceback
import inspect
import threading
import json
from datetime import datetime
from urllib import request

__all__ = [
    "log", "watch", "assert_log", "timeit", "configure", "set_tags",
    "clear_tags", "enable_level", "disable_level", "enable_stack",
    "disable_stack", "enable_colors", "disable_colors", "set_output",
    "set_format", "set_whitelist", "set_filters", "enable_json",
    "disable_json", "enable_remote", "disable_remote", "set_remote_url",
    "get_logger"
]

class DebugLogger:
    COLOR_CODES = {
        "reset": "\033[0m",
        "bold": "\033[1m",
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "gray": "\033[90m",
    }

    LEVEL_COLORS = {
        "INFO": "cyan",
        "WARN": "yellow",
        "ERROR": "red",
        "DEBUG": "green",
        "TIMER": "magenta"
    }

    def __init__(self):
        self.lock = threading.Lock()
        self.tags = set()
        self.filters = {
            "modules": set(),
            "functions": set(),
            "levels": set(),
            "tags": set()
        }
        self.output = "console"  # console, file, both, callback
        self.callback = None
        self.whitelist = set()
        self.log_file = "debug.log"
        self.use_colors = True
        self.include_stack = False
        self.enabled_levels = {"INFO", "DEBUG", "WARN", "ERROR", "TIMER"}
        self.log_format = "[{time}] [{level}] {location} {tags} - {message}"
        self.json_output = False
        self.remote_enabled = False
        self.remote_url = None

    def _colorize(self, text, color):
        if self.use_colors and color in self.COLOR_CODES:
            return f"{self.COLOR_CODES[color]}{text}{self.COLOR_CODES['reset']}"
        return text

    def _get_location(self, skip=3):
        frame = inspect.stack()[skip]
        module = inspect.getmodule(frame[0])
        filename = os.path.basename(module.__file__) if module and hasattr(module, '__file__') else "?"
        return f"{filename}:{frame.lineno} in {frame.function}()"

    def _passes_filters(self, level, module_name, function_name, tags):
        f = self.filters
        return (
            (not f["levels"] or level in f["levels"]) and
            (not f["modules"] or module_name in f["modules"]) and
            (not f["functions"] or function_name in f["functions"]) and
            (not f["tags"] or bool(f["tags"] & tags))
        )

    def _write(self, data: str, json_data: dict = None):
        with self.lock:
            if self.output in {"console", "both"}:
                print(data)
            if self.output in {"file", "both"}:
                with open(self.log_file, "a", encoding="utf-8") as f:
                    f.write(data + "\n")
            if self.output == "callback" and self.callback:
                self.callback(data)
            if self.remote_enabled and self.remote_url and json_data:
                threading.Thread(target=self._send_remote, args=(json_data,)).start()

    def _send_remote(self, payload):
        try:
            req = request.Request(self.remote_url, method="POST")
            req.add_header("Content-Type", "application/json")
            request.urlopen(req, data=json.dumps(payload).encode("utf-8"), timeout=5)
        except Exception:
            pass  # don't crash if remote fails

    def _format(self, level, message, tags, location, stack=None):
        tag_str = f"[{','.join(sorted(tags))}]" if tags else ""
        log_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
        if self.json_output:
            payload = {
                "timestamp": log_time,
                "level": level,
                "location": location,
                "tags": list(tags),
                "message": message,
                "stack": stack if stack else None
            }
            return json.dumps(payload), payload
        else:
            formatted = self.log_format.format(
                time=log_time,
                level=level,
                location=location,
                message=message,
                tags=tag_str
            )
            return self._colorize(formatted, self.LEVEL_COLORS.get(level, "")), None

    def log(self, message, *args, level="INFO", tags=None, include_stack=None):
        if level not in self.enabled_levels:
            return

        caller = inspect.stack()[2]
        module = inspect.getmodule(caller[0])
        module_name = module.__name__ if module else "?"
        func_name = caller.function
        if self.whitelist and module_name not in self.whitelist:
            return
        all_tags = self.tags.union(tags or set())
        if not self._passes_filters(level, module_name, func_name, all_tags):
            return

        location = self._get_location()
        message = message % args if args else message
        stack = None
        if include_stack or (include_stack is None and self.include_stack):
            stack = "".join(traceback.format_stack(limit=6)[:-1])

        output_str, json_data = self._format(level, message, all_tags, location, stack)
        self._write(output_str, json_data)

    def watch(self, **kwargs):
        pairs = ", ".join(f"{k}={v!r}" for k, v in kwargs.items())
        self.log("WATCH: " + pairs, level="DEBUG")

    def assert_log(self, condition, message="Assertion failed"):
        if not condition:
            self.log("ASSERT: " + message, level="ERROR", include_stack=True)
            raise AssertionError(message)

    def timeit(self, label=None):
        def decorator(fn):
            def wrapper(*args, **kwargs):
                start = time.perf_counter()
                result = fn(*args, **kwargs)
                duration = (time.perf_counter() - start) * 1000
                self.log(f"{label or fn.__name__} took {duration:.2f}ms", level="TIMER")
                return result
            return wrapper
        return decorator

    # === Configuration API ===
    def configure(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_tags(self, *tags): self.tags = set(tags)
    def clear_tags(self): self.tags.clear()
    def enable_level(self, level): self.enabled_levels.add(level)
    def disable_level(self, level): self.enabled_levels.discard(level)
    def enable_stack(self): self.include_stack = True
    def disable_stack(self): self.include_stack = False
    def enable_colors(self): self.use_colors = True
    def disable_colors(self): self.use_colors = False
    def enable_json(self): self.json_output = True
    def disable_json(self): self.json_output = False
    def enable_remote(self): self.remote_enabled = True
    def disable_remote(self): self.remote_enabled = False
    def set_output(self, mode, callback=None):
        self.output = mode
        self.callback = callback
    def set_format(self, format_str): self.log_format = format_str
    def set_whitelist(self, *modules): self.whitelist = set(modules)
    def set_filters(self, levels=None, modules=None, functions=None, tags=None):
        if levels is not None: self.filters["levels"] = set(levels)
        if modules is not None: self.filters["modules"] = set(modules)
        if functions is not None: self.filters["functions"] = set(functions)
        if tags is not None: self.filters["tags"] = set(tags)
    def set_remote_url(self, url): self.remote_url = url

# Singleton instance
_logger = DebugLogger()

# Public API
log = _logger.log
watch = _logger.watch
assert_log = _logger.assert_log
timeit = _logger.timeit
configure = _logger.configure
set_tags = _logger.set_tags
clear_tags = _logger.clear_tags
enable_level = _logger.enable_level
disable_level = _logger.disable_level
enable_stack = _logger.enable_stack
disable_stack = _logger.disable_stack
enable_colors = _logger.enable_colors
disable_colors = _logger.disable_colors
enable_json = _logger.enable_json
disable_json = _logger.disable_json
enable_remote = _logger.enable_remote
disable_remote = _logger.disable_remote
set_output = _logger.set_output
set_format = _logger.set_format
set_whitelist = _logger.set_whitelist
set_filters = _logger.set_filters
set_remote_url = _logger.set_remote_url
get_logger = lambda: _logger
