# 🎵 Cảm âm sáo Đô — Web đọc bản nhạc

Web nhỏ đọc **file nhạc số (MusicXML/MIDI)** hoặc **ảnh bản nhạc scan/chụp**
và xuất **bảng cảm âm sáo Đô** (Đô Rê Mi…) kèm **ngón bấm** cho sáo trúc Đô 6 lỗ.

Dự án luyện tập — xem lộ trình chi tiết trong [PROGRESS.md](PROGRESS.md).

## Đã làm được

**Tuần 1–2 · Core logic**
- Upload file `.musicxml` / `.xml` / `.mxl` / `.mid` / `.midi`
- Parse bằng `music21` → danh sách (tên nốt, quãng tám, trường độ)
- Tra bảng cảm âm sáo Đô: tên cảm âm + ngón bấm (`●` bịt, `○` mở, `◐` nửa lỗ)
- Đánh dấu nốt thăng/giáng, dấu lặng, nốt **ngoài tầm sáo**

**Tuần 3–4 · OMR (đọc ảnh scan)** *(thử nghiệm)*
- Upload ảnh `.png` / `.jpg` → chạy `oemer` (OMR pretrained) → MusicXML → cùng pipeline cảm âm
- Lỗi được báo rõ ràng, không làm sập server (ảnh mờ, không phải khuông nhạc, chưa cài oemer…)

**Giao diện**
- Kéo thả file/ảnh, bảng cảm âm, thống kê, tải về `.txt`
- Dark mode + nút đổi theme, hero đĩa gỗ + waveform, "album art" cho bài đang đọc
- `demo.html`: bản demo tĩnh chạy không cần server (dữ liệu mẫu nhúng sẵn)

## Cách chạy

```bash
# 1. Tạo môi trường ảo + cài thư viện (chỉ làm 1 lần)
python -m venv .venv
.venv\Scripts\pip install -r requirements.txt

# 2. (Tuỳ chọn) Bật đọc ảnh scan — nặng, lần đầu tự tải model
.venv\Scripts\pip install -r requirements-omr.txt

# 3. Chạy server
.venv\Scripts\python -m uvicorn main:app --reload

# 4. Mở trình duyệt → http://localhost:8000
```

Không cài phần OMR thì web vẫn chạy bình thường với file MusicXML/MIDI;
khu đọc ảnh sẽ báo "đang chuẩn bị" và hướng dẫn cách bật.

## Bản demo trực tuyến

Mỗi lần push lên `main`, GitHub Actions tự deploy thư mục `static/` lên
**GitHub Pages**. Bản demo (`demo.html`) chạy được ngay trên Pages vì đã
nhúng sẵn dữ liệu mẫu; bản upload đầy đủ cần chạy server ở máy.

## Tạo file nhạc mẫu để test

```bash
.venv\Scripts\python scripts\tao_file_mau.py
# → sinh file .musicxml + .mid trong thư mục samples/
```

## Cấu trúc thư mục

```
main.py                  # FastAPI: /api/parse, /api/parse-image, /api/omr-status
mapping/sao_do.py        # Bảng cảm âm + ngón bấm sáo Đô 6 lỗ
omr/reader.py            # Wrapper OMR: ảnh → MusicXML (oemer)
static/                  # Giao diện (HTML/CSS/JS thuần) + demo.html
scripts/tao_file_mau.py  # Sinh file nhạc mẫu
samples/                 # File nhạc mẫu để test
.github/workflows/       # Auto-deploy GitHub Pages
```

## API

| Endpoint | Mô tả |
|----------|-------|
| `GET /api/omr-status` | OMR có sẵn sàng không (`{"omr_san_sang": bool}`) |
| `POST /api/parse` | form-data `file` = MusicXML/MIDI → JSON cảm âm |
| `POST /api/parse-image` | form-data `file` = ảnh scan → OMR → JSON cảm âm |

JSON trả về (rút gọn):

```json
{
  "ten_file": "twinkle_c5.musicxml",
  "nguon": "file",
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

- Tuần 5–6: tự nhận tone + transpose về tầm sáo Đô
- Tuần 7–8: thử train một classifier ký hiệu nhạc nhỏ + hoàn thiện
