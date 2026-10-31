#!/usr/bin/env python3
"""Apply the economical Codex policy after a Gentle AI install/sync."""
import datetime
import json
import os
from pathlib import Path
import re
import shutil
import tomllib

ROOT = Path(__file__).resolve().parent
BACKUP = ROOT / 'backups' / ('economy-' + datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%S%fZ'))
BACKUP.mkdir(parents=True)
ROLES = {
    'odd-explorer': ('gpt-6-luna', 'low', 'Read-only exploration of one bounded question.'),
    'odd-worker': ('gpt-6-luna', 'medium', 'Implement one bounded task with applicable verification.'),
    'odd-verify': ('gpt-6.1-sol', 'medium', 'Read-only independent verification when the task names a material risk.'),
}

def save(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        target = BACKUP / str(path).lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
    path.write_text(content)

def set_key(text, section, key, value):
    lines = text.splitlines()
    start, end = 0, len(lines)
    headers = [(i, l.strip()[1:-1]) for i, l in enumerate(lines) if re.fullmatch(r'\s*\[[^\[\]]+\]\s*', l)]
    if section:
        found = next(((i, name) for i, name in headers if name == section), None)
        if found is None:
            return text.rstrip() + f'\n\n[{section}]\n{key} = {value}\n'
        start = found[0] + 1
    end = next((i for i, _ in headers if i >= start), len(lines))
    pattern = re.compile(r'^\s*' + re.escape(key) + r'\s*=')
    matches = [i for i in range(start, end) if pattern.match(lines[i])]
    if matches:
        lines[matches[0]] = f'{key} = {value}'
        for i in reversed(matches[1:]):
            del lines[i]
    else:
        lines.insert(end, f'{key} = {value}')
    return '\n'.join(lines) + '\n'

policy = '''<!-- gentle-economy:start -->
## Gentle AI: economical Codex routing

Use gpt-6-luna with medium reasoning for the main session. Complete small,
understood tasks inline. Delegate only when a bounded task benefits from it;
never delegate merely to fill a role. No nested delegation. Pass only the task,
relevant paths, and acceptance conditions, without full conversation history.

| Worker class | Model | reasoning_effort |
|---|---|---|
| odd-explorer | gpt-6-luna | low |
| odd-worker | gpt-6-luna | medium |
| odd-verify | gpt-6.1-sol | medium |

Use the matching native role when available. With spawn_agent use the table's
exact model and effort and fork_turns="none". Use a verifier only for a named
material risk or an explicit review request. Avoid duplicate reviews and repeated
passing tests. Escalate difficult work when evidence warrants it.

Retrieve only relevant Engram memories; record decisions and useful discoveries.
Use CodeGraph only in indexed projects, with bounded symbol queries. Fetch
Context7 documentation only when needed for the current library question.
Keep tool output and final responses concise. Do not load whole documentation
files when a targeted search suffices. Preserve appropriate functional checks.
<!-- gentle-economy:end -->
'''

homes = {Path.home() / '.codex', Path(os.environ.get('CODEX_HOME', str(Path.home() / '.codex'))), ROOT / '.codex'}
for home in sorted(homes):
    path = home / 'config.toml'
    text = path.read_text() if path.exists() else ''
    # Engram's current Codex plugin explicitly requires keeping built-in prompts.
    text = re.sub(r'(?m)^(?:model_instructions_file|experimental_compact_prompt_file)\s*=.*\n?', '', text)
    for section, key, value in [
        ('', 'model', '"gpt-6-luna"'),
        ('', 'model_reasoning_effort', '"medium"'),
        ('', 'model_verbosity', '"low"'),
        ('features', 'multi_agent', 'true'),
        ('agents', 'max_threads', '2'),
        ('agents', 'max_depth', '1'),
        ('mcp_servers.engram', 'command', '"/home/agent/.local/bin/engram"'),
        ('mcp_servers.engram', 'args', '["mcp", "--tools=agent"]'),
        ('mcp_servers.codegraph', 'command', '"/home/agent/.local/bin/codegraph"'),
        ('mcp_servers.codegraph', 'args', '["serve", "--mcp"]'),
        ('mcp_servers.context7', 'url', '"https://mcp.context7.com/mcp"'),
    ]:
        text = set_key(text, section, key, value)
    for role, (model, effort, description) in ROLES.items():
        rolepath = home / 'agents' / (role + '.toml')
        roletext = f'model = "{model}"\nmodel_reasoning_effort = "{effort}"\n'
        if role != 'odd-worker':
            roletext += 'sandbox_mode = "read-only"\n'
        tomllib.loads(roletext)
        save(rolepath, roletext)
        text = set_key(text, 'agents.' + role, 'description', json.dumps(description))
        text = set_key(text, 'agents.' + role, 'config_file', json.dumps(str(rolepath)))
    parsed = tomllib.loads(text)
    assert parsed['agents']['max_depth'] == 1
    assert parsed['model'] == 'gpt-6-luna'
    save(path, text)
    instructions = home / 'AGENTS.md'
    body = instructions.read_text() if instructions.exists() else ''
    body = re.sub(r'<!-- gentle-economy:start -->.*?<!-- gentle-economy:end -->\n?', '', body, flags=re.S)
    for role, (model, effort, _) in ROLES.items():
        body = re.sub(r'(?m)^\| `' + role + r'` \|.*$', f'| `{role}` | `{model}` | `{effort}` |', body)
    save(instructions, body.rstrip() + '\n\n' + policy)

statepath = Path.home() / '.gentle-ai/state.json'
state = json.loads(statepath.read_text())
state['codexOrchestratorAssignment'] = {'model': 'gpt-6-luna', 'effort': 'medium'}
state['codexModelAssignments'] = {role: v[1] for role, v in ROLES.items()}
state['codexPhaseModelAssignments'] = {role: v[0] for role, v in ROLES.items()}
state['codexCarrilModelAssignments'] = {'sdd-cheap': 'gpt-6-luna', 'sdd-mid': 'gpt-6-luna', 'sdd-strong': 'gpt-6.1-sol'}
save(statepath, json.dumps(state, indent=2) + '\n')
print('Economical policy applied to:', ', '.join(str(p) for p in sorted(homes)))
print('Backups:', BACKUP)
