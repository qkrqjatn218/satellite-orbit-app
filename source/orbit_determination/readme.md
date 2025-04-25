# Obrit propagation & estimation

## Propagation

## `ddper`

이 함수는 깊은 공간(long-period deep-space) 주기성 섭동(deep space periodic perturbations)을 처리합니다. `dpper`는 위성의 평균 궤도 요소(mean orbital elements)에 적용되는 **장주기(long-period)** 섭동 효과를 계산하고 반영합니다.


🔭 함수 목적 요약

- `dpper`는 태양과 달에 의한 장주기 섭동을 계산하여, 위성의 궤도 요소에 보정값(periodic correction)을 더합니다.
- 이 보정값은 SGP4에서 기본적으로 사용하는 평균 궤도 요소들을 더 현실에 맞게 조정해줍니다.
- Epoch(기준시점)에서는 섭동값이 0이 되도록 설계되어 있으며, 시간 `t`가 증가함에 따라 점차 효과가 누적됩니다.
- `dpper`는 SGP4에서 위성 궤도의 장주기 섭동을 계산하고 궤도 요소에 반영하는 핵심 함수입니다.
- 태양과 달의 섭동을 시간에 따라 반영하여 궤도 요소의 정확도를 향상시킵니다.
- `dpper`는 깊은 우주 섭동이 고려되는 경우(SDP4)에만 호출되며, 보통 **고궤도 위성(GEO, Molniya 등)** 에서 사용됩니다.


🧩 주요 변수 역할

| 변수 | 설명 |
|------|------|
| `t` | Epoch 이후 경과 시간 (minutes) |
| `zmos`, `zmol` | 태양/달 섭동의 기준 위상 (solar/lunar mean anomalies at epoch) |
| `zns`, `znl` | 태양/달 섭동 주기 계수 |
| `se2`, `se3`, `si2`, ..., `xl4` | 깊은 공간 섭동을 위한 사전 계산된 계수 |
| `ep`, `inclp`, `nodep`, `argpp`, `mp` | 평균 궤도 요소들 (eccentricity, inclination, RAAN, argument of perigee, mean anomaly) |


### 1. 태양 섭동에 대한 주기 함수 계산
```python
zm = zmos + zns * t
zf = zm + 2 * zes * sin(zm)
```
- 태양 섭동에 따른 평균 근점 이각을 계산하고, 이에 기반한 `f2`, `f3`, `sinzf`를 계산합니다.
- 이를 기반으로 태양의 섭동 효과를 나타내는 `ses`, `sis`, `sls`, `sghs`, `shs`를 구합니다.

### 2. 달 섭동에 대한 주기 함수 계산
```python
zm = zmol + znl * t
zf = zm + 2 * zel * sin(zm)
```
- 위와 유사한 방식으로 달의 섭동에 대한 효과(`sel`, `sil`, `sll`, `sghl`, `shll`)를 계산합니다.

### 3. 섭동 총합 계산
```python
pe = ses + sel
pinc = sis + sil
pl = sls + sll
pgh = sghs + sghl
ph = shs + shll
```
- 태양과 달에 의한 섭동값을 합쳐 최종 보정값 생성

### 4. Epoch 이후 호출 시, 원래 값과의 차이를 사용
```python
if init == 'n':
    pe -= peo
    pinc -= pinco
    ...
```
- `init == 'y'`일 때는 초기화 목적이므로 섭동 적용 X
- `init == 'n'`일 때만 실제 섭동 적용


🛠️ 섭동 적용 방식

- **기본적 적용 (inclination ≥ 0.2 rad)**:
  - 선형 보정을 통해 `mp`, `argpp`, `nodep` 등을 업데이트

- **Lyddane 보정법 적용 (inclination < 0.2 rad)**:
  - 낮은 경사각에서는 수치적 불안정성이 발생할 수 있으므로 Lyddane 수정법 사용
  - 삼각함수를 이용한 기하학적 방식으로 `nodep`, `argpp` 재계산



📚 참고문헌 기반

