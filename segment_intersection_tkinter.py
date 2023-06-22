from dataclasses import dataclass
import random
import tkinter as tk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

window = tk.Tk()
fig = Figure()
canvas = FigureCanvasTkAgg(fig, master=window)
canvas.get_tk_widget().grid(row=0, column=0, columnspan=8, sticky=tk.NSEW)
canvas.draw()


@dataclass
class Point:
    x: float
    y: float


@dataclass
class Segment:
    start: Point
    end: Point


test_cases = {
    'overlapping': (Segment(Point(2, 2), Point(5, 5)), Segment(Point(3.5, 3.5), Point(8, 8))),
    'no_intersection': (Segment(Point(2, 2), Point(5, 5)), Segment(Point(2, 4), Point(4, 6))),
    'intersection': (Segment(Point(2, 2), Point(5, 5)), Segment(Point(1, 5), Point(5, 1))),
    'point_start': (Segment(Point(2, 2), Point(5, 5)), Segment(Point(3, 3), Point(4, 6))),
}


def process_intersection(seg_1, seg_2, ax):
    plot_segments(seg_1, seg_2, ax)
    title, intersection_point, overlapping_segment = run_calculations(seg_1, seg_2)
    plot_intersection(overlapping_segment, intersection_point, ax)
    ax.legend(prop={'size': 10})
    ax.title.set_text(title)
    canvas.draw()


def plot_segments(seg_1, seg_2, ax):
    x1, y1 = ((seg_1.start.x, seg_1.end.x), (seg_1.start.y, seg_1.end.y))
    x2, y2 = ((seg_2.start.x, seg_2.end.x), (seg_2.start.y, seg_2.end.y))

    ax.plot(x1, y1, label=f"Odcinek 1 {x1[0], y1[0]} , {x1[1], y1[1]}", color='red', linestyle='--')

    ax.plot(x2, y2, label=f"Odcinek 2 {x2[0], y2[0]} , {x2[1], y2[1]}", color='blue', linestyle=':')

    # pokaż współrzędne punktów na wykresie używając x1, y1, x2, y2
    ax.text(seg_1.start.x, seg_1.start.y, f"{seg_1.start.x}, {seg_1.start.y}")
    ax.text(seg_1.end.x, seg_1.end.y, f"{seg_1.end.x}, {seg_1.end.y}")
    ax.text(seg_2.start.x, seg_2.start.y, f"{seg_2.start.x}, {seg_2.start.y}", linespacing=1.5)
    ax.text(seg_2.end.x, seg_2.end.y, f"{seg_2.end.x}, {seg_2.end.y}", linespacing=1.5)


def plot_intersection(overlapping_segment, intersection_point, ax):
    if overlapping_segment:
        x3, y3 = ((overlapping_segment.start.x, overlapping_segment.end.x),
                  (overlapping_segment.start.y, overlapping_segment.end.y))
        ax.plot(x3, y3, label='Wspólna część odcinków', color='orange', linewidth=6, alpha=0.5)
    if intersection_point:
        ax.plot(intersection_point.x, intersection_point.y,
                label=f"Punkt przecięcia {round(intersection_point.x, 2), round(intersection_point.y, 2)}", color='k',
                marker='o')
        ax.text(intersection_point.x, intersection_point.y,
                f"{round(intersection_point.x, 2)}, {round(intersection_point.y, 2)}",
                ha='left', va='bottom')


