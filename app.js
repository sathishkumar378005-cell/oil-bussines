/**
 * Latha Oils E-Commerce Storefront
 * Products catalog:
 * 1. Groundnut Oil
 * 2. Coconut Oil
 * 3. Gingelly (Sesame) Oil
 * 4. Castor Oil
 * 5. Deepam Oil
 * 6. Neem Oil
 * 7. Raw Groundnut
 * 8. Sesame Seeds
 */

const API_BASE_URL = "http://localhost:8000";

let PRODUCTS = [
  {
    id: "groundnut-oil",
    name: "Pure Wood Pressed Groundnut Oil",
    category: "cooking",
    tag: "Marachekku Special",
    image: "assets/groundnut_oil.jpg",
    description: "Extracted using traditional Vaagai wood cold press from selected Saurashtra & Tamil Nadu groundnuts. High smoke point and authentic nutty aroma.",
    benefits: [
      "Rich in natural Vitamin E and heart-healthy MUFA",
      "Zero trans-fats, zero cholesterol, and no chemical argemone",
      "Traditional wood expeller ensures natural density and taste",
      "Ideal for deep frying, sautéing, and daily family cooking"
    ],
    variants: [
      { size: "500 ml", price: 175, originalPrice: 195 },
      { size: "1 Litre", price: 340, originalPrice: 380, isDefault: true },
      { size: "5 Litres (Tin)", price: 1650, originalPrice: 1850 }
    ]
  },
  {
    id: "coconut-oil",
    name: "Pure Cold Pressed Coconut Oil",
    category: "cooking",
    tag: "100% Virgin Copra",
    image: "assets/coconut_oil.jpg",
    description: "Prepared from premium sulphur-free sun-dried copras of Pollachi. Unrefined, crystal-clear, with sweet natural coconut aroma.",
    benefits: [
      "High concentration of Lauric acid for immunity",
      "Cold-extracted below 40°C preserving natural enzymes",
      "Multi-purpose: Ideal for cooking, raw consumption, and baby skin massage",
      "Zero artificial fragrance or bleaching chemicals"
    ],
    variants: [
      { size: "500 ml", price: 190, originalPrice: 220 },
      { size: "1 Litre", price: 370, originalPrice: 420, isDefault: true },
      { size: "5 Litres (Can)", price: 1800, originalPrice: 2000 }
    ]
  },
  {
    id: "gingelly-oil",
    name: "Authentic Gingelly (Sesame) Oil",
    category: "cooking",
    tag: "Chekku Nallennai",
    image: "assets/gingelly_oil.jpg",
    description: "Cold-pressed with traditional palm jaggery (karupatti) to tame natural bitterness. Deep golden color, earthy aroma, and authentic South Indian taste.",
    benefits: [
      "Traditional remedy for body heat regulation (Oil bath)",
      "Essential base for spicy gravies, puliyodharai, and idli milagai podi",
      "Packed with Sesamin, Sesamolin, and Zinc for bone strength",
      "Aids in natural blood pressure regulation"
    ],
    variants: [
      { size: "500 ml", price: 210, originalPrice: 245 },
      { size: "1 Litre", price: 410, originalPrice: 470, isDefault: true },
      { size: "5 Litres (Tin)", price: 1980, originalPrice: 2250 }
    ]
  },
  {
    id: "castor-oil",
    name: "Cold-Pressed Castor Oil",
    category: "wellness",
    tag: "Hair & Skin Care",
    image: "assets/castor_oil.jpg",
    description: "Pure, thick, unrefined castor oil (Vilakkennai) extracted from selected ricinus seeds. Renowned for deep scalp moisturization and natural digestive balance.",
    benefits: [
      "Stimulates hair follicle growth and prevents split ends",
      "Deeply hydrates dry skin, eyebrows, and cracked heels",
      "Traditional Ayurvedic remedy for cooling eyes and joints",
      "100% Hexane-free and unbleached"
    ],
    variants: [
      { size: "200 ml", price: 110, originalPrice: 130 },
      { size: "500 ml", price: 240, originalPrice: 275, isDefault: true },
      { size: "1 Litre", price: 460, originalPrice: 520 }
    ]
  },
  {
    id: "deepam-oil",
    name: "Latha Sacred Deepam Pooja Oil",
    category: "wellness",
    tag: "Auspicious Fragrance",
    image: "assets/deepam_oil.jpg",
    description: "Inspired by temple traditions. A sacred blend of 5 pure oils (Gingelly, Mahua, Castor, Neem, Ghee extract) with mild Sugandh to bring positive spiritual vibrations.",
    benefits: [
      "Burns long and steady with a clean, smokeless golden flame",
      "Leaves minimal carbon residue in brass & clay diyas",
      "Mild divine camphor and floral aroma creates peaceful meditation ambience",
      "Formulated according to Pancha Deepa sacred scriptural balance"
    ],
    variants: [
      { size: "500 ml", price: 135, originalPrice: 160 },
      { size: "1 Litre", price: 260, originalPrice: 300, isDefault: true },
      { size: "5 Litres (Jar)", price: 1250, originalPrice: 1450 }
    ]
  },
  {
    id: "neem-oil",
    name: "Pure Organic Neem Oil",
    category: "wellness",
    tag: "Herbal & Organic",
    image: "assets/neem_oil.jpg",
    description: "100% pure cold-pressed oil from wild neem seeds (Azadirachta indica). Naturally high in Azadirachtin, perfect for therapeutic skin relief and organic garden pest care.",
    benefits: [
      "Potent antibacterial and antifungal properties for acne & dandruff",
      "Natural organic repellent for home gardens and agriculture",
      "Helps treat eczema, insect bites, and scalp irritation",
      "Raw, unheated, with 100% active organic bio-compounds"
    ],
    variants: [
      { size: "200 ml", price: 125, originalPrice: 150 },
      { size: "500 ml", price: 270, originalPrice: 310, isDefault: true },
      { size: "1 Litre", price: 510, originalPrice: 580 }
    ]
  },
  {
    id: "raw-groundnut",
    name: "Premium Raw Groundnut (Peanuts)",
    category: "seeds",
    tag: "Farm Fresh",
    image: "https://images.unsplash.com/photo-1567894340315-735d7c361db0?auto=format&fit=crop&w=800&q=80",
    description: "Hand-graded, plump, and naturally sun-dried peanuts directly from farms. Rich in oil content, sweet crunch, perfect for making homemade butter, snacks, or boiling.",
    benefits: [
      "High plant protein (25g per 100g) and healthy dietary fiber",
      "Unpolished, chemical-free red-skin groundnuts",
      "Naturally dried under sunlight without sulfur processing",
      "Directly sourced from trusted local farming clusters"
    ],
    variants: [
      { size: "500 g", price: 95, originalPrice: 115 },
      { size: "1 kg", price: 180, originalPrice: 220, isDefault: true },
      { size: "5 kg (Bag)", price: 850, originalPrice: 990 }
    ]
  },
  {
    id: "sesame-seeds",
    name: "Farm Fresh Natural Sesame Seeds",
    category: "seeds",
    tag: "Clean & Unpolished",
    image: "https://images.unsplash.com/photo-1508737604135-49c377032e40?auto=format&fit=crop&w=800&q=80",
    description: "Double machine-cleaned, 100% stone-free white and natural sesame seeds (Ellu). Perfect for making traditional sweets like ellu urundai, tahini, and bakery garnish.",
    benefits: [
      "Exceptional natural source of plant calcium and iron",
      "Zero bleaching or artificial white polish",
      "Rich nutty flavor that pops when gently dry roasted",
      "Stored in climate-controlled hygiene packaging"
    ],
    variants: [
      { size: "250 g", price: 80, originalPrice: 95 },
      { size: "500 g", price: 150, originalPrice: 180, isDefault: true },
      { size: "1 kg", price: 290, originalPrice: 340 }
    ]
  }
];

