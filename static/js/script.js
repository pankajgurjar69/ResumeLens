const resumeInput = document.getElementById("resume");
const fileName = document.getElementById("file-name");
if (resumeInput && fileName) {
  resumeInput.addEventListener("change", () => {
    fileName.textContent = resumeInput.files.length ? `Selected: ${resumeInput.files[0].name}` : "PDF only. Your original file is deleted after text extraction.";
  });
}
const zone = document.querySelector(".upload-zone");
if (zone && resumeInput) {
  ["dragenter", "dragover"].forEach(name => zone.addEventListener(name, e => { e.preventDefault(); zone.classList.add("dragging"); }));
  ["dragleave", "drop"].forEach(name => zone.addEventListener(name, e => { e.preventDefault(); zone.classList.remove("dragging"); }));
  zone.addEventListener("drop", e => { if (e.dataTransfer.files.length) { resumeInput.files = e.dataTransfer.files; resumeInput.dispatchEvent(new Event("change")); } });
}
document.querySelectorAll('.quiz-check').forEach((button) => button.addEventListener('click', () => {
  const group = button.closest('.quiz-question');
  const selected = group.querySelector('input[type="radio"]:checked');
  const feedback = group.querySelector('.quiz-feedback');
  if (!selected) { feedback.textContent = ' Choose an answer first.'; return; }
  feedback.textContent = (Number(selected.value) === Number(button.dataset.answer) ? ' Correct. ' : ' Not quite. ') + button.dataset.explanation;
}));
