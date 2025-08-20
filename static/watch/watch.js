const socket = new WebSocket("wss://bf687d07959b.ngrok-free.app");

let marketData = {};

socket.onopen = () => {
  console.log("Connected to WebSocket");
  const subscription = {
    request: "subscribe",
    symbols: [
      "BAFL",
      "PAEL",
      "LUCK",
      "GHNI",
      "AGTL",
      "AGL",
      "ATRL",
      "BOP",
      "FATIMA",
      "FCL",
      "LOTCHEM",
      "INIL",
    ], // or whatever symbols you need
  };
  socket.send(JSON.stringify(subscription));
};

socket.onmessage = (event) => {
  const msg = JSON.parse(event.data);
    console.log("Recieved Data", msg);
    if (msg && msg.tick && msg.tick.symbol_code) {
      marketData[msg.tick.symbol_code] = msg.tick;
      updateTable(marketData);
    } else {
      console.warn("Tick data missing:", msg);
    }
};

socket.onerror = (err) => {
  console.error("WebSocket error:", err);
};

// function updateTable(dataObj) {
//   const tbody = document.querySelector(".watchlist-table tbody");
//   tbody.innerHTML = "";

//   Object.values(dataObj).forEach((row) => {
//     const changePercent =
//       (row.net_change / row.last_day_close_price) * 100 || 0;
//     const changeClass = changePercent >= 0 ? "green" : "red";

//     const tr = document.createElement("tr");
//     tr.innerHTML = `
//                 <td>${row.market_code}</td>
//                 <td class="watchlist-action-btns">
//                     <button class="watchlist-buy-btn" >Buy</button>
//                     <button class="watchlist-sell-btn">Sell</button>
//                 </td>
//                 <td>${row.symbol_code}</td>
//                 <td>${row.bid_volume.toLocaleString()}</td>
//                 <td>${row.bid_price}</td>
//                 <td>${row.ask_price}</td>
//                 <td>${row.ask_volume.toLocaleString()}</td>
//                 <td>Change</td>
//                 <td>${row.total_traded_volume.toLocaleString()}</td>
//                 <td>${row.high_price}</td>
//                 <td>${row.low_price}</td>
//                 <td class="mkt-range-column">
//                     <div class="mkt-range-wrapper">
//                         <div class="mkt-range"></div>
//                         <div class="mkt-marker"></div>
//                     </div>
//                     <div class="mkt-range-values">
//                         <p class="low-price">${row.low_price}</p>
//                         <p class="high-price">${row.high_price}</p>
//                     </div>
//                 </td>
//                 <td>${row.last_trade_price}</td>
//                 <td class="${changeClass}">${changePercent.toFixed(2)}%</td>
//                 <td>Upper Cap</td>
//                 <td>Lower Lock</td>
//                 <td>Close</td>
//                 <td>${row.open_price}</td>
//                 <td>${row.last_trade_volume}</td>
//                 <td>${row.last_day_close_price}</td>
//                 <td>${row.average_price.toLocaleString()}</td>
//                 <td>${row.total_trades.toLocaleString()}</td>
//                 <td>${row.timestamp}</td>
//                 <td>${row.symbol_state}</td>
//             `;
//     const high = parseFloat(row.high_price);
//     const low = parseFloat(row.low_price);
//     const close = parseFloat(row.last_trade_price);
//     let percent = ((close - low) / (high - low)) * 100;
//     percent = Math.max(0, Math.min(100, percent)); // clamp between 0-100%
//     const marker = document.getElementsByClassName("mkt-marker");
//     console.log(high, low ,marker)
//     // marker.style.left = `calc(${percent}% - 1px)`; // -1px to center marker

