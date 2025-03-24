reset_dapr:
	dapr stop
	dapr uninstall
	docker stop $(shell docker ps -aq) || true
	docker rm $(shell docker ps -aq) || true
	docker volume rm $(shell docker volume ls -q) || true
	docker system prune -a -f --volumes
	rm -f /workspaces/llm-plan-and-execute-knowledge-provider-mesh/dapr_multi_agent_actor_example/services/workflow-llm/LLMOrchestrator_state.json
