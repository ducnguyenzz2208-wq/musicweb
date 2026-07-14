# -*- coding: utf-8 -*-
"""
Web đọc bản nhạc -> Cảm âm sáo Đô — Backend FastAPI (Tuần 1-2).

Chức năng hiện có:
- GET  /            : trang web (static/index.html)
- POST /api/parse   : nhận file MusicXML/MIDI, trả JSON danh sách cảm âm

Chạy server:
    .venv\\Scripts\\python.exe -m uvicorn main:app --reload
"""

import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from music21 import converter, note as m21_note, chord as m21_chord

from mapping.sao_do import tra_cam_am, ten_truong_do

app = FastAPI(title="Cảm âm sáo Đô", version="0.1.0")

# Các đuôi file chấp nhận (MusicXML và MIDI)
DUOI_FILE_HOP_LE = {".xml", ".musicxml", ".mxl", ".mid", ".midi"}


def doc_ban_nhac(duong_dan: str) -> list[dict]:
    """Parse file nhạc bằng music21, trả về danh sách nốt kèm cảm âm.

    Với hợp âm (chord) thì lấy nốt cao nhất — thường là giai điệu chính.
    Dấu lặng (rest) cũng đưa vào để người thổi biết chỗ ngắt hơi.
    """
    score = converter.parse(duong_dan)
    ket_qua = []

    for phan_tu in score.flatten().notesAndRests:
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

    if not notes:
        raise HTTPException(status_code=422, detail="File hợp lệ nhưng không tìm thấy nốt nhạc nào.")

    so_ngoai_tam = sum(1 for n in notes if n["ngoai_tam"])
    so_thang = sum(1 for n in notes if n["la_thang"])
    return {
        "ten_file": file.filename,
        "tong_so_not": len([n for n in notes if not n["la_lang"]]),
        "so_ngoai_tam": so_ngoai_tam,
        "so_not_thang": so_thang,
        "notes": notes,
    }


# Mount static SAU các route API để không che mất /api/*
app.mount("/", StaticFiles(directory="static", html=True), name="static")
