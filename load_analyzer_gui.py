import csv
import math
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure


SECTION_DIMENSIONS = {
    "사각형": ("b", "h"),
    "원형봉": ("d",),
    "원형관": ("D", "d"),
    "사각형관": ("B", "H", "t"),
    "H형강": ("B", "H", "tw", "tf"),
}


def read_load_data(csv_path: Path) -> tuple[list[float], list[float], int]:
    times = []
    forces = []
    excluded_rows = 0

    with csv_path.open(newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        required_columns = {"time_s", "force_N"}
        if not required_columns.issubset(reader.fieldnames or []):
            raise ValueError("CSV에 time_s와 force_N 열이 필요합니다.")

        for row in reader:
            values = []
            for column in ("time_s", "force_N"):
                raw_value = row.get(column)
                try:
                    value = float(raw_value)
                    if not math.isfinite(value):
                        raise ValueError
                except (TypeError, ValueError):
                    break
                values.append(value)
            else:
                times.append(values[0])
                forces.append(values[1])
                continue

            excluded_rows += 1

    return times, forces, excluded_rows


def calculate_stresses(
    forces: list[float], area_mm2: float
) -> tuple[list[float], int]:
    stresses = [force / area_mm2 for force in forces]
    if not all(math.isfinite(stress) for stress in stresses):
        raise ValueError("입력한 치수로 유한한 응력을 계산할 수 없습니다.")
    maximum_index = max(range(len(stresses)), key=stresses.__getitem__)
    return stresses, maximum_index


def calculate_section_area(section_type: str, dimensions: dict[str, float]) -> float:
    required_dimensions = SECTION_DIMENSIONS.get(section_type)
    if required_dimensions is None:
        raise ValueError("지원하지 않는 단면 종류입니다.")

    try:
        values = {name: dimensions[name] for name in required_dimensions}
    except KeyError as error:
        raise ValueError(f"필요한 치수 {error.args[0]}를 입력하세요.") from error
    if not all(math.isfinite(value) and value > 0 for value in values.values()):
        raise ValueError("모든 치수는 0보다 큰 유한한 숫자여야 합니다.")

    try:
        if section_type == "사각형":
            area = values["b"] * values["h"]
        elif section_type == "원형봉":
            area = math.pi * values["d"] ** 2 / 4
        elif section_type == "원형관":
            if values["D"] <= values["d"]:
                raise ValueError("외경 D는 내경 d보다 커야 합니다.")
            area = math.pi * (values["D"] ** 2 - values["d"] ** 2) / 4
        elif section_type == "사각형관":
            if 2 * values["t"] >= min(values["B"], values["H"]):
                raise ValueError("두께 t는 폭 B와 높이 H의 절반보다 작아야 합니다.")
            area = values["B"] * values["H"] - (
                (values["B"] - 2 * values["t"])
                * (values["H"] - 2 * values["t"])
            )
        else:
            if 2 * values["tf"] >= values["H"]:
                raise ValueError("플랜지 두께 tf의 두 배는 높이 H보다 작아야 합니다.")
            if values["tw"] > values["B"]:
                raise ValueError("웨브 두께 tw는 플랜지 폭 B보다 클 수 없습니다.")
            area = (
                2 * values["B"] * values["tf"]
                + (values["H"] - 2 * values["tf"]) * values["tw"]
            )
    except OverflowError as error:
        raise ValueError("입력한 치수로 유한한 단면적을 계산할 수 없습니다.") from error

    if not math.isfinite(area) or area <= 0:
        raise ValueError("유효한 단면적을 계산할 수 없습니다.")
    return area


class LoadAnalyzerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("하중 분석기")
        self.root.geometry("850x650")
        self.root.minsize(650, 500)
        self.times: list[float] = []
        self.forces: list[float] = []

        file_panel = ttk.Frame(root, padding=10)
        file_panel.pack(fill=tk.X)

        self.browse_button = ttk.Button(
            file_panel, text="CSV 찾아보기", command=self.choose_csv
        )
        self.browse_button.pack(side=tk.LEFT)

        self.path_var = tk.StringVar()
        self.path_entry = ttk.Entry(
            file_panel, textvariable=self.path_var, state="readonly"
        )
        self.path_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(10, 0))

        self.count_var = tk.StringVar(value="유효 데이터 수: 0개")
        self.count_label = ttk.Label(root, textvariable=self.count_var, padding=(10, 0))
        self.count_label.pack(anchor=tk.W)

        analysis_panel = ttk.LabelFrame(root, text="단면 및 분석", padding=10)
        analysis_panel.pack(fill=tk.X, padx=10, pady=(5, 0))

        ttk.Label(analysis_panel, text="단면 종류").grid(row=0, column=0, sticky=tk.W)
        self.section_type = ttk.Combobox(
            analysis_panel,
            values=tuple(SECTION_DIMENSIONS),
            state="readonly",
            width=12,
        )
        self.section_type.current(0)
        self.section_type.grid(row=0, column=1, padx=(5, 15), sticky=tk.W)
        self.area_var = tk.StringVar()
        ttk.Label(analysis_panel, text="단면적 A").grid(row=0, column=2, sticky=tk.W)
        ttk.Label(analysis_panel, textvariable=self.area_var).grid(
            row=0, column=3, padx=(5, 0), sticky=tk.W
        )

        self.dimension_vars = {
            section: {
                name: tk.StringVar(value="10")
                for name in dimensions
            }
            for section, dimensions in SECTION_DIMENSIONS.items()
        }
        for section_dimensions in self.dimension_vars.values():
            for variable in section_dimensions.values():
                variable.trace_add("write", self.update_area)

        self.dimensions_panel = ttk.Frame(analysis_panel)
        self.dimensions_panel.grid(
            row=1, column=0, columnspan=8, sticky=tk.W, pady=(8, 0)
        )
        self.analyze_button = ttk.Button(
            analysis_panel, text="분석", command=self.analyze
        )
        self.analyze_button.grid(
            row=2, column=0, columnspan=2, pady=(10, 0), sticky=tk.W
        )
        self.maximum_stress_var = tk.StringVar(value="최대 응력: -")
        ttk.Label(analysis_panel, textvariable=self.maximum_stress_var).grid(
            row=2, column=2, columnspan=6, pady=(10, 0), sticky=tk.W
        )
        self.section_type.bind("<<ComboboxSelected>>", self.section_changed)

        graph_panel = ttk.Frame(root, padding=(10, 5, 10, 10))
        graph_panel.pack(fill=tk.BOTH, expand=True)

        self.figure = Figure(figsize=(7, 4), dpi=100)
        self.axes = self.figure.add_subplot(111)
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Stress (MPa)")
        self.axes.grid(True)

        self.canvas = FigureCanvasTkAgg(self.figure, master=graph_panel)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        self.canvas.draw()
        self.section_changed()
        self.update_area()

    def choose_csv(self) -> None:
        selected_path = filedialog.askopenfilename(
            title="CSV 파일 선택",
            filetypes=[("CSV 파일", "*.csv"), ("모든 파일", "*.*")],
        )
        if not selected_path:
            return

        csv_path = Path(selected_path)
        try:
            times, forces, excluded_rows = read_load_data(csv_path)
        except (OSError, UnicodeError, csv.Error, ValueError) as error:
            messagebox.showerror("CSV 읽기 오류", str(error), parent=self.root)
            return

        self.path_var.set(str(csv_path))
        self.times = times
        self.forces = forces
        self.count_var.set(f"유효 데이터 수: {len(times)}개")
        self.clear_analysis()

        if excluded_rows:
            messagebox.showwarning(
                "유효하지 않은 데이터",
                f"유효하지 않은 행 {excluded_rows}개를 제외했습니다.",
                parent=self.root,
            )

    def section_changed(self, *_: object) -> None:
        for widget in self.dimensions_panel.winfo_children():
            widget.destroy()

        section = self.section_type.get()
        for column, name in enumerate(SECTION_DIMENSIONS[section]):
            ttk.Label(self.dimensions_panel, text=f"{name} (mm)").grid(
                row=0, column=column * 2, sticky=tk.W
            )
            ttk.Entry(
                self.dimensions_panel,
                textvariable=self.dimension_vars[section][name],
                width=10,
            ).grid(row=0, column=column * 2 + 1, padx=(5, 15), sticky=tk.W)
        self.update_area()

    def get_section_area(self) -> float:
        section = self.section_type.get()
        dimensions = {
            name: float(variable.get())
            for name, variable in self.dimension_vars[section].items()
        }
        return calculate_section_area(section, dimensions)

    def update_area(self, *_: object) -> None:
        try:
            area = self.get_section_area()
        except (KeyError, ValueError):
            self.area_var.set("입력 확인 (mm²)")
        else:
            self.area_var.set(f"{area:g} mm²")
        self.clear_analysis()

    def clear_analysis(self) -> None:
        self.maximum_stress_var.set("최대 응력: -")
        self.axes.clear()
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Stress (MPa)")
        self.axes.grid(True)
        self.figure.tight_layout()
        self.canvas.draw()

    def analyze(self) -> None:
        if not self.times:
            messagebox.showinfo(
                "분석할 데이터 없음",
                "먼저 유효한 데이터가 있는 CSV 파일을 선택하세요.",
                parent=self.root,
            )
            return

        try:
            area = self.get_section_area()
        except (KeyError, ValueError) as error:
            messagebox.showerror(
                "잘못된 단면 치수",
                str(error),
                parent=self.root,
            )
            return

        try:
            stresses, maximum_index = calculate_stresses(self.forces, area)
        except ValueError as error:
            messagebox.showerror(
                "응력 계산 오류",
                str(error),
                parent=self.root,
            )
            return

        maximum_stress = stresses[maximum_index]
        maximum_time = self.times[maximum_index]
        self.maximum_stress_var.set(
            f"최대 응력: {maximum_stress:g} MPa  |  "
            f"해당 시간: {maximum_time:g} s"
        )

        self.axes.clear()
        self.axes.plot(self.times, stresses, marker="o")
        self.axes.scatter(
            maximum_time, maximum_stress, color="red", zorder=3
        )
        self.axes.set_xlabel("Time (s)")
        self.axes.set_ylabel("Stress (MPa)")
        self.axes.grid(True)
        self.figure.tight_layout()
        self.canvas.draw()


def main() -> None:
    root = tk.Tk()
    LoadAnalyzerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
