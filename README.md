
# 🐞 bestdebug.py — Ultimate Python Debugging Module (v4.0.0)

**A flexible and powerful logging module for modern Python development.**

> Now with Remote Logging, Log Filters, JSON support, and full customization.

---

## 🔧 Features

- ✅ Simple `log()` function with levels, tags, stack trace, and location.
- 🖍️ Colored console output with level-based theming.
- 📂 Log output options: console, file, both, or custom callback.
- 🪝 Remote logging to any HTTP endpoint.
- 🧠 Smart filtering by module, function, level, or tags.
- 📜 JSON-formatted output support.
- 🕵️ `watch()` to inspect variables easily.
- 💥 `assert_log()` to raise + log on failed conditions.
- ⏱️ `@timeit` decorator to benchmark functions.
- 🧪 Full configuration API and global singleton for easy usage.

---

## 📦 Installation

No external dependencies required. Just drop the file in your project:

```bash
bestdebug.py
```

Then in your Python code:

```python
from bestdebug import log, timeit, assert_log, configure
```

---

## 🚀 Quick Start

```python
from bestdebug import log, watch, timeit, assert_log

log("This is an info log")
log("Something went wrong!", level="ERROR")
watch(variable1=42, name="Alice")

@timeit()
def slow_func():
    time.sleep(0.5)

slow_func()

assert_log(1 + 1 == 2, "Math is broken")
```

---

## 📚 API Overview

### 🔹 Logging

```python
log("Message", level="INFO", tags={"network"}, include_stack=True)
```

Levels: `INFO`, `DEBUG`, `WARN`, `ERROR`, `TIMER`

---

### 🔹 Watch Variables

```python
watch(counter=10, user="Bob")
# Output: WATCH: counter=10, user='Bob'
```

---

### 🔹 Assert with Logging

```python
assert_log(user is not None, "User should not be None")
```

---

### 🔹 Time Execution

```python
@timeit("heavy_task")
def compute():
    ...
```

---

## ⚙️ Configuration

```python
configure(output="both", log_file="logs/output.log", use_colors=False)
```

Or individually:

```python
set_output("file")
enable_json()
enable_stack()
set_tags("auth", "api")
set_filters(levels=["ERROR"], modules=["mymodule"])
set_remote_url("https://my-log-server/api/logs")
enable_remote()
```

---

## 🎨 Output Customization

### 🔹 Format String

```python
set_format("[{time}] [{level}] {location} {tags} - {message}")
```

- `{time}` – Timestamp  
- `{level}` – Log level  
- `{location}` – File, line, function  
- `{tags}` – Set of tags  
- `{message}` – Your log message  

---

## 🛠 Advanced Filters

```python
set_filters(
    levels=["ERROR", "WARN"],
    modules=["auth", "db"],
    functions=["handle_login"],
    tags=["security"]
)
```

---

## ☁️ Remote Logging

```python
set_remote_url("https://example.com/logs")
enable_remote()
```

Sends log payloads as JSON via HTTP POST.

---

## 🧪 JSON Output

```python
enable_json()
```

Logs become machine-readable JSON:

```json
{
  "timestamp": "2025-07-15 14:23:12.345",
  "level": "ERROR",
  "location": "main.py:42 in myfunc()",
  "tags": ["api"],
  "message": "Something went wrong"
}
```

---

## 🔁 Thread-Safe

All log operations are thread-safe using internal locks.
