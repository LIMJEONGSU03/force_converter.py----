import csv
import math
from pathlib import Path

import matplotlib.pyplot as plt


def main():
    csv_path = Path(__file__).with_name("load_bad.csv")
    result_path = Path(__file__).with_name("load_result.csv")
    plot_path = Path(__file__).with_name("stress_plot.png")
    area_mm2 = 100
    reference_stress_MPa = 6
    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        required_columns = {"time_s", "force_N"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError("CSV에 time_s와 force_N 열이 필요합니다.")

        data = []
        excluded_rows = 0
        for row in reader:
            parsed_values = {}
            row_is_invalid = False
            for column in ("time_s", "force_N"):
                raw_value = row.get(column)
                try:
                    value = float(raw_value)
                    if not math.isfinite(value):
                        raise ValueError
                except (TypeError, ValueError):
                    reason = (
                        "빈칸"
                        if raw_value is None or not raw_value.strip()
                        else "유효한 숫자가 아님"
                    )
                    print(
                        f"문제: 원본 CSV {reader.line_num}행, "
                        f"{column} 값={raw_value!r} ({reason})"
                    )
                    row_is_invalid = True
                else:
                    parsed_values[column] = value

            if row_is_invalid:
                excluded_rows += 1
                continue

            time_s = parsed_values["time_s"]
            force_N = parsed_values["force_N"]
            data.append(
                {
                    "time_s": time_s,
                    "force_N": force_N,
                    "stress_MPa": force_N / area_mm2,
                }
            )

    print(f"제외한 행 수: {excluded_rows}개")
    print(f"유효한 데이터 수: {len(data)}개")
    if not data:
        print("유효한 데이터가 없어 계산을 중단합니다.")
        return

    with result_path.open("w", newline="", encoding="utf-8") as result_file:
        writer = csv.DictWriter(
            result_file, fieldnames=["time_s", "force_N", "stress_MPa"]
        )
        writer.writeheader()
        writer.writerows(data)

    maximum_load = max(data, key=lambda row: row["force_N"])
    maximum_stress = max(data, key=lambda row: row["stress_MPa"])
    above_reference_count = sum(
        row["stress_MPa"] > reference_stress_MPa for row in data
    )

    plt.plot(
        [row["time_s"] for row in data],
        [row["stress_MPa"] for row in data],
        marker="o",
    )
    plt.scatter(
        maximum_stress["time_s"],
        maximum_stress["stress_MPa"],
        color="red",
        zorder=3,
    )
    plt.annotate(
        f"Max: {maximum_stress['stress_MPa']:g} MPa",
        (maximum_stress["time_s"], maximum_stress["stress_MPa"]),
        xytext=(8, -18),
        textcoords="offset points",
    )
    plt.xlabel("Time (s)")
    plt.ylabel("Stress (MPa)")
    plt.savefig(plot_path)
    plt.close()

    print(f"최대 하중: {maximum_load['force_N']:g} N")
    print(f"해당 시간: {maximum_load['time_s']:g} s")
    print(f"최대 응력: {maximum_stress['stress_MPa']:g} MPa")
    print(f"해당 시간: {maximum_stress['time_s']:g} s")
    print(
        f"기준응력 초과 데이터 개수 (> {reference_stress_MPa:g} MPa): "
        f"{above_reference_count}개"
    )


if __name__ == "__main__":
    main()