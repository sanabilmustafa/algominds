const socket = new WebSocket("wss://bf687d07959b.ngrok-free.app");

// const socket = new WebSocket("wss://localhost:8765");
const output = document.getElementById("output");
const screenerBody = document.getElementById("screenerBody");
const thead = document.querySelector("#stockTable thead");
const tableRows = {};

let selectedProfileId = null;
let lastSubscription = null;
let selectedTickKeys = [];
let selectedIndicatorKeys = [];

function formatColumnName(key) {
  return key.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
}

// 1️⃣ Setup the <thead> with both tick + indicator columns
function setSelectedColumns(tickKeys, indicatorKeys) {
  selectedTickKeys = tickKeys || [];
  selectedIndicatorKeys = indicatorKeys || [];

  thead.innerHTML = "";
  const tr = document.createElement("tr");

  const symbolTh = document.createElement("th");
  symbolTh.textContent = "Symbol";
  tr.appendChild(symbolTh);

  selectedTickKeys.forEach(key => {
    const th = document.createElement("th");
    th.dataset.col = key;
    th.textContent = formatColumnName(key);
    tr.appendChild(th);
  });

  selectedIndicatorKeys.forEach(key => {
    const th = document.createElement("th");
    th.dataset.col = key;
    th.textContent = formatColumnName(key);
    tr.appendChild(th);
  });

  thead.appendChild(tr);
}

function updateTableRow(data) {
  const { symbol, indicators, tick = {} } = data;
  if (!symbol) return;

  let entry = tableRows[symbol];
  let row, lastValues;

  if (!entry) {
    row = document.createElement("tr");

    const img = document.createElement("img");
    img.src = `/static/assets/stocks/${symbol}.png`;
    img.className = "stock-logo";
    
    const symbolTd = document.createElement("td");
    symbolTd.classList.add("symbol-column")
    symbolTd.appendChild(img);
    symbolTd.appendChild(document.createTextNode(`${symbol}`));
    row.appendChild(symbolTd);

    selectedTickKeys.forEach(key => {
      const td = document.createElement("td");
      td.dataset.col = key;
      td.textContent = tick[key] ?? "-";
      row.appendChild(td);
    });

    selectedIndicatorKeys.forEach(key => {
      const td = document.createElement("td");
      td.dataset.col = key;
      td.textContent = indicators?.[key] ?? "-";
      row.appendChild(td);
    });

    screenerBody.appendChild(row);
    lastValues = {};
    tableRows[symbol] = { row, lastValues };
  } else {
    row = entry.row;
    lastValues = entry.lastValues || {};
  }

  const cells = row.querySelectorAll("td");
  let index = 1;

  selectedTickKeys.forEach(key => {
    const newVal = tick[key];
    const td = cells[index++];
    animateCellChange(td, key, newVal, lastValues);
  });

  selectedIndicatorKeys.forEach(key => {
    const newVal = indicators?.[key];
    const td = cells[index++];
    animateCellChange(td, key, newVal, lastValues);
  });

  tableRows[symbol] = { row, lastValues };
}

async function fetchProfileSubscription(profileId) {
  try {
    const res = await fetch(`http://localhost:8000/screener/api/profile-subscription-data/${profileId}`);
    if (!res.ok) throw new Error("Failed to fetch subscription data");
    return await res.json();
  } catch (err) {
    output.textContent += "❌ Error fetching profile subscription: " + err.message + "\n";
    return null;
  }
}

async function sendSubscription(profileId) {
  const data = await fetchProfileSubscription(profileId);
  if (!data) return;

  const { indicators = [], selected_columns = [], symbols = [] } = data;
  const tickColumns = selected_columns.filter(col => col !== "symbol");

  if (lastSubscription) {
    const unsubscribe = {
      request: "unsubscribe",
      symbols: lastSubscription.symbols,
      indicators: lastSubscription.indicators,
    };
    socket.send(JSON.stringify(unsubscribe));
  }

  screenerBody.innerHTML = "";
  Object.keys(tableRows).forEach(k => delete tableRows[k]);

  setSelectedColumns(tickColumns, indicators);

  console.log(indicators)
  const subscription = {
    request: "subscribe",
    symbols: symbols,
    indicators: indicators,
  };
  console.log("the testing for subscription is", subscription)
  socket.send(JSON.stringify(subscription));
  lastSubscription = subscription;
}

socket.onopen = () => {
  output.textContent = "✅ Connected to server.\n";
  if (selectedProfileId) {
    sendSubscription(selectedProfileId);
  }
};

socket.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log("Data", data)
  const currentSymbols = lastSubscription?.symbols || [];

  if (!currentSymbols.includes(data.symbol)) {
    // console.log(⏩ Ignoring data for ${data.symbol}, not in current profile.);
    return;
  }

  // console.log("📩 Received data:", data);
  updateTableRow(data);
};

socket.onerror = (err) => {
  output.textContent += "❌ WebSocket error: " + err.message + "\n";
};

socket.onclose = () => {
  output.textContent += "🔌 WebSocket closed.\n";
};

async function onProfileSelected(profileId) {
  selectedProfileId = profileId;

  // 1️⃣ Update URL without reload
  const newUrl = `/screener/${profileId}`;
  window.history.pushState({ profileId }, '', newUrl);

  output.textContent = "";

  // 2️⃣ Send WebSocket subscription
  if (socket.readyState === WebSocket.OPEN) {
    await sendSubscription(profileId);
  } else {
    socket.onopen = async () => {
      await sendSubscription(profileId);
    };
  }
}

// 3️⃣ Handle dropdown click
listContainer.addEventListener("click", (e) => {
  const profileItem = e.target.closest(".profiles_dropdown-item");
  if (profileItem) {
    const profileId = parseInt(profileItem.dataset.profileId);
    selectedProfileId = profileId;
    renderProfiles(allProfiles);
    filterStocksByProfile(profileId);
    dropdown.classList.add("hidden");
    onProfileSelected(profileId);
  }
});

// 4️⃣ On page load, load profile if URL has profileId
document.addEventListener("DOMContentLoaded", () => {
  if (selectedProfileIdFromServer) {
    onProfileSelected(selectedProfileIdFromServer);
  }
});
// lighting effect
function animateCellChange(td, key, newVal, lastValues = {}) {
  const oldVal = lastValues[key];
  const parsedNewVal = parseFloat(newVal);

  td.textContent = newVal ?? "-";

  if (!isFinite(parsedNewVal) || parsedNewVal === oldVal) return;

  const up = parsedNewVal > oldVal;
  const down = parsedNewVal < oldVal;

  td.classList.remove("flash-up", "flash-down");
  void td.offsetWidth;

  if (up) {
    td.classList.add("flash-up");
    td.innerHTML = `<i class="fa-solid fa-arrow-trend-up"></i> ${parsedNewVal} `;
  } else if (down) {
    td.classList.add("flash-down");
    td.innerHTML = `<i class="fa-solid fa-arrow-trend-down"></i> ${parsedNewVal}`  ;
  }

  lastValues[key] = parsedNewVal;

  setTimeout(() => {
    td.classList.remove("flash-up", "flash-down");
    td.textContent = parsedNewVal;
  }, 2000);
}