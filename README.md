# 🎵 Cảm âm sáo Đô — Web đọc bản nhạc

Web nhỏ đọc file nhạc số (MusicXML/MIDI) và xuất **bảng cảm âm sáo Đô**
(Đô Rê Mi…) kèm **ngón bấm** cho sáo trúc Đô 6 lỗ.

Dự án luyện tập — xem lộ trình chi tiết trong [PROGRESS.md](PROGRESS.md).

## Đã làm được (Tuần 1–2)

- Upload file `.musicxml` / `.xml` / `.mxl` / `.mid` / `.midi`
- Parse bằng `music21` → danh sách (tên nốt, quãng tám, trường độ)
- Tra bảng cảm âm sáo Đô: tên cảm âm + ngón bấm (`●` bịt, `○` mở, `◐` nửa lỗ)
- Đánh dấu nốt thăng/giáng, dấu lặng, nốt **ngoài tầm sáo**
- Giao diện web: kéo thả file, bảng kết quả, tải về `.txt`

## Cách chạy

```bash
# 1. Tạo môi trường ảo + cài thư viện (chỉ làm 1 lần)
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. Chạy server
.venv\Scripts\python -m uvicorn main:app --reload

# 3. Mở trình duyệt
# http://localhost:8000
```

## Tạo file nhạc mẫu để test

```bash
.venv\Scripts\python scripts\tao_file_mau.py
# → sinh file .musicxml + .mid trong thư mục samples/
```

## Cấu trúc thư mục

```
main.py                  # FastAPI: POST /api/parse + serve trang web
mapping/sao_do.py        # Bảng cảm âm + ngón bấm sáo Đô 6 lỗ
static/                  # Giao diện (HTML/CSS/JS thuần)
scripts/tao_file_mau.py  # Sinh file nhạc mẫu
samples/                 # File nhạc mẫu để test
```

## API

`POST /api/parse` — form-data với field `file` (MusicXML/MIDI). Trả về:

```json
{
  "ten_file": "twinkle_c5.musicxml",
  "tong_so_not": 14,
  "so_ngoai_tam": 0,
  "so_not_thang": 0,
  "notes": [
    { "stt": 1, "ten_not": "C5", "cam_am": "Đô", "ngon_bam": "●●●●●●",
      "truong_do": "Nốt đen", "ghi_chu": "", "ngoai_tam": false }
  ]
}
```

## Tiếp theo (theo roadmap)

- Tuần 3–4: đọc ảnh bản nhạc scan bằng OMR (`oemer`)
- Tuần 5–6: tự nhận tone + transpose về tầm sáo Đô
- Tuần 7–8: thử train một classifier ký hiệu nhạc nhỏ + hoàn thiện
