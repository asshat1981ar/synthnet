#!/usr/bin/env python3
"""
GitHub Actions Integration for MCP Testing Framework
Provides utilities and templates for GitHub Actions CI/CD integration.
"""

import json
import yaml
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

@dataclass
class GitHubActionsConfig:
    """Configuration for GitHub Actions integration."""
    workflow_name: str = "MCP Server Testing"
    trigger_events: List[str] = field(default_factory=lambda: ["push", "pull_request"])
    test_types: List[str] = field(default_factory=lambda: ["unit", "integration", "protocol", "performance", "security"])
    python_versions: List[str] = field(default_factory=lambda: ["3.8", "3.9", "3.10", "3.11"])
    node_versions: List[str] = field(default_factory=lambda: ["16", "18", "20"])
    os_matrix: List[str] = field(default_factory=lambda: ["ubuntu-latest", "windows-latest", "macos-latest"])
    artifact_retention_days: int = 30
    enable_parallel_testing: bool = True
    enable_coverage_reporting: bool = True
    enable_security_scanning: bool = True
    enable_performance_benchmarks: bool = True

class GitHubActionsIntegration:
    """GitHub Actions integration for MCP testing framework."""
    
    def __init__(self, config: Optional[GitHubActionsConfig] = None):
        """Initialize GitHub Actions integration."""
        self.config = config or GitHubActionsConfig()
    
    def generate_workflow_files(self, output_dir: str) -> Dict[str, str]:
        """Generate GitHub Actions workflow files."""
        output_path = Path(output_dir)
        workflows_path = output_path / ".github" / "workflows"
        workflows_path.mkdir(parents=True, exist_ok=True)
        
        generated_files = {}
        
        # Main testing workflow
        main_workflow = self._generate_main_workflow()
        main_path = workflows_path / "mcp-testing.yml"
        with open(main_path, 'w') as f:
            f.write(main_workflow)
        generated_files['main'] = str(main_path)
        
        # Security scanning workflow
        if self.config.enable_security_scanning:
            security_workflow = self._generate_security_workflow()
            security_path = workflows_path / "security-scan.yml"
            with open(security_path, 'w') as f:
                f.write(security_workflow)
            generated_files['security'] = str(security_path)
        
        # Performance benchmarking workflow
        if self.config.enable_performance_benchmarks:
            performance_workflow = self._generate_performance_workflow()
            performance_path = workflows_path / "performance-benchmark.yml"
            with open(performance_path, 'w') as f:
                f.write(performance_workflow)
            generated_files['performance'] = str(performance_path)
        
        # Release workflow
        release_workflow = self._generate_release_workflow()
        release_path = workflows_path / "release.yml"
        with open(release_path, 'w') as f:
            f.write(release_workflow)
        generated_files['release'] = str(release_path)
        
        # Dependency update workflow
        dependency_workflow = self._generate_dependency_update_workflow()
        dependency_path = workflows_path / "dependency-update.yml"
        with open(dependency_path, 'w') as f:
            f.write(dependency_workflow)
        generated_files['dependency'] = str(dependency_path)
        
        return generated_files
    
    def _generate_main_workflow(self) -> str:
        """Generate main testing workflow."""
        workflow = {
            'name': self.config.workflow_name,
            'on': self._generate_trigger_config(),
            'jobs': {
                'test': {
                    'runs-on': '${{ matrix.os }}',
                    'strategy': {
                        'matrix': {
                            'os': self.config.os_matrix,
                            'python-version': self.config.python_versions,
                            'node-version': self.config.node_versions
                        }
                    },
                    'steps': self._generate_test_steps()
                },
                'coverage': {
                    'needs': 'test',
                    'runs-on': 'ubuntu-latest',
                    'if': self.config.enable_coverage_reporting,
                    'steps': self._generate_coverage_steps()
                }
            }
        }
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def _generate_security_workflow(self) -> str:
        """Generate security scanning workflow."""
        workflow = {
            'name': 'Security Scan',
            'on': {
                'push': {'branches': ['main', 'develop']},
                'pull_request': {'branches': ['main']},
                'schedule': [{'cron': '0 6 * * 1'}]  # Weekly on Monday
            },
            'jobs': {
                'security-scan': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v3'},
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt'
                        },
                        {
                            'name': 'Run security scan',
                            'run': 'python -m mcp_testing_framework.core.security_scanner . --output security_report.json'
                        },
                        {
                            'name': 'Upload security report',
                            'uses': 'actions/upload-artifact@v3',
                            'with': {
                                'name': 'security-report',
                                'path': 'security_report.json',
                                'retention-days': self.config.artifact_retention_days
                            }
                        },
                        {
                            'name': 'Security scan summary',
                            'run': '''
                                echo "## Security Scan Results" >> $GITHUB_STEP_SUMMARY
                                python -c "
import json
with open('security_report.json', 'r') as f:
    data = json.load(f)
    for result in data:
        vulnerabilities = result.get('vulnerabilities', [])
        critical = len([v for v in vulnerabilities if v.get('severity') == 'critical'])
        high = len([v for v in vulnerabilities if v.get('severity') == 'high'])
        print(f'- {result.get(\"test_name\", \"Unknown\")}: {critical} critical, {high} high vulnerabilities')
                                "
                            '''
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def _generate_performance_workflow(self) -> str:
        """Generate performance benchmarking workflow."""
        workflow = {
            'name': 'Performance Benchmark',
            'on': {
                'push': {'branches': ['main']},
                'pull_request': {'branches': ['main']},
                'workflow_dispatch': {}
            },
            'jobs': {
                'benchmark': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v3'},
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt'
                        },
                        {
                            'name': 'Run performance benchmarks',
                            'run': '''
                                python -m mcp_testing_framework.core.performance_tester . \\
                                  --test-type basic \\
                                  --output performance_basic.json
                                
                                python -m mcp_testing_framework.core.performance_tester . \\
                                  --test-type load \\
                                  --concurrent-users 10 \\
                                  --duration 60 \\
                                  --output performance_load.json
                            '''
                        },
                        {
                            'name': 'Upload performance reports',
                            'uses': 'actions/upload-artifact@v3',
                            'with': {
                                'name': 'performance-reports',
                                'path': 'performance_*.json',
                                'retention-days': self.config.artifact_retention_days
                            }
                        },
                        {
                            'name': 'Performance benchmark summary',
                            'run': '''
                                echo "## Performance Benchmark Results" >> $GITHUB_STEP_SUMMARY
                                
                                if [ -f performance_basic.json ]; then
                                    echo "### Basic Performance Test" >> $GITHUB_STEP_SUMMARY
                                    python -c "
import json
with open('performance_basic.json', 'r') as f:
    data = json.load(f)
    for result in data:
        metrics = result.get('metrics', {})
        print(f'- Avg Response Time: {metrics.get(\"average_response_time\", \"N/A\")}s')
        print(f'- Requests/sec: {metrics.get(\"requests_per_second\", \"N/A\")}')
        print(f'- Error Rate: {metrics.get(\"error_rate\", \"N/A\")}')
                                    " >> $GITHUB_STEP_SUMMARY
                                fi
                                
                                if [ -f performance_load.json ]; then
                                    echo "### Load Test Results" >> $GITHUB_STEP_SUMMARY
                                    python -c "
import json
with open('performance_load.json', 'r') as f:
    data = json.load(f)
    for result in data:
        metrics = result.get('metrics', {})
        print(f'- Peak Throughput: {metrics.get(\"requests_per_second\", \"N/A\")} req/s')
        print(f'- 95th Percentile: {metrics.get(\"p95_response_time\", \"N/A\")}s')
                                    " >> $GITHUB_STEP_SUMMARY
                                fi
                            '''
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def _generate_release_workflow(self) -> str:
        """Generate release workflow."""
        workflow = {
            'name': 'Release',
            'on': {
                'push': {'tags': ['v*']},
                'workflow_dispatch': {}
            },
            'jobs': {
                'pre-release-tests': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v3'},
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Install dependencies',
                            'run': 'pip install -r requirements.txt'
                        },
                        {
                            'name': 'Run full test suite',
                            'run': '''
                                python -m mcp_testing_framework.core.test_runner . \\
                                  --test-types unit integration protocol performance security \\
                                  --output-dir test_results \\
                                  --report-formats html junit json
                            '''
                        },
                        {
                            'name': 'Upload test results',
                            'uses': 'actions/upload-artifact@v3',
                            'with': {
                                'name': 'release-test-results',
                                'path': 'test_results/',
                                'retention-days': 90
                            }
                        }
                    ]
                },
                'release': {
                    'needs': 'pre-release-tests',
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v3'},
                        {
                            'name': 'Create Release',
                            'uses': 'actions/create-release@v1',
                            'env': {'GITHUB_TOKEN': '${{ secrets.GITHUB_TOKEN }}'},
                            'with': {
                                'tag_name': '${{ github.ref }}',
                                'release_name': 'Release ${{ github.ref }}',
                                'draft': False,
                                'prerelease': False,
                                'body': '''
                                    ## What's Changed
                                    - Full test suite passed with all test types
                                    - Performance benchmarks completed
                                    - Security scanning completed
                                    
                                    ## Test Results
                                    All tests passed successfully. See attached artifacts for detailed reports.
                                '''
                            }
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def _generate_dependency_update_workflow(self) -> str:
        """Generate dependency update workflow."""
        workflow = {
            'name': 'Dependency Update',
            'on': {
                'schedule': [{'cron': '0 8 * * 1'}],  # Weekly on Monday
                'workflow_dispatch': {}
            },
            'jobs': {
                'update-dependencies': {
                    'runs-on': 'ubuntu-latest',
                    'steps': [
                        {'uses': 'actions/checkout@v3'},
                        {
                            'name': 'Set up Python',
                            'uses': 'actions/setup-python@v4',
                            'with': {'python-version': '3.11'}
                        },
                        {
                            'name': 'Update Python dependencies',
                            'run': '''
                                pip install --upgrade pip pip-tools
                                pip-compile --upgrade requirements.in
                                pip install -r requirements.txt
                            '''
                        },
                        {
                            'name': 'Run security scan on updated dependencies',
                            'run': 'python -m mcp_testing_framework.core.security_scanner . --scan-type dependencies'
                        },
                        {
                            'name': 'Run basic tests',
                            'run': '''
                                python -m mcp_testing_framework.core.test_runner . \\
                                  --test-types unit integration \\
                                  --output-dir test_results
                            '''
                        },
                        {
                            'name': 'Create Pull Request',
                            'uses': 'peter-evans/create-pull-request@v5',
                            'with': {
                                'token': '${{ secrets.GITHUB_TOKEN }}',
                                'commit-message': 'chore: update dependencies',
                                'title': 'chore: Weekly dependency update',
                                'body': '''
                                    ## Dependency Update
                                    
                                    This PR updates all dependencies to their latest versions.
                                    
                                    - Security scan passed
                                    - Basic tests passed
                                    - Ready for review
                                ''',
                                'branch': 'dependency-update/weekly',
                                'delete-branch': True
                            }
                        }
                    ]
                }
            }
        }
        
        return yaml.dump(workflow, default_flow_style=False, sort_keys=False)
    
    def _generate_trigger_config(self) -> Dict[str, Any]:
        """Generate workflow trigger configuration."""
        config = {}
        
        for event in self.config.trigger_events:
            if event == "push":
                config['push'] = {
                    'branches': ['main', 'develop'],
                    'paths-ignore': ['README.md', 'docs/**', '*.md']
                }
            elif event == "pull_request":
                config['pull_request'] = {
                    'branches': ['main', 'develop'],
                    'types': ['opened', 'synchronize', 'reopened']
                }
            elif event == "schedule":
                config['schedule'] = [{'cron': '0 6 * * *'}]  # Daily at 6 AM
            elif event == "workflow_dispatch":
                config['workflow_dispatch'] = {}
        
        return config
    
    def _generate_test_steps(self) -> List[Dict[str, Any]]:
        """Generate test steps for the main workflow."""
        steps = [
            {'uses': 'actions/checkout@v3'},
            {
                'name': 'Set up Python ${{ matrix.python-version }}',
                'uses': 'actions/setup-python@v4',
                'with': {'python-version': '${{ matrix.python-version }}'}
            },
            {
                'name': 'Set up Node.js ${{ matrix.node-version }}',
                'uses': 'actions/setup-node@v3',
                'with': {'node-version': '${{ matrix.node-version }}'}
            },
            {
                'name': 'Install Python dependencies',
                'run': '''
                    python -m pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov pytest-json-report
                '''
            },
            {
                'name': 'Install Node.js dependencies',
                'run': 'npm install',
                'if': "hashFiles('package.json') != ''"
            },
            {
                'name': 'Lint code',
                'run': '''
                    # Python linting
                    pip install flake8 black isort
                    flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
                    black --check .
                    isort --check-only .
                '''
            }
        ]
        
        # Add test type specific steps
        for test_type in self.config.test_types:
            if test_type == "unit":
                steps.append({
                    'name': 'Run unit tests',
                    'run': '''
                        python -m mcp_testing_framework.core.test_runner . \\
                          --test-types unit \\
                          --output-dir test_results_unit \\
                          --report-formats junit json
                    '''
                })
            elif test_type == "integration":
                steps.append({
                    'name': 'Run integration tests',
                    'run': '''
                        python -m mcp_testing_framework.core.test_runner . \\
                          --test-types integration \\
                          --output-dir test_results_integration \\
                          --report-formats junit json
                    '''
                })
            elif test_type == "protocol":
                steps.append({
                    'name': 'Run protocol compliance tests',
                    'run': '''
                        python -m mcp_testing_framework.core.mcp_protocol_tester . \\
                          --output protocol_results.json
                    '''
                })
            elif test_type == "performance":
                steps.append({
                    'name': 'Run performance tests',
                    'run': '''
                        python -m mcp_testing_framework.core.performance_tester . \\
                          --test-type basic \\
                          --output performance_results.json
                    ''',
                    'if': "matrix.os == 'ubuntu-latest' && matrix.python-version == '3.11'"
                })
            elif test_type == "security":
                steps.append({
                    'name': 'Run security tests',
                    'run': '''
                        python -m mcp_testing_framework.core.security_scanner . \\
                          --output security_results.json
                    '''
                })
        
        # Upload test results
        steps.extend([
            {
                'name': 'Upload test results',
                'uses': 'actions/upload-artifact@v3',
                'if': 'always()',
                'with': {
                    'name': 'test-results-${{ matrix.os }}-py${{ matrix.python-version }}',
                    'path': 'test_results*/',
                    'retention-days': self.config.artifact_retention_days
                }
            },
            {
                'name': 'Upload individual results',
                'uses': 'actions/upload-artifact@v3',
                'if': 'always()',
                'with': {
                    'name': 'test-outputs-${{ matrix.os }}-py${{ matrix.python-version }}',
                    'path': '*_results.json',
                    'retention-days': self.config.artifact_retention_days
                }
            },
            {
                'name': 'Publish test results',
                'uses': 'EnricoMi/publish-unit-test-result-action@v2',
                'if': 'always()',
                'with': {
                    'files': 'test_results*/junit_results.xml',
                    'check_name': 'Test Results (${{ matrix.os }}, Python ${{ matrix.python-version }})'
                }
            }
        ])
        
        return steps
    
    def _generate_coverage_steps(self) -> List[Dict[str, Any]]:
        """Generate coverage reporting steps."""
        return [
            {'uses': 'actions/checkout@v3'},
            {
                'name': 'Set up Python',
                'uses': 'actions/setup-python@v4',
                'with': {'python-version': '3.11'}
            },
            {
                'name': 'Download test artifacts',
                'uses': 'actions/download-artifact@v3',
                'with': {'path': 'artifacts/'}
            },
            {
                'name': 'Install coverage tools',
                'run': 'pip install coverage codecov'
            },
            {
                'name': 'Combine coverage reports',
                'run': '''
                    coverage combine artifacts/*/coverage.dat
                    coverage report
                    coverage xml
                '''
            },
            {
                'name': 'Upload coverage to Codecov',
                'uses': 'codecov/codecov-action@v3',
                'with': {
                    'file': 'coverage.xml',
                    'fail_ci_if_error': True
                }
            }
        ]

def generate_github_actions_config(project_dir: str, config: Optional[GitHubActionsConfig] = None) -> Dict[str, str]:
    """Generate GitHub Actions configuration for a project."""
    integration = GitHubActionsIntegration(config)
    return integration.generate_workflow_files(project_dir)

def create_pr_template(output_dir: str) -> str:
    """Create pull request template."""
    pr_template = """## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change which fixes an issue)
- [ ] New feature (non-breaking change which adds functionality)
- [ ] Breaking change (fix or feature that would cause existing functionality to not work as expected)
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Protocol compliance tests pass
- [ ] Performance tests pass (if applicable)
- [ ] Security tests pass

## Performance Impact
- [ ] No performance impact
- [ ] Performance improvement
- [ ] Potential performance regression (please describe)

## Security Considerations
- [ ] No security impact
- [ ] Security improvement
- [ ] Potential security issue (please describe)

## Checklist
- [ ] My code follows the project's style guidelines
- [ ] I have performed a self-review of my code
- [ ] I have commented my code, particularly in hard-to-understand areas
- [ ] I have made corresponding changes to the documentation
- [ ] My changes generate no new warnings
- [ ] I have added tests that prove my fix is effective or that my feature works
- [ ] New and existing unit tests pass locally with my changes

## Screenshots (if applicable)
Add screenshots here

## Additional Notes
Any additional information about the changes
"""
    
    template_dir = Path(output_dir) / ".github"
    template_dir.mkdir(parents=True, exist_ok=True)
    
    template_path = template_dir / "pull_request_template.md"
    with open(template_path, 'w') as f:
        f.write(pr_template)
    
    return str(template_path)

def create_issue_templates(output_dir: str) -> Dict[str, str]:
    """Create GitHub issue templates."""
    template_dir = Path(output_dir) / ".github" / "ISSUE_TEMPLATE"
    template_dir.mkdir(parents=True, exist_ok=True)
    
    templates = {}
    
    # Bug report template
    bug_template = """---
name: Bug report
about: Create a report to help us improve
title: '[BUG] '
labels: 'bug'
assignees: ''
---

## Bug Description
A clear and concise description of what the bug is.

## Steps to Reproduce
1. Go to '...'
2. Click on '....'
3. Scroll down to '....'
4. See error

## Expected Behavior
A clear and concise description of what you expected to happen.

## Actual Behavior
A clear and concise description of what actually happened.

## Test Environment
- OS: [e.g. Ubuntu 20.04, Windows 10, macOS 12]
- Python Version: [e.g. 3.9.7]
- MCP Testing Framework Version: [e.g. 1.0.0]
- Server Type: [e.g. Healthcare FHIR, Education LMS]

## Test Results
If applicable, add test results or error messages.

## Additional Context
Add any other context about the problem here.
"""
    
    bug_path = template_dir / "bug_report.md"
    with open(bug_path, 'w') as f:
        f.write(bug_template)
    templates['bug'] = str(bug_path)
    
    # Feature request template
    feature_template = """---
name: Feature request
about: Suggest an idea for this project
title: '[FEATURE] '
labels: 'enhancement'
assignees: ''
---

## Is your feature request related to a problem?
A clear and concise description of what the problem is. Ex. I'm always frustrated when [...]

## Describe the solution you'd like
A clear and concise description of what you want to happen.

## Describe alternatives you've considered
A clear and concise description of any alternative solutions or features you've considered.

## Use Case
Describe the specific use case or scenario where this feature would be helpful.

## Testing Considerations
How should this feature be tested? What test cases should be considered?

## Additional Context
Add any other context or screenshots about the feature request here.
"""
    
    feature_path = template_dir / "feature_request.md"
    with open(feature_path, 'w') as f:
        f.write(feature_template)
    templates['feature'] = str(feature_path)
    
    return templates

if __name__ == "__main__":
    # Test the GitHub Actions integration
    def test_integration():
        config = GitHubActionsConfig(
            workflow_name="Test MCP Server",
            test_types=["unit", "integration", "protocol"],
            python_versions=["3.9", "3.10", "3.11"],
            enable_performance_benchmarks=True,
            enable_security_scanning=True
        )
        
        integration = GitHubActionsIntegration(config)
        files = integration.generate_workflow_files("test_output")
        
        print("Generated workflow files:")
        for name, path in files.items():
            print(f"- {name}: {path}")
        
        # Generate PR template
        pr_template_path = create_pr_template("test_output")
        print(f"- PR template: {pr_template_path}")
        
        # Generate issue templates
        issue_templates = create_issue_templates("test_output")
        print("- Issue templates:")
        for name, path in issue_templates.items():
            print(f"  - {name}: {path}")
    
    test_integration()