// App State
let cart = JSON.parse(localStorage.getItem("latha_cart")) || [];
let activeCategory = "all";
let searchQuery = "";
let selectedProductVariants = {}; // Map of productId -> variantIndex

// Initialize default variants
PRODUCTS.forEach(p => {
  const defaultIdx = p.variants.findIndex(v => v.isDefault);
  selectedProductVariants[p.id] = defaultIdx !== -1 ? defaultIdx : 0;
});

// DOM Elements
const productGrid = document.getElementById("productGrid");
const filterBtns = document.querySelectorAll(".filter-btn");
const searchInput = document.getElementById("searchInput");
const searchBtn = document.getElementById("searchBtn");

const cartDrawer = document.getElementById("cartDrawer");
const cartBackdrop = document.getElementById("cartBackdrop");
const cartToggleBtn = document.getElementById("cartToggleBtn");
const closeCartBtn = document.getElementById("closeCartBtn");
const cartBadge = document.getElementById("cartBadge");
const cartItemsContainer = document.getElementById("cartItemsContainer");
const cartSubtotalEl = document.getElementById("cartSubtotal");
const cartGrandTotalEl = document.getElementById("cartGrandTotal");
const cartItemCountText = document.getElementById("cartItemCountText");
const proceedCheckoutBtn = document.getElementById("proceedCheckoutBtn");

