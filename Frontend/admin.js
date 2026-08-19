// admin.js
// ------------------------------------------------------
// Handles the admin login screen and dashboard on admin.html.
// Talks to the FastAPI backend's /admin/login and /admin/dashboard.
// ------------------------------------------------------

// Change this if your backend runs somewhere else
const API_BASE_URL = "http://127.0.0.1:8000";

let salesChart = null; // keeps a reference so we can redraw without duplicating charts


// ==========================================
// LOGIN
// ==========================================

async function attemptLogin() {

    const passcodeInput = document.getElementById("passcode-input");
    const errorText = document.getElementById("login-error");

    const passcode = passcodeInput.value;

    errorText.textContent = "";

    try {

        const response = await fetch(`${API_BASE_URL}/admin/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ passcode: passcode })
        });

        if (!response.ok) {
            errorText.textContent = "Incorrect passcode. Try again.";
            return;
        }

        const data = await response.json();

        // Store the token for this browser tab/session only.
        // sessionStorage clears automatically when the tab is closed —
        // safer than localStorage for something like an admin session.
        sessionStorage.setItem("adminToken", data.token);

        showDashboard();

    } catch (error) {
        console.error("Login request failed:", error);
        errorText.textContent =
            "Couldn't reach the server. Is the backend running?";
    }
}


function logoutAdmin() {
    sessionStorage.removeItem("adminToken");
    document.getElementById("dashboard").style.display = "none";
    document.getElementById("login-overlay").style.display = "flex";
    document.getElementById("passcode-input").value = "";
}


// ==========================================
// DASHBOARD
// ==========================================

function showDashboard() {
    document.getElementById("login-overlay").style.display = "none";
    document.getElementById("dashboard").style.display = "block";
    loadDashboard();
}


async function loadDashboard() {

    const token = sessionStorage.getItem("adminToken");

    if (!token) {
        // No token at all — show the login screen instead of trying the request
        document.getElementById("dashboard").style.display = "none";
        document.getElementById("login-overlay").style.display = "flex";
        return;
    }

    try {

        const response = await fetch(`${API_BASE_URL}/admin/dashboard`, {
            method: "GET",
            headers: {
                "X-Admin-Token": token
            }
        });

        if (response.status === 401) {
            // Token missing/expired/invalid — send them back to login
            alert("Your admin session has expired. Please log in again.");
            logoutAdmin();
            return;
        }

        if (!response.ok) {
            throw new Error("Server responded with an error");
        }

        const data = await response.json();
        console.log("Dashboard data received:", data);

        // Render each piece independently — if the chart fails for any
        // reason (e.g. Chart.js didn't load), the table should still show up.
        try {
            renderSalesChart(data.sales);
        } catch (chartError) {
            console.error("Failed to render sales chart:", chartError);
        }

        try {
            renderIngredientTable(data.ingredients);
            populateRestockDropdown(data.ingredients);
        } catch (tableError) {
            console.error("Failed to render ingredient table:", tableError);
        }

    } catch (error) {
        console.error("Failed to load dashboard:", error);
        alert("Couldn't load admin data. Is the backend running?");
    }
}


// ==========================================
// RENDER: SALES PIE CHART + STATS
// ==========================================

function renderSalesChart(sales) {

    document.getElementById("best-seller").textContent =
        sales.best_seller || "No sales yet";

    document.getElementById("total-coffees").textContent =
        sales.total_coffees_sold;

    document.getElementById("total-orders").textContent =
        sales.total_orders;

    const labels = Object.keys(sales.sales_by_coffee);
    const values = Object.values(sales.sales_by_coffee);

    const canvas = document.getElementById("sales-chart");

    if (typeof Chart === "undefined") {
        console.error(
            "Chart.js did not load — check your internet connection " +
            "or that the <script> tag for Chart.js in admin.html is reachable."
        );
        return;
    }

    // If a chart already exists (e.g. from a previous refresh), destroy it
    // first — otherwise Chart.js just draws on top of the old one.
    if (salesChart) {
        salesChart.destroy();
    }

    if (labels.length === 0) {
        // No sales yet — skip drawing an empty chart
        return;
    }

    salesChart = new Chart(canvas, {
        type: "pie",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                backgroundColor: [
                    "#3e2723",
                    "#6d4c41",
                    "#8d6e63",
                    "#a1887f",
                    "#bcaaa4",
                    "#d7ccc8"
                ]
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom"
                }
            }
        }
    });
}


// ==========================================
// RENDER: INGREDIENT TABLE
// ==========================================

function renderIngredientTable(ingredients) {

    const tableBody = document.getElementById("ingredient-table-body");
    tableBody.innerHTML = "";

    ingredients.forEach(ingredient => {

        // Show in liters/kg if the amount is 1000+ (ml/g), otherwise show as-is
        const displayAmount = (value) => {
            if (ingredient.unit === "ml" && value >= 1000) {
                return (value / 1000).toFixed(2) + " L";
            }
            if (ingredient.unit === "g" && value >= 1000) {
                return (value / 1000).toFixed(2) + " kg";
            }
            return value + " " + ingredient.unit;
        };

        tableBody.innerHTML += `
            <tr>
                <td>${ingredient.name}</td>
                <td>${displayAmount(ingredient.starting)}</td>
                <td>${displayAmount(ingredient.used)}</td>
                <td>${displayAmount(ingredient.remaining)}</td>
            </tr>
        `;
    });
}

function populateRestockDropdown(ingredients) {

    const select = document.getElementById("restock-ingredient-select");
    if (!select) return;

    select.innerHTML = "";

    ingredients.forEach(ingredient => {
        select.innerHTML += `
            <option value="${ingredient.id}">
                ${ingredient.name} (${ingredient.unit})
            </option>
        `;
    });
}


async function restockIngredient() {

    const token = sessionStorage.getItem("adminToken");
    const ingredientId = document.getElementById("restock-ingredient-select").value;
    const amount = Number(document.getElementById("restock-amount").value);
    const messageEl = document.getElementById("restock-message");

    messageEl.textContent = "";

    if (!amount || amount <= 0) {
        messageEl.textContent = "Enter a valid amount.";
        return;
    }

    try {

        const response = await fetch(
            `${API_BASE_URL}/admin/ingredients/${ingredientId}/restock`,
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Admin-Token": token
                },
                body: JSON.stringify({ amount: amount })
            }
        );

        if (response.status === 401) {
            alert("Your admin session has expired. Please log in again.");
            logoutAdmin();
            return;
        }

        if (!response.ok) {
            throw new Error("Restock request failed");
        }

        const result = await response.json();

        messageEl.textContent =
            `${result.name} restocked. New total: ${result.new_total} ${result.unit}`;

        document.getElementById("restock-amount").value = "";

        loadDashboard();

    } catch (error) {
        console.error("Restock failed:", error);
        messageEl.textContent = "Something went wrong. Try again.";
    }
}

// ==========================================
// ON PAGE LOAD
// ==========================================

// If we already have a token from earlier in this tab's session,
// skip straight to the dashboard instead of asking to log in again.
const existingToken = sessionStorage.getItem("adminToken");

if (existingToken) {
    showDashboard();
}