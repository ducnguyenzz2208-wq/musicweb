// =========================================================
// Cảm âm sáo Đô — logic giao diện
// Upload file -> gọi POST /api/parse -> vẽ bảng cảm âm
// =========================================================

const dropzone = document.getElementById("dropzone");
const fileInput = document.getElementById("fileInput");
const uploadStatus = document.getElementById("uploadStatus");
const resultsSection = document.getElementById("ket-qua");
const statsBox = document.getElementById("stats");
const tableBody = document.querySelector("#noteTable tbody");
const btnDownload = document.getElementById("btnDownload");

const readingEmpty = document.getElementById("readingEmpty");
const readingInfo = document.getElementById("readingInfo");
const readingName = document.getElementById("readingName");
const readingFacts = document.getElementById("readingFacts");

const coverNote = document.getElementById("coverNote");
const coverWave = document.getElementById("coverWave");

const playbar = document.getElementById("playbar");
const playbarName = document.getElementById("playbarName");
const playbarSub = document.getElementById("playbarSub");
const playbarStrip = document.getElementById("playbarStrip");
const playbarCount = document.getElementById("playbarCount");

const themeToggle = document.getElementById("themeToggle");
const heroWave = document.getElementById("heroWave");

let ketQuaHienTai = null; // giữ kết quả gần nhất để nút "Tải về" dùng

// ---- Theme sáng/tối: nhớ lựa chọn trong localStorage ----
const themeLuu = localStorage.getItem("saolab-theme");
if (themeLuu) document.documentElement.setAttribute("data-theme", themeLuu);
themeToggle?.addEventListener("click", () => {
  const dangDark =
    document.documentElement.getAttribute("data-theme") === "dark" ||
    (!document.documentElement.getAttribute("data-theme") &&
      window.matchMedia("(prefers-color-scheme: dark)").matches);
  const moi = dangDark ? "light" : "dark";
  document.documentElement.setAttribute("data-theme", moi);
  localStorage.setItem("saolab-theme", moi);
});

// ---- Waveform trang trí ở hero (chiều cao ngẫu nhiên, nhịp lệch pha) ----
if (heroWave) {
  for (let i = 0; i < 16; i++) {
    const s = document.createElement("span");
    s.style.height = 8 + Math.round(Math.random() * 20) + "px";
    s.style.animationDelay = (i * 0.07).toFixed(2) + "s";
    heroWave.appendChild(s);
  }
}

// ---- Chọn file: click hoặc kéo thả ----
dropzone.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("keydown", (e) => {
  if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); }
});
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) guiFile(fileInput.files[0]);
});

["dragenter", "dragover"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.add("dragover");
  })
);
["dragleave", "drop"].forEach((ev) =>
  dropzone.addEventListener(ev, (e) => {
    e.preventDefault();
    dropzone.classList.remove("dragover");
  })
);
dropzone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files?.[0];
  if (file) guiFile(file);
});

// ---- Gửi file lên server ----
async function guiFile(file) {
  uploadStatus.textContent = `Đang đọc "${file.name}"…`;
  uploadStatus.className = "upload-status busy";

  const form = new FormData();
  form.append("file", file);

  try {
    const res = await fetch("/api/parse", { method: "POST", body: form });
    const data = await res.json();

    if (!res.ok) {
      // Server trả detail tiếng Việt -> hiện thẳng cho người dùng
      throw new Error(data.detail || "Có lỗi không rõ, thử lại nhé.");
    }

    ketQuaHienTai = data;
    uploadStatus.textContent = `Đã đọc xong "${data.ten_file}" — ${data.tong_so_not} nốt nhạc.`;
    uploadStatus.className = "upload-status";
    veKetQua(data);
  } catch (err) {
    uploadStatus.textContent = err.message;
    uploadStatus.className = "upload-status error";
  } finally {
    fileInput.value = ""; // cho phép chọn lại đúng file cũ
  }
}

