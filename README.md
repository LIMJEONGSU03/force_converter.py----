# 힘 단위 변환기

## 용도

Tkinter 데스크톱 프로그램으로, 입력한 힘을 뉴턴(N), 킬로뉴턴(kN), 킬로그램힘(kgf)으로 변환해 세 단위의 결과를 함께 보여줍니다. 입력 단위는 `N`, `kN`, `kgf` 중에서 선택할 수 있으며, 기본 선택은 `kN`입니다.

## 화면 조작

- **전체 화면** 버튼 또는 `F11` 키로 전체 화면과 창 모드를 전환합니다.
- 전체 화면에서 `Esc` 키를 누르면 창 모드로 돌아갑니다.
- **최소화** 버튼으로 프로그램 창을 작업 표시줄로 내릴 수 있습니다.

## 필요한 환경

- Python 3
- Tkinter를 사용할 수 있는 Python 설치

이 프로그램은 Python 표준 라이브러리의 `tkinter`만 사용합니다. Tkinter가 설치되어 있지 않다면 해당 Python 환경에 Tkinter를 추가해야 합니다.

## 실행 명령

터미널에서 프로그램 파일이 있는 폴더로 이동한 다음 실행합니다.

```bash
python "force_converter.py 계산기.py"
```

Windows에서는 Python Launcher를 사용해 실행할 수도 있습니다.

```powershell
py ".\force_converter.py 계산기.py"
```

## 입력 예시

### 정상 입력

입력값 `2.5`, 단위 `kN`을 선택하고 **변환**을 누르면 다음 결과가 표시됩니다.

```text
입력 값: 2.50 kN
결과: 2500.00 N
결과: 2.50 kN
결과: 254.93 kgf
```

### 오류 입력

`abc`처럼 숫자가 아닌 값, `0`, 또는 `-1`을 입력하면 다음 오류가 표시됩니다.

```text
잘못된 입력입니다. 양의 숫자를 입력하세요.
```

## 변환 기준

- `1 N = 1 N`
- `1 kN = 1,000 N`
- `1 kgf = 9.80665 N`

결과는 소수점 둘째 자리까지 표시됩니다.

## CSV 하중 분석 프로그램

`load_analyzer.py`는 같은 폴더의 `load_bad.csv`를 읽어 행별 응력과 최대값을 분석합니다. 입력 CSV에는 다음 열이 있어야 합니다.

| 열 이름 | 의미 | 단위 |
| --- | --- | --- |
| `time_s` | 측정 시간 | s |
| `force_N` | 하중 | N |

응력은 `stress_MPa = force_N / area_mm2`로 계산합니다. `N/mm2`는 `MPa`와 같으며, 단면적은 `load_analyzer.py`의 `area_mm2 = 100`에서 설정합니다. 기준응력은 `reference_stress_MPa = 6`이며, 이 값보다 큰 응력(`> 6 MPa`)의 데이터 개수를 출력합니다.

### 필요한 환경

- Python 3
- `matplotlib`

`csv`, `math`, `pathlib`는 Python 표준 라이브러리입니다. `matplotlib`이 없다면 분석에 사용할 Python 환경에 설치합니다.

```bash
python -m pip install matplotlib
```

### 실행 명령

프로그램 파일과 CSV가 있는 폴더에서 실행합니다.

```bash
python .\load_analyzer.py
```

Windows에서는 다음 명령도 사용할 수 있습니다.

```powershell
py .\load_analyzer.py
```

다른 입력 파일을 사용하려면 `load_analyzer.py`의 `csv_path` 파일명을 변경합니다.

### 출력

- 콘솔: 제외한 행 수, 유효 데이터 수, 최대 하중과 해당 시간, 최대 응력과 해당 시간, 기준응력 초과 데이터 수
- `load_result.csv`: 유효 데이터의 `time_s`, `force_N`, 계산된 `stress_MPa` 열
- `stress_plot.png`: 시간–응력 그래프. 최대 응력점은 빨간 점과 값으로 표시합니다.

결과 파일은 프로그램과 같은 폴더에 저장됩니다. 원본 입력 CSV는 수정하지 않습니다.

### 오류 처리

- 입력 CSV에 `time_s` 또는 `force_N` 열이 없으면 필요한 열을 알리는 오류로 분석을 중단합니다.
- 각 행의 `time_s`나 `force_N`이 비어 있거나 숫자가 아니면 원본 CSV의 행 번호와 문제값을 출력하고 해당 행을 분석에서 제외합니다. 제외 행은 한 번만 집계합니다.
- 유효하지 않은 행을 제외한 뒤 유효 데이터가 하나도 남지 않으면 안내를 출력하고 계산을 중단합니다. 이 경우 결과 CSV와 그래프는 새로 저장되지 않습니다.
