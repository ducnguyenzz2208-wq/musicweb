# -*- coding: utf-8 -*-
"""
OMR wrapper — đọc ảnh bản nhạc scan/chụp -> file MusicXML (Tuần 3-4).

Dùng thư viện `oemer` (pretrained, cài qua pip) chạy bằng subprocess.
Thiết kế "mềm": nếu chưa cài oemer thì KHÔNG làm sập server — chỉ báo
cho người dùng biết tính năng OMR chưa sẵn sàng.

oemer chạy khá chậm (10-60s/ảnh) và lần đầu sẽ tự tải model (~vài trăm MB).
"""

import shutil
import subprocess
import sys
from pathlib import Path


class LoiOMR(Exception):
    """Lỗi khi đọc ảnh bằng OMR — kèm thông điệp tiếng Việt thân thiện."""


def tim_oemer() -> str | None:
    """Tìm đường dẫn tới lệnh `oemer` trong venv hoặc PATH.

    Trả về đường dẫn nếu có, None nếu chưa cài.
    """
    # Ưu tiên oemer nằm cùng thư mục Scripts với python đang chạy (venv)
    scripts_dir = Path(sys.executable).parent
    for ten in ("oemer.exe", "oemer"):
        ung_vien = scripts_dir / ten
        if ung_vien.exists():
            return str(ung_vien)
    # Nếu không thấy trong venv thì thử PATH
    return shutil.which("oemer")


def oemer_kha_dung() -> bool:
    """True nếu oemer đã cài và gọi được."""
    return tim_oemer() is not None


# Đuôi ảnh chấp nhận cho OMR
DUOI_ANH_HOP_LE = {".png", ".jpg", ".jpeg", ".bmp", ".tif", ".tiff"}


# Ảnh rộng hơn ngưỡng này sẽ được thu nhỏ trước khi chạy OMR.
# oemer chạy inference theo cửa sổ trượt nên thời gian tăng rất nhanh theo
# kích thước ảnh (ảnh 3600px mất ~11 phút, thu về 1800px chỉ còn ~2-3 phút)
# mà độ chính xác cao độ gần như không đổi.
RONG_TOI_DA = 1800


def _thu_nho_neu_can(duong_dan_anh: str, thu_muc: str) -> str:
    """Thu nhỏ ảnh quá lớn để OMR chạy nhanh hơn. Trả về đường dẫn ảnh dùng thật."""
    try:
        from PIL import Image
    except ImportError:
        return duong_dan_anh  # không có Pillow thì cứ dùng ảnh gốc

    with Image.open(duong_dan_anh) as im:
        if im.width <= RONG_TOI_DA:
            return duong_dan_anh
        ty_le = RONG_TOI_DA / im.width
        moi = im.resize((RONG_TOI_DA, round(im.height * ty_le)), Image.LANCZOS)
        dich = Path(thu_muc) / f"resized_{Path(duong_dan_anh).name}"
        moi.save(dich)
    return str(dich)


def anh_sang_musicxml(duong_dan_anh: str, thu_muc_ra: str, timeout: int = 600) -> str:
    """Chạy oemer trên 1 ảnh -> trả về đường dẫn file .musicxml sinh ra.

    Tham số:
        duong_dan_anh: ảnh đầu vào (đã lưu ra đĩa)
        thu_muc_ra:    thư mục để oemer ghi kết quả
        timeout:       giây tối đa chờ oemer (OMR chạy khá lâu)

    Ném LoiOMR nếu: chưa cài oemer, oemer chạy lỗi, hoặc không sinh ra file.
    """
    oemer = tim_oemer()
    if not oemer:
        raise LoiOMR(
            "Tính năng đọc ảnh (OMR) chưa sẵn sàng trên máy chủ. "
            "Cần cài thư viện: pip install -r requirements-omr.txt "
            "rồi chạy: python scripts/tai_model_omr.py. "
            "Trong lúc chờ, bạn có thể dùng file MusicXML/MIDI."
        )

    ra = Path(thu_muc_ra)
    ra.mkdir(parents=True, exist_ok=True)
    anh = Path(_thu_nho_neu_can(duong_dan_anh, thu_muc_ra))

    # oemer <ảnh> -o <thư mục ra>  → sinh <tên ảnh>.musicxml
    try:
        proc = subprocess.run(
            [oemer, str(anh), "-o", str(ra)],
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise LoiOMR(
            "Đọc ảnh quá lâu (hết thời gian chờ). Ảnh có thể quá lớn hoặc "
            "lần đầu đang tải model — hãy thử lại sau ít phút."
        )
    except Exception as loi:
        raise LoiOMR(f"Không chạy được OMR: {loi}")

    if proc.returncode != 0:
        loi_day_du = (proc.stderr or "") + (proc.stdout or "")

        # Hai lỗi "hạ tầng" hay gặp -> chỉ rõ cách sửa thay vì đổ lỗi cho ảnh
        if "NO_SUCHFILE" in loi_day_du or "model.onnx failed" in loi_day_du:
            raise LoiOMR(
                "Thiếu file model của OMR. Chạy lệnh này rồi thử lại: "
                "python scripts/tai_model_omr.py"
            )
        if "invalid index to scalar variable" in loi_day_du:
            raise LoiOMR(
                "OMR lỗi do OpenCV quá mới (oemer chỉ chạy với OpenCV 4.x). "
                'Sửa bằng: pip install "opencv-python-headless<5"'
            )

        # Còn lại: nhiều khả năng do ảnh
        dong = loi_day_du.strip().splitlines()
        goi_y = dong[-1] if dong else "không rõ nguyên nhân"
        raise LoiOMR(
            f"OMR không đọc được ảnh này ({goi_y}). "
            "Hãy thử ảnh rõ nét hơn, chụp thẳng, đủ sáng và chỉ chứa khuông nhạc."
        )

    # oemer đặt tên theo stem của ảnh
    file_ra = ra / f"{anh.stem}.musicxml"
    if not file_ra.exists():
        # Phòng khi oemer đổi cách đặt tên: quét mọi .musicxml trong thư mục
        ung_vien = list(ra.glob("*.musicxml"))
        if not ung_vien:
            raise LoiOMR(
                "OMR chạy xong nhưng không tạo được bản nhạc từ ảnh. "
                "Ảnh có thể không phải khuông nhạc rõ ràng."
            )
        file_ra = ung_vien[0]

    return str(file_ra)
