from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools import tool_collections

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

@CrewBase
class PrOptimizer():
	"""PrOptimizer crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools

	@agent
	def pr_analyzer(self) -> Agent:
		return Agent(
			config=self.agents_config['pr_analyzer'],
			tools=tool_collections['git_tools'] + tool_collections['code_analysis'],
			verbose=True
		)

	@agent
	def pr_splitter(self) -> Agent:
		return Agent(
			config=self.agents_config['pr_splitter'],
			tools=tool_collections['git_tools'] + tool_collections['github_api'],
			verbose=True
		)

	@agent
	def pr_reviewer(self) -> Agent:
		return Agent(
			config=self.agents_config['pr_reviewer'],
			tools=tool_collections['code_analysis'] + tool_collections['github_api'],
			verbose=True
		)

	@task
	def analyze_pr(self) -> Task:
		return Task(
			config=self.tasks_config['analyze_pr'],
			output_file='analysis_report.md'
		)

	@task
	def create_split_strategy(self) -> Task:
		return Task(
			config=self.tasks_config['create_split_strategy'],
			output_file='split_strategy.md'
		)

	@task
	def validate_splits(self) -> Task:
		return Task(
			config=self.tasks_config['validate_splits'],
			output_file='validation_report.md'
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the PrOptimizer crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
