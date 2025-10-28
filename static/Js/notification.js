document.addEventListener("DOMContentLoaded", function () {
  const notificationsToggle = document.querySelector(".notifications-toggle");
  const notificationsPanel = document.querySelector(".notifications-panel");
  const notificationsList = document.getElementById("notifications-list");
  const notificationBadge = document.getElementById("notification-badge");
  const markAllReadBtn = document.querySelector(".mark-all-read");

  // Toggle notifications panel
  notificationsToggle.addEventListener("click", function (e) {
    e.stopPropagation();
    notificationsPanel.classList.toggle("show");
  });

  // Load notifications
  function loadNotifications() {
    fetch("/notifications")
      .then((response) => response.json())
      .then((notifications) => {
        if (notifications.length === 0) {
          notificationsList.innerHTML = `
            <div class="empty-state">
              <i class="fas fa-bell-slash"></i>
              <p>No new notifications</p>
            </div>
          `;
          return;
        }

        notificationsList.innerHTML = notifications
          .map(
            (notification) => `
          <div class="notification ${notification.is_read ? "" : "unread"}" 
               data-id="${notification.id}" 
               data-type="${notification.type}">
            <div class="notification-icon">
              ${getNotificationIcon(notification.type)}
            </div>
            <div class="notification-content">
              <h5>${notification.title}</h5>
              <p>${notification.message}</p>
              <small>${formatTime(notification.created_at)}</small>
            </div>
          </div>
        `
          )
          .join("");

        updateBadgeCount();

        // Add click handlers
        document.querySelectorAll(".notification").forEach((notification) => {
          notification.addEventListener("click", function () {
            if (this.classList.contains("unread")) {
              markNotificationRead(this.dataset.id);
              this.classList.remove("unread");
              updateBadgeCount();
            }
            // Handle navigation based on type
            handleNotificationClick(this.dataset.type, this.dataset.id);
          });
        });
      });
  }

  // Mark all as read
  markAllReadBtn.addEventListener("click", function (e) {
    e.stopPropagation();
    fetch("/notifications/read-all", { method: "POST" })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          document.querySelectorAll(".notification.unread").forEach((el) => {
            el.classList.remove("unread");
          });
          updateBadgeCount();
        }
      });
  });

  // Helper functions
  function getNotificationIcon(type) {
    const icons = {
      prescription: '<i class="fas fa-prescription-bottle-alt"></i>',
      diagnosis: '<i class="fas fa-stethoscope"></i>',
      payment: '<i class="fas fa-money-bill-wave"></i>',
      inventory: '<i class="fas fa-pills"></i>',
      appointment: '<i class="fas fa-calendar-check"></i>',
      patient: '<i class="fas fa-user-injured"></i>',
      staff: '<i class="fas fa-user"></i>',
      medicine: '<i class="fas fa-capsules"></i>',
      disease: '<i class="fas fa-disease"></i>',
    };
    return icons[type] || icons["system"];
  }

  function formatTime(isoString) {
    const date = new Date(isoString);
    return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  }

  function updateBadgeCount() {
    const unreadCount = document.querySelectorAll(
      ".notification.unread"
    ).length;
    notificationBadge.textContent = unreadCount;
    notificationBadge.style.display = unreadCount > 0 ? "flex" : "none";
  }

  function markNotificationRead(id) {
    fetch(`/notifications/${id}/read`, { method: "POST" });
  }

  // setInterval(loadNotifications, 1000);

  updateBadgeCount();
});
