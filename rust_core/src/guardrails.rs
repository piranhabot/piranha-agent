// rust_core/src/guardrails.rs

use anyhow::{bail, Result};
use parking_lot::Mutex;
use std::sync::Arc;
use tracing::warn;

use crate::types::{GuardrailConfig, GuardrailParams, GuardrailType};

#[derive(Debug, Clone)]
pub struct GuardrailContext {
    pub agent_id: uuid::Uuid,
    pub session_id: uuid::Uuid,
    pub tokens_used: u64,
    pub token_budget: Option<u64>,
    pub calls_last_minute: u32,
    pub pending_action: Option<String>,
}

#[derive(Debug, Clone, PartialEq)]
pub enum GuardrailVerdict {
    Allow,
    Warn(String),
    Block(String),
}

#[derive(Clone)]
pub struct GuardrailEngine {
    rules: Arc<Mutex<Vec<GuardrailConfig>>>,
    call_times: Arc<Mutex<std::collections::VecDeque<std::time::Instant>>>,
}

impl GuardrailEngine {
    pub fn new(rules: Vec<GuardrailConfig>) -> Self {
        GuardrailEngine {
            rules: Arc::new(Mutex::new(rules)),
            call_times: Arc::new(Mutex::new(std::collections::VecDeque::new())),
        }
    }

    pub fn add_rule(&self, rule: GuardrailConfig) {
        self.rules.lock().push(rule);
    }

    pub fn check(&self, ctx: &GuardrailContext) -> Result<GuardrailVerdict> {
        let rules = self.rules.lock().clone();
        let mut final_verdict = GuardrailVerdict::Allow;

        for rule in &rules {
            let verdict = self.evaluate_rule(rule, ctx)?;
            match &verdict {
                GuardrailVerdict::Block(msg) => {
                    if rule.is_hard_limit {
                        warn!(
                            rule_name = %rule.name,
                            %msg,
                            "Hard guardrail violation — blocking action"
                        );
                        bail!("Guardrail '{}' blocked: {}", rule.name, msg);
                    } else {
                        warn!(
                            rule_name = %rule.name,
                            %msg,
                            "Soft guardrail warning"
                        );
                        final_verdict = GuardrailVerdict::Warn(msg.clone());
                    }
                }
                GuardrailVerdict::Warn(msg) => {
                    if final_verdict == GuardrailVerdict::Allow {
                        final_verdict = GuardrailVerdict::Warn(msg.clone());
                    }
                }
                GuardrailVerdict::Allow => {}
            }
        }

        Ok(final_verdict)
    }

    fn evaluate_rule(
        &self,
        rule: &GuardrailConfig,
        ctx: &GuardrailContext,
    ) -> Result<GuardrailVerdict> {
        match &rule.params {
            GuardrailParams::TokenBudget { max_tokens, warn_at_pct } => {
                self.check_token_budget(ctx, *max_tokens, *warn_at_pct)
            }
            GuardrailParams::RateLimit { max_calls_per_minute } => {
                self.check_rate_limit(*max_calls_per_minute)
            }
            GuardrailParams::ContentFilter { blocked_patterns } => {
                self.check_content_filter(ctx, blocked_patterns)
            }
            GuardrailParams::Custom { .. } => Ok(GuardrailVerdict::Allow),
        }
    }

    fn check_token_budget(
        &self,
        ctx: &GuardrailContext,
        max_tokens: u64,
        warn_at_pct: u8,
    ) -> Result<GuardrailVerdict> {
        let budget = ctx.token_budget.unwrap_or(max_tokens);

        if ctx.tokens_used >= budget {
            return Ok(GuardrailVerdict::Block(format!(
                "Token budget exhausted: used {} / {} tokens (100%)",
                ctx.tokens_used, budget
            )));
        }

        let pct_used = (ctx.tokens_used * 100) / budget.max(1);
        if pct_used >= warn_at_pct as u64 {
            return Ok(GuardrailVerdict::Warn(format!(
                "Token budget at {}%: {} / {} tokens used",
                pct_used, ctx.tokens_used, budget
            )));
        }

        Ok(GuardrailVerdict::Allow)
    }

