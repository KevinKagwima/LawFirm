function openTab(event, tabName) {
  // Hide all tab contents
  const tabContents = document.querySelectorAll(".tab-content");
  tabContents.forEach((content) => {
    content.classList.remove("active");
  });

  // Remove active class from all buttons
  const tabButtons = document.querySelectorAll(".menu-item");
  tabButtons.forEach((button) => {
    button.classList.remove("active");
  });

  // Show the selected tab content and add active class to the button
  document.getElementById(tabName).classList.add("active");
  event.currentTarget.classList.add("active");
}

function openSideBar() {
  const sidebar = document.querySelector(".sidebar");
  sidebar.classList.add("open");
}

function closeSideBar() {
  const sidebar = document.querySelector(".sidebar");
  sidebar.classList.remove("open");
}

document.addEventListener("DOMContentLoaded", function () {
  // Close button functionality
  document.querySelectorAll(".flash-close").forEach((button) => {
    button.addEventListener("click", function () {
      const message = this.closest(".flash-message");
      message.style.transform = "translateX(100%)";
      message.style.opacity = "0";
      setTimeout(() => message.remove(), 300);
    });
  });

  // Auto-dismiss after 5 seconds
  document.querySelectorAll(".flash-message").forEach((message) => {
    setTimeout(() => {
      message.style.transform = "translateX(100%)";
      message.style.opacity = "0";
      setTimeout(() => message.remove(), 300);
    }, 10000);
  });
});
