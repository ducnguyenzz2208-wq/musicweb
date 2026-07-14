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


def anh_sang_musicxml(duong_dan_anh: str, thu_muc_ra: str, timeout: int = 240) -> str:
    """Chạy oemer trên 1 ảnh -> trả về đường dẫn file .musicxml sinh ra.

    Tham số:
        duong_dan_anh: ảnh đầu vào (đã lưu ra đĩa)
        thu_muc_ra:    thư mục để oemer ghi kết quả
        timeout:       giây tối đa chờ oemer (mặc định 240s vì lần đầu tải model)

    Ném LoiOMR nếu: chưa cài oemer, oemer chạy lỗi, hoặc không sinh ra file.
    """
    oemer = tim_oemer()
    if not oemer:
        raise LoiOMR(
            "Tính năng đọc ảnh (OMR) chưa sẵn sàng trên máy chủ. "
            "Cần cài thư viện: pip install oemer. "
            "Trong lúc chờ, bạn có thể dùng file MusicXML/MIDI."
        )

    anh = Path(duong_dan_anh)
    ra = Path(thu_muc_ra)
    ra.mkdir(parents=True, exist_ok=True)

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
        # Lấy vài dòng cuối stderr để gợi ý, nhưng không đổ nguyên trace cho user
        loi_tom_tat = (proc.stderr or proc.stdout or "").strip().splitlines()
        goi_y = loi_tom_tat[-1] if loi_tom_tat else "không rõ nguyên nhân"
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