//     tbody.appendChild(tr);
//     // updateMarketRange(row, td);
//   });
// }
function updateTable(dataObj) {
    const tbody = document.querySelector(".watchlist-table tbody");
    tbody.innerHTML = "";
  
    Object.values(dataObj).forEach((row) => {
      const changePercent =
        (row.net_change / row.last_day_close_price) * 100 || 0;
      const changeClass = changePercent >= 0 ? "green" : "red";
  
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${row.market_code}</td>
        <td class="watchlist-action-btns">
            <button class="watchlist-buy-btn">Buy</button>
            <button class="watchlist-sell-btn">Sell</button>
        </td>
        <td>${row.symbol_code}</td>
        <td>${(row.bid_volume != null) ? row.bid_volume.toLocaleString() : 0 }</td>
        <td class="buyer-price-value">${(row.bid_price != null) ? row.bid_price : 0}</td>
        <td class="seller-price-value">${(row.ask_price != null) ? row.ask_price : 0}</td>
        <td>${(row.ask_volume != null) ? row.ask_volume.toLocaleString() : 0}</td>
        <td>Change</td>
        <td>${row.total_traded_volume.toLocaleString()}</td>
        <td>${(row.high_price != null) ? row.high_price : 0}</td>
        <td>${(row.low_price) ? row.low_price : 0}</td>
        <td class="mkt-range-column">
            <div class="mkt-range-wrapper">
                <div class="mkt-range"></div>
                <div class="mkt-marker"></div>
            </div>
            <div class="mkt-range-values">
                <p class="low-price">${(row.low_price) ? row.low_price : 0}</p>
                <p class="high-price">${(row.high_price != null) ? row.high_price : 0}</p>
            </div>
        </td>
        <td>${(row.last_trade_price != null) ? row.last_trade_price : 0}</td>
        <td class="${changeClass}">${changePercent.toFixed(2)}%</td>
        <td>Upper Cap</td>
        <td>Lower Lock</td>
        <td>Close</td>
        <td>${(row.open_price != null) ? row.open_price : 0}</td>
        <td>${(row.last_trade_volume != null) ? row.last_trade_volume : 0}</td>
        <td>${row.last_day_close_price}</td>
        <td>${row.average_price.toLocaleString()}</td>
        <td>${row.total_trades.toLocaleString()}</td>
        <td>${row.timestamp}</td>
        <td>${row.symbol_state}</td>
      `;
  
      // calculate percent position
      const high = parseFloat(row.high_price);
      const low = parseFloat(row.low_price);
      const close = parseFloat(row.last_trade_price);
      let percent = ((close - low) / (high - low)) * 100;
      percent = Math.max(0, Math.min(100, percent)); // clamp 0–100%
  
      // ✅ select marker inside this row only
      const marker = tr.querySelector(".mkt-marker");
      if (marker) {
        marker.style.left = `calc(${percent}% - 2px)`; // adjust offset
      }
  
      tbody.appendChild(tr);
    });
  }
  
function updateMarketRange(row, element) {
  console.log("inside update market");
  const high = parseFloat(row.high_price);
  const low = parseFloat(row.low_price);
  const close = parseFloat(row.last_trade_price);

  const wrapper = element.querySelector(".mkt-range-wrapper");
  const marker = wrapper.querySelector(".mkt-marker");
  // const highEl = element.querySelector(".high-price");
  // const lowEl = element.querySelector(".low-price");

  // Set high & low values
  // highEl.textContent = high;
  // lowEl.textContent = low;

  // Calculate percentage position of close price
  let percent = ((close - low) / (high - low)) * 100;
  percent = Math.max(0, Math.min(100, percent)); // clamp between 0-100%

  // Position the marker
  marker.style.left = `calc(${percent}% - 1px)`; // -1px to center marker
}

// // Example usage:
// document.querySelectorAll(".mkt-range-column").forEach((td, idx) => {
//     // Replace with your actual row data
//     const rowData = {
//         high_price: 200,
//         low_price: 100,
//         close_price: 160
//     };
//     updateMarketRange(rowData, td);
// });

const pnValue = document.getElementsByClassName("pn-value");
const pnIndexValue = document.getElementsByClassName("pn-index-value");
for (let el of pnValue) {
  // console.log(el.innerText);
  const value = parseFloat(el.innerText);

  if (value > 0) {
    el.classList.add("green");
    pnIndexValue[0].classList.add("green");
  } else if (value < 0) {
    el.classList.add("red");
    pnIndexValue[0].classList.add("red");
  }
}
const marketStatus = document.getElementById("market-status");
if (marketStatus) {
  const status = marketStatus.innerText;
  if (status === "OPEN") {
    marketStatus.classList.add("green");
  } else if (status === "CLOSED") {
    marketStatus.classList.add("red");
  }
}
const NavigationButtons = document.querySelectorAll(".watch-nav-btn");

NavigationButtons.forEach((btn) => {
  btn.addEventListener("click", () => {
    // Remove 'active' class from all buttons
    NavigationButtons.forEach((b) => b.classList.remove("active"));

    // Add 'active' class to the clicked button
    btn.classList.add("active");
  });
});

const navbar = document.getElementById("watchlist-navbar");

let mouseAtTop = false;

// Show navbar if mouse is near the top
document.addEventListener("mousemove", (e) => {
  if (e.clientY < 10) {
    // 50px from the top
    if (!mouseAtTop) {
      navbar.classList.add("show");
      mouseAtTop = true;
    }
  } else if (e.clientY > 50) {
    // 50px from the top
    if (mouseAtTop) {
      navbar.classList.remove("show");
      mouseAtTop = false;
    }
  }
});

// //Create WatchList
// document.querySelector(".create-watchlist-btn").addEventListener("click", async () => {
//     document.getElementById("createWatchlistModal").style.display = "block";

//     // Fetch stocks dynamically
//     const res = await fetch("http://localhost:8000/watch/api/stocks/symbols");
//     const stocks = await res.json();

//     const stocksSelect = document.getElementById("stocksSelect");
//     stocksSelect.innerHTML = "";
//     stocks.forEach(stock => {
//         const option = document.createElement("option");
//         option.value = stock.id;
//         option.textContent = stock.symbol;
//         stocksSelect.appendChild(option);
//     });
// });
// ===== CREATE WATCHLIST MODAL =====
document.addEventListener("DOMContentLoaded", () => {
  const createBtn = document.querySelector(".create-watchlist-btn");
  const modal = document.getElementById("createWatchlistModal");
  const closeBtn = document.getElementById("closeModal");

  const stocksSelect = document.getElementById("stocksSelect");
  const stockOptions = document.getElementById("stockOptions");
  const selectedTags = document.getElementById("selectedTags");
  const stockSearchInput = document.getElementById("stockSearch");

  // ======= Open modal & load stocks =======
  createBtn.addEventListener("click", async () => {
    modal.style.display = "block";

    // Fetch stocks
    const res = await fetch("http://localhost:8000/watch/api/stocks/symbols");
    const stocks = await res.json();

    // Clear previous
    stocksSelect.innerHTML = "";
    stockOptions.innerHTML = "";
    selectedTags.innerHTML = "";
    stockSearchInput.value = "";

    // Populate hidden select & dropdown
    stocks.forEach((stock) => {
      // hidden select
      const option = document.createElement("option");
      option.value = stock.id;
      option.textContent = stock.symbol;
      stocksSelect.appendChild(option);

      // dropdown div
      const div = document.createElement("div");
      div.textContent = stock.symbol;
      div.dataset.value = stock.id;

      div.addEventListener("click", () => {
        toggleStockSelection(stock.id, stock.symbol);
      });

      stockOptions.appendChild(div);
    });

    // Render tags initially
    renderSelectedTags();
  });

  // ======= Toggle stock selection =======
  function toggleStockSelection(id, symbol) {
    const option = Array.from(stocksSelect.options).find((o) => o.value == id);
    if (!option) return;

    option.selected = !option.selected;
    renderSelectedTags();
  }

  // ======= Render tags from selected <option>s =======
  function renderSelectedTags() {
    selectedTags.innerHTML = "";
    Array.from(stocksSelect.selectedOptions).forEach((opt) => {
      const tag = document.createElement("div");
      tag.className = "tag";
      tag.innerHTML = `${opt.textContent} <span>&times;</span>`;

      tag.querySelector("span").addEventListener("click", () => {
        opt.selected = false;
        renderSelectedTags();
      });

      selectedTags.appendChild(tag);
    });
  }

  // ======= Search functionality =======
  stockSearchInput.addEventListener("input", () => {
    const term = stockSearchInput.value.toLowerCase();
    const options = stockOptions.querySelectorAll("div");
    options.forEach((opt) => {
      opt.style.display = opt.textContent.toLowerCase().includes(term)
        ? "block"
        : "none";
    });
    stockOptions.style.display = term ? "block" : "none";
  });

  stockSearchInput.addEventListener(
    "focus",
    () => (stockOptions.style.display = "block")
  );
  stockSearchInput.addEventListener("blur", () => {
    setTimeout(() => (stockOptions.style.display = "none"), 150);
  });

  // ======= Close modal =======
  closeBtn.addEventListener("click", () => (modal.style.display = "none"));
  window.addEventListener("click", (e) => {
    if (e.target === modal) modal.style.display = "none";
  });
});
// Columns pills (unchanged from previous)
const columnsSelect = document.getElementById("columnsSelect");
const columnPills = document.getElementById("columnPills");
Array.from(columnsSelect.options).forEach((opt) => {
  const pill = document.createElement("div");
  pill.className = "pill";
  pill.textContent = opt.text;
  pill.addEventListener("click", () => {
    opt.selected = !opt.selected;
    pill.classList.toggle("active", opt.selected);
  });
  columnPills.appendChild(pill);
});

//Form Saved to Database
document.getElementById("closeModal").addEventListener("click", () => {
  document.getElementById("createWatchlistModal").style.display = "none";
});

document.getElementById("saveWatchlist").addEventListener("click", async () => {
  const profileName = document.getElementById("profileName").value;
  const stockOptions = Array.from(
    document.getElementById("stocksSelect").selectedOptions
  );
  const columnOptions = Array.from(
    document.getElementById("columnsSelect").selectedOptions
  );
  const isDefault = document.getElementById("isDefault").checked;

  const stocks = stockOptions.map((opt) => ({
    id: parseInt(opt.value),
    columns: columnOptions.map((c) => c.value),
  }));

  const payload = {
    watch_id: 1,
    profile_name: profileName,
    stocks: stocks,
    is_default: isDefault,
  };

  const res = await fetch("/watch/api/watchlist", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  const result = await res.json();
  if (result.success) {
    alert("Watchlist created!");
    document.getElementById("createWatchlistModal").style.display = "none";
    location.reload();
  } else {
    alert("Error: " + result.error);
  }
});

//my watchlists
document
  .querySelector(".my-watchlist-btn")
  .addEventListener("click", async () => {
    const dropdown = document.getElementById("watchProfilesDropdown");
    dropdown.innerHTML = ""; // clear old data

    // Toggle dropdown visibility
    dropdown.style.display =
      dropdown.style.display === "none" ? "block" : "none";

    if (dropdown.style.display === "block") {
      const res = await fetch("/watch/api/watchlist/profiles");
      const profiles = await res.json();

      dropdown.innerHTML = profiles
        .map((profile) => {
          return `
                    <div class="profiles_dropdown-item" data-profile-id="${profile.id}">
                        <span class="profile-name">${profile.profile_name}</span>
                        <i class="fa-solid fa-edit edit-icon" data-profile-id="${profile.id}"></i>
                    </div>
                `;
        })
        .join("");

      if (profiles.length === 0) {
        dropdown.innerHTML = "<div class='no-profiles'>No profiles found</div>";
      }
    }
  });

let availableStocks = []; // Will hold [{id, symbol}, ...]

document.addEventListener("DOMContentLoaded", async () => {
  // Load stocks from API once at page load
  await loadAvailableStocks();

  // ===== CREATE MODAL =====
  const createModal = document.getElementById("createWatchlistModal");
  const openCreateBtn = document.querySelector(".create-watchlist-btn");
  const closeCreateBtn = document.getElementById("closeModal");

  // Populate create form stocks
  populateStockSelect(document.getElementById("stocksSelect"));

  // Open create modal
  openCreateBtn.addEventListener("click", () => {
    createModal.style.display = "block";
  });

  // Close create modal
  closeCreateBtn.addEventListener("click", () => {
    createModal.style.display = "none";
  });

  // Close create modal by clicking outside
  window.addEventListener("click", (e) => {
    if (e.target === createModal) createModal.style.display = "none";
  });
});

// Fetch all available stocks (for both create & edit forms)
async function loadAvailableStocks() {
  try {
    const res = await fetch("http://localhost:8000/watch/api/stocks/symbols");
    availableStocks = await res.json();
  } catch (err) {
    console.error("Error loading stocks:", err);
  }
}

// Populate a given <select multiple> with stock symbols
function populateStockSelect(selectElement, selectedStockIds = []) {
  selectElement.innerHTML = "";
  availableStocks.forEach((stock) => {
    const option = document.createElement("option");
    option.value = stock.id;
    option.textContent = stock.symbol;
    if (selectedStockIds.includes(stock.id)) {
      option.selected = true;
    }
    selectElement.appendChild(option);
  });
}

// ===== EDIT MODAL =====
document.addEventListener("click", async (e) => {
  if (e.target.classList.contains("edit-icon")) {
    const profileId = e.target.dataset.profileId;

    // Fetch the profile details from backend
    const res = await fetch(`/watch/api/watchlist/profiles/${profileId}`);
    const profile = await res.json();

    // Populate edit form fields
    document.getElementById("editProfileName").value = profile.profile_name;
    document.getElementById("editProfileDefault").checked = profile.is_default;

    // Populate stock select with preselected stocks
    populateStockSelect(
      document.getElementById("editStocksSelect"),
      profile.stocks.map((s) => s.id) // assuming s.id exists
    );

    // Preselect columns
    const columnSelect = document.getElementById("editColumnsSelect");
    Array.from(columnSelect.options).forEach((option) => {
      option.selected = profile.columns.includes(option.value);
    });

    // Store profile ID for later use
    document.getElementById("editProfileModal").dataset.profileId = profileId;

    // Show edit modal
    document.getElementById("editProfileModal").style.display = "block";
  }
});

// Close edit modal
document.getElementById("cancelEditBtn").addEventListener("click", () => {
  document.getElementById("editProfileModal").style.display = "none";
});

// Save edited profile
document
  .getElementById("saveProfileBtn")
  .addEventListener("click", async () => {
    const modal = document.getElementById("editProfileModal");
    const profileId = modal.dataset.profileId;

    const selectedStockIds = Array.from(
      document.getElementById("editStocksSelect").selectedOptions
    ).map((option) => parseInt(option.value));

    const selectedColumns = Array.from(
      document.getElementById("editColumnsSelect").selectedOptions
    ).map((option) => option.value);

    const updatedProfile = {
      profile_name: document.getElementById("editProfileName").value.trim(),
      is_default: document.getElementById("editProfileDefault").checked,
      stocks: selectedStockIds, // array of integers
      columns: selectedColumns, // array of strings
    };

    console.log(updatedProfile);
    await fetch(`/watch/api/watchlist/profiles/${profileId}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(updatedProfile),
    });

    modal.style.display = "none";
    // location.reload();
  });

