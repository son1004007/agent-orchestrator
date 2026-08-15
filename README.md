# Agent Orchestrator

멀티 LLM 코딩 에이전트를 하나의 워크플로우에서 운영하기 위한 오케스트레이션 프로젝트입니다.

## 목표

- Codex, Claude Code, Gemini CLI를 교체 가능한 실행 Agent로 사용
- 특정 IDE나 특정 LLM에 종속되지 않는 Supervisor 중심 구조
- 브라우저/DB/GitHub 등 외부 도구는 MCP 계층으로 분리
- 단계별 결과를 명시적으로 저장해 재현 가능한 워크플로우 제공
- Agent 실패/쿼터 초과 시 fallback 가능한 구조
- 향후 A2A adapter 추가 가능

## 권장 역할

| 단계 | 기본 Agent | Fallback |
|---|---|---|
| 요구사항 분석 | Claude | Gemini |
| 아키텍처 설계 | Claude | Gemini |
| Java/Python 구현 | Codex | Claude |
| 테스트/수정 | Codex | Claude |
| 독립 리뷰 | Claude + Gemini | Codex |
| 브라우저 검증 | MCP Browser Tool | 동일 도구를 모든 Agent가 공유 |

## 구조

```text
agent-orchestrator/
├─ AGENTS.md
├─ WORKFLOW.md
├─ pyproject.toml
├─ .env.example
├─ orchestrator/
│  ├─ __init__.py
│  ├─ supervisor.py
│  ├─ models.py
│  └─ adapters/
│     ├─ __init__.py
│     ├─ base.py
│     ├─ codex.py
│     ├─ claude.py
│     └─ gemini.py
├─ workflows/
│  └─ feature.yaml
└─ docs/
   └─ WINDOWS_SETUP.md
```

## 실행 개념

```text
사용자 요청
   ↓
Supervisor
   ↓
requirements → architecture → implement → test → review → fix → final_test
   ↓              ↓                ↓                ↓
Claude/Gemini   Claude/Gemini     Codex          Codex/Claude
                           
브라우저/DB/GitHub → MCP Tool Layer
```

## 시작

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e .
Copy-Item .env.example .env
python -m orchestrator.supervisor workflows/feature.yaml "Spring Boot 로그인 기능 구현"
```

각 CLI가 PATH에서 실행 가능해야 합니다.

```powershell
codex --version
claude --version
gemini --version
```

자세한 설치 및 운영 기준은 `docs/WINDOWS_SETUP.md`, Agent 규칙은 `AGENTS.md`, 워크플로우 정책은 `WORKFLOW.md`를 확인하세요.

## 보안 원칙

- API Key, 토큰, SSH private key, 비밀번호를 Git에 저장하지 않습니다.
- `.env`는 커밋하지 않습니다.
- 외부 시스템 write/delete/deploy는 승인 단계를 두는 것을 기본으로 합니다.
- Agent 출력은 명령이 아니라 비신뢰 입력으로 취급하고 Supervisor가 검증합니다.
