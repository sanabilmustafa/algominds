if (!window.f4ListenerAdded) {
    window.f4ListenerAdded = true;
    document.addEventListener("keydown", (event) => {
      if (event.key === "F4") {
        event.preventDefault();
        console.log("F4 key pressed, toggling modal");
        const buySellForm = document.querySelector(".buy-sell-main");
        const buyBtn = document.querySelector(".section")
        const submitBuy = document.getElementById("submitBtn")
        console.log(buySellForm)
        buySellForm.style.display = 
          (buySellForm.style.display === "block") ? "none" : "block";
        buyBtn.classList.remove("sell-selected")
        buyBtn.classList.add("buy-selected")
        submitBuy.classList.remove("sell")
        submitBuy.classList.add("buy")
        submitBuy.textContent = "BUY"
      }
      if (event.key === "Escape") {
        const buySellForm = document.querySelector(".buy-sell-main");
        buySellForm.style.display = "none";
      }
    });
  }
  
if (!window.f5ListenerAdded) {
    window.f5ListenerAdded = true;
    document.addEventListener("keydown", (event) => {
      if (event.key === "F5") {
        event.preventDefault();
        console.log("F5 key pressed, toggling modal");
        const buySellForm = document.querySelector(".buy-sell-main");
        const sellBtn = document.querySelector(".section")
        const submitSell = document.getElementById("submitBtn")
        console.log(buySellForm)
        buySellForm.style.display = 
          (buySellForm.style.display === "block") ? "none" : "block";
        sellBtn.classList.remove("buy-selected")
        sellBtn.classList.add("sell-selected")
        submitSell.classList.remove("buy") 
        submitSell.classList.add("sell")
        submitSell.textContent = "SELL"
      }
      if (event.key === "Escape") {
        const buySellForm = document.querySelector(".buy-sell-main");
        buySellForm.style.display = "none";
      }
    });
  }
  