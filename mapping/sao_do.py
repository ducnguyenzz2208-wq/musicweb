# -*- coding: utf-8 -*-
"""
Bảng cảm âm sáo Đô (6 lỗ bấm).

Quy ước trong file này:
- Sáo Đô: nốt thấp nhất là Đô (C5 theo ký hiệu quốc tế, tức nốt Đô
  cao hơn Đô giữa đàn piano 1 quãng tám).
- Ngón bấm viết thành chuỗi 6 ký tự, đọc TỪ LỖ GẦN LỖ THỔI NHẤT
  đến lỗ xa nhất:  ● = bịt lỗ, ○ = mở lỗ, ◐ = bịt nửa lỗ (nốt thăng/giáng).
- Quãng 1 (Đô -> Si): thổi hơi bình thường.
- Quãng 2 (Đô2 -> Si2): ngón bấm gần như giống quãng 1 nhưng THỔI MẠNH HƠN
  (riêng Đô2 mở lỗ 1 để dễ lấy hơi).
"""

# Tên cảm âm tiếng Việt theo pitch class (0 = C, 1 = C#, ... 11 = B)
TEN_CAM_AM = {
    0: "Đô",
    1: "Đô#",
    2: "Rê",
    3: "Rê#",
    4: "Mi",
    5: "Fa",
    6: "Fa#",
    7: "Sol",
    8: "Sol#",
    9: "La",
    10: "La#",
    11: "Si",
}

# Ngón bấm quãng 1 (C5 - B5) theo pitch class.
# Nốt thăng dùng nửa lỗ (◐) - đây là cách bấm gần đúng, đủ dùng cho người mới.
NGON_BAM_QUANG_1 = {
    0: "●●●●●●",   # Đô
    1: "●●●●●◐",   # Đô#
    2: "●●●●●○",   # Rê
    3: "●●●●◐○",   # Rê#
    4: "●●●●○○",   # Mi
    5: "●●●○○○",   # Fa
    6: "●●◐○○○",   # Fa#
    7: "●●○○○○",   # Sol
    8: "●◐○○○○",   # Sol#
    9: "●○○○○○",   # La
    10: "◐○○○○○",  # La#
    11: "○○○○○○",  # Si
}

# Tầm âm sáo Đô 6 lỗ (tính theo số MIDI):
# C5 = 72 (thấp nhất) ... khoảng B6 = 95 là giới hạn chơi thoải mái.
MIDI_THAP_NHAT = 72   # C5 - Đô quãng 1
MIDI_CAO_NHAT = 95    # B6 - Si quãng 2

# Tên trường độ tiếng Việt theo quarterLength của music21
TEN_TRUONG_DO = {
    4.0: "Nốt tròn",
    3.0: "Trắng chấm dôi",
    2.0: "Nốt trắng",
    1.5: "Đen chấm dôi",
    1.0: "Nốt đen",
    0.75: "Móc đơn chấm dôi",
    0.5: "Móc đơn",
    0.25: "Móc kép",
    0.125: "Móc ba",
}


def ten_truong_do(quarter_length: float) -> str:
    """Đổi quarterLength (music21) sang tên trường độ tiếng Việt.

    Nếu không khớp giá trị chuẩn nào (ví dụ liên ba) thì trả về dạng số
    để người dùng vẫn đọc được.
    """
    ql = float(quarter_length)
    if ql in TEN_TRUONG_DO:
        return TEN_TRUONG_DO[ql]
    return f"{ql:g} phách"


def tra_cam_am(midi: int) -> dict:
    """Tra cảm âm + ngón bấm sáo Đô cho 1 nốt (theo số MIDI).

    Trả về dict:
    - cam_am: tên cảm âm, thêm số quãng nếu cao (vd "Đô2", "Sol2")
    - ngon_bam: chuỗi 6 ký tự ●○◐, hoặc "—" nếu ngoài tầm
    - ghi_chu: hướng dẫn thổi ("thổi mạnh" cho quãng 2...)
    - ngoai_tam: True nếu nốt nằm ngoài tầm sáo Đô
    - la_thang: True nếu là nốt thăng/giáng (bấm nửa lỗ, khó hơn)
    """
    pitch_class = midi % 12
    ten = TEN_CAM_AM[pitch_class]
    la_thang = pitch_class in (1, 3, 6, 8, 10)

    # Ngoài tầm sáo: vẫn trả tên cảm âm để người dùng biết nốt gì,
    # nhưng đánh dấu ngoai_tam để giao diện cảnh báo.
    if midi < MIDI_THAP_NHAT:
        return {
            "cam_am": ten,
            "ngon_bam": "—",
            "ghi_chu": "Thấp hơn tầm sáo Đô (cần transpose lên — làm ở Tuần 5-6)",
            "ngoai_tam": True,
            "la_thang": la_thang,
        }
    if midi > MIDI_CAO_NHAT:
        return {
            "cam_am": ten,
            "ngon_bam": "—",
            "ghi_chu": "Cao hơn tầm sáo Đô (cần transpose xuống — làm ở Tuần 5-6)",
            "ngoai_tam": True,
            "la_thang": la_thang,
        }

    # Quãng 1: C5(72) -> B5(83)
    if midi <= 83:
        return {
            "cam_am": ten,
            "ngon_bam": NGON_BAM_QUANG_1[pitch_class],
            "ghi_chu": "Bấm nửa lỗ (◐)" if la_thang else "",
            "ngoai_tam": False,
            "la_thang": la_thang,
        }

    # Quãng 2: C6(84) -> B6(95) — ngón giống quãng 1, thổi mạnh hơn.
    # Riêng Đô2 mở lỗ gần lỗ thổi để dễ lấy hơi (cách bấm phổ biến).
    if pitch_class == 0:
        ngon = "○●●●●●"
    else:
        ngon = NGON_BAM_QUANG_1[pitch_class]
    ghi_chu = "Thổi mạnh hơn (quãng 2)"
    if la_thang:
        ghi_chu += ", bấm nửa lỗ (◐)"
    return {
        "cam_am": ten + "2",
        "ngon_bam": ngon,
        "ghi_chu": ghi_chu,
        "ngoai_tam": False,
        "la_thang": la_thang,
    }
