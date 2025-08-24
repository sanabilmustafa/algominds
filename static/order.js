// document.addEventListener("DOMContentLoaded", function () {
//     // Chart width setup
//     const chartwidth = document.getElementById("chartPlaceholder").clientWidth;
//     console.log("Chart width:", chartwidth);
  
//     new TradingView.widget({
//       container: "chartContainer",
//       locale: "en",
//       library_path: "/charting_library/",
//       datafeed: new Datafeeds.UDFCompatibleDatafeed("/chart"),
//       symbol: "CPHL",
//       interval: "1D",
//       fullscreen: false,
//       width: chartwidth,
//       height: 300,
//       debug: true,
//     });
  
    // Market type buttons
    document.querySelectorAll(".section-select .market-type .market-input").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll(".section-select .market-type .market-input").forEach((btn) =>
          btn.classList.remove("active")
        );
        button.classList.add("active");
      });
    });
  
    // Order type buttons
    document.querySelectorAll(".section-select .order-type button").forEach((button) => {
      button.addEventListener("click", () => {
        document.querySelectorAll(".section-select .order-type button").forEach((btn) =>
          btn.classList.remove("active")
        );
        button.classList.add("active");
      });
    });
  
    // -------------------
    const marketButtons = document.querySelectorAll(".market-input");
    const marketCodeInput = document.getElementById("market_code");
  
    marketButtons.forEach((button) => {
      button.addEventListener("click", () => {
        marketButtons.forEach((btn) => btn.classList.remove("active"));
        button.classList.add("active");
        marketCodeInput.value = button.getAttribute("data-code");
      });
    });
  
    // -------------------
    const orderButtons = document.querySelectorAll(".order-input");
    const orderBtnInput = document.getElementById("order_type");
  
    orderButtons.forEach((button) => {
      button.addEventListener("click", () => {
        orderButtons.forEach((btn) => btn.classList.remove("active"));
        button.classList.add("active");
        orderBtnInput.value = button.getAttribute("data-code");
      });
    });
  
    // -------------------
    const sideButtons = document.querySelectorAll(".side-btn");
    const sidebtnInput = document.getElementById("side");
  
    sideButtons.forEach((button) => {
      button.addEventListener("click", () => {
        sideButtons.forEach((btn) => btn.classList.remove("active"));
        button.classList.add("active");
        sidebtnInput.value = button.getAttribute("data-code");
      });
    });
  
    // Action buy/sell
    function action_buy(type) {
      const section = document.querySelector(".section");
      const submitBtn = document.getElementById("submitBtn");
  
      if (type === "SELL") {
        section.classList.remove("buy-selected");
        section.classList.add("sell-selected");
        submitBtn.textContent = "SELL";
        submitBtn.classList.add("sell");
      } else {
        section.classList.remove("sell-selected");
        section.classList.add("buy-selected");
        submitBtn.textContent = "BUY";
        submitBtn.classList.remove("sell");
      }
    }
    window.action_buy = action_buy; // expose globally if called from HTML
  
    // Form submission
    document.querySelector("form").addEventListener("submit", function (e) {
      e.preventDefault();
      const formData = new FormData(this);
      console.log("Form Data:");
      for (let [key, value] of formData.entries()) {
        console.log(`${key}: ${value}`);
      }
      this.submit();
    });
  
    // Order type fields toggle
    const buttons = document.querySelectorAll(".order-input");
    const discVolume = document.getElementById("discVolume");
    const limitPrice = document.getElementById("limitPrice");
  
    function updateFields(orderType) {
      if (orderType === "3") {
        discVolume.disabled = false;
        limitPrice.disabled = false;
        discVolume.classList.remove("disabled-input");
        limitPrice.classList.remove("disabled-input");
      } else {
        discVolume.disabled = true;
        limitPrice.disabled = true;
        discVolume.classList.add("disabled-input");
        limitPrice.classList.add("disabled-input");
      }
    }
  
    buttons.forEach((btn) => {
      btn.addEventListener("click", function () {
        const orderType = this.getAttribute("data-code");
        updateFields(orderType);
      });
    });
  
    updateFields("1"); // default
  
    // OUTSTANDING LOGS
    const outstandingLogs = JSON.parse(document.getElementById("logs-data").textContent);
    console.log("Outstanding Logs", outstandingLogs);
  
    const outstandingOrders = outstandingLogs?.data?.orders || {};
    const outstandingHeaders = outstandingOrders.headers || [];
    const outstandingRows = outstandingOrders.data || [];
  
    let outstandingTableHTML = "<table><thead><tr>";
    outstandingHeaders.forEach((header) => {
      outstandingTableHTML += `<th>${header}</th>`;
    });
    outstandingTableHTML += "</tr></thead><tbody>";
  
    if (!outstandingRows || outstandingRows.length === 0) {
      for (let i = 0; i < 3; i++) {
        outstandingTableHTML += "<tr>";
        outstandingHeaders.forEach(() => {
          outstandingTableHTML += "<td>null</td>";
        });
        outstandingTableHTML += "</tr>";
      }
    } else {
      outstandingRows.forEach((row) => {
        outstandingTableHTML += "<tr>";
        outstandingHeaders.forEach((_, index) => {
          outstandingTableHTML += `<td>${row[index] !== null ? row[index] : "null"}</td>`;
        });
        outstandingTableHTML += "</tr>";
      });
    }
    outstandingTableHTML += "</tbody></table>";
    document.querySelector(".outstanding_logs_table").innerHTML = outstandingTableHTML;
  
    // ACTIVITY LOGS
    const activityLogs = JSON.parse(document.getElementById("activity-logs-data").textContent);
    console.log("Activity Logs:", activityLogs);
  
    const activityData = activityLogs?.data || {};
    const activityHeaders = activityData.headers || [];
    const activityRows = activityData.data || [];
  
    let activityTableHTML = "<table><thead><tr>";
    activityHeaders.forEach((header) => {
      activityTableHTML += `<th>${header}</th>`;
    });
    activityTableHTML += "</tr></thead><tbody>";
  
    if (!activityRows || activityRows.length === 0) {
      for (let i = 0; i < 3; i++) {
        activityTableHTML += "<tr>";
        activityHeaders.forEach(() => {
          activityTableHTML += "<td>null</td>";
        });
        activityTableHTML += "</tr>";
      }
    } else {
      activityRows.forEach((row) => {
        activityTableHTML += "<tr>";
        activityHeaders.forEach((_, index) => {
          activityTableHTML += `<td>${row[index] !== null ? row[index] : "null"}</td>`;
        });
        activityTableHTML += "</tr>";
      });
    }
    activityTableHTML += "</tbody></table>";
    document.querySelector(".activity_logs_table").innerHTML = activityTableHTML;
  
    // Toggle display function
    window.showLogs = function (type) {
      const outSection = document.getElementById("outstanding_logs");
      const actSection = document.getElementById("activity_logs");
  
      document.querySelectorAll(".log-buttons button").forEach((btn) => btn.classList.remove("active"));
      if (type === "outstanding") {
        outSection.style.display = "block";
        actSection.style.display = "none";
        document.querySelector(".log-buttons button:nth-child(1)").classList.add("active");
      } else {
        outSection.style.display = "none";
        actSection.style.display = "block";
        document.querySelector(".log-buttons button:nth-child(2)").classList.add("active");
      }
    };
  
    // Sidebar collapse
    const collapseIcon = document.querySelector(".collapse-icon");
    const uncollapseIcon = document.querySelector(".uncollapse-icon");
    const sideBar = document.querySelector(".side-bar");
  
    collapseIcon.addEventListener("click", function () {
      sideBar.classList.add("active");
    });
    uncollapseIcon.addEventListener("click", function () {
      sideBar.classList.remove("active");
    });
    window.addEventListener("click", function (e) {
      if (!sideBar.contains(e.target) && !collapseIcon.contains(e.target)) {
        sideBar.classList.remove("active");
      }
    });
  