// ============================================
// ADMIN PANEL FRONTEND SCRIPT
// ============================================

document.addEventListener("DOMContentLoaded", function () {
    console.log("Admin panel script initialised");

    // ----------------------------------------
    // Admin Login Handling
    // ----------------------------------------

    const loginForm = document.getElementById("adminLoginForm");
    const loginError = document.getElementById("adminLoginError");
    const loginButton = document.getElementById("adminLoginButton");

    if (loginForm) {
        loginForm.addEventListener("submit", async function (event) {
            event.preventDefault();

            const emailInput = document.getElementById("adminEmail");
            const passwordInput = document.getElementById("adminPassword");

            if (!emailInput || !passwordInput) {
                return;
            }

            const email = emailInput.value.trim();
            const password = passwordInput.value;

            if (!email || !password) {
                showLoginError("Please enter both email and password.");
                return;
            }

            try {
                if (loginButton) {
                    loginButton.disabled = true;
                    loginButton.textContent = "Signing in...";
                }

                const response = await fetch("/admin/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email, password })
                });

                const data = await response.json().catch(() => ({}));

                if (response.ok && data && data.success) {
                    window.location.href = "/admin/dashboard";
                    return;
                }

                const message =
                    (data && (data.error || data.message)) ||
                    "Login failed. Please check your credentials.";
                showLoginError(message);
            } catch (error) {
                console.error("Admin login error:", error);
                showLoginError("Unable to connect. Please try again.");
            } finally {
                if (loginButton) {
                    loginButton.disabled = false;
                    loginButton.textContent = "Sign in";
                }
            }
        });
    }

    function showLoginError(message) {
        if (!loginError) return;
        loginError.textContent = message;
        loginError.hidden = false;
    }

    // ----------------------------------------
    // Sidebar Toggle (Responsive)
    // ----------------------------------------

    const sidebar = document.querySelector(".admin-sidebar");
    const sidebarToggle = document.querySelector(".sidebar-toggle");

    if (sidebar && sidebarToggle) {
        sidebarToggle.addEventListener("click", () => {
            sidebar.classList.toggle("is-open");
        });

        document.addEventListener("click", (event) => {
            if (
                window.innerWidth <= 960 &&
                sidebar.classList.contains("is-open") &&
                !sidebar.contains(event.target) &&
                event.target !== sidebarToggle
            ) {
                sidebar.classList.remove("is-open");
            }
        });
    }

    // ----------------------------------------
    // Sidebar Active Navigation
    // ----------------------------------------

    const navLinks = document.querySelectorAll(".sidebar-link");
    const path = window.location.pathname;

    navLinks.forEach((link) => {
        const href = link.getAttribute("href") || "";
        if (href && path.startsWith(href)) {
            link.classList.add("active");
        }

        link.addEventListener("click", () => {
            navLinks.forEach((l) => l.classList.remove("active"));
            link.classList.add("active");
        });
    });

    // ----------------------------------------
    // Generic Search Filters
    // ----------------------------------------

    const userSearch = document.querySelector("#userSearch");
    if (userSearch) {
        userSearch.addEventListener("input", function () {
            const value = this.value.toLowerCase();
            const rows = document.querySelectorAll("#usersTable tr");
            rows.forEach((row) => {
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(value) ? "" : "none";
            });
        });
    }

    const orderSearch = document.querySelector("#orderSearch");
    if (orderSearch) {
        orderSearch.addEventListener("input", function () {
            const value = this.value.toLowerCase();
            const table = document.querySelector("#ordersTable") || document.querySelector("#recentOrdersBody");
            if (!table) return;

            const rows = table.querySelectorAll("tr");
            rows.forEach((row) => {
                if (row.classList.contains("placeholder-row")) return;
                const text = row.innerText.toLowerCase();
                row.style.display = text.includes(value) ? "" : "none";
            });
        });
    }

    // ----------------------------------------
    // Menu Item Interactions (other admin pages)
    // ----------------------------------------

    document.querySelectorAll(".delete-item").forEach((btn) => {
        btn.addEventListener("click", function () {
            const card = btn.closest(".menu-card");
            if (!card) return;
            if (confirm("Delete this menu item?")) {
                card.remove();
            }
        });
    });

    document.querySelectorAll(".edit-item").forEach((btn) => {
        btn.addEventListener("click", function () {
            const card = btn.closest(".menu-card");
            if (!card) return;
            const title = card.querySelector("h3");
            if (!title) return;
            const newName = prompt("Edit item name", title.innerText);
            if (newName) {
                title.innerText = newName;
            }
        });
    });

    // ----------------------------------------
    // Order Status Change (other admin pages)
    // ----------------------------------------

    document.querySelectorAll(".status-select").forEach((select) => {
        select.addEventListener("change", function () {
            const status = select.value;
            const badge = select.parentElement.querySelector(".status-badge");
            if (!badge) return;
            badge.innerText = status;
            badge.className = "status-badge " + status.toLowerCase();
        });
    });

    // ----------------------------------------
    // Settings Meal Mode (other admin pages)
    // ----------------------------------------

    const mealButtons = document.querySelectorAll(".meal-mode");
    mealButtons.forEach((btn) => {
        btn.addEventListener("click", function () {
            mealButtons.forEach((b) => b.classList.remove("active"));
            btn.classList.add("active");
        });
    });

    // Load current meal mode from backend (settings page)
    const mealModeLabel = document.querySelector('[data-metric="meal-mode-label"]');
    if (mealButtons.length && mealModeLabel) {
        fetch("/admin/api/settings")
            .then((r) => (r.ok ? r.json() : null))
            .then((data) => {
                if (!data || !data.meal_mode) return;
                const mode = String(data.meal_mode).toLowerCase();
                mealButtons.forEach((b) => {
                    if ((b.dataset.mealMode || "").toLowerCase() === mode) {
                        mealButtons.forEach((x) => x.classList.remove("active"));
                        b.classList.add("active");
                        mealModeLabel.textContent =
                            mode === "all" ? "All Meals" : mode.charAt(0).toUpperCase() + mode.slice(1);
                    }
                });
            })
            .catch(() => {});

        const saveBtn = document.getElementById("saveMealModeBtn");
        if (saveBtn) {
            saveBtn.addEventListener("click", async () => {
                const active = document.querySelector(".meal-mode.active");
                const mode = active ? active.dataset.mealMode : "all";
                try {
                    const res = await fetch("/admin/set-meal-mode", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({ meal_mode: mode })
                    });
                    const out = await res.json().catch(() => ({}));
                    if (res.ok && out.success) {
                        mealModeLabel.textContent =
                            mode === "all" ? "All Meals" : mode.charAt(0).toUpperCase() + mode.slice(1);
                    } else {
                        alert(out.error || "Failed to save meal mode");
                    }
                } catch (e) {
                    alert("Failed to save meal mode");
                }
            });
        }
    }

    // ----------------------------------------
    // Dashboard Metric Placeholders
    // ----------------------------------------

    document.querySelectorAll("[data-metric]").forEach((el) => {
        if (!el.textContent || !el.textContent.trim()) {
            el.textContent = "--";
        }
    });

    // ----------------------------------------
    // Dashboard Charts (empty data placeholders)
    // ----------------------------------------

    if (typeof Chart !== "undefined") {
        const revenueCanvas = document.getElementById("revenueChart");
        if (revenueCanvas) {
            new Chart(revenueCanvas, {
                type: "line",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Revenue",
                            data: [],
                            borderColor: "#22c55e",
                            borderWidth: 2,
                            tension: 0.45,
                            fill: false
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { display: false } },
                        y: { grid: { color: "rgba(55, 65, 81, 0.55)" } }
                    }
                }
            });
        }

        const categoryCanvas = document.getElementById("categoryChart");
        if (categoryCanvas) {
            new Chart(categoryCanvas, {
                type: "bar",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Categories",
                            data: [],
                            backgroundColor: "#22c55e",
                            borderRadius: 6
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { grid: { display: false } },
                        y: { grid: { color: "rgba(55, 65, 81, 0.55)" } }
                    }
                }
            });
        }

        const orderCanvas = document.getElementById("orderChart");
        if (orderCanvas) {
            new Chart(orderCanvas, {
                type: "doughnut",
                data: {
                    labels: [],
                    datasets: [
                        {
                            data: [],
                            backgroundColor: ["#f59e0b", "#3b82f6", "#22c55e"],
                            borderWidth: 0
                        }
                    ]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: { legend: { display: false } },
                    cutout: "72%"
                }
            });
        }
    }

    // ----------------------------------------
    // Admin Menu Page (DB-backed)
    // ----------------------------------------

    const menuGrid = document.getElementById("menuGrid");
    const menuSearch = document.querySelector(".menu-toolbar input.field-input");
    const addMenuBtn = document.querySelector(".menu-add-button");

    function renderMenuCards(items) {
        if (!menuGrid) return;
        menuGrid.innerHTML = "";
        if (!items || !items.length) {
            menuGrid.innerHTML = `
                <div class="placeholder-row" style="grid-column: 1/-1; padding: 18px; text-align:center; color:#9ca3af;">
                    No menu items found.
                </div>
            `;
            return;
        }

        items.forEach((it) => {
            const price = it.price != null ? String(it.price) : "0.00";
            const active = !!it.is_active;
            const card = document.createElement("article");
            card.className = "menu-card";
            card.dataset.itemId = it.id;
            card.innerHTML = `
                <header class="menu-card-header">
                    <h2 class="menu-card-title">${escapeHtml(it.name || "Item")}</h2>
                    <span class="menu-card-price">₹${escapeHtml(price)}</span>
                </header>
                <p class="menu-card-description">
                    Category: <strong>${escapeHtml(it.category || "-")}</strong> • Diet: <strong>${escapeHtml(it.diet_type || "-")}</strong>
                </p>
                <div class="menu-card-tags">
                    <span class="tag-pill">${escapeHtml(it.category || "category")}</span>
                    <span class="tag-pill tag-soft">${escapeHtml(it.diet_type || "diet")}</span>
                    <span class="tag-pill" style="border-color:${active ? "rgba(34,197,94,0.4)" : "rgba(245,158,11,0.4)"};">
                        ${active ? "Active" : "Inactive"}
                    </span>
                </div>
                <footer class="menu-card-footer">
                    <button type="button" class="btn btn-text js-toggle">${active ? "Deactivate" : "Activate"}</button>
                    <button type="button" class="btn btn-text js-edit">Edit</button>
                    <button type="button" class="btn btn-text js-delete">Delete</button>
                </footer>
            `;
            menuGrid.appendChild(card);
        });
    }

    function escapeHtml(str) {
        return String(str)
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#039;");
    }

    async function loadAdminMenuItems() {
        if (!menuGrid) return;
        const res = await fetch("/admin/api/menu-items");
        const data = await res.json().catch(() => ({}));
        const items = data.items || [];
        window.__adminMenuItems = items;
        renderMenuCards(items);
    }

    if (menuGrid) {
        loadAdminMenuItems().catch(() => {});

        menuGrid.addEventListener("click", async (e) => {
            const btn = e.target.closest("button");
            const card = e.target.closest(".menu-card");
            if (!btn || !card) return;
            const id = Number(card.dataset.itemId);

            if (btn.classList.contains("js-toggle")) {
                const isActive = btn.textContent.trim().toLowerCase() === "activate";
                const res = await fetch("/admin/toggle-item", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ id, is_active: isActive })
                });
                const out = await res.json().catch(() => ({}));
                if (!res.ok || !out.success) {
                    alert(out.error || "Failed to toggle item");
                    return;
                }
                await loadAdminMenuItems();
                return;
            }

            if (btn.classList.contains("js-delete")) {
                if (!confirm("Delete this menu item?")) return;
                const res = await fetch(`/admin/menu-item/${id}`, { method: "DELETE" });
                const out = await res.json().catch(() => ({}));
                if (!res.ok || !out.success) {
                    alert(out.error || "Failed to delete item");
                    return;
                }
                await loadAdminMenuItems();
                return;
            }

            if (btn.classList.contains("js-edit")) {
                const items = window.__adminMenuItems || [];
                const item = items.find((x) => Number(x.id) === id);
                if (!item) return;

                const name = prompt("Item name", item.name || "");
                if (name == null) return;
                const price = prompt("Price", item.price ?? "");
                if (price == null) return;
                const category = prompt("Category (breakfast/lunch/dinner/snacks)", item.category || "lunch");
                if (category == null) return;
                const dietType = prompt("Diet type (diet/non-diet)", item.diet_type || "diet");
                if (dietType == null) return;

                const payload = {
                    name,
                    price,
                    image_url: item.image_url || "",
                    protein: item.protein || 0,
                    carbs: item.carbs || 0,
                    fats: item.fats || 0,
                    calories: item.calories || 0,
                    category,
                    diet_type: dietType
                };

                const res = await fetch(`/admin/menu-item/${id}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const out = await res.json().catch(() => ({}));
                if (!res.ok || !out.success) {
                    alert(out.error || "Failed to update item");
                    return;
                }
                await loadAdminMenuItems();
            }
        });

        if (menuSearch) {
            menuSearch.addEventListener("input", () => {
                const q = menuSearch.value.trim().toLowerCase();
                const items = window.__adminMenuItems || [];
                const filtered = !q ? items : items.filter((it) => String(it.name || "").toLowerCase().includes(q));
                renderMenuCards(filtered);
            });
        }

        if (addMenuBtn) {
            addMenuBtn.addEventListener("click", async () => {
                const name = prompt("Item name");
                if (!name) return;
                const price = prompt("Price");
                if (price == null) return;
                const category = prompt("Category (breakfast/lunch/dinner/snacks)", "lunch");
                if (!category) return;
                const dietType = prompt("Diet type (diet/non-diet)", "diet");
                if (!dietType) return;

                const payload = {
                    name,
                    price,
                    image_url: "",
                    protein: 0,
                    carbs: 0,
                    fats: 0,
                    calories: 0,
                    category,
                    diet_type: dietType,
                    is_active: 0
                };

                const res = await fetch("/admin/menu-item", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });
                const out = await res.json().catch(() => ({}));
                if (!res.ok || !out.success) {
                    alert(out.error || "Failed to add item");
                    return;
                }
                await loadAdminMenuItems();
            });
        }
    }
});

