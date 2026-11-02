// Cloner Frontend Controller
(function() {
  let detectedApps = [];
  let activeClones = [];
  let selectedApp = null;
  let selectedColor = "#3B82F6";

  // Elements
  const appsRow = document.getElementById("appsRow");
  const clonesGrid = document.getElementById("clonesGrid");
  const clonesCountBadge = document.getElementById("clonesCountBadge");
  const detectedCount = document.getElementById("detectedCount");
  const btnRefreshApps = document.getElementById("btnRefreshApps");

  // Modal elements
  const modalBackdrop = document.getElementById("modalBackdrop");
  const btnCloseModal = document.getElementById("btnCloseModal");
  const btnCancelClone = document.getElementById("btnCancelClone");
  const btnConfirmClone = document.getElementById("btnConfirmClone");
  const modalTitle = document.getElementById("modalTitle");
  const profileNameInput = document.getElementById("profileNameInput");
  const colorPickerRow = document.getElementById("colorPickerRow");
  const previewBaseIcon = document.getElementById("previewBaseIcon");
  const previewBadge = document.getElementById("previewBadge");
  const previewBadgeText = document.getElementById("previewBadgeText");
  const previewCloneName = document.getElementById("previewCloneName");
  const previewDataPath = document.getElementById("previewDataPath");
  const toastNotification = document.getElementById("toastNotification");

  // Initialize
  document.addEventListener("DOMContentLoaded", () => {
    setupEventListeners();
    refreshAll();
  });

  function setupEventListeners() {
    btnRefreshApps.addEventListener("click", () => {
      refreshAll();
      showToast("Refreshed apps and clones");
    });

    btnCloseModal.addEventListener("click", closeModal);
    btnCancelClone.addEventListener("click", closeModal);

    modalBackdrop.addEventListener("click", (e) => {
      if (e.target === modalBackdrop) closeModal();
    });

    profileNameInput.addEventListener("input", updateLivePreview);

    colorPickerRow.addEventListener("click", (e) => {
      const swatch = e.target.closest(".color-swatch");
      if (!swatch) return;
      document.querySelectorAll(".color-swatch").forEach(s => s.classList.remove("active"));
      swatch.classList.add("active");
      selectedColor = swatch.dataset.color;
      updateLivePreview();
    });

    btnConfirmClone.addEventListener("click", handleCreateClone);
  }

  // Native Bridge abstraction
  function postNativeMessage(action, payload = {}) {
    return new Promise((resolve) => {
      const callbackId = "cb_" + Math.random().toString(36).substring(2, 9);
      window[callbackId] = (response) => {
        delete window[callbackId];
        resolve(response);
      };

      const msg = { action, payload, callbackId };

      if (window.webkit && window.webkit.messageHandlers && window.webkit.messageHandlers.clonerBridge) {
        window.webkit.messageHandlers.clonerBridge.postMessage(msg);
      } else {
        // Fallback for browser testing
        console.log("[Native Bridge Call]", msg);
        setTimeout(() => {
          resolve(mockNativeResponse(action, payload));
        }, 300);
      }
    });
  }

  // Handle messages sent back from Swift
  window.handleNativeResponse = function(callbackId, response) {
    if (window[callbackId]) {
      window[callbackId](response);
    }
  };

  async function refreshAll() {
    loadApps();
    loadClones();
  }

  async function loadApps() {
    const res = await postNativeMessage("getApps");
    detectedApps = res.apps || [];
    renderAppsGallery();
  }

  async function loadClones() {
    const res = await postNativeMessage("getClones");
    activeClones = res.clones || [];
    renderClonesGrid();
  }

  function renderAppsGallery() {
    appsRow.innerHTML = "";
    if (detectedApps.length === 0) {
      appsRow.innerHTML = `<div class="empty-state"><p>No supported AI desktop apps detected in /Applications</p></div>`;
      detectedCount.textContent = "0 AI apps detected";
      return;
    }

    detectedCount.textContent = `${detectedApps.length} AI apps detected`;

    detectedApps.forEach(app => {
      const card = document.createElement("div");
      card.className = "squircle-card";
      card.title = `Click to create a new profile clone of ${app.name}`;

      // Real app icon or fallback
      const iconUrl = app.icon_base64 ? `data:image/png;base64,${app.icon_base64}` : getAppSvgIcon(app.key);

      card.innerHTML = `
        <div class="squircle-icon-frame">
          <img src="${iconUrl}" class="squircle-img" alt="${app.name}">
        </div>
        <span class="squircle-label">${app.name}</span>
        ${app.is_featured ? `<span class="squircle-badge-pill">Detected</span>` : ""}
      `;

      card.addEventListener("click", () => openCreateModal(app));
      appsRow.appendChild(card);
    });

    // Add "+ Custom App" squircle card at the end
    const customCard = document.createElement("div");
    customCard.className = "squircle-card add-custom";
    customCard.title = "Choose any other macOS application from your Mac";
    customCard.innerHTML = `
      <div class="squircle-icon-frame add-frame">
        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
          <line x1="12" y1="5" x2="12" y2="19"></line>
          <line x1="5" y1="12" x2="19" y2="12"></line>
        </svg>
      </div>
      <span class="squircle-label">Add App...</span>
    `;
    customCard.addEventListener("click", async () => {
      const res = await postNativeMessage("pickCustomApp");
      if (res && res.success && res.app) {
        openCreateModal(res.app);
      }
    });
    appsRow.appendChild(customCard);
  }

  function renderClonesGrid() {
    clonesGrid.innerHTML = "";
    clonesCountBadge.textContent = `${activeClones.length} Clones`;

    if (activeClones.length === 0) {
      clonesGrid.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6">
              <rect x="2" y="3" width="20" height="14" rx="2"></rect>
              <line x1="8" y1="21" x2="16" y2="21"></line>
              <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
          </div>
          <h3>No clones created yet</h3>
          <p>Click any application in the row above to create an independent account clone.</p>
        </div>
      `;
      return;
    }

    activeClones.forEach(clone => {
      const card = document.createElement("div");
      card.className = "clone-card";

      const iconUrl = clone.icon_base64 ? `data:image/png;base64,${clone.icon_base64}` : getAppSvgIcon(clone.base_app_name.toLowerCase());

      card.innerHTML = `
        <div class="clone-header">
          <div class="clone-icon-wrapper">
            <img src="${iconUrl}" class="clone-icon-img" alt="${clone.name}">
            <div class="clone-badge-tag" style="background-color: ${clone.badge_color || '#3B82F6'}"></div>
          </div>
          <div class="clone-info">
            <div class="clone-title" title="${clone.name}">${clone.name}</div>
            <div class="clone-meta">
              <span>Profile: <strong>${clone.profile_name}</strong></span>
              <span>•</span>
              <span>${clone.data_size || '0 MB'}</span>
              <span>•</span>
              <span class="status-indicator ${clone.is_running ? 'running' : 'ready'}">
                <span class="status-dot"></span>
                ${clone.is_running ? 'Running' : 'Ready'}
              </span>
            </div>
          </div>
        </div>

        <div class="clone-actions">
          <button class="btn-launch" title="Launch this independent account instance">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="currentColor">
              <polygon points="5 3 19 12 5 21 5 3"></polygon>
            </svg>
            Open
          </button>
          <button class="btn-icon-action finder" title="Reveal .app in Finder">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>
            </svg>
          </button>
          <button class="btn-icon-action data" title="Open isolated profile storage folder">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <ellipse cx="12" cy="5" rx="9" ry="3"></ellipse>
              <path d="M21 12c0 1.66-4 3-9 3s-9-1.34-9-3"></path>
              <path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"></path>
            </svg>
          </button>
          <button class="btn-icon-action delete" title="Delete clone">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="3 6 5 6 21 6"></polyline>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            </svg>
          </button>
        </div>
      `;

      // Event handlers
      card.querySelector(".btn-launch").addEventListener("click", () => launchClone(clone.path));
      card.querySelector(".btn-icon-action.finder").addEventListener("click", () => revealInFinder(clone.path));
      card.querySelector(".btn-icon-action.data").addEventListener("click", () => openDataFolder(clone.data_dir));
      card.querySelector(".btn-icon-action.delete").addEventListener("click", () => deleteClone(clone));

      clonesGrid.appendChild(card);
    });
  }

  function openCreateModal(app) {
    selectedApp = app;
    modalTitle.textContent = `Clone ${app.name}`;
    profileNameInput.value = "";
    previewBaseIcon.src = app.icon_base64 ? `data:image/png;base64,${app.icon_base64}` : getAppSvgIcon(app.key);
    updateLivePreview();
    modalBackdrop.classList.add("active");
    setTimeout(() => profileNameInput.focus(), 100);
  }

  function closeModal() {
    modalBackdrop.classList.remove("active");
    btnConfirmClone.classList.remove("loading");
    btnConfirmClone.disabled = false;
  }

  function updateLivePreview() {
    const rawVal = profileNameInput.value.trim();
    const profile = rawVal || "Work";
    const appName = selectedApp ? selectedApp.name : "App";

    previewCloneName.textContent = `${appName} (${profile})`;
    previewBadge.style.backgroundColor = selectedColor;

    const initials = profile.substring(0, 2).toUpperCase();
    previewBadgeText.textContent = initials;
    previewDataPath.textContent = `~/Library/Application Support/Cloner/${appName.toLowerCase()}/${profile.toLowerCase().replace(/ /g, '-')}`;
  }

  async function handleCreateClone() {
    if (!selectedApp) return;
    const profileName = profileNameInput.value.trim() || "Work";

    btnConfirmClone.classList.add("loading");
    btnConfirmClone.disabled = true;

    try {
      const res = await postNativeMessage("createClone", {
        app_path: selectedApp.path,
        profile_name: profileName,
        badge_color: selectedColor
      });

      if (res && res.success) {
        showToast(`Created ${res.clone_name} in Cloner folder!`);
        closeModal();
        await loadClones();
      } else {
        alert("Error creating clone: " + (res.error || "Unknown error"));
        btnConfirmClone.classList.remove("loading");
        btnConfirmClone.disabled = false;
      }
    } catch (err) {
      alert("Failed to communicate with Cloner engine: " + err.message);
      btnConfirmClone.classList.remove("loading");
      btnConfirmClone.disabled = false;
    }
  }

  async function launchClone(clonePath) {
    showToast("Launching app clone...");
    await postNativeMessage("launchClone", { clone_path: clonePath });
  }

  async function revealInFinder(path) {
    await postNativeMessage("revealClone", { path: path });
  }

  async function openDataFolder(dataDir) {
    await postNativeMessage("openDataFolder", { data_dir: dataDir });
  }

  async function deleteClone(clone) {
    const confirmDel = confirm(`Delete "${clone.name}"?\n\nThis removes the app from ~/Desktop/Cloner.`);
    if (!confirmDel) return;

    const removeData = confirm(`Do you also want to delete the isolated session data for profile "${clone.profile_name}"?`);

    const res = await postNativeMessage("deleteClone", {
      clone_path: clone.path,
      remove_data: removeData
    });

    if (res && res.success) {
      showToast(`Deleted ${clone.name}`);
      await loadClones();
    }
  }

  function showToast(msg) {
    toastNotification.textContent = msg;
    toastNotification.classList.add("show");
    setTimeout(() => {
      toastNotification.classList.remove("show");
    }, 2800);
  }

  // Fallback crisp SVG icons matching dark aesthetic
  function getAppSvgIcon(key) {
    const cleanKey = (key || "").toLowerCase();
    if (cleanKey.includes("chatgpt")) {
      return "data:image/svg+xml;utf8," + encodeURIComponent(`
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
          <rect width="100" height="100" rx="22" fill="#10A37F"/>
          <path d="M50 25C36.2 25 25 36.2 25 50C25 63.8 36.2 75 50 75C63.8 75 75 63.8 75 50C75 36.2 63.8 25 50 25ZM50 32C59.9 32 68 40.1 68 50C68 59.9 59.9 68 50 68C40.1 68 32 59.9 32 50C32 40.1 40.1 32 50 32Z" fill="#FFFFFF"/>
        </svg>`);
    } else if (cleanKey.includes("claude")) {
      return "data:image/svg+xml;utf8," + encodeURIComponent(`
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
          <rect width="100" height="100" rx="22" fill="#D97706"/>
          <circle cx="50" cy="50" r="26" fill="#FFFFFF"/>
          <circle cx="50" cy="50" r="14" fill="#D97706"/>
        </svg>`);
    } else if (cleanKey.includes("antigravity")) {
      return "data:image/svg+xml;utf8," + encodeURIComponent(`
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
          <rect width="100" height="100" rx="22" fill="#4F46E5"/>
          <polygon points="50,22 78,72 22,72" fill="#FFFFFF"/>
        </svg>`);
    }
    return "data:image/svg+xml;utf8," + encodeURIComponent(`
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none">
        <rect width="100" height="100" rx="22" fill="#2563EB"/>
        <rect x="28" y="28" width="44" height="44" rx="8" fill="#FFFFFF"/>
      </svg>`);
  }

  // Browser testing mock
  function mockNativeResponse(action, payload) {
    if (action === "getApps") {
      return {
        apps: [
          { name: "ChatGPT", key: "chatgpt", path: "/Applications/ChatGPT.app", is_featured: true },
          { name: "Claude", key: "claude", path: "/Applications/Claude.app", is_featured: true },
          { name: "AntiGravity", key: "antigravity", path: "/Applications/AntiGravity.app", is_featured: true },
          { name: "AntiGravity IDE", key: "antigravity-ide", path: "/Applications/AntiGravity IDE.app", is_featured: true }
        ]
      };
    }
    if (action === "getClones") {
      return { clones: [] };
    }
    if (action === "createClone") {
      return { success: true, clone_name: `${payload.app_path.split('/').pop().replace('.app','')} (${payload.profile_name})` };
    }
    return { success: true };
  }
})();
