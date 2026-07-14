# -*- coding: utf-8 -*-
"""
Tạo file nhạc mẫu (MusicXML + MIDI) để test endpoint /api/parse.

Chạy:  .venv\\Scripts\\python.exe scripts\\tao_file_mau.py
Kết quả nằm trong thư mục samples/
"""

from pathlib import Path

from music21 import stream, note, meter, tempo

THU_MUC = Path(__file__).resolve().parent.parent / "samples"
THU_MUC.mkdir(exist_ok=True)


def tao_bai(ten_file: str, tieu_de: str, cac_not: list[tuple[str, float]]):
    """Tạo 1 bài từ danh sách (tên nốt, trường độ). 'nghi' = dấu lặng."""
    bai = stream.Stream()
    bai.append(tempo.MetronomeMark(number=90))
    bai.append(meter.TimeSignature("4/4"))
    for ten, truong_do in cac_not:
        if ten == "nghi":
            n = note.Rest(quarterLength=truong_do)
        else:
            n = note.Note(ten, quarterLength=truong_do)
        bai.append(n)

    bai.write("musicxml", fp=THU_MUC / f"{ten_file}.musicxml")
    bai.write("midi", fp=THU_MUC / f"{ten_file}.mid")
    print(f"Đã tạo: samples/{ten_file}.musicxml + .mid ({tieu_de})")


# Bài 1: "Twinkle Twinkle" viết ở quãng sáo Đô (C5) — nằm gọn trong tầm sáo
tao_bai(
    "twinkle_c5",
    "Twinkle Twinkle (C5, vừa tầm sáo)",
    [
        ("C5", 1), ("C5", 1), ("G5", 1), ("G5", 1),
        ("A5", 1), ("A5", 1), ("G5", 2),
        ("F5", 1), ("F5", 1), ("E5", 1), ("E5", 1),
        ("D5", 1), ("D5", 1), ("C5", 2),
    ],
)

# Bài 2: giai điệu ở C4 — THẤP hơn tầm sáo Đô, để test cảnh báo ngoài tầm
tao_bai(
    "giai_dieu_c4_ngoai_tam",
    "Giai điệu C4 (thấp hơn tầm sáo — test cảnh báo)",
    [
        ("C4", 1), ("D4", 1), ("E4", 1), ("F4", 1),
        ("G4", 2), ("nghi", 1), ("G4", 1),
        ("A4", 1), ("F4", 1), ("C5", 2),
    ],
)

# Bài 3: có nốt thăng + dấu lặng + quãng 2 — test đủ loại ký hiệu
tao_bai(
    "test_thang_va_quang2",
    "Test nốt thăng, dấu lặng, quãng 2",
    [
        ("C5", 1), ("F#5", 0.5), ("G5", 0.5), ("nghi", 1),
        ("C6", 1), ("D6", 1), ("E6", 2),
        ("A#5", 1), ("G5", 1), ("C5", 2),
    ],
)

print("Xong! Mở web và thử upload các file trong samples/")