이 함수는 NORAD에서 개발한 SGP4의 일부이며, 다음과 같은 문헌에 기반을 두고 있습니다:
- Hoots & Roehrich (Spacetrack Report #3, 1980)
- Vallado et al. (2006) – SGP4/SDP4 재정립 및 C++/Python 구현

---
---

## `dscom`

 `dscom` 함수는 SGP4 모델의 **깊은 우주(Deep Space) 섭동 모델** 중에서 핵심적인 전처리 루틴으로, 이후 사용하는 `dpper` (장주기 주기 섭동)나 `dsinit` (장주기 세속 섭동)에서 공통적으로 쓰이는 변수들을 계산합니다. 이름도 **Deep Space COMmon**의 약자야.

🧠 핵심 목적

`dscom`은 다음과 같은 **공통 파라미터 및 계수들을 사전 계산**해서 반환해줍니다:

- 태양과 달에 의한 섭동을 위한 **삼각함수 계수 및 중간 변수**
- SGP4에서 쓰이는 다양한 고정 상수들
- **장주기 섭동**을 위해 필요한 고차 항 계산
- 후속 루틴(`dpper`, `dsinit`)의 효율성을 위한 사전 준비


📌 요약

| 항목 | 설명 |
|------|------|
| 🌍 함수 역할 | 태양/달 섭동을 위한 공통 변수 계산 |
| 🛠️ 출력 | `dpper`, `dsinit`에서 사용하는 모든 고차 계수, 각종 sin/cos 기반 계수 등 |
| 🔁 처리 루프 | 1회차: 태양 섭동 계수 저장, 2회차: 달 섭동 계수 계산 |
| 📅 위상 변수 | `zmos`, `zmol` 계산해서 시간 기반 진동 함수에 쓰임 |
| 📚 참고문헌 | Vallado (2006), Spacetrack Report #3, #6 등 고전적 궤도역학 문헌 기반 |

🔧 주요 기능별 설명

### 1. 상수 초기화

```python
zes = 0.01675   # 태양 섭동 계수
zel = 0.05490   # 달 섭동 계수
c1ss, c1l = ... # 섭동 항을 위한 scaling factor
```

### 2. 궤도 요소에서 유도된 기초 삼각함수 값 계산

```python
snodm = sin(nodep)
cnodm = cos(nodep)
sinomm = sin(argpp)
cosomm = cos(argpp)
sinim = sin(inclp)
cosim = cos(inclp)
emsq = ep^2
```

이 값들은 나중에 궤도 요소의 섭동 항을 계산할 때 쓰이는 **기초 요소들**이다.


### 3. Epoch을 기반으로 태양/달의 위치 파악

```python
day = epoch + 18261.5 + tc / 1440.0
xnodce = (4.5236020 - 9.2422029e-4 * day) % twopi
```

- `xnodce`는 달의 평균 상승교점에 해당하는 위치.
- 태양과 달의 위치 변화량을 `day` 기준으로 계산.


### 4. 태양계 섭동 계수 계산 (두 번 루프 돌면서 태양, 달 각각 처리)

- 첫 번째 루프 (`lsflg == 1`)에서는 **태양 계수 저장**
- 두 번째 루프 (`lsflg == 2`)에서는 **달 계수 계산**
  
여기에서 계산되는 건 대부분 고차항 포함된 값들이야:

```python
z1, z2, z3         # 태양/달 중력 간섭의 이차 이상 계수
z11, ..., z33      # 고차 섭동 항
s1~s7, ss1~ss7     # 섭동 효과 계수들
sz1~sz33           # 섭동 텐서 요소들
```

예시:

```python
z1 = 3(a1² + a2²) + z31 * em²
z11 = -6a1a5 + em² * (복잡한 섭동 항들)
s1 = -15 * em * s4
```

이 항들은 궤도의 평균운동, 이심률, 경사각, 근점이각, RAAN 등의 요소들이 **태양과 달의 섭동에 따라 어떻게 영향을 받는지**를 수학적으로 모델링한 것들이야.


### 5. 섭동 항 파라미터 계산

각종 섭동 계수들을 최종적으로 계산해서 이후 `dpper`와 `dsinit`에서 궤도 요소를 조정할 수 있도록 준비:

- 태양 섭동 계수:
  ```python
  se2, se3, si2, si3, sl2, sl3, sl4, sgh2, sgh3, sgh4, sh2, sh3
  ```

- 달 섭동 계수:
  ```python
  ee2, e3, xi2, xi3, xl2, xl3, xl4, xgh2, xgh3, xgh4, xh2, xh3
  ```

- 위 계수들은 `dpper()`에서 시간 `t`에 따른 진동 함수와 함께 사용되어 위성 궤도 요소에 섭동을 적용해.


### 6. 위상 변수 계산

```python
zmol = (4.7199672 + 0.22997150  * day - gam) % twopi  # 달 위상
zmos = (6.2565837 + 0.017201977 * day) % twopi        # 태양 위상
```
이 위상 변수들은 `dpper`에서 시간 함수의 기준점으로 사용됨.


---
---

## `dsinit`

이 함수 `_dsinit`는 SGP4 (Simplified General Perturbations model 4)의 딥스페이스 초기화 루틴으로, 위성이 지구 중심에서 멀리 떨어진 심우주 (deep-space) 궤도일 때 적용되는 특별한 전파 조건을 준비하기 위한 핵심 알고리즘이야. 일반 LEO보다 높은 궤도 (e.g., GEO, Molniya 등)에서의 궤도 공명을 처리하기 위한 전처리 단계로 보면 돼. 이 함수의 주요 목적은 공명 조건을 분석하고, 태양과 달에 의한 장기 섭동(long-period perturbations) 효과를 계산하는 거야.

핵심 구성은 다음과 같아:


### 🌌 1. Deep-space 공명 조건 확인 (`irez`)
- 위성의 평균 운동(nm)을 통해 위성이 공명 상태인지 판단:
  - `irez = 1`: synchronous resonance (GEO 근처)
  - `irez = 2`: 12-hour resonance (Molniya 등)
  - 그 외: non-resonant (irez = 0)


### 🌞 2. 태양 섭동 계산
- `ses`, `sis`, `sls`, `sghs`, `shs` 계산
- 위성 궤도 요소 변화율인 `dedt`, `didt`, `dmdt`, `domdt`, `dnodt` 등을 구함


### 🌙 3. 달 섭동 계산
- lunar terms 포함 (`sghl`, `shll`)
- inclination 180도 근처의 특이점 처리


### 📡 4. 장기 섭동 영향을 반영한 요소 갱신
- `em`, `inclm`, `argpm`, `nodem`, `mm` 등의 변화 적용
- `theta`는 현재 GST (Greenwich Sidereal Time)와 관련


### 🌀 5. 공명 시 추가 항 계산 (only when `irez ≠ 0`)
- `gxxx`, `fxxx`: 계수로 사용되는 고차 다항식 (궤도 공명 계수)
- `dxxxx`: 공명에 의한 주기적 항의 계수
- `xfact`, `xlamo`, `xli`, `xni` 등은 공명 적분기의 초기 상태 설정용


🔄 출력값
궤도 요소와 공명 변수들을 리턴하며, 이 값들은 SGP4 알고리즘의 메인 루틴에서 시간에 따라 업데이트에 사용돼.

🔍 정리하면
- 이 함수는 *SGP4 전용*의 **딥스페이스 공명과 섭동을 고려한 초기화 알고리즘**이야.
- 주로 GEO 이상의 궤도에서 **장기적인 궤도 진화 예측**에 사용돼.
- "해석적 궤도 전파"와는 다르며, 정확하게는 *반해석적 (semi-analytical)* 접근에 해당함.
- LEO와 같은 저궤도 위성에서는 거의 사용되지 않아 (SGP4의 deep-space branch가 아님).


📌 참고로, GPS pseudorange 기반의 저궤도 위성 궤도결정에선 보통 Kalman filter + 수치 전파 (ex. Cowell's method, RK4 등)를 써. `SGP4`는 관측자료 없이 TLE 기반으로만 전파하는 모델이야.

---
---

## `dspace`

이 함수는 SGP4 위성 궤도 전파 모델 중 **Deep Space (심우주) 전파기**에서 사용하는 `_dspace` 함수야. 이건 기본적으로 위성이 지구에서 멀리 떨어진 고궤도(예: 정지궤도, Molniya 궤도 등)에 있을 때 적용되는 **공명 효과 및 외력(태양, 달)의 영향**을 수치적으로 보정하는 **수치 적분 기반의 보정 루틴**이야.

✅ `_dspace` 함수의 목적
- 시간 `t`만큼 지난 후 궤도 요소들의 변화를 계산하기 위해 **수치적분 방식으로 공명 효과(resonance effects)**를 모델링
- `_dsinit`에서 초기화된 공명 계수와 지자기, 태양/달 중력 간섭 계수를 이용해서, 궤도 요소의 변화량(`dndt`, `xni`, `mm`, 등)을 누적적으로 계산


🔧 주요 처리 흐름 요약
1. **기본 궤도 요소 보정**
   - `em`, `inclm`, `argpm`, `nodem`, `mm` 등을 `dedt`, `didt`, `domdt`, `dnodt`, `dmdt`를 이용해 선형적으로 시간 `t`만큼 업데이트

2. **수치 적분 초기화**
   - 이전 적분 시간 `atime`이 `t`와 조건을 만족하지 않으면 새로 시작
   - 적분 간격은 `stepp` (720초) 또는 `stepn` (-720초)

3. **수치 적분 반복 (while 루프)**
   - 공명 계수를 이용해 `xndt` (속도 변화량), `xnddt` (가속도) 계산
   - 현재 위상 `xli`, 평균 운동 `xni` 업데이트
   - `atime`을 갱신하며 `t`까지 반복

4. **최종 평균 운동 `nm`, 평균 이각 `mm` 보정**
   - 마지막으로 예측된 운동량(`xni`)과 속도 보정을 이용해 `nm`, `mm`를 갱신
   - 이는 추후 위치 계산에서 주요 입력이 됨


💡 핵심 변수 정리

| 변수       | 설명 |
|------------|------|
| `irez`     | 공명 종류: 0(없음), 1(정지궤도 근처), 2(12시간 공명) |
| `xli`      | 위성의 위상 (lamo) |
| `xni`      | 평균 운동량 (angular velocity) |
| `del1~del3`, `d2201~d5433` | 공명 보정 계수 |
| `t`, `atime` | 현재 시간, 이전 적분 시간 |
| `xndt`, `xnddt` | 속도, 가속도 변화량 |
| `mm`, `nm` | 평균 이각, 평균 운동 |


🧠 핵심 아이디어
- 공명 효과는 위성 궤도에서 특정 주기로 반복되는 천체역학적 현상인데, 이것이 위성의 평균 운동에 미세하지만 지속적인 영향을 준다.
- 이를 반영하지 않으면 장기간 예측에서 큰 오차가 발생하기 때문에, 이 함수는 시간에 따른 궤도 요소의 보정값을 수치 적분을 통해 계산한다.

---
---

## `initl`

`_initl()` 함수란
SGP4 알고리즘의 **초기화 루틴** 중 하나로, 위성의 궤도 요소와 지구 상수들을 기반으로 한 보조 변수들(auxiliary variables)을 계산한다. 이 함수는 특히 **비-Kozai 평균 운동 보정**과 **sidereal time 계산**을 포함하며, 이 값들은 궤도 전파에서 핵심적으로 사용돼.


🔧 주요 목적
1. **평균 운동 보정**  
   TLE의 평균 운동(`no`)은 지구의 비구형성(J2 효과)을 반영한 게 아니라서, 이를 **un-Kozai 보정**을 통해 정규화된 평균 운동으로 환산함.

2. **궤도 요소 보조 변수 계산**  
   - 반장반축(`ao`), 궤도 이심률 제곱(`eccsq`), 궤도 경사각의 코사인(`cosio`) 등
   - 궤도 주기 관련 변수(`ainv`, `po`, `posq`, `rp` 등)

3. **그리니치 항성시(GST) 계산**  
   `opsmode`에 따라 구 방식(a-mode) 또는 현대식(i-mode)을 선택해 계산함.


⚙️ 주요 계산 흐름

1. **평균 운동 관련 보정**

```python
ak = pow(xke / no, 2.0 / 3.0)  # 초기 반장반축 비례값
d1 = 0.75 * j2 * (3cos²i - 1) / (sqrt(1-e²) * (1-e²))
del_ = d1 / ak²
adel = ak * (1 - del_² - del_ * (1/3 + 134del_² / 81))
no = no / (1 + del_)  # 최종적으로 보정된 평균 운동
```

이 과정은 지구의 불균일한 중력장을 고려한 **un-Kozai 보정** 이라고 부름


2. **보조 궤도 변수 계산**

```python
ao = pow(xke / no, 2.0 / 3.0)  # 보정된 반장반축
po = ao * (1 - e²)             # 반장반축 x (1 - 이심률 제곱)
rp = ao * (1 - e)              # 근지점 거리
ainv = 1 / ao                  # 1 / 반장반축
con42 = 1 - 5 * cos²i          # 공식용 변수
con41 = -con42 - 2cos²i        # 공식용 변수
```

이런 변수들은 SGP4 본 루틴에서 공력 항력 및 지오포텐셜 관련 항에서 사용됨.


3. **그리니치 항성시(GST) 계산**

```python
if opsmode == 'a':  # "a"는 전통적인 AFSPC 방식
    gsto = 오래된 방식으로 계산
else:
    gsto = _gstime(epoch + 2433281.5)  # 현대식 계산 (기준점이 다름)
```

GST는 위성의 위치를 지구 기준계에서 표현하기 위해 필수적인 요소


📦 반환값

| 반환값      | 설명 |
|-------------|------|
| `no`        | 보정된 평균 운동 |
| `method`    | 전파기 방식 (SGP4는 `n`) |
| `ainv`, `ao`| 궤도 반장반축 관련 값 |
| `con41`, `con42` | 공식 내부에서 쓰이는 경사각 관련 보조 항 |
| `cosio`, `cosio2`| 경사각의 코사인 및 제곱 |
| `eccsq`, `omeosq`| 이심률 제곱과 1 - 이심률 제곱 |
| `posq`, `rp` | 궤도 면적, 근지점 거리 |
| `rteosq` | √(1 - e²) |
| `sinio` | sin(inclination) |
| `gsto` | 초기 항성시 |


🧠 정리: `_initl`의 역할할

> 위성 궤도 전파를 위한 **기초 준비 단계**로,  
> - 평균 운동을 보정하고  
> - 필요한 보조 변수들을 계산하고  
> - 초기 시간에 대한 항성시를 계산함  
> 이 과정 없이 SGP4 본 루틴은 정확한 위치/속도 예측을 할 수 없어.

---
---

## `sgp4init`

이 함수는 SGP4(Simple General Perturbations 4) 모델을 초기화하는 핵심 함수로, 위성의 TLE 데이터를 바탕으로 전파에 필요한 내부 변수들을 설정하는 과정을 수행. `sgp4init`는 SGP4 모델이 궤도를 정확히 예측할 수 있도록, 위성의 초기 궤도 요소들을 바탕으로 필요한 상수들과 파생 변수들을 계산해서 `satrec` 객체(위성 객체)에 저장하는 역할


🔧 주요 입력 인자
- `whichconst`: 물리 상수들 묶음 (예: xke, j2, mu 등)
- `opsmode`: 운영 모드 ('a': 오래된 방식, 'i': 현대식)
- `satn`: 위성 번호
- `epoch`: 에포크 시간 (UTC Julian Date - 2433281.5 기준)
- `xbstar`, `xndot`, `xnddot`: 대기항력 관련 요소
- `xecco`: 이심률  
- `xargpo`: 근일점 경도  
- `xinclo`: 경사각  
- `xmo`: 평균 근점 이각  
- `xno_kozai`: 평균 운동 (Kozai mean motion)
- `xnodeo`: 승교점 경도  
- `satrec`: 위성 구조체 (출력 저장용)


🧩 전체 흐름 요약

1. **변수 초기화**
   - `satrec`에 저장될 모든 변수들을 0 또는 초기값으로 설정.

2. **물리 상수 세팅**
   - `whichconst`에서 지구의 중력계수, 반지름, J2, J3 등의 상수값 추출.

3. **평균 운동 Un-Kozai 처리**
   - Kozai 보정을 적용하여 `no_kozai`에서 "진짜" 평균 운동을 도출.

4. **공전 궤도 특성값 계산**
   - 반장축(`a`), 근지점 고도, 원지점 고도, 각종 수치적 안정성을 위한 보조 상수들 계산.

5. **저궤도 위성 여부 판단**
   - 궤도가 지표면에서 너무 낮은 경우 `isimp` 플래그를 설정.

6. **공기 저항 모델 초기화**
   - CC1~CC5, T2~T5계수 계산 → 시간에 따른 대기항력 예측에 쓰임.

7. **심우주 전파 초기화 (Deep-space Mode)**
   - 위성이 225분 이상 주기를 가지면 SGP4가 아닌 SDP4 모드로 진입
   - `_dscom`, `_dpper`, `_dsinit` 등을 통해 공전 요소 재정의

8. **SGP4 실행을 통한 에포크 상시화**
   - 초기 시간 t=0에서 SGP4 한 번 실행 → 내부 변수 정렬


📘 내부 함수들 간 역할 요약

| 함수 | 역할 |
|------|------|
| `_initl` | 평균 운동 보정, 기본 궤도 요소 계산 |
| `_dscom` | 심우주에서의 궤도 요소 보정 (precession 등) |
| `_dpper` | 심우주 환경에서의 perturbation 보정 |
| `_dsinit` | 심우주 전파기에서 사용하는 변수들 초기화 |
| `sgp4` | 초기 시점(t=0.0)에서 궤도 예측 (1회 실행) |


📦 최종적으로 설정되는 주요 값들 (satrec 내부에 저장)

- `no_unkozai`: Un-Kozai된 평균 운동
- `a`: 반장축
- `cc1 ~ cc5`: 대기 저항 계수
- `mdot`, `argpdot`, `nodedot`: 평균 이각, 근일점, 승교점 변화율
- `irez`: 공진 여부 (0, 1, 2)
- `xlamo`, `xli`, `xni`: 공진 상태에서의 위상, 주기 등
- `method`: 'n' (near-Earth), 'd' (deep-space)
- `init`: 초기화 완료 후 `'n'`으로 변경됨

---
---

## `sgp4`

`sgp4` 함수는 SGP4(Simple General Perturbations 4) 위성 궤도 전파 모델의 중심 함수로, 위성의 초기 궤도 요소들과 경과 시간(`tsince`)을 이용해 **위성의 위치와 속도를 계산**하는 최종 루틴이야. 아래에 이 함수의 작동 원리를 단계적으로 정리해봤어:


🌐 1. 입력값

- `satrec`: 위성의 궤도 요소와 상수들을 담고 있는 구조체 (보통 `sgp4init`에서 초기화됨)
- `tsince`: 에포크로부터 경과된 시간 (분 단위)


🧠 2. 상수 및 준비

- `x2o3`: 2/3, 자주 쓰이는 상수
- `twopi`: 2π
- `vkmpersec`: 속도를 km/s 단위로 변환하는 상수


🔄 3. 평균 궤도 요소 업데이트 (Secular Effects)

- 중력장 비대칭(J2)과 대기 항력 등을 고려해서 선형 변화량 반영
  - `xmdf`, `argpdf`, `nodedf`: 평균 근점이각, 평균 이각, 평균 상승경도
  - `tempa`, `tempe`, `templ`: 항력 관련 보정값


🧠 4. Deep Space 보정 (if `method == 'd'`)

- geostationary나 HEO처럼 주기가 긴 위성은 심우주 보정을 적용
- `_dspace` 함수 호출로 심우주 공명 효과 반영
  - 결과로 mean motion(`nm`)이나 inclination(`inclm`) 등이 보정됨



🧮 5. 평균 운동량 재계산

- `am`: 궤도 반장축
- `nm`: 평균 운동량 보정 (위 값에 기반)
- `em`: eccentricity 업데이트

이때 보정된 excentricity나 mean motion이 물리적으로 유효한지 검사를 하고, 오류 메시지를 생성할 수도 있음.


📈 6. 평균 요소 → 진 요소로 변환

- 평균 궤도 요소를 기반으로 실제 위치 계산을 위해 진 요소로 변환
- 다시 `_dpper` 호출로 lunisolar perturbation 고려
- `Kepler's Equation`을 수치적으로 풀어서 eccentric anomaly 구함


📐 7. 위치/속도 계산 (in perifocal frame → ECI)

- `r`, `v` 계산: 위성의 위치와 속도를 ECI (지구 중심 관성 좌표계) 기준으로 계산
  - 보통 단위는 km, km/s

- 벡터 회전을 통해 궤도 좌표계를 관성 좌표계로 변환


⚠️ 8. 오류 처리

- 궤도가 타원인지 확인 (`em < 1.0`)
- `pl`, `mrt` 등이 음수면 물리적으로 의미 없는 상태로 판단 → 오류 플래그 설정


✅ 9. 결과 반환

```python
return r, v
```

- `r`: 위성의 위치 벡터 (x, y, z) in km
- `v`: 속도 벡터 (vx, vy, vz) in km/s


💡 참고 요약

| 항목 | 의미 |
|------|------|
| `satrec` | 위성 상태 구조체 (SGP4 내부 상태 포함) |
| `tempa, tempe, templ` | 대기 항력에 의한 보정 요소 |
| `_dspace` | 심우주 공명 효과 반영 |
| `_dpper` | 태양/달에 의한 장주기 섭동 반영 |
| `Kepler 반복` | eccentric anomaly 구하기 위한 수치해 |
| `mrt < 1.0` | 위성 고도가 지표면 아래면 → decayed 상태 |

