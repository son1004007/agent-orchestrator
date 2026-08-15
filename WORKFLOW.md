# Workflow Policy

## 기본 Feature Workflow

```text
requirements
→ architecture
→ implement
→ test
→ review
→ fix
→ final_test
```

## 단계별 정책

| 단계 | 기본 Agent | 실패 시 |
|---|---|---|
| requirements | claude | gemini |
| architecture | claude | gemini |
| implement | codex | claude |
| test | codex | claude |
| review | claude | gemini |
| fix | codex | claude |
| final_test | codex | claude |

## 재시도

- 동일 Agent 재시도: 최대 1회
- 이후 fallback Agent로 전환
- 모든 후보 실패 시 workflow를 FAILED로 종료하고 오류를 보존

## Agent가 결정하지 않는 것

다음은 LLM이 임의로 바꾸지 않습니다.
- workflow 단계 순서
- 승인 필요 작업 목록
- secret 처리 정책
- 최대 retry/timeout
- repository destructive operation 정책

## 향후 확장

현재는 CLI/SDK adapter를 우선 사용합니다. Agent 간 상호운용성이 필요해지면 adapter 경계 뒤에 A2A transport를 추가합니다.
