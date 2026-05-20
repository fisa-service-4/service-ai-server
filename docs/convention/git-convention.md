# git-convention.md

# git convention

## 브랜치 전략

| 브랜치     | 역할    |
|---------|-------|
| main    | 운영 배포 |
| develop | 개발 통합 |

- main 직접 push 금지
- develop 직접 push 금지
- PR 기반으로만 merge

---

## 작업 브랜치 규칙

### 순서

```
1. 이슈 생성 (이슈 템플릿 사용)
2. 브랜치 생성
3. 작업
4. PR 생성
```

### 브랜치 네이밍

```
type/#이슈번호-description

예시
feat/#12-login-api
fix/#31-assets-chart
refactor/#44-home-layout
docs/#55-api-spec
```

### 브랜치 타입

| 타입       | 설명                | 예시                         |
|----------|-------------------|----------------------------|
| feat     | 새로운 기능 추가         | 로그인 기능 추가, 자산 조회 API 구현    |
| fix      | 버그 수정             | 차트 렌더링 오류 수정, 로그인 실패 문제 해결 |
| refactor | 기능 변화 없는 코드 구조 개선 | 컴포넌트 분리, 서비스 레이어 구조 개선     |
| docs     | 문서 수정             | API 명세 수정, README 업데이트     |
| style    | 코드 스타일 및 UI 수정    | CSS 수정, prettier 적용, 마진 조정 |
| test     | 테스트 코드 추가 및 수정    | 단위 테스트 추가, Mock 테스트 작성     |
| chore    | 설정/빌드/패키지 등 유지보수  | eslint 설정, dependency 업데이트 |
| hotfix   | 운영 환경 긴급 수정       | 운영 서버 장애 수정, 긴급 배포 대응      |

---

## 커밋 규칙

### 메시지 형식

```
type(domain): 내용 간략하게
- 설명1
- 설명2
```

### 예시

```
feat(auth): 로그인 API 연동
fix(stocks): 주문 수량 validation 수정
refactor(home): 카드 컴포넌트 분리
```

### 규칙

- .gitmessage 템플릿 사용
- 하나의 commit에는 하나의 작업만 포함
- 제목 50자 이내
- 제목 끝에 마침표(.) 금지
- 제목과 본문 사이 한 줄 공백
- 본문 한 줄 72자 이내

### .gitmessage 로컬 설정

```bash
git config --global commit.template .gitmessage
```

### .gitmessage 내용

```
# ------------------------------------------------------------------
# Commit Message Template
# type(scope): subject
# ------------------------------------------------------------------
#
# 타입 종류
# feat     : 새로운 기능 추가
# fix      : 버그 수정
# refactor : 리팩토링
# docs     : 문서 수정
# style    : 코드 포맷팅, UI/CSS 수정
# test     : 테스트 코드
# chore    : 빌드, 설정, 패키지 관리
# hotfix   : 운영 긴급 수정
#
# 예시
# feat(auth): 로그인 API 연동
# fix(stocks): 주문 수량 validation 수정
# refactor(home): 카드 컴포넌트 분리
#
# ------------------------------------------------------------------
# 제목은 50자 이내
# 제목과 본문 사이 한 줄 공백
# 제목 끝에 마침표(.) 금지
# 명령문 형태 사용 (ex: 수정한다(X) / 수정(O))

type(scope): subject

# ------------------------------------------------------------------
# Body (선택)
# 무엇을 왜 변경했는지 작성
# 한 줄은 72자 이내 권장
# ------------------------------------------------------------------

# - 로그인 실패 시 예외 처리 추가
# - JWT 만료 검증 로직 수정
# - 잘못된 응답 코드 반환 문제 해결

# ------------------------------------------------------------------
# Footer (선택)
# 관련 이슈 작성
# ------------------------------------------------------------------

# Closes #이슈번호
# Related to #이슈번호
```

---

## PR 규칙

### PR 제목

```
[type/domain] 작업 내용

예시
[feat/auth] 로그인 기능 구현
[fix/assets] 자산 차트 오류 수정
```

### domain 목록

| domain       | 설명    |
|--------------|-------|
| auth         | 인증    |
| home         | 홈     |
| assets       | 자산    |
| stocks       | 증권    |
| contracts    | 계약    |
| notification | 알림    |
| mypage       | 마이페이지 |
| admin        | 관리자   |
| ai           | AI    |
| mydata       | 마이데이터 |
| infra        | 인프라   |
| batch        | 배치    |
| gateway      | 게이트웨이 |

### PR 생성 규칙

- 작업 완료 후 PR 생성
- PR 템플릿 필수 작성

---

## Merge 규칙

- main 직접 merge 금지
- force push 금지
- develop 머지: 최소 1명 승인
- main 머지: 최소 2명 승인
- Squash merge 사용
    - 1개 issue → 1개 branch → commit 여러 개 → squash merge
- 머지 후 브랜치 삭제