def check_intersection(seg_1, seg_2):
    # Konstruujemy składowe wektorów z odcinków 1 i 2
    vec_x1 = seg_1.end.x - seg_1.start.x
    vec_y1 = seg_1.end.y - seg_1.start.y
    vec_x2 = seg_2.end.x - seg_2.start.x
    vec_y2 = seg_2.end.y - seg_2.start.y

    # wektor 3 od początku odcinka 2 do początku odcinka 1
    vec_x3 = seg_1.start.x - seg_2.start.x
    vec_y3 = seg_1.start.y - seg_2.start.y

    # liczymy iloczyn wektorowy wektorów 1 i 2  który pozwoli sprawdzić czy odcinki są równoległe
    det = vec_x1 * vec_y2 - vec_y1 * vec_x2

    # liczymy iloczyn wektorowy odcinka 1 i wektora 3 oraz odcinka 2 i wektora 3
    det1 = vec_x1 * vec_y3 - vec_y1 * vec_x3
    det2 = vec_x2 * vec_y3 - vec_y2 * vec_x3

    # jeżeli iloczyn wektorowy wektorów 1 i 2 jest równy 0 to odcinki są równoległe
    if det == 0:
        # jeżeli iloczy wektorowy wektora 1 i wektora 3 jest równy 0 oraz iloczyn wektorowy wektora 2 i wektora 3
        # jest równy 0 to znaczy że wektor 3 jest równoległy do obu odcinków i odcinki są współliniowe
        if det1 == 0 and det2 == 0:
            overlapping_segment = find_overlapping_segment(seg_1, seg_2)
            return overlapping_segment
        # jeżeli wektor 3 nie jest równoległy do obu odcinków to odcinki są równoległe ale nie współliniowe
        else:
            return None

    # jeżeli iloczyn wektorowy wektorów 1 i 2 nie jest równy 0 to odcinki nie są równoległe
    # używając równania prostych liczymy parametr prostej dla odcinka 1 i 2
    # jeżeli proste się przecinają to ich równania są równe
    # używając metody Kramera budujemy układ równań i liczymy parametry dla których te dwie proste się przecinają

    # wzór parametr prostej zawierającej odcinek 1
    t1 = det1 / det
    # parametr prostej zawierającej odcinek 2
    t2 = det2 / det

    # liczymy współrzędne punktu przecięcia leżącego na prostej
    intersection_x = seg_1.start.x + t2 * vec_x1
    intersection_y = seg_1.start.y + t2 * vec_y1

    # sprawdzamy czy punkt przecięcia należy do obu odcinków

    # Jeśli t2 = 0, punkt przecięcia pokrywa się z początkowym punktem drugiego odcinka.
    # Jeśli t2 = 1, punkt przecięcia pokrywa się z końcowym punktem drugiego odcinka.
    # Jeśli t2 jest pomiędzy 0 i 1, punkt przecięcia leży wewnątrz drugiego odcinka.

    # Jeśli t1 = 0, punkt przecięcia pokrywa się z początkowym punktem pierwszego odcinka.
    # Jeśli t1 = 1, punkt przecięcia pokrywa się z końcowym punktem pierwszego odcinka.
    # Jeśli t1 jest pomiędzy 0 i 1, punkt przecięcia leży wewnątrz pierwszego odcinka.

    if 0 <= t1 <= 1 and 0 <= t2 <= 1:
        return Point(intersection_x, intersection_y)

    # jeżeli punkt przecięcia nie należy do odcinków to znaczy że odcinki nie są równoległe ale nie przecinają się
    return None


def find_overlapping_segment(seg_1, seg_2):
    # analizując współrzędne początku i końca odcinków znajdujemy współrzędne początku i końca odcinka wspólnego
    x_start = max(min(seg_1.start.x, seg_1.end.x), min(seg_2.start.x, seg_2.end.x))
    y_start = max(min(seg_1.start.y, seg_1.end.y), min(seg_2.start.y, seg_2.end.y))

    x_end = min(max(seg_1.start.x, seg_1.end.x), max(seg_2.start.x, seg_2.end.x))
    y_end = min(max(seg_1.start.y, seg_1.end.y), max(seg_2.start.y, seg_2.end.y))

    return Segment(Point(x_start, y_start), Point(x_end, y_end))


def generate_random_segments_pair():
    # wygeneruj 2 odcinki o losowych współrzędnych w zakresie -20, 20
    seg_1 = Segment(Point(round(random.uniform(-20, 20, ), 2), round(random.uniform(-20, 20), 2)),
                    Point(round(random.uniform(-20, 20), 2), round(random.uniform(-20, 20), 2)))
    seg_2 = Segment(Point(round(random.uniform(-20, 20), 2), round(random.uniform(-20, 20), 2)),
                    Point(round(random.uniform(-20, 20), 2), round(random.uniform(-20, 20), 2)))
    return seg_1, seg_2


def run_calculations(seg_1, seg_2):
    intersection_result = check_intersection(seg_1, seg_2)
    intersection_point = None
    overlapping_segments = None
    if intersection_result is None:
        print("Odcinki nie przecinają się")
        title = "Odcinki nie przecinają się"
    elif type(intersection_result) is Point:
        print(f"Znaleziono punkt przecięcia: ({intersection_result.x}, {intersection_result.y})")
        title = "Znaleziono punkt przecięcia"
        intersection_point = intersection_result
    else:
        print(
            f"Część wspólna odcinków: ({intersection_result.start.x}, {intersection_result.start.y}), ({intersection_result.end.x}, {intersection_result.end.y})")
        title = "Odcinki mają część wspólną"
        overlapping_segments = intersection_result

    return title, intersection_point, overlapping_segments


def single_run(seg_1, seg_2):
    ax = fig.add_subplot(111)
    process_intersection(seg_1, seg_2, ax)
    ax.remove()


def run_random():
    segment_1, segment_2 = generate_random_segments_pair()
    single_run(segment_1, segment_2)


def run_tests(test_case):
    segment_1, segment_2 = test_cases[test_case]
    single_run(segment_1, segment_2)


def run_manual():
    x1 = entry_x1.get()
    y1 = entry_y1.get()
    x2 = entry_x2.get()
    y2 = entry_y2.get()
    x3 = entry_x3.get()
    y3 = entry_y3.get()
    x4 = entry_x4.get()
    y4 = entry_y4.get()

    # Sprawdź czy wszystkie pola są wypełnione
    if x1 and y1 and x2 and y2 and x3 and y3 and x4 and y4:
        # Sprawdz czy wszystkie współrzędne są liczbami
        try:
            x1 = float(x1)
            y1 = float(y1)
            x2 = float(x2)
            y2 = float(y2)
            x3 = float(x3)
            y3 = float(y3)
            x4 = float(x4)
            y4 = float(y4)
        except ValueError:
            hint_label.config(text="Wszystkie współrzędne muszą być liczbami zmiennorzecinkowymi")
        else:
            segment_1 = Segment(Point(x1, y1), Point(x2, y2))
            segment_2 = Segment(Point(x3, y3), Point(x4, y4))
            single_run(segment_1, segment_2)
    else:
        hint_label.config(text="Uzupełnij wszystkie współrzędne")


