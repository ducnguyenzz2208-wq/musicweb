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
- [x] Ghi chú tỷ lệ chính xác thực tế — đo trên bài "Đàn gà con" (xem bên dưới)

#### Kết quả đo OMR thực tế (bài "Đàn gà con", ảnh piano 2 khuông, 3621×2560)
| Hạng mục | Kết quả |
|----------|---------|
| Cao độ (pitch) | **26/26 = 100% đúng** |
| Số nốt | 26/26 đúng |
| Trường độ (duration) | **Sai gần hết** — oemer trả về toàn "nốt tròn" dù bản nhạc là nhịp 2/4 toàn móc đơn/nốt đen |
| Dấu lặng | Có **dấu lặng ma** (oemer chèn thêm chỗ không có) |
| Thời gian chạy | ~250s (sau khi thu nhỏ ảnh về 1800px) |

Kết luận: **oemer đọc cao độ rất tốt, nhưng trường độ không tin được.**
Với mục tiêu "cảm âm sáo" thì cao độ là thứ quan trọng nhất (người thổi tự
biết nhịp theo bài), nên vẫn dùng được. Nếu cần trường độ chính xác thì phải
dùng file MusicXML/MIDI thay vì ảnh.

Ghi chú: 18/26 nốt của bài này nằm DƯỚI tầm sáo Đô (giai điệu ở G4–C5, sáo Đô
bắt đầu từ C5) → cần transpose lên 1 quãng tám. Đúng việc của Tuần 5-6.

#### 3 lỗi hạ tầng đã gặp và cách sửa (ghi lại kẻo quên)
1. **oemer thiếu model**: package chỉ ship `unet_big`, thiếu `seg_net/model.onnx`,
   mà oemer lại chỉ kiểm tra `unet_big` để quyết định có tải hay không → không bao
   giờ tự tải. Sửa: chạy `python scripts/tai_model_omr.py`.
2. **OpenCV 5 làm oemer crash**: OpenCV 5 đổi shape trả về của `cv2.HoughLinesP`
   từ `(N,1,4)` sang `(N,4)` → `IndexError: invalid index to scalar variable`.
   Sửa: ghim `opencv-python-headless<5`.
3. **Bè bass lẫn vào giai điệu**: bản piano có 2 khuông trong 1 part (`<staves>2`).
   `score.flatten()` trộn cả bass vào → cảm âm sai bét (42 nốt lộn xộn).
   Sửa: `chon_be_giai_dieu()` chọn PartStaff có cao độ trung bình cao nhất.

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
