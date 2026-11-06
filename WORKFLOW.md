> **2026-11-07 구독·정책 게이트:** 아래 역할/대체표는 과거 개념 설계이며, 세 벤더 소비자 구독을 하나의 앱에서 무제한 전환할 수 있다는 의미가 아닙니다. 현재 코드에서 기본 허용하는 것은 직접 ChatGPT 구독 로그인한 Codex CLI뿐입니다. Claude는 개인 native CLI 구독·명시적 opt-in 검증 후에만, AGY는 다른 에이전트가 호출하지 않는 별도 공식 워크플로우에서 실행해야 합니다. 구독 전용 경로와 dry-run은 `workflows/subscription-safe.yaml`; 정책 세부는 `docs/OPENCODE_GAP_AND_SUBSCRIPTION_POLICY.md` 참조. 자동 완료·재실행·API 과금을 전제로 하지 않습니다.

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
