# Windows 11 Setup

## 1. 전제 조건

- Git
- Python 3.12+
- Codex CLI
- Claude Code
- Gemini CLI
- 각 CLI에 필요한 인증 완료

PowerShell에서 확인합니다.

```powershell
git --version
py --version
codex --version
claude --version
gemini --version
```

## 2. 저장소 준비

```powershell
git clone https://github.com/son1004007/agent-orchestrator.git
cd agent-orchestrator
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
Copy-Item .env.example .env
```

CLI가 PATH에 없다면 `.env`의 `CODEX_BIN`, `CLAUDE_BIN`, `GEMINI_BIN`에 절대 경로를 지정합니다. `.env` 자체는 Git에 올리지 않습니다.

## 3. 실행

```powershell
python -m orchestrator.supervisor workflows/feature.yaml "요구사항"
```

## 4. Browser 제어

브라우저 기능을 Codex 내부 기능에 종속시키지 않는 것을 원칙으로 합니다. Playwright MCP 같은 browser MCP server를 별도 Tool Layer로 두고 Codex, Claude, Gemini 또는 Supervisor가 동일한 인터페이스로 사용하도록 구성합니다.

초기 버전은 LLM CLI adapter와 workflow 경계를 먼저 고정합니다. 다음 단계에서 MCP client/tool registry와 browser adapter를 추가합니다.

## 5. 운영 권장사항

- 실제 프로젝트 repository의 루트에서 Supervisor를 실행합니다.
- Agent가 변경한 diff를 단계별로 확인할 수 있도록 작업 브랜치를 사용합니다.
- production deploy, 데이터 삭제, credential 변경은 자동 승인하지 않습니다.
- CI에서 unit/integration test를 최종 gate로 사용합니다.
