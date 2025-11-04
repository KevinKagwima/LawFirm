// Modal elements
const modal = document.getElementById("NoteFormModal");
const addBtn = document.getElementById("OpenNoteModalBtn");
const noteCloseBtn = document.querySelector(".close-note");

const Paymentmodal = document.getElementById("PaymentFormModal");
const paymentBtn = document.getElementById("OpenPaymentModalBtn");
const paymentCloseBtn = document.querySelector(".close-payment");

// Toggle modal
addBtn.addEventListener("click", () => (modal.style.display = "flex"));
noteCloseBtn.addEventListener("click", () => (modal.style.display = "none"));

paymentBtn.addEventListener(
  "click",
  () => (Paymentmodal.style.display = "flex")
);
paymentCloseBtn.addEventListener(
  "click",
  () => (Paymentmodal.style.display = "none")
);

// Close modal when clicking outside
window.addEventListener("click", (e) => {
  if (e.target === modal) {
    modal.style.display = "none";
  } else if (e.target === Paymentmodal) {
    Paymentmodal.style.display = "none";
  }
});
