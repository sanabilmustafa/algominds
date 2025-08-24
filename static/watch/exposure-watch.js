// OPENING THE ACCOUNT DETAILS MODAL WITH BUTTONS
document.addEventListener("DOMContentLoaded", () => {
  const accountDetailsForm = document.querySelector(".exposure-watch-container");
  const accountDetailsBtn = document.getElementById("account_details_button");
  const closeModalBtn = document.getElementById("close_modal_button");
  if (accountDetailsBtn && accountDetailsForm) {
    accountDetailsBtn.addEventListener("click", () => {
      accountDetailsForm.style.display = "block";
    });
    closeModalBtn.addEventListener("click", () => {
      accountDetailsForm.style.display = "none";
    });

  }
});

// OPENING THE ACCOUNT DETAILS MODAL WITH THE F2 KEY
if (!window.f2ListenerAdded) {
  window.f2ListenerAdded = true;
  document.addEventListener("keydown", (event) => {
    if (event.key === "F2") {
      event.preventDefault();
      console.log("F2 key pressed, toggling modal");
      const accountDetailsForm = document.querySelector(".exposure-watch-container");
      accountDetailsForm.style.display = 
        (accountDetailsForm.style.display === "block") ? "none" : "block";
    }
    if (event.key === "Escape") {
      const accountDetailsForm = document.querySelector(".exposure-watch-container");
      accountDetailsForm.style.display = "none";
    }
  });
}