// ---- Vẽ kết quả ra giao diện ----
function veKetQua(data) {
  // 1. Thẻ thống kê
  const soLang = data.notes.filter((n) => n.la_lang).length;
  statsBox.innerHTML = "";
  themStat(data.tong_so_not, "Nốt nhạc");
  themStat(data.so_not_thang, "Nốt thăng/giáng");
  themStat(soLang, "Dấu lặng");
  themStat(data.so_ngoai_tam, "Ngoài tầm sáo", data.so_ngoai_tam > 0);

  // 2. Bảng nốt
  tableBody.innerHTML = "";
  for (const n of data.notes) {
    const tr = document.createElement("tr");
    if (n.la_lang) tr.className = "row-rest";
    else if (n.ngoai_tam) tr.className = "row-out";
    else if (n.la_thang) tr.className = "row-sharp";

    tr.innerHTML = `
      <td class="td-num">${n.stt}</td>
      <td class="td-pitch">${n.ten_not}</td>
      <td class="td-camam">${n.cam_am}</td>
      <td class="td-finger">${n.ngon_bam}</td>
      <td>${n.truong_do}</td>
      <td class="td-note-extra">${n.ghi_chu || ""}</td>`;
    tableBody.appendChild(tr);
  }

  resultsSection.hidden = false;
  resultsSection.classList.remove("reveal");
  void resultsSection.offsetWidth; // reset animation
  resultsSection.classList.add("reveal");

  // 3. Rail "Đang đọc" — album art lấy cảm âm nốt đầu tiên
  readingEmpty.hidden = true;
  readingInfo.hidden = false;
  const notDau = data.notes.find((n) => !n.la_lang);
  coverNote.textContent = notDau ? notDau.cam_am.replace("2", "") : "♪";
  veCoverWave(data.notes);
  readingName.textContent = data.ten_file;
  readingFacts.innerHTML = "";
  themFact("Tổng số nốt", data.tong_so_not);
  themFact("Thăng/giáng", data.so_not_thang);
  themFact("Dấu lặng", soLang);
  themFact("Ngoài tầm", data.so_ngoai_tam, data.so_ngoai_tam > 0);

  // 4. Playbar: dải cảm âm kiểu waveform
  playbar.hidden = false;
  playbarName.textContent = data.ten_file;
  playbarSub.textContent = "Cảm âm sáo Đô";
  playbarCount.textContent = `${data.tong_so_not} nốt`;
  vePlaybarStrip(data.notes);

  resultsSection.scrollIntoView({ behavior: "smooth", block: "start" });
}

function themStat(so, nhan, canhBao = false) {
  const div = document.createElement("div");
  div.className = "stat" + (canhBao ? " warn" : "");
  div.innerHTML = `<p class="num">${so}</p><p class="lbl">${nhan}</p>`;
  statsBox.appendChild(div);
}

function themFact(nhan, giaTri, canhBao = false) {
  const div = document.createElement("div");
  div.innerHTML = `<dt>${nhan}</dt><dd${canhBao ? ' class="warn"' : ""}>${giaTri}</dd>`;
  readingFacts.appendChild(div);
}

// Waveform nhỏ trong "album art" — lấy tối đa 22 nốt
function veCoverWave(notes) {
  coverWave.innerHTML = "";
  const hien = notes.slice(0, 22);
  for (const n of hien) {
    const s = document.createElement("span");
    let h = 20;
    if (!n.la_lang && n.octave != null) {
      h = Math.max(15, Math.min(85, 20 + (n.octave - 4) * 22));
    } else if (n.la_lang) {
      h = 12;
    }
    s.style.height = h + "%";
    if (n.la_lang) s.style.opacity = ".3";
    coverWave.appendChild(s);
  }
}

// Mỗi nốt là 1 thanh: cao thấp theo cao độ, màu lime; lặng = xám; ngoài tầm = đỏ
function vePlaybarStrip(notes) {
  playbarStrip.innerHTML = "";
  const hien = notes.slice(0, 90); // đủ lấp thanh, tránh vẽ quá nhiều
  for (const n of hien) {
    const bar = document.createElement("span");
    bar.className = "bar" + (n.la_lang ? " rest" : n.ngoai_tam ? " out" : "");
    let h = 8;
    if (!n.la_lang && n.octave != null) {
      // C4=8px ... B6=32px: chuyển cao độ thành chiều cao thanh
      const b = (n.octave - 4) * 12;
      h = Math.max(6, Math.min(32, 8 + b));
    }
    bar.style.height = h + "px";
    playbarStrip.appendChild(bar);
  }
}

// ---- Tải kết quả về dạng .txt ----
btnDownload.addEventListener("click", () => {
  if (!ketQuaHienTai) return;
  const d = ketQuaHienTai;

  const dong = [
    `CẢM ÂM SÁO ĐÔ — ${d.ten_file}`,
    `Tổng số nốt: ${d.tong_so_not} · Ngoài tầm: ${d.so_ngoai_tam}`,
    `Ký hiệu ngón bấm: ● bịt lỗ · ○ mở lỗ · ◐ nửa lỗ (đọc từ lỗ gần lỗ thổi)`,
    "".padEnd(60, "-"),
  ];

  // Dòng cảm âm liền mạch để đọc khi thổi
  const camAmLien = d.notes
    .map((n) => (n.la_lang ? "(nghỉ)" : n.cam_am))
    .join(" ");
  dong.push("CẢM ÂM:", camAmLien, "".padEnd(60, "-"), "CHI TIẾT:");

  for (const n of d.notes) {
    dong.push(
      `${String(n.stt).padStart(3)}. ${n.cam_am.padEnd(6)} ${n.ngon_bam.padEnd(8)} ${n.truong_do}${n.ghi_chu ? " — " + n.ghi_chu : ""}`
    );
  }

  const blob = new Blob(["﻿" + dong.join("\n")], { type: "text/plain;charset=utf-8" });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = (d.ten_file || "cam-am").replace(/\.[^.]+$/, "") + "-cam-am.txt";
  a.click();
  URL.revokeObjectURL(a.href);
});
