# -*- coding: utf-8 -*-
"""
Tải model còn thiếu của oemer (bắt buộc trước khi dùng tính năng đọc ảnh).

Vì sao cần script này?
    oemer chỉ kiểm tra `checkpoints/unet_big/model.onnx` để quyết định có tải
    model hay không. File đó có sẵn trong package, nên oemer TƯỞNG đã đủ model
    và bỏ qua bước tải — trong khi `checkpoints/seg_net/model.onnx` lại KHÔNG
    được ship. Chạy OMR sẽ crash: "NO_SUCHFILE ... seg_net/model.onnx".

Chạy:  .venv\\Scripts\\python.exe scripts\\tai_model_omr.py
"""

import urllib.request
from pathlib import Path

import oemer

# Model thiếu: seg_net (dùng để tách ký hiệu nhạc khỏi nền)
URL = "https://github.com/BreezeWhite/oemer/releases/download/checkpoints/2nd_model.onnx"
KICH_THUOC_MONG_DOI = 38_448_467  # bytes

thu_muc = Path(oemer.__file__).parent / "checkpoints" / "seg_net"
dich = thu_muc / "model.onnx"


def tai():
    if dich.exists() and dich.stat().st_size == KICH_THUOC_MONG_DOI:
        print(f"Model đã có sẵn: {dich}")
        return

    thu_muc.mkdir(parents=True, exist_ok=True)
    print(f"Đang tải model OMR (~37 MB) từ GitHub release của oemer…")
    print(f"  {URL}")

    with urllib.request.urlopen(URL) as resp:
        tong = int(resp.getheader("Content-Length", KICH_THUOC_MONG_DOI))
        da_tai = 0
        with open(dich, "wb") as f:
            while True:
                khoi = resp.read(1 << 16)
                if not khoi:
                    break
                da_tai += f.write(khoi)
                print(f"\r  {da_tai * 100 / tong:.0f}%  ({da_tai:,}/{tong:,} bytes)", end="")
    print()

    if dich.stat().st_size != KICH_THUOC_MONG_DOI:
        raise SystemExit(f"Tải lỗi: file chỉ có {dich.stat().st_size} bytes. Xoá và thử lại.")

    print(f"Xong! Model lưu tại: {dich}")
    print("Giờ có thể upload ảnh bản nhạc lên web để đọc cảm âm.")


if __name__ == "__main__":
    tai()
