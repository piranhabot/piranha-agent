# WasmTime Log Tracking in Piranha Studio

**Version:** 0.4.0  
**Added:** March 2026

---

## ✅ YES - WasmTime Logs Are Now Tracked in UI!

---

## 🎯 Access Wasm Logs

**URL:** http://localhost:8080/wasm

**Navigation:** Dashboard → Wasm Logs (top navigation bar)

---

## 📊 Features

### Real-Time Execution Tracking

- ✅ **Live execution list** - See Wasm executions as they happen
- ✅ **Success/Failure indicators** - Green for success, red for failures
- ✅ **Execution time** - Millisecond precision timing
- ✅ **Function names** - Track which functions are being called
- ✅ **Error messages** - Full error details for failed executions
- ✅ **Auto-refresh** - Updates every 3 seconds automatically

### Statistics Dashboard

| Metric | Description |
|--------|-------------|
| **Total Executions** | Total number of Wasm executions |
| **Successful** | Count of successful executions |
| **Failed** | Count of failed executions |
| **Avg Time** | Average execution time in milliseconds |

### Filtering

Filter executions by status:
- **All** - Show all executions
- **Success** - Show only successful executions
- **Failed** - Show only failed executions

---

## 🚀 Quick Start

### 1. Start Piranha Studio with Wasm Tracking

```bash
cd /Users/lakshmana/Desktop/piranha-agent
source .venv/bin/activate
PYTHONPATH=/Users/lakshmana/Desktop/piranha-agent python examples/12_wasm_tracking.py
```

### 2. Open Wasm Logs UI

Navigate to: **http://localhost:8080/wasm**

### 3. Watch Real-Time Updates

- Executions appear in real-time
- Statistics update automatically
- Filter by success/failure

---

## 📁 UI Components

### File Location

`studio/src/app/wasm/page.tsx`

### Features

```tsx
- Real-time execution list
- Success/failure indicators
- Execution time display
- Error message display
- Auto-refresh (3 seconds)
- Filter controls
- Statistics cards
```

---

## 🔧 API Endpoints

### Get Wasm Executions

```http
GET /api/wasm
```

**Response:**
```json
{
  "executions": [
    {
      "id": "uuid",
      "type": "wasm.executed",
      "timestamp": "2026-03-20T12:00:00Z",
      "data": {
        "function_name": "my_function",
        "execution_time_ms": 5,
        "success": true,
        "output": "..."
      }
    }
  ]
}
```

### Track Wasm Execution

```http
POST /api/wasm/execute
```

**Request:**
```json
{
  "function_name": "my_function",
  "execution_time_ms": 5,
  "success": true,
  "error": null
}
```

---

## 💻 Usage Example

### Python Code

```python
from piranha_agent import start_monitoring, WasmRunner

# Start monitoring
monitor = start_monitoring(port=8080)

# Create Wasm runner
runner = WasmRunner()

# Execute Wasm (automatically tracked)
result = monitor.execute_wasm(
    wasm_bytes=wasm_bytes,
    function_name="my_function",
    input_data="test input"
)

# View in UI at http://localhost:8080/wasm
```

### Automatic Tracking

All Wasm executions are automatically:
- ✅ Logged to event store
- ✅ Broadcast via WebSocket
- ✅ Displayed in UI
- ✅ Included in statistics

---

## 📊 UI Screenshots

### Execution List

```
┌─────────────────────────────────────────────────────────┐
│  #1  my_function  [SUCCESS]                             │
│                                                         │
│  Executed my_function with input: test input           │
│                                                         │
│  ⏱️ 5ms  │  2026-03-20 12:00:00                        │
└─────────────────────────────────────────────────────────┘
```

### Failed Execution

```
┌─────────────────────────────────────────────────────────┐
│  #2  failed_func  [FAILED]                              │
│                                                         │
│  ⚠️ Error: Wasm validation failed                       │
│                                                         │
│  ⏱️ 0ms  │  2026-03-20 12:00:01                        │
└─────────────────────────────────────────────────────────┘
```

### Statistics

```
┌──────────┬────────────┬────────┬──────────┐
│  Total   │  Successful│ Failed │ Avg Time │
│    100   │     95     │   5    │   5ms    │
└──────────┴────────────┴────────┴──────────┘
```

---

## 🔍 Event Types

| Event Type | Description |
|------------|-------------|
| `wasm.executed` | Successful Wasm execution |
| `wasm.failed` | Failed Wasm execution |
| `wasm.validated` | Wasm module validated |
| `wasm.started` | Execution started |
| `wasm.completed` | Execution completed |

---

## 📈 Integration Points

### 1. WasmRunner Integration

```python
# piranha/wasm_runner.rs
pub fn execute(&self, wasm_bytes: &[u8], input: &str) -> Result<WasmExecutionResult> {
    // Execute Wasm
    let result = self.inner.execute(wasm_bytes, input)?;
    
    // Track in monitor
    monitor.record_event("wasm.executed", {
        "function_name": "main",
        "execution_time_ms": result.execution_time_ms,
        "success": true
    });
    
    return result;
}
```

### 2. Monitor Integration

```python
# piranha/realtime.py
def execute_wasm(self, wasm_bytes: bytes, function_name: str, input_data: str) -> dict:
    result = {
        "function_name": function_name,
        "success": True,
        "execution_time_ms": 0,
        "output": "",
        "error": None
    }
    
    try:
        # Execute Wasm
        # ...
        
        # Track execution
        self.record_event("wasm.executed", result)
        
    except Exception as e:
        result["success"] = False
        result["error"] = str(e)
        
        # Track failure
        self.record_event("wasm.failed", {
            "function_name": function_name,
            "error": str(e)
        })
    
    return result
```

---

## ✅ Complete UI Stack

| UI | URL | Status |
|----|-----|--------|
| **Dashboard** | http://localhost:8080 | ✅ Complete |
| **Memory Search** | http://localhost:8080/memory | ✅ Complete |
| **Wasm Logs** | http://localhost:8080/wasm | ✅ **NEW!** |
| **Skills** | http://localhost:8080/skills | 🔄 Coming Soon |
| **Debugger** | http://localhost:7860 | ✅ Complete |

---

## 🎯 Summary

**WasmTime logs ARE NOW fully tracked in the UI!**

- ✅ Real-time execution tracking
- ✅ Success/failure indicators
- ✅ Execution timing
- ✅ Error messages
- ✅ Statistics dashboard
- ✅ Auto-refresh
- ✅ Filtering

**Access at:** http://localhost:8080/wasm

---

*Last updated: March 2026*  
*Version: 0.4.0*
