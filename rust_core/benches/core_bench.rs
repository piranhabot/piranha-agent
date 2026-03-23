use criterion::{criterion_group, criterion_main, Criterion};
use piranha_core::types::AgentState;
use uuid::Uuid;

fn bench_agent_state_creation(c: &mut Criterion) {
    c.bench_function("agent_state_creation", |b| {
        b.iter(|| {
            AgentState {
                id: Uuid::new_v4(),
                name: "test_agent".to_string(),
                ..Default::default()
            }
        })
    });
}

criterion_group!(benches, bench_agent_state_creation);
criterion_main!(benches);