// Delete profile
document
  .getElementById("deleteProfileBtn")
  .addEventListener("click", async () => {
    const modal = document.getElementById("editProfileModal");
    const profileId = modal.dataset.profileId;

    if (confirm("Are you sure you want to delete this profile?")) {
      await fetch(`/watch/api/watchlist/profiles/${profileId}`, {
        method: "DELETE",
      });
      location.reload();
      modal.style.display = "none";
    }
  });



  const messageBtn = document.querySelector(".message-btn");
  const messageBox = document.querySelector(".message-box");

  messageBtn.addEventListener("click", () => {
    messageBox.classList.toggle("active");
  });


  new Sortable(document.getElementById("watch-header"), {
    animation: 150,
    onEnd: function (evt) {
      let oldIndex = evt.oldIndex;
      let newIndex = evt.newIndex;

      // For each row, move the cell
      document.querySelectorAll("#watch-body tr").forEach(row => {
        let cells = row.children;
        if (newIndex < oldIndex) {
          row.insertBefore(cells[oldIndex], cells[newIndex]);
        } else {
          row.insertBefore(cells[oldIndex], cells[newIndex].nextSibling);
        }
      });
    }
  });
  // Row reorder (still works)
  new Sortable(document.getElementById("watch-body"), {
    animation: 150
  });
//   document.addEventListener("DOMContentLoaded", () => {
//     const tableBody = document.getElementById("watch-table");
  
//     Sortable.create(tableBody, {
//       animation: 150,   // smooth animation
//       ghostClass: "sortable-ghost", // CSS class for dragged row
//       chosenClass: "sortable-chosen",
//       dragClass: "sortable-drag",
//     });
//   });