# 코드 주석 컨벤션

## 개요

| 언어 | 함수/클래스 주석 | 인라인 주석 | FIXME 마킹 |
|------|----------------|------------|-----------|
| Java | Javadoc (`/** */`) | `//` | `// FIXME(tag):` |
| TypeScript | JSDoc (`/** */`) | `//` | `// FIXME(tag):` |
| Python | Docstring (`""" """`) | `#` | `# FIXME(tag):` |

---

## 1. 함수/클래스 설명 주석

### Java — Javadoc

```java
/**
 * 간단한 한 줄 설명.
 *
 * <p>필요 시 상세 설명을 추가한다.</p>
 *
 * @param userId 사용자 ID
 * @return 사용자 정보 객체
 * @throws UserNotFoundException 사용자를 찾을 수 없는 경우
 */
public User getUser(Long userId) {  }
```

**규칙**
- 첫 줄: 마침표로 끝나는 한 줄 요약
- 상세 설명이 필요한 경우 `<p>` 태그로 분리
- 모든 `@param`, `@return`, `@throws` 명시
- `void` 반환은 `@return` 생략

---

### TypeScript — JSDoc

```typescript
/**
 * 간단한 한 줄 설명.
 *
 * @param userId - 사용자 ID
 * @returns 사용자 정보 객체
 * @throws {UserNotFoundException} 사용자를 찾을 수 없는 경우
 */
function getUser(userId: number): User {  }
```

**규칙**
- `@param` 이름 뒤에 `-` 구분자 사용
- `@throws`는 `{ErrorType}` 형식으로 타입 명시
- TypeScript 타입이 명확하면 `@param {type}` 타입 생략 가능

---

### Python — Docstring

```python
def get_user(user_id: int) -> User:
    """간단한 한 줄 설명.

    Args:
        user_id: 사용자 ID

    Returns:
        사용자 정보 객체

    Raises:
        UserNotFoundException: 사용자를 찾을 수 없는 경우
    """
```

**규칙**
- Google Style Docstring 사용
- 한 줄로 충분하면 `"""한 줄 설명."""` 형식 허용
- Type hint가 있으면 Args에서 타입 생략 가능

---

## 2. 인라인 로직 설명 주석

코드만 봐도 알 수 있는 것은 주석을 달지 않는다.  
**무엇(What)** 이 아닌 **왜(Why)** 위주로 작성한다.

```java
// Java
int adjusted = value * 2; // 픽셀 밀도 보정 (Retina 디스플레이 대응)
```

```typescript
// TypeScript
const delay = 300; // debounce: 연속 입력 중 불필요한 API 호출 방지
```

```python
# Python
result = data[1:]  # 첫 번째 행은 헤더이므로 제외
```

**규칙**
- 로직의 의도나 이유가 불명확한 경우에만 작성
- 코드와 같은 줄 또는 바로 윗줄에 위치
- 주석이 없으면 이해하기 어려운 경우에만 추가

---

## 3. FIXME / TODO 마킹

### 포맷

```
// FIXME(태그): 설명
// TODO: 설명
```

### 태그 종류

| 태그 | 용도 | 예시 |
|------|------|------|
| `MOCK` | 임시 하드코딩 / Mock 데이터 | API 연동 전 더미 데이터 |
| `#이슈번호` | 특정 이슈/티켓과 연결 | `FIXME(#123):` |
| `TEMP` | 임시 처리 / 추후 제거 필요 | 긴급 핫픽스 등 |

### 예시

```java
// Java
// FIXME(MOCK): 실제 API 연동 전 임시 하드코딩 데이터
List<User> users = List.of(new User(1L, "테스트유저"));

// FIXME(#42): 결제 실패 케이스 예외처리 미완성
// TODO: 캐싱 전략 검토 후 적용
```

```typescript
// TypeScript
// FIXME(MOCK): 인증 API 붙이기 전 임시 토큰
const token = "mock-token-1234";
```

```python
# Python
# FIXME(MOCK): DB 연결 전 임시 반환값
return {"id": 1, "name": "홍길동"}
```

**규칙**
- `FIXME`: 반드시 수정이 필요한 것
- `TODO`: 기능 개선이나 리팩토링 등 선택적 작업
- 태그는 소괄호 `()` 안에 작성, 이유나 이슈번호 명시 권장