close_button = tk.Button(master=window, text="Zakończ", command=window.destroy)
random_button = tk.Button(master=window, text="Generuj losowo", command=lambda: run_random())
example_intersection_button = tk.Button(master=window, text="Przecięcie", command=lambda: run_tests('intersection'))
example_no_intersection_button = tk.Button(master=window, text="Brak przecięcia",
                                           command=lambda: run_tests('no_intersection'))
example_no_overlapping_button = tk.Button(master=window, text="Część wspólna",
                                          command=lambda: run_tests('overlapping'))
example_point_start_button = tk.Button(master=window, text="Początek w drugim odcinku",
                                       command=lambda: run_tests('point_start'))
chosen_coords_button = tk.Button(master=window, text="Oblicz dla podanych współrzędnych", command=lambda: run_manual())

hint_label = tk.Label(master=window, text="", font=("Arial", 22))
test_cases_label = tk.Label(master=window, text="Przykłady testowe", font=("Arial", 16))

label_x1 = tk.Label(master=window, text="x1")
label_y1 = tk.Label(master=window, text="y1")
label_x2 = tk.Label(master=window, text="x2")
label_y2 = tk.Label(master=window, text="y2")
label_x3 = tk.Label(master=window, text="x3")
label_y3 = tk.Label(master=window, text="y3")
label_x4 = tk.Label(master=window, text="x4")
label_y4 = tk.Label(master=window, text="y4")

entry_x1 = tk.Entry(master=window)
entry_y1 = tk.Entry(master=window)
entry_x2 = tk.Entry(master=window)
entry_y2 = tk.Entry(master=window)
entry_x3 = tk.Entry(master=window)
entry_y3 = tk.Entry(master=window)
entry_x4 = tk.Entry(master=window)
entry_y4 = tk.Entry(master=window)

hint_label.grid(row=1, column=0, columnspan=8, padx=10, pady=10, sticky=tk.NSEW)

label_x1.grid(row=2, column=0, padx=4, pady=2)
entry_x1.grid(row=2, column=1, padx=1, pady=2)
label_y1.grid(row=2, column=2, padx=1, pady=2)
entry_y1.grid(row=2, column=3, padx=1, pady=2)
label_x2.grid(row=2, column=4, padx=1, pady=2)
entry_x2.grid(row=2, column=5, padx=1, pady=2)
label_y2.grid(row=2, column=6, padx=1, pady=2)
entry_y2.grid(row=2, column=7, padx=4, pady=2)
label_x3.grid(row=3, column=0, padx=4, pady=2)
entry_x3.grid(row=3, column=1, padx=1, pady=2)
label_y3.grid(row=3, column=2, padx=1, pady=2)
entry_y3.grid(row=3, column=3, padx=1, pady=2)
label_x4.grid(row=3, column=4, padx=1, pady=2)
entry_x4.grid(row=3, column=5, padx=1, pady=2)
label_y4.grid(row=3, column=6, padx=1, pady=2)
entry_y4.grid(row=3, column=7, padx=4, pady=2)

chosen_coords_button.grid(row=4, column=0, columnspan=4, padx=10, pady=5)
random_button.grid(row=4, column=4, columnspan=4, padx=10, pady=5)
test_cases_label.grid(row=5, column=0, columnspan=8, padx=10, pady=5)
example_intersection_button.grid(row=6, column=0, columnspan=2, padx=15, pady=5)
example_no_intersection_button.grid(row=6, column=2, columnspan=2, padx=10, pady=5)
example_no_overlapping_button.grid(row=6, column=4, columnspan=2, padx=10, pady=5)
example_point_start_button.grid(row=6, column=6, columnspan=2, padx=15, pady=5)
close_button.grid(row=7, column=0, columnspan=8, padx=10, pady=5)

window.grid_rowconfigure(0, weight=2)
window.grid_rowconfigure(1, weight=1)
window.grid_rowconfigure(2, weight=1)
window.grid_rowconfigure(3, weight=1)
window.grid_rowconfigure(4, weight=1)
window.grid_rowconfigure(5, weight=1)
window.grid_rowconfigure(6, weight=1)
window.grid_rowconfigure(7, weight=1)

window.grid_columnconfigure(0, weight=2)
window.grid_columnconfigure(1, weight=1)
window.grid_columnconfigure(2, weight=1)
window.grid_columnconfigure(3, weight=1)
window.grid_columnconfigure(4, weight=1)
window.grid_columnconfigure(5, weight=1)
window.grid_columnconfigure(6, weight=1)
window.grid_columnconfigure(7, weight=1)

window.mainloop()
