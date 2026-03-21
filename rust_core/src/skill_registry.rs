// rust_core/src/skill_registry.rs

use anyhow::{bail, Context, Result};
use parking_lot::RwLock;
use serde_json::Value;
use std::collections::{HashMap, HashSet};
use std::sync::Arc;
use tracing::{debug, info, warn};

use crate::types::{AgentId, Permission, SkillDefinition, SkillId, SkillType};

#[derive(Debug, Clone)]
pub struct AgentGrant {
    pub agent_id: AgentId,
    pub allowed_skills: HashSet<SkillId>,
    pub effective_permissions: HashSet<Permission>,
    pub delegatable_skills: HashSet<SkillId>,
}

impl AgentGrant {
    pub fn can_invoke(&self, skill_id: &SkillId) -> bool {
        self.allowed_skills.contains(skill_id)
    }

    pub fn can_delegate(&self, skills: &[SkillId]) -> Result<()> {
        for skill in skills {
            if !self.delegatable_skills.contains(skill) {
                bail!(
                    "Privilege escalation blocked: agent {:?} cannot delegate skill '{}' \
                     (not in its delegatable set)",
                    self.agent_id,
                    skill
                );
            }
        }
        Ok(())
    }
}

#[derive(Clone)]
pub struct SkillRegistry {
    skills: Arc<RwLock<HashMap<SkillId, SkillDefinition>>>,
    grants: Arc<RwLock<HashMap<AgentId, AgentGrant>>>,
}

impl SkillRegistry {
    pub fn new() -> Self {
        let registry = SkillRegistry {
            skills: Arc::new(RwLock::new(HashMap::new())),
            grants: Arc::new(RwLock::new(HashMap::new())),
        };
        registry.register_builtins();
        registry
    }

    pub fn register(&self, skill: SkillDefinition) -> Result<()> {
        self.validate_skill_definition(&skill)?;
        let id = skill.id.clone();
        let mut skills = self.skills.write();
        if skills.contains_key(&id) {
            bail!("Skill '{}' is already registered. Use a unique ID.", id);
        }
        info!(skill_id = %id, skill_name = %skill.name, "Skill registered");
        skills.insert(id, skill);
        Ok(())
    }

    pub fn register_dynamic(
        &self,
        name: &str,
        description: &str,
        parameters_schema: Value,
        registering_agent_id: AgentId,
    ) -> Result<SkillId> {
        let skill_id = format!("dynamic:{}:{}", registering_agent_id, name);
        let skill = SkillDefinition {
            id: skill_id.clone(),
            name: name.to_string(),
            description: description.to_string(),
            parameters_schema,
            required_permissions: vec![Permission::CodeExecution],
            skill_type: SkillType::Dynamic,
            inheritable: true,
            is_privileged: false,
        };
        self.register(skill)?;

        let mut grants = self.grants.write();
        if let Some(grant) = grants.get_mut(&registering_agent_id) {
            grant.allowed_skills.insert(skill_id.clone());
            grant.delegatable_skills.insert(skill_id.clone());
            grant.effective_permissions.insert(Permission::CodeExecution);
        }

        info!(
            skill_id = %skill_id,
            %registering_agent_id,
            "Dynamic skill registered"
        );
        Ok(skill_id)
    }

    pub fn grant_skills_to_agent(
        &self,
        agent_id: AgentId,
        skill_ids: &[SkillId],
    ) -> Result<AgentGrant> {
        let skills_map = self.skills.read();
        let mut allowed_skills = HashSet::new();
        let mut effective_permissions = HashSet::new();

        for skill_id in skill_ids {
            let skill = skills_map.get(skill_id).with_context(|| {
                format!("Cannot grant unknown skill '{}'. Register it first.", skill_id)
            })?;
            allowed_skills.insert(skill_id.clone());
            for perm in &skill.required_permissions {
                effective_permissions.insert(perm.clone());
            }
        }

        let grant = AgentGrant {
            agent_id,
            allowed_skills: allowed_skills.clone(),
            effective_permissions,
            delegatable_skills: allowed_skills,
        };

        self.grants.write().insert(agent_id, grant.clone());
        info!(%agent_id, skill_count = skill_ids.len(), "Skills granted to agent");
        Ok(grant)
    }

    pub fn delegate_to_child(
        &self,
        parent_agent_id: AgentId,
        child_agent_id: AgentId,
        skills_to_delegate: &[SkillId],
    ) -> Result<AgentGrant> {
        let grants = self.grants.read();
        let parent_grant = grants.get(&parent_agent_id).with_context(|| {
            format!("Parent agent {} has no registered grant", parent_agent_id)
        })?;
        parent_grant.can_delegate(skills_to_delegate)?;
        drop(grants);
        self.grant_skills_to_agent(child_agent_id, skills_to_delegate)
    }

    pub fn authorize_invocation(&self, agent_id: AgentId, skill_id: &SkillId) -> Result<()> {
        let grants = self.grants.read();
        let grant = grants.get(&agent_id).with_context(|| {
            format!(
                "Security violation: agent {} has no grants registered.",
                agent_id
            )
        })?;

        if !grant.can_invoke(skill_id) {
            let skills_map = self.skills.read();
            let skill_name = skills_map
                .get(skill_id)
                .map(|s| s.name.as_str())
                .unwrap_or("unknown");

            warn!(
                %agent_id,
                %skill_id,
                skill_name,
                "SECURITY: Skill invocation denied"
            );

            bail!(
                "Permission denied: agent {} is not authorized to invoke skill '{}' ({}).",
                agent_id,
                skill_id,
                skill_name
            );
        }

        debug!(%agent_id, %skill_id, "Skill invocation authorized");
        Ok(())
    }

    pub fn get_agent_skill_schemas(&self, agent_id: AgentId) -> Result<Value> {
        let grants = self.grants.read();
        let grant = grants.get(&agent_id).with_context(|| {
            format!("No grants found for agent {}", agent_id)
        })?;

        let allowed_skills: HashSet<_> = grant.allowed_skills.iter().cloned().collect();
        drop(grants);

        let skills_map = self.skills.read();
        let schemas: Vec<Value> = allowed_skills
            .iter()
            .filter_map(|skill_id| skills_map.get(skill_id))
            .map(skill_to_openai_schema)
            .collect();

        Ok(serde_json::json!({ "tools": schemas }))
    }

    pub fn get_skill(&self, skill_id: &str) -> Option<SkillDefinition> {
        self.skills.read().get(skill_id).cloned()
    }

    pub fn list_all_skills(&self) -> Vec<SkillDefinition> {
        self.skills.read().values().cloned().collect()
    }

    fn register_builtins(&self) {
        let builtins = vec![
            SkillDefinition {
                id: "builtin:web_search".to_string(),
                name: "web_search".to_string(),
                description: "Search the web for current information.".to_string(),
                parameters_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "query": { "type": "string", "description": "The search query" },
                        "max_results": { "type": "integer", "default": 5 }
                    },
                    "required": ["query"]
                }),
                required_permissions: vec![Permission::NetworkRead],
                skill_type: SkillType::Static,
                inheritable: true,
                is_privileged: false,
            },
            SkillDefinition {
                id: "builtin:code_exec".to_string(),
                name: "execute_code".to_string(),
                description: "Execute code in a secure Wasm sandbox. No host OS access.".to_string(),
                parameters_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "language": { "type": "string", "enum": ["python", "javascript"] },
                        "code": { "type": "string" },
                        "timeout_ms": { "type": "integer", "default": 5000 }
                    },
                    "required": ["language", "code"]
                }),
                required_permissions: vec![Permission::CodeExecution],
                skill_type: SkillType::Static,
                inheritable: true,
                is_privileged: false,
            },
            SkillDefinition {
                id: "builtin:spawn_agent".to_string(),
                name: "spawn_sub_agent".to_string(),
                description: "Create a specialized sub-agent to handle a subtask.".to_string(),
                parameters_schema: serde_json::json!({
                    "type": "object",
                    "properties": {
                        "agent_name": { "type": "string" },
                        "task": { "type": "string" },
                        "skills_to_delegate": {
                            "type": "array",
                            "items": { "type": "string" }
                        },
                        "token_budget": { "type": "integer" }
                    },
                    "required": ["agent_name", "task"]
                }),
                required_permissions: vec![Permission::SpawnSubAgent],
                skill_type: SkillType::Static,
                inheritable: false,
                is_privileged: true,
            },
        ];

        let mut skills_map = self.skills.write();
        for skill in builtins {
            skills_map.insert(skill.id.clone(), skill);
        }
    }

    fn validate_skill_definition(&self, skill: &SkillDefinition) -> Result<()> {
        if skill.id.is_empty() {
            bail!("Skill ID cannot be empty");
        }
        if skill.name.is_empty() {
            bail!("Skill name cannot be empty");
        }
        if skill.description.len() < 10 {
            bail!("Skill '{}' description too short (<10 chars).", skill.id);
        }
        if !skill.parameters_schema.is_object() {
            bail!("Skill '{}' parameters_schema must be a JSON object", skill.id);
        }
        Ok(())
    }
}

impl Default for SkillRegistry {
    fn default() -> Self {
        Self::new()
    }
}

fn skill_to_openai_schema(skill: &SkillDefinition) -> Value {
    serde_json::json!({
        "type": "function",
        "function": {
            "name": skill.name,
            "description": skill.description,
            "parameters": skill.parameters_schema,
        }
    })
}

#[cfg(test)]
mod tests {
    use super::*;
    use uuid::Uuid;

    #[test]
    fn test_grant_and_authorize() {
        let registry = SkillRegistry::new();
        let agent_id = Uuid::new_v4();
        registry.grant_skills_to_agent(agent_id, &["builtin:web_search".to_string()]).unwrap();
        registry.authorize_invocation(agent_id, &"builtin:web_search".to_string()).unwrap();
        let result = registry.authorize_invocation(agent_id, &"builtin:code_exec".to_string());
        assert!(result.is_err());
    }

    #[test]
    fn test_privilege_escalation_prevention() {
        let registry = SkillRegistry::new();
        let parent_id = Uuid::new_v4();
        let child_id = Uuid::new_v4();
        registry.grant_skills_to_agent(parent_id, &["builtin:web_search".to_string()]).unwrap();
        let result = registry.delegate_to_child(
            parent_id,
            child_id,
            &["builtin:code_exec".to_string()],
        );
        assert!(result.is_err());
        assert!(result.unwrap_err().to_string().contains("Privilege escalation blocked"));
    }
}