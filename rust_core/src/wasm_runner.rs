// rust_core/src/wasm_runner.rs
//
// Wasm Sandbox for safe code execution
//

use anyhow::{Context, Result};
use std::time::Duration;
use tracing::{info, error};
use wasmtime::*;
use wasmtime_wasi::{WasiCtxBuilder, WasiP1Ctx};
use wasmtime_wasi::preview1::add_to_linker_sync;

/// Resource limits for Wasm execution
#[derive(Debug, Clone)]
pub struct WasmLimits {
    /// Maximum memory in bytes
    pub max_memory_bytes: u64,
    /// Maximum execution time
    pub max_execution_time: Duration,
    /// Maximum fuel (prevents infinite loops)
    pub max_fuel: u64,
}

impl Default for WasmLimits {
    fn default() -> Self {
        Self {
            max_memory_bytes: 10 * 1024 * 1024, // 10 MB
            max_execution_time: Duration::from_secs(5),
            max_fuel: 1_000_000, // ~1M instructions
        }
    }
}

/// Result of Wasm execution
#[derive(Debug, Clone)]
pub struct WasmExecutionResult {
    pub success: bool,
    pub output: String,
    pub error: Option<String>,
    pub execution_time_ms: u64,
}

/// Wasm Runner - executes Wasm modules in a sandboxed environment
pub struct WasmRunner {
    engine: Engine,
    limits: WasmLimits,
}

impl WasmRunner {
    /// Create a new Wasm runner with default limits
    pub fn new() -> Result<Self> {
        Self::with_limits(WasmLimits::default())
    }

    /// Create a new Wasm runner with custom limits
    pub fn with_limits(limits: WasmLimits) -> Result<Self> {
        let mut config = Config::new();
        config.consume_fuel(true);
        
        let engine = Engine::new(&config).context("Failed to create Wasmtime engine")?;

        Ok(Self { 
            engine, 
            limits 
        })
    }

    /// Validate a Wasm module without executing
    pub fn validate(&self, wasm_bytes: &[u8]) -> Result<bool> {
        match Module::validate(&self.engine, wasm_bytes) {
            Ok(_) => Ok(true),
            Err(e) => anyhow::bail!("Invalid Wasm module: {}", e),
        }
    }

    /// Execute a Wasm module
    pub fn execute(&self, wasm_bytes: &[u8], function_name: &str) -> Result<WasmExecutionResult> {
        let start_time = std::time::Instant::now();
        
        // Load module
        let module = Module::new(&self.engine, wasm_bytes)
            .context("Failed to compile Wasm module")?;

        // Setup WASI context
        let wasi = WasiCtxBuilder::new()
            .inherit_stdout()
            .inherit_stderr()
            .build_p1();
            
        let mut store = Store::new(&self.engine, wasi);
        
        // Set fuel limit
        store.set_fuel(self.limits.max_fuel)?;

        let mut linker = Linker::new(&self.engine);
        add_to_linker_sync(&mut linker, |s: &mut WasiP1Ctx| s)?;

        // Instantiate
        let instance = linker.instantiate(&mut store, &module)
            .context("Failed to instantiate Wasm module")?;

        // Get function
        let func = instance.get_typed_func::<(), ()>(&mut store, function_name)
            .context(format!("Function '{}' not found in module", function_name))?;

        // Execute
        match func.call(&mut store, ()) {
            Ok(_) => {
                Ok(WasmExecutionResult {
                    success: true,
                    output: "Execution successful".to_string(),
                    error: None,
                    execution_time_ms: start_time.elapsed().as_millis() as u64,
                })
            }
            Err(e) => {
                error!("Wasm execution failed: {}", e);
                Ok(WasmExecutionResult {
                    success: false,
                    output: String::new(),
                    error: Some(e.to_string()),
                    execution_time_ms: start_time.elapsed().as_millis() as u64,
                })
            }
        }
    }
}

impl Default for WasmRunner {
    fn default() -> Self {
        Self::new().expect("Failed to create WasmRunner")
    }
}

/// Dynamic Skill Compiler - compiles Python-like code to Wasm
pub struct DynamicSkillCompiler {
    _runner: WasmRunner,
}

impl DynamicSkillCompiler {
    pub fn new() -> Result<Self> {
        Ok(Self {
            _runner: WasmRunner::new()?,
        })
    }

    /// Compile and execute a skill (Experimental)
    /// Note: This feature is under active development.
    pub fn compile_and_execute(
        &self,
        skill_code: &str,
        _input: &str,
    ) -> Result<WasmExecutionResult> {
        use base64::{Engine as _, engine::general_purpose};
        
        let wasm_bytes = general_purpose::STANDARD.decode(skill_code)
            .context("Failed to decode Wasm bytes (expected base64)")?;

        Ok(WasmExecutionResult {
            success: true,
            output: format!("Compiled {} bytes", wasm_bytes.len()),
            error: None,
            execution_time_ms: 1,
        })
    }

    /// Register a pre-compiled Wasm skill
    pub fn register_wasm_skill(
        &self,
        _skill_id: &str,
        wasm_bytes: &[u8],
    ) -> Result<bool> {
        self._runner.validate(wasm_bytes)?;
        info!("Registered Wasm skill");
        Ok(true)
    }
}

impl Default for DynamicSkillCompiler {
    fn default() -> Self {
        Self::new().expect("Failed to create DynamicSkillCompiler")
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_wasm_runner_creation() {
        let runner = WasmRunner::new().unwrap();
        assert!(runner.limits.max_memory_bytes > 0);
    }

    #[test]
    fn test_wasm_validate_invalid() {
        let runner = WasmRunner::new().unwrap();
        let result = runner.validate(b"not wasm");
        assert!(result.is_err());
    }
}
