# -*- coding: utf-8 -*-
"""
Web đọc bản nhạc -> Cảm âm sáo Đô — Backend FastAPI.

Chức năng:
- GET  /               : trang web (static/index.html)
- GET  /api/omr-status : cho biết tính năng đọc ảnh (OMR) có sẵn sàng không
- POST /api/parse      : nhận file MusicXML/MIDI, trả JSON cảm âm (Tuần 1-2)
- POST /api/parse-image: nhận ảnh bản nhạc scan -> OMR -> JSON cảm âm (Tuần 3-4)

Chạy server:
    .venv\\Scripts\\python.exe -m uvicorn main:app --reload
"""

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.staticfiles import StaticFiles
from music21 import converter, note as m21_note, chord as m21_chord

from mapping.sao_do import tra_cam_am, ten_truong_do
from omr.reader import (
    LoiOMR,
    DUOI_ANH_HOP_LE,
    anh_sang_musicxml,
    oemer_kha_dung,
)

app = FastAPI(title="Cảm âm sáo Đô", version="0.2.0")

# Các đuôi file nhạc số chấp nhận (MusicXML và MIDI)
DUOI_FILE_HOP_LE = {".xml", ".musicxml", ".mxl", ".mid", ".midi"}


def _cao_do_tb(part) -> float:
    """Cao độ trung bình của 1 bè (dùng để đoán bè nào là giai điệu)."""
    cac_midi = []
    for n in part.flatten().notes:
        if isinstance(n, m21_chord.Chord):
            cac_midi.append(max(p.midi for p in n.pitches))
        else:
            cac_midi.append(n.pitch.midi)
    return sum(cac_midi) / len(cac_midi) if cac_midi else 0.0


def chon_be_giai_dieu(score):
    """Chọn bè để lấy cảm âm.

    Bản nhạc piano có 2 khuông (treble + bass) = 2 bè. Sáo chỉ thổi giai
    điệu, nên phải lấy bè CAO NHẤT — nếu flatten cả bản thì nốt bass sẽ bị
    trộn vào giữa giai điệu và cảm âm ra sai bét.
    """
    parts = list(getattr(score, "parts", []))
    if len(parts) <= 1:
        return score  # chỉ 1 bè (hoặc file MIDI phẳng) -> dùng luôn
    return max(parts, key=_cao_do_tb)


def doc_ban_nhac(duong_dan: str) -> list[dict]:
    """Parse file nhạc bằng music21, trả về danh sách nốt kèm cảm âm.

    Chỉ lấy bè giai điệu (bè cao nhất) — xem chon_be_giai_dieu().
    Trong 1 bè, nếu gặp hợp âm thì lấy nốt cao nhất.
    Dấu lặng (rest) cũng đưa vào để người thổi biết chỗ ngắt hơi.
    """
    score = converter.parse(duong_dan)
    giai_dieu = chon_be_giai_dieu(score)
    ket_qua = []

    for phan_tu in giai_dieu.flatten().notesAndRests:
        if isinstance(phan_tu, m21_note.Note):
            p = phan_tu.pitch
        elif isinstance(phan_tu, m21_chord.Chord):
            p = max(phan_tu.pitches, key=lambda x: x.midi)  # nốt cao nhất
        else:
            # Dấu lặng
            ket_qua.append({
                "stt": len(ket_qua) + 1,
                "ten_not": "Lặng",
                "octave": None,
                "cam_am": "—",
                "ngon_bam": "(nghỉ)",
                "truong_do": ten_truong_do(phan_tu.quarterLength),
                "ghi_chu": "Ngắt hơi",
                "ngoai_tam": False,
                "la_thang": False,
                "la_lang": True,
            })
            continue

        cam_am = tra_cam_am(p.midi)
        ket_qua.append({
            "stt": len(ket_qua) + 1,
            "ten_not": p.nameWithOctave,      # vd: "C5", "F#4"
            "octave": p.octave,
            "cam_am": cam_am["cam_am"],
            "ngon_bam": cam_am["ngon_bam"],
            "truong_do": ten_truong_do(phan_tu.quarterLength),
            "ghi_chu": cam_am["ghi_chu"],
            "ngoai_tam": cam_am["ngoai_tam"],
            "la_thang": cam_am["la_thang"],
            "la_lang": False,
        })

    return ket_qua


