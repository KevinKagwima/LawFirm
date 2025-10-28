const maintabs = document.querySelectorAll(".nav-item");
const maintabContents = document.querySelectorAll(".tabContent");

maintabs.forEach((maintab) => {
  maintab.addEventListener("click", () => {
    // Remove active class from all tabs and contents
    maintabs.forEach((t) => t.classList.remove("active"));
    maintabContents.forEach((x) => x.classList.remove("active"));

    // Add active class to clicked tab and corresponding content
    maintab.classList.add("active");
    const maintabId = maintab.getAttribute("data-tab");
    document.getElementById(maintabId).classList.add("active");
  });
});

const tabs = document.querySelectorAll(".tab");
const tabContents = document.querySelectorAll(".tab-content");

tabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    // Remove active class from all tabs and contents
    tabs.forEach((t) => t.classList.remove("active"));
    tabContents.forEach((c) => c.classList.remove("active"));

    // Add active class to clicked tab and corresponding content
    tab.classList.add("active");
    const tabId = tab.getAttribute("data-tab");
    document.getElementById(tabId).classList.add("active");
  });
});

const medicaltabs = document.querySelectorAll(".med-tab");
const medical_table = document.querySelectorAll(".medical-data-table");

medicaltabs.forEach((tab) => {
  tab.addEventListener("click", () => {
    // Remove active class from all tabs and contents
    medicaltabs.forEach((t) => t.classList.remove("active"));
    medical_table.forEach((c) => c.classList.remove("active"));

    // Add active class to clicked tab and corresponding content
    tab.classList.add("active");
    const tabId = tab.getAttribute("data-tab");
    document.getElementById(tabId).classList.add("active");
  });
});

const payBtns = document.querySelectorAll("#pay-btn");
const modal = document.querySelector(".modal");
const modalFooter = document.querySelector(".modal-footer");

payBtns.forEach((payBtn) => {
  payBtn.addEventListener("click", () => {
    const target_id = payBtn.getAttribute("data-id");
    modal.style.display = "flex";

    modalFooter.innerHTML = "";

    const cancelBtn = document.createElement("button");
    cancelBtn.innerHTML = "Cancel";
    cancelBtn.classList = "btn cancel-btn";

    const confirmBtn = document.createElement("button");
    confirmBtn.innerHTML = "Confirm";
    confirmBtn.classList = "btn confirm-btn";

    const paymentLink = document.createElement("a");
    paymentLink.href = `/pay/prescription/${target_id}`;

    paymentLink.appendChild(confirmBtn);

    modalFooter.append(cancelBtn);
    modalFooter.append(paymentLink);

    cancelBtn.addEventListener("click", () => {
      modal.style.display = "none";
    });
  });
});

const branchmodal = document.getElementById("branchModal");
const addBtn = document.getElementById("addBranchBtn");
const closeBtn = document.querySelector(".close");
const cancelBtn = document.getElementById("cancelBtn");

// Toggle modal
addBtn.addEventListener("click", () => (branchmodal.style.display = "flex"));
closeBtn.addEventListener("click", () => (branchmodal.style.display = "none"));
cancelBtn.addEventListener("click", () => (branchmodal.style.display = "none"));

// Close modal when clicking outside
window.addEventListener("click", (e) => {
  if (e.target === modal) {
    branchmodal.style.display = "none";
  }
});

const notification_bell = document.querySelector(".fa-bell");
const notification_box = document.querySelector(".notifications-container");

notification_bell.addEventListener("click", () => {
  notification_box.classList.toggle("show-notification-box");
});