    fn check_rate_limit(&self, max_calls_per_minute: u32) -> Result<GuardrailVerdict> {
        let now = std::time::Instant::now();
        let one_minute_ago = now - std::time::Duration::from_secs(60);
        let mut times = self.call_times.lock();

        while times.front().map(|t| *t < one_minute_ago).unwrap_or(false) {
            times.pop_front();
        }

        if times.len() >= max_calls_per_minute as usize {
            return Ok(GuardrailVerdict::Block(format!(
                "Rate limit exceeded: {} calls in the last minute (max: {})",
                times.len(),
                max_calls_per_minute
            )));
        }

        times.push_back(now);
        Ok(GuardrailVerdict::Allow)
    }

    fn check_content_filter(
        &self,
        ctx: &GuardrailContext,
        blocked_patterns: &[String],
    ) -> Result<GuardrailVerdict> {
        if let Some(action) = &ctx.pending_action {
            let action_lower = action.to_lowercase();
            for pattern in blocked_patterns {
                if action_lower.contains(&pattern.to_lowercase()) {
                    return Ok(GuardrailVerdict::Block(format!(
                        "Content filter triggered: action contains blocked pattern '{}'",
                        pattern
                    )));
                }
            }
        }
        Ok(GuardrailVerdict::Allow)
    }
}

pub fn default_guardrails(token_budget: u64) -> Vec<GuardrailConfig> {
    vec![
        GuardrailConfig {
            name: "token_budget".to_string(),
            rule_type: GuardrailType::TokenBudget,
            is_hard_limit: true,
            params: GuardrailParams::TokenBudget {
                max_tokens: token_budget,
                warn_at_pct: 80,
            },
        },
        GuardrailConfig {
            name: "rate_limit".to_string(),
            rule_type: GuardrailType::RateLimit,
            is_hard_limit: false,
            params: GuardrailParams::RateLimit {
                max_calls_per_minute: 60,
            },
        },
        GuardrailConfig {
            name: "dangerous_commands".to_string(),
            rule_type: GuardrailType::ContentFilter,
            is_hard_limit: true,
            params: GuardrailParams::ContentFilter {
                blocked_patterns: vec![
                    "rm -rf".to_string(),
                    "DROP TABLE".to_string(),
                    "DELETE FROM".to_string(),
                    "sudo".to_string(),
                    "chmod 777".to_string(),
                    "curl | bash".to_string(),
                    "wget | bash".to_string(),
                ],
            },
        },
    ]
}

#[cfg(test)]
mod tests {
    use super::*;
    use uuid::Uuid;

    fn test_ctx(tokens_used: u64, budget: u64) -> GuardrailContext {
        GuardrailContext {
            agent_id: Uuid::new_v4(),
            session_id: Uuid::new_v4(),
            tokens_used,
            token_budget: Some(budget),
            calls_last_minute: 0,
            pending_action: None,
        }
    }

    #[test]
    fn test_token_budget_warning() {
        let engine = GuardrailEngine::new(default_guardrails(1000));
        let ctx = test_ctx(820, 1000);
        let verdict = engine.check(&ctx).unwrap();
        assert!(matches!(verdict, GuardrailVerdict::Warn(_)));
    }

    #[test]
    fn test_token_budget_hard_block() {
        let engine = GuardrailEngine::new(default_guardrails(1000));
        let ctx = test_ctx(1001, 1000);
        let result = engine.check(&ctx);
        assert!(result.is_err());
    }

    #[test]
    fn test_content_filter_blocks_dangerous() {
        let engine = GuardrailEngine::new(default_guardrails(100_000));
        let mut ctx = test_ctx(0, 100_000);
        ctx.pending_action = Some("execute: rm -rf /".to_string());
        let result = engine.check(&ctx);
        assert!(result.is_err());
    }

    #[test]
    fn test_allow_normal_action() {
        let engine = GuardrailEngine::new(default_guardrails(100_000));
        let mut ctx = test_ctx(100, 100_000);
        ctx.pending_action = Some("search web for rust async".to_string());
        let verdict = engine.check(&ctx).unwrap();
        assert_eq!(verdict, GuardrailVerdict::Allow);
    }
}