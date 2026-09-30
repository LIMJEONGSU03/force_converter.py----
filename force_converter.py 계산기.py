# force_converter.py

import tkinter as tk


UNIT_TO_NEWTON = {
    "N": 1,
    "kN": 1000,
    "kgf": 9.80665,
}


def convert_force():
    try:
        value = float(force_entry.get())
        if value <= 0:
            raise ValueError
    except ValueError:
        result_label.config(
            text="잘못된 입력입니다. 양의 숫자를 입력하세요.", fg="red"
        )
        force_entry.focus_set()
        return

    input_unit = unit_var.get()
    newton = value * UNIT_TO_NEWTON[input_unit]
    kn = newton / UNIT_TO_NEWTON["kN"]
    kgf = newton / UNIT_TO_NEWTON["kgf"]
    result_label.config(
        text=(
            f"입력 값: {value:.2f} {input_unit}\n"
            f"결과: {newton:.2f} N\n"
            f"결과: {kn:.2f} kN\n"
            f"결과: {kgf:.2f} kgf"
        ),
        fg="black",
    )


def clear_input():
    force_entry.delete(0, tk.END)
    result_label.config(text="결과가 여기에 표시됩니다.", fg="black")
    force_entry.focus_set()


def toggle_fullscreen(event=None):
    is_fullscreen = not root.attributes("-fullscreen")
    root.attributes("-fullscreen", is_fullscreen)
    fullscreen_button.config(text="창 모드" if is_fullscreen else "전체 화면")
    if event:
        return "break"


def exit_fullscreen(event=None):
    root.attributes("-fullscreen", False)
    fullscreen_button.config(text="전체 화면")
    return "break"


root = tk.Tk()
root.title("힘 단위 변환기")
root.resizable(False, False)

main_frame = tk.Frame(root, padx=24, pady=24)
main_frame.pack()

window_controls = tk.Frame(main_frame)
window_controls.pack(fill=tk.X, pady=(0, 8))

fullscreen_button = tk.Button(
    window_controls, text="전체 화면", command=toggle_fullscreen
)
fullscreen_button.pack(side=tk.LEFT)
tk.Button(window_controls, text="최소화", command=root.iconify).pack(side=tk.RIGHT)

tk.Label(main_frame, text="힘 단위 변환기", font=("맑은 고딕", 16, "bold")).pack(
    pady=(0, 16)
)

input_frame = tk.Frame(main_frame)
input_frame.pack()

tk.Label(input_frame, text="힘 입력:").pack(side=tk.LEFT, padx=(0, 8))
force_entry = tk.Entry(input_frame, width=16, justify="right")
force_entry.pack(side=tk.LEFT)
force_entry.bind("<Return>", lambda event: convert_force())

unit_var = tk.StringVar(value="kN")
unit_menu = tk.OptionMenu(input_frame, unit_var, *UNIT_TO_NEWTON)
unit_menu.config(width=5)
unit_menu.pack(side=tk.LEFT, padx=(8, 0))

button_frame = tk.Frame(main_frame)
button_frame.pack(pady=16)

tk.Button(button_frame, text="변환", width=10, command=convert_force).pack(
    side=tk.LEFT, padx=4
)
tk.Button(button_frame, text="지우기", width=10, command=clear_input).pack(
    side=tk.LEFT, padx=4
)

result_label = tk.Label(main_frame, text="결과가 여기에 표시됩니다.", justify=tk.LEFT)
result_label.pack(anchor="w")

root.bind("<F11>", toggle_fullscreen)
root.bind("<Escape>", exit_fullscreen)

force_entry.focus_set()
root.mainloop()