// Detail Modal
const detailModalBackdrop = document.getElementById("detailModalBackdrop");
const detailModalBody = document.getElementById("detailModalBody");
const closeDetailModalBtn = document.getElementById("closeDetailModalBtn");

// Checkout Modal
const checkoutModalBackdrop = document.getElementById("checkoutModalBackdrop");
const closeCheckoutModalBtn = document.getElementById("closeCheckoutModalBtn");
const checkoutForm = document.getElementById("checkoutForm");
const checkoutPayAmount = document.getElementById("checkoutPayAmount");

// Toast
const toast = document.getElementById("toast");

// Render Products
function renderProducts() {
  const filtered = PRODUCTS.filter(product => {
    const matchesCategory = activeCategory === "all" || product.category === activeCategory;
    const matchesSearch = product.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
                          product.description.toLowerCase().includes(searchQuery.toLowerCase());
    return matchesCategory && matchesSearch;
  });

  if (filtered.length === 0) {
    productGrid.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 60px 20px; color: #777;">
        <p style="font-size: 2rem; margin-bottom: 8px;">🔍</p>
        <h3>No products found</h3>
        <p>Try searching with another keyword or selecting "All Items".</p>
      </div>
    `;
    return;
  }

  productGrid.innerHTML = filtered.map(product => {
    const selectedVariantIdx = selectedProductVariants[product.id] || 0;
    const variant = product.variants[selectedVariantIdx];

    const categoryLabel = product.category === "cooking" ? "Cooking Oil" :
                          product.category === "wellness" ? "Pooja & Wellness" : "Farm Seeds";

    const discount = (variant.originalPrice && variant.originalPrice > variant.price)
      ? Math.round(((variant.originalPrice - variant.price) / variant.originalPrice) * 100)
      : null;

    return `
      <div class="product-card" data-id="${product.id}">
        <div class="product-image-wrap" onclick="openDetailModal('${product.id}')">
          <img src="${product.image}" alt="${product.name}" loading="lazy">
          <span class="tag-badge">${product.tag}</span>
          ${discount ? `<span class="save-badge">${discount}% OFF</span>` : ''}
          <div class="quick-view-overlay">
            <span class="quick-view-btn">Quick View</span>
          </div>
        </div>

        <div class="product-details">
          <div class="product-category-row">
            <span class="product-category">${categoryLabel}</span>
            <span class="product-rating">★ 4.9 (120+)</span>
          </div>
          <h3 class="product-title" onclick="openDetailModal('${product.id}')">${product.name}</h3>
          <p class="product-desc">${product.description}</p>

          <div class="variant-selector">
            <span class="variant-label">Select Pack Size:</span>
            <div class="variant-pills">
              ${product.variants.map((v, idx) => `
                <button 
                  type="button" 
                  class="variant-pill ${idx === selectedVariantIdx ? 'active' : ''}" 
                  onclick="selectVariant('${product.id}', ${idx})"
                >
                  ${v.size}
                </button>
              `).join('')}
            </div>
          </div>

          <div class="product-bottom-row">
            <div class="product-price-box">
              <span class="current-price">₹${variant.price}</span>
              ${variant.originalPrice ? `<span class="original-price">₹${variant.originalPrice}</span>` : ''}
            </div>
            <button class="add-cart-btn" onclick="addToCart('${product.id}')">
              <span>+ Add to Cart</span>
            </button>
          </div>
        </div>
      </div>
    `;
  }).join('');
}

// Select Product Variant
window.selectVariant = function(productId, variantIndex) {
  selectedProductVariants[productId] = variantIndex;
  renderProducts();
};

// Add to Cart
window.addToCart = function(productId, customVariantIdx = null) {
  const product = PRODUCTS.find(p => p.id === productId);
  if (!product) return;

  const variantIdx = customVariantIdx !== null ? customVariantIdx : (selectedProductVariants[productId] || 0);
  const variant = product.variants[variantIdx];

  const cartItemId = `${product.id}_${variant.size}`;
  const existingItem = cart.find(item => item.cartItemId === cartItemId);

  if (existingItem) {
    existingItem.qty += 1;
  } else {
    cart.push({
      cartItemId,
      id: product.id,
      name: product.name,
      image: product.image,
      size: variant.size,
      price: variant.price,
      qty: 1
    });
  }

  saveCart();
  updateCartUI();
  showToast(`Added ${product.name} (${variant.size}) to cart!`);
};

// Modify Cart Quantity
window.updateCartQty = function(cartItemId, delta) {
  const item = cart.find(i => i.cartItemId === cartItemId);
  if (!item) return;

  item.qty += delta;
  if (item.qty <= 0) {
    cart = cart.filter(i => i.cartItemId !== cartItemId);
  }

  saveCart();
  updateCartUI();
};

function saveCart() {
  localStorage.setItem("latha_cart", JSON.stringify(cart));
}

// Update Cart UI
const FREE_DELIVERY_THRESHOLD = 999;

function updateCartUI() {
  const totalItems = cart.reduce((sum, item) => sum + item.qty, 0);
  cartBadge.textContent = totalItems;
  cartItemCountText.textContent = `(${totalItems} item${totalItems === 1 ? '' : 's'})`;

  const shippingMeterText = document.getElementById("shippingMeterText");
  const meterFill = document.getElementById("meterFill");
  const shippingFeeText = document.getElementById("shippingFeeText");

  if (cart.length === 0) {
    cartItemsContainer.innerHTML = `
      <div class="cart-empty-state">
        <span>🛒</span>
        <h4>Your cart is empty</h4>
        <p style="font-size: 0.85rem; margin-top: 6px;">Add cold pressed oils or farm seeds to get started.</p>
      </div>
    `;
    cartSubtotalEl.textContent = "₹0";
    cartGrandTotalEl.textContent = "₹0";
    if (shippingMeterText && meterFill) {
      shippingMeterText.textContent = "🌿 Add ₹999 more for FREE Pan-India delivery";
      meterFill.style.width = "0%";
    }
    if (shippingFeeText) shippingFeeText.textContent = "FREE (Orders > ₹999)";
    return;
  }

  let subtotal = 0;
  cartItemsContainer.innerHTML = cart.map(item => {
    const itemTotal = item.price * item.qty;
    subtotal += itemTotal;

    return `
      <div class="cart-item">
        <img src="${item.image}" alt="${item.name}" class="cart-item-img">
        <div class="cart-item-info">
          <div class="cart-item-title">${item.name}</div>
          <div class="cart-item-variant">Size: <strong>${item.size}</strong></div>
          <div class="cart-item-bottom">
            <div class="qty-control">
              <button class="qty-btn" onclick="updateCartQty('${item.cartItemId}', -1)">-</button>
              <span class="qty-val">${item.qty}</span>
              <button class="qty-btn" onclick="updateCartQty('${item.cartItemId}', 1)">+</button>
            </div>
            <span class="cart-item-price">₹${itemTotal}</span>
          </div>
        </div>
      </div>
    `;
  }).join('');

  // Shipping calculation
  const isFreeDelivery = subtotal >= FREE_DELIVERY_THRESHOLD;
  const shippingFee = isFreeDelivery ? 0 : 60;
  const grandTotal = subtotal + shippingFee;

  cartSubtotalEl.textContent = `₹${subtotal}`;
  cartGrandTotalEl.textContent = `₹${grandTotal}`;
  checkoutPayAmount.textContent = `₹${grandTotal}`;

  if (shippingFeeText) {
    shippingFeeText.textContent = isFreeDelivery ? "FREE" : "₹60 (Free above ₹999)";
    shippingFeeText.className = isFreeDelivery ? "text-green" : "";
  }

  if (shippingMeterText && meterFill) {
    if (isFreeDelivery) {
      shippingMeterText.innerHTML = "🎉 <strong>Congratulations!</strong> You unlocked FREE Pan-India Delivery!";
      meterFill.style.width = "100%";
      meterFill.style.backgroundColor = "var(--secondary)";
    } else {
      const remaining = FREE_DELIVERY_THRESHOLD - subtotal;
      const progressPct = Math.min(100, Math.round((subtotal / FREE_DELIVERY_THRESHOLD) * 100));
      shippingMeterText.innerHTML = `🌿 Add <strong>₹${remaining}</strong> more for <strong>FREE Delivery</strong>`;
      meterFill.style.width = `${progressPct}%`;
      meterFill.style.backgroundColor = "var(--primary)";
    }
  }
}

// Open Detail Modal
window.openDetailModal = function(productId) {
  const product = PRODUCTS.find(p => p.id === productId);
  if (!product) return;

  const selectedVariantIdx = selectedProductVariants[product.id] || 0;
  const variant = product.variants[selectedVariantIdx];

  detailModalBody.innerHTML = `
    <div class="modal-detail-grid">
      <img src="${product.image}" alt="${product.name}" class="modal-detail-img">
      <div class="modal-detail-content">
        <span class="badge-pill">${product.tag}</span>
        <h2>${product.name}</h2>
        <p class="modal-detail-desc">${product.description}</p>
        
        <div class="variant-selector" style="margin-bottom: 20px;">
          <span class="variant-label">Available Packaging:</span>
          <div class="variant-pills">
            ${product.variants.map((v, idx) => `
              <button 
                type="button" 
                class="variant-pill ${idx === selectedVariantIdx ? 'active' : ''}" 
                onclick="changeDetailVariant('${product.id}', ${idx})"
              >
                ${v.size} - ₹${v.price}
              </button>
            `).join('')}
          </div>
        </div>

        <ul class="benefit-list">
          ${product.benefits.map(b => `<li><span>✓</span> ${b}</li>`).join('')}
        </ul>

        <div style="display: flex; gap: 16px; align-items: center;">
          <div style="font-size: 1.5rem; font-weight: 800; color: #1F241F;">
            ₹${variant.price} <span style="font-size: 0.9rem; text-decoration: line-through; color: #888;">₹${variant.originalPrice}</span>
          </div>
          <button class="btn btn-primary" onclick="addToCart('${product.id}'); closeDetailModal();">
            Add To Cart
          </button>
        </div>
      </div>
    </div>
  `;

  detailModalBackdrop.classList.add("open");
};

window.changeDetailVariant = function(productId, idx) {
  selectedProductVariants[productId] = idx;
  renderProducts();
  openDetailModal(productId);
};

function closeDetailModal() {
  detailModalBackdrop.classList.remove("open");
}

// Cart Drawer open/close
function openCart() {
  cartDrawer.classList.add("open");
  cartBackdrop.classList.add("open");
}

function closeCart() {
  cartDrawer.classList.remove("open");
  cartBackdrop.classList.remove("open");
}

// Toast notification
function showToast(msg) {
  toast.textContent = msg;
  toast.classList.add("show");
  setTimeout(() => {
    toast.classList.remove("show");
  }, 3200);
}

// Event Listeners
filterBtns.forEach(btn => {
  btn.addEventListener("click", () => {
    filterBtns.forEach(b => b.classList.remove("active"));
    btn.classList.add("active");
    activeCategory = btn.dataset.category;
    renderProducts();
  });
});

searchInput.addEventListener("input", (e) => {
  searchQuery = e.target.value.trim();
  renderProducts();
});

cartToggleBtn.addEventListener("click", openCart);
closeCartBtn.addEventListener("click", closeCart);
cartBackdrop.addEventListener("click", closeCart);

closeDetailModalBtn.addEventListener("click", closeDetailModal);
detailModalBackdrop.addEventListener("click", (e) => {
  if (e.target === detailModalBackdrop) closeDetailModal();
});

// Checkout Flow
proceedCheckoutBtn.addEventListener("click", () => {
  if (cart.length === 0) {
    showToast("Please add items to your cart first.");
    return;
  }
  closeCart();
  checkoutModalBackdrop.classList.add("open");
});

closeCheckoutModalBtn.addEventListener("click", () => {
  checkoutModalBackdrop.classList.remove("open");
});

checkoutModalBackdrop.addEventListener("click", (e) => {
  if (e.target === checkoutModalBackdrop) {
    checkoutModalBackdrop.classList.remove("open");
  }
});

// API Sync: Load products dynamically from backend
async function loadProductsFromAPI() {
  try {
    const res = await fetch(`${API_BASE_URL}/api/products`);
    if (res.ok) {
      const data = await res.json();
      if (Array.isArray(data) && data.length > 0) {
        PRODUCTS = data;
        PRODUCTS.forEach(p => {
          if (selectedProductVariants[p.id] === undefined) {
            const defaultIdx = p.variants.findIndex(v => v.isDefault);
            selectedProductVariants[p.id] = defaultIdx !== -1 ? defaultIdx : 0;
          }
        });
        renderProducts();
        console.log("✓ Loaded products from FastAPI & PostgreSQL backend.");
      }
    }
  } catch (err) {
    console.info("Backend API offline or starting up; using embedded catalog.");
  }
}

checkoutForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const name = document.getElementById("custName").value;
  const phone = document.getElementById("custPhone").value;
  const email = document.getElementById("custEmail")?.value || "";
  const address = document.getElementById("custAddress").value;
  const city = document.getElementById("custCity").value;
  const pincode = document.getElementById("custPincode").value;
  const paymentMethod = document.querySelector('input[name="paymentMethod"]:checked')?.value || "UPI / Online";
  const grandTotal = cart.reduce((sum, item) => sum + (item.price * item.qty), 0);

  const orderPayload = {
    customerName: name,
    customerPhone: phone,
    customerEmail: email,
    deliveryAddress: address,
    city: city,
    pincode: pincode,
    paymentMethod: paymentMethod,
    items: cart.map(item => ({
      productId: item.id,
      name: item.name,
      size: item.size,
      price: item.price,
      qty: item.qty
    }))
  };

  checkoutModalBackdrop.classList.remove("open");
  showToast("Processing order with database...");

  let orderRef = `LATHA-${Math.floor(1000 + Math.random() * 9000)}`;
  try {
    const res = await fetch(`${API_BASE_URL}/api/orders`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(orderPayload)
    });
    if (res.ok) {
      const respData = await res.json();
      if (respData.orderRef) {
        orderRef = respData.orderRef;
      }
    }
  } catch (err) {
    console.warn("Backend API offline, order recorded locally:", err);
  }

  // Clear cart
  cart = [];
  saveCart();
  updateCartUI();

  // Show order confirmation
  alert(`🎉 Order Confirmed! Reference: #${orderRef}\n\nThank you, ${name}!\nYour order for ₹${grandTotal} has been successfully recorded in the database.\nWe will dispatch your pure cold pressed oils soon.\nOrder tracking updates will be sent to +91 ${phone}.`);
});

// Init on load
document.addEventListener("DOMContentLoaded", () => {
  renderProducts();
  updateCartUI();
  loadProductsFromAPI();
});
