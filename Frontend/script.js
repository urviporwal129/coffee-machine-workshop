// Change this if your backend runs somewhere else
const API_BASE_URL = "http://127.0.0.1:8000";

// Get cart from localStorage
let cart = JSON.parse(localStorage.getItem("cart")) || [];


// ==========================================
// STOCK SHORTAGE POPUP
// ==========================================

function showStockErrorModal(message) {
    const modal = document.getElementById("stock-error-modal");
    const messageEl = document.getElementById("stock-error-message");

    if (!modal || !messageEl) {
        // Fallback in case this page doesn't have the modal markup
        alert(message);
        return;
    }

    messageEl.textContent = message;
    modal.style.display = "flex";
}

function closeStockErrorModal() {
    const modal = document.getElementById("stock-error-modal");
    if (modal) {
        modal.style.display = "none";
    }
}


// ADD TO CART
async function addToCart(coffeeId, name, price, button) {

    const card = button.parentElement;

    const quantity = Number(
        card.querySelector(".quant").value
    );

    const existingItem = cart.find(
        item => item.id === coffeeId
    );

    // How many of this coffee the cart would contain in total
    // if this add goes through (existing amount + what's being added now)
    const totalRequestedQuantity =
        (existingItem ? existingItem.quantity : 0) + quantity;

    // Ask the backend if there's enough of every ingredient
    // BEFORE we add anything to the cart.
    button.disabled = true;

    try {

        const response = await fetch(`${API_BASE_URL}/check-stock`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                coffee_id: coffeeId,
                quantity: totalRequestedQuantity
            })
        });

        if (!response.ok) {
            throw new Error("Stock check request failed");
        }

        const result = await response.json();

        if (!result.available) {
            showStockErrorModal(
                `Sorry! We don't have enough ${result.insufficient_ingredients.join(", ")} ` +
                `to make ${totalRequestedQuantity} × ${name} right now.`
            );
            return; // stop here — do NOT add to cart
        }

    } catch (error) {
        console.error("Stock check failed:", error);
        showStockErrorModal(
            "Couldn't check ingredient stock. " +
            "Make sure the backend server is running, then try again."
        );
        return;

    } finally {
        button.disabled = false;
    }

    // Stock is sufficient — proceed exactly as before
    if (existingItem) {

        existingItem.quantity += quantity;

    } else {

        cart.push({
            id: coffeeId,
            name: name,
            price: price,
            quantity: quantity
        });

    }

    localStorage.setItem(
        "cart",
        JSON.stringify(cart)
    );

    showCartPopup(name + " added to cart!");
}


// DISPLAY CART
function displayCart() {

    const cartItems =
        document.getElementById("cart-items");

    const totalElement =
        document.getElementById("total");

    // If we're not on cart.html, stop
    if (!cartItems || !totalElement) {
        return;
    }

    cartItems.innerHTML = "";

    let total = 0;

    cart.forEach((item, index) => {

        const itemTotal =
            item.price * item.quantity;

        total += itemTotal;

        cartItems.innerHTML += `
        
        <div class="cart-item">

            <h3>${item.name}</h3>

            <p>₹${item.price}</p>

            <label>Quantity:</label>

            <select onchange="updateQuantity(${index}, this.value)">

                <option value="1"
                    ${item.quantity == 1 ? "selected" : ""}>
                    1
                </option>

                <option value="2"
                    ${item.quantity == 2 ? "selected" : ""}>
                    2
                </option>

                <option value="3"
                    ${item.quantity == 3 ? "selected" : ""}>
                    3
                </option>

                <option value="4"
                    ${item.quantity == 4 ? "selected" : ""}>
                    4
                </option>

                <option value="5"
                    ${item.quantity == 5 ? "selected" : ""}>
                    5
                </option>

            </select>

            <strong>₹${itemTotal}</strong>

            <button onclick="removeItem(${index})">
                Remove
            </button>

        </div>

        `;
    });

    totalElement.textContent = total;
}


// UPDATE QUANTITY
function updateQuantity(index, quantity) {

    cart[index].quantity = Number(quantity);

    localStorage.setItem(
        "cart",
        JSON.stringify(cart)
    );

    displayCart();
}


// REMOVE ITEM
function removeItem(index) {

    cart.splice(index, 1);

    localStorage.setItem(
        "cart",
        JSON.stringify(cart)
    );

    displayCart();
}

function proceedToPayment() {

    if (cart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    window.location.href = "payment.html";
}

let savedCart = localStorage.getItem("cart");

if (savedCart) {
    cart = JSON.parse(savedCart);
}

if (document.getElementById("cart-items")) {
    displayCart();
}

// Re-sync cart with localStorage if this page is restored from the
// browser's back/forward cache (bfcache) instead of freshly loaded —
// otherwise cart.html can keep showing stale items after payment clears it.
window.addEventListener("pageshow", function (event) {
    if (event.persisted) {
        cart = JSON.parse(localStorage.getItem("cart")) || [];
        displayCart();
    }
});


// ==========================================
// PAYMENT PAGE - ORDER SUMMARY
// ==========================================

function displayPaymentOrder() {

    const billItems = document.getElementById("bill-items");
    const totalElement = document.getElementById("total-price");

    // If we are not on payment.html, do nothing
    if (!billItems || !totalElement) {
        return;
    }

    // Get the latest cart data (fetched straight from the cart page's storage)
    const paymentCart =
        JSON.parse(localStorage.getItem("cart")) || [];

    billItems.innerHTML = "";

    let total = 0;

    // Empty cart
    if (paymentCart.length === 0) {

        billItems.innerHTML = `
            <p class="empty-cart">
                Your cart is empty.
            </p>
        `;

        totalElement.textContent = "0";

        return;
    }


    // Display each selected item
    paymentCart.forEach(function (item) {

        const itemTotal =
            item.price * item.quantity;

        total += itemTotal;

        billItems.innerHTML += `

            <div class="bill-item">

                <span class="item-name">
                    ${item.name} × ${item.quantity}
                </span>

                <span class="item-price">
                    ₹${itemTotal}
                </span>

            </div>

        `;
    });


    // Display total
    totalElement.textContent = total;
}
function completePayment() {

    const paymentCart =
        JSON.parse(localStorage.getItem("cart")) || [];

    if (paymentCart.length === 0) {
        alert("Your cart is empty!");
        return;
    }

    const modal = document.getElementById("payment-modal");

    if (modal) {
        modal.style.display = "flex";
        modal.classList.add("show");
    }
}


function closeModal() {

    const modal = document.getElementById("payment-modal");

    if (modal) {
        modal.classList.remove("show");
        modal.style.display = "none";
    }

    localStorage.removeItem("cart");
    cart = [];

    window.location.href = "index.html";
}


// Run on every page load — harmless no-op if bill-items isn't on the page
displayPaymentOrder();

function showCartPopup(message) {
    const popup = document.createElement("div");

    popup.className = "cart-popup";
    popup.textContent = message;

    document.body.appendChild(popup);

    setTimeout(() => {
        popup.classList.add("show");
    }, 10);

    setTimeout(() => {
        popup.classList.remove("show");

        setTimeout(() => {
            popup.remove();
        }, 300);
    }, 1800);
}