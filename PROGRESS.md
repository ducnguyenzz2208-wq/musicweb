# PROGRESS.md — Dự án: Web đọc bản nhạc → Cảm âm sáo

## Bối cảnh dự án
- Sinh viên ngành Industrial Engineering (IE), không thiên về code nặng.
- Mục tiêu: dự án luyện tập (1-2 tháng) để làm quen xây web + thử train AI ở mức cơ bản, KHÔNG phải đồ án chính (đồ án chính sẽ là train AI riêng).
- Vì vậy: ưu tiên đơn giản, chạy được, học được kỹ năng — không cần production-grade.

## Mục tiêu chức năng
1. Người dùng upload file nhạc số (MusicXML/MIDI) hoặc ảnh bản nhạc scan.
2. Hệ thống đọc nốt nhạc, tự nhận diện tone (giọng).
3. Transpose về tone phù hợp sáo Đô nếu cần.
4. Xuất bảng cảm âm (Đô Rê Mi Fa Sol La Si...) + ngón bấm tương ứng.
5. Hiển thị kết quả trên web, cho tải về (txt/pdf).

## Phạm vi (Scope) — CHỈ làm trong 1-2 tháng
- ✅ Chỉ hỗ trợ sáo Đô (6 lỗ), không làm đa loại sáo.
- ✅ Dùng model OMR có sẵn (Oemer, pretrained) — KHÔNG tự train OMR từ đầu.
- ✅ Phần "train AI" trong dự án này chỉ ở mức thử nghiệm nhỏ (xem mục "Phần train AI thử nghiệm" bên dưới), không phải mục tiêu chính.
- ❌ Không làm sơ đồ ngón bấm đồ họa phức tạp — dùng text/ký hiệu đơn giản trước.
- ❌ Không tối ưu UI responsive hoàn chỉnh — làm chạy được là đủ.

## Tech stack đã chọn
- Backend: Python + FastAPI
- Xử lý nhạc: thư viện `music21`
- OMR (ảnh → nốt nhạc): `oemer` (pretrained, cài qua pip)
- Frontend: HTML/JS đơn giản (hoặc React nếu người dùng quen hơn) — quyết định ở Giai đoạn 1
- Không dùng database ở bản đầu (xử lý theo request, không lưu lịch sử)

## Roadmap theo tuần

### Tuần 1-2: Core logic (KHÔNG cần OMR, KHÔNG cần train gì)
- [x] Setup FastAPI project, endpoint nhận file MusicXML/MIDI
- [x] Dùng music21 parse file → lấy ra danh sách (tên nốt, octave, trường độ)
- [x] Viết bảng mapping cảm âm sáo Đô (file `mapping/sao_do.py`)
- [x] Endpoint trả JSON: danh sách cảm âm tương ứng từng nốt
- [x] Test bằng vài file MIDI/MusicXML mẫu (tự tạo bằng script `scripts/tao_file_mau.py`)

### Tuần 3-4: Tích hợp OMR (đọc ảnh scan)
- [x] Cài oemer (0.1.8) — thêm vào `requirements-omr.txt` (tách riêng vì nặng)
- [x] Viết wrapper `omr/reader.py`: ảnh upload → oemer (subprocess) → MusicXML → nối pipeline Tuần 1-2
- [x] Endpoint `POST /api/parse-image` + `GET /api/omr-status`; frontend tự định tuyến ảnh
- [x] Xử lý lỗi khi OMR đọc sai/không đọc được (báo tiếng Việt rõ, không crash):
      chưa cài oemer → 503, ảnh sai định dạng → 400, oemer fail/không ra nốt → 422
- [ ] Ghi chú tỷ lệ chính xác thực tế: CẦN ảnh khuông nhạc thật để đo (chưa có mẫu
      trong môi trường dev — thử với ảnh scan thật khi làm báo cáo)

### Tuần 5-6: Transpose + Frontend
- [ ] Auto detect tone bài nhạc (`score.analyze('key')` trong music21)
- [ ] Viết logic transpose về tone Đô nếu bài viết ở tone khác
- [ ] Cảnh báo nếu nốt vượt tầm sáo Đô (quá cao/quá thấp)
- [ ] Làm giao diện: nút upload, hiển thị bảng cảm âm, nút tải kết quả

### Tuần 7-8 (buffer): Phần train AI thử nghiệm + hoàn thiện
- [ ] (Thử nghiệm) Train một mô hình nhỏ, đơn giản — ví dụ: classifier phân loại
      loại ký hiệu nhạc cơ bản (nốt đen/nốt trắng/dấu lặng) trên tập ảnh nhỏ tự thu thập,
      dùng CNN cơ bản (không cần dataset lớn, mục đích là TRẢI NGHIỆM quy trình train,
      không cần độ chính xác cao). Có thể dùng transfer learning từ model có sẵn (nhẹ hơn).
- [ ] Polish UI, viết README hướng dẫn chạy
- [ ] Chuẩn bị demo/báo cáo (nếu cần nộp)

## Trạng thái hiện tại
- Ngày cập nhật: 2026-07-14
- Giai đoạn đang làm: Xong Tuần 1-2 và phần lớn Tuần 3-4 (OMR); tiếp theo là Tuần 5-6 (transpose)
- Việc vừa hoàn thành:
  - Toàn bộ core logic Tuần 1-2 (parse MusicXML/MIDI → JSON cảm âm)
  - Tuần 3-4: tích hợp OMR đọc ảnh (oemer) — wrapper `omr/reader.py`,
    endpoint /api/parse-image + /api/omr-status, xử lý lỗi mượt
  - Auto-deploy GitHub Pages (`.github/workflows/pages.yml`) cho bản demo tĩnh;
    index.html tự hiện banner dẫn sang demo khi không có backend
  - Giao diện web hoàn chỉnh: upload kéo thả (file + ảnh), bảng cảm âm,
    thống kê, tải về .txt — tông kem ấm "music studio", sidebar espresso,
    dark mode + nút đổi theme, hero đĩa gỗ + waveform, "album art" bài đang đọc
  - Thêm `static/demo.html`: bản demo tĩnh chạy không cần server
    (dữ liệu mẫu nhúng sẵn, chọn 3 bài ví dụ) — mở tại /demo.html
  - 3 file nhạc mẫu trong `samples/` (vừa tầm / ngoài tầm / thăng+quãng 2)
  - Đã test: MusicXML, MIDI, file sai định dạng, nốt ngoài tầm, nốt thăng, dấu lặng
- Việc đang mắc kẹt (nếu có): không
- Quyết định đã chốt (để không hỏi lại):
  - Frontend dùng: HTML/CSS/JS thuần (không React) — nằm trong `static/`
  - Bảng cảm âm sáo Đô: đã viết ở `mapping/sao_do.py` (kèm ngón bấm ●○◐,
    quãng 1 + quãng 2, đánh dấu ngoài tầm C5-B6)
  - Chạy web: `.venv\Scripts\python -m uvicorn main:app --reload` → localhost:8000

## Lưu ý khi làm việc với Claude Code
- Đây là dự án LUYỆN TẬP, ưu tiên code đơn giản, dễ hiểu, có comment giải thích —
  không cần kiến trúc phức tạp/enterprise-grade.
- Khi bắt đầu session mới, đọc file này trước, cập nhật mục "Trạng thái hiện tại"
  trước khi kết thúc session.
- Nếu cần quyết định kỹ thuật mới, hỏi trước khi tự ý đổi hướng đã chốt ở trên.
- Ưu tiên chạy được từng bước nhỏ (test ngay sau mỗi tính năng) hơn là code nhiều rồi mới test.