def dong_goi_ket_qua(notes: list[dict], ten_file: str, nguon: str = "file") -> dict:
    """Gói danh sách nốt thành JSON trả về cho frontend (dùng chung mọi nguồn)."""
    if not notes:
        raise HTTPException(status_code=422, detail="Không tìm thấy nốt nhạc nào.")
    return {
        "ten_file": ten_file,
        "nguon": nguon,  # "file" hoặc "anh" — frontend hiển thị nhãn khác nhau
        "tong_so_not": len([n for n in notes if not n["la_lang"]]),
        "so_ngoai_tam": sum(1 for n in notes if n["ngoai_tam"]),
        "so_not_thang": sum(1 for n in notes if n["la_thang"]),
        "notes": notes,
    }


@app.get("/api/omr-status")
async def omr_status():
    """Cho frontend biết tính năng đọc ảnh có bật được không (để đổi giao diện)."""
    return {"omr_san_sang": oemer_kha_dung()}


@app.post("/api/parse")
async def parse_file(file: UploadFile = File(...)):
    """Nhận file MusicXML/MIDI, trả về danh sách cảm âm sáo Đô dạng JSON."""
    duoi = Path(file.filename or "").suffix.lower()
    if duoi not in DUOI_FILE_HOP_LE:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ nhận file {', '.join(sorted(DUOI_FILE_HOP_LE))} — bạn gửi '{duoi or 'không rõ'}'",
        )

    noi_dung = await file.read()
    if not noi_dung:
        raise HTTPException(status_code=400, detail="File rỗng, hãy chọn file khác.")

    # music21 cần đường dẫn file thật -> ghi tạm ra đĩa rồi parse
    with tempfile.NamedTemporaryFile(suffix=duoi, delete=False) as f:
        f.write(noi_dung)
        duong_dan_tam = f.name

    try:
        notes = doc_ban_nhac(duong_dan_tam)
    except Exception as loi:  # music21 báo lỗi đa dạng -> gom lại báo thân thiện
        raise HTTPException(
            status_code=422,
            detail=f"Không đọc được bản nhạc: {loi}. Hãy kiểm tra file có đúng định dạng MusicXML/MIDI không.",
        )
    finally:
        Path(duong_dan_tam).unlink(missing_ok=True)

    return dong_goi_ket_qua(notes, file.filename or "bản nhạc", nguon="file")


@app.post("/api/parse-image")
async def parse_image(file: UploadFile = File(...)):
    """Nhận ẢNH bản nhạc scan/chụp -> OMR (oemer) -> cảm âm sáo Đô.

    Đây là tính năng thử nghiệm (Tuần 3-4): độ chính xác phụ thuộc chất
    lượng ảnh. Lỗi được báo rõ ràng, không làm sập server.
    """
    duoi = Path(file.filename or "").suffix.lower()
    if duoi not in DUOI_ANH_HOP_LE:
        raise HTTPException(
            status_code=400,
            detail=f"Chỉ nhận ảnh {', '.join(sorted(DUOI_ANH_HOP_LE))} — bạn gửi '{duoi or 'không rõ'}'",
        )

    noi_dung = await file.read()
    if not noi_dung:
        raise HTTPException(status_code=400, detail="Ảnh rỗng, hãy chọn ảnh khác.")

    # Làm việc trong 1 thư mục tạm rồi dọn sạch sau khi xong
    with tempfile.TemporaryDirectory() as thu_muc:
        duong_dan_anh = Path(thu_muc) / f"input{duoi}"
        duong_dan_anh.write_bytes(noi_dung)

        try:
            file_xml = anh_sang_musicxml(str(duong_dan_anh), thu_muc)
            notes = doc_ban_nhac(file_xml)
        except LoiOMR as loi:
            # Chưa cài oemer -> 503 (dịch vụ chưa sẵn sàng); còn lại -> 422
            ma = 503 if not oemer_kha_dung() else 422
            raise HTTPException(status_code=ma, detail=str(loi))
        except Exception as loi:
            raise HTTPException(
                status_code=422,
                detail=f"Đọc được ảnh nhưng không dựng được cảm âm: {loi}",
            )

    return dong_goi_ket_qua(notes, file.filename or "ảnh bản nhạc", nguon="anh")


# Mount static SAU các route API để không che mất /api/*
app.mount("/", StaticFiles(directory="static", html=True), name="static")
