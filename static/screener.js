const statusEl = document.getElementById("status");
const tableBody = document.getElementById("screenerBody");

// Store rows by symbol so we can update them
let allSymbols = [];
let selectedSymbols = new Set();

//   ------------------------------------------------------------------------------------------


document.addEventListener('DOMContentLoaded', function () {
    const rangeInput = document.getElementById('indicator-period');
    const rangeValue = document.getElementById('indicator-period-value');

    rangeInput.addEventListener('input', function () {
        rangeValue.textContent = rangeInput.value;
    });
});
//   ------------------------------------------------------------------------------------------
document.addEventListener('DOMContentLoaded', function () {
    const stockSelect = document.getElementById('select-stocks');
    if (stockSelect) {
        // Temporarily enable to initialize Select2
        stockSelect.removeAttribute('disabled');

        $(stockSelect).select2({
            placeholder: "Select stocks",
            width: '90%'
        });
    }
});
document.addEventListener('DOMContentLoaded', function () {
    const stockSelect = document.getElementById('edit-profile-stock-select');
    if (stockSelect) {
        // Temporarily enable to initialize Select2
        stockSelect.removeAttribute('disabled');

        $(stockSelect).select2({
            placeholder: "Select stocks",
            width: '90%'
        });
    }
});
document.addEventListener('DOMContentLoaded', function () {
    const columnSelect = document.getElementById('selected-columns');
    if (columnSelect) {
        // Temporarily enable the select so Select2 can initialize
        columnSelect.removeAttribute('disabled');

        // Initialize Select2
        $(columnSelect).select2({
            placeholder: "Select columns",
            width: '90%'
        });
    }
});
document.addEventListener('DOMContentLoaded', function () {
    const inidicatorSelect = document.getElementById('indicator-name');
    if (inidicatorSelect) {
        // Temporarily enable the select so Select2 can initialize
        inidicatorSelect.removeAttribute('disabled');

        // Initialize Select2
        $(inidicatorSelect).select2({
            placeholder: "Select Indicator",
            width: '80%'
        });

    }
});
document.addEventListener('DOMContentLoaded', function () {
    const indicatorIntervalSelect = document.getElementById('indicator-interval');
    if (indicatorIntervalSelect) {
        // Temporarily enable the select so Select2 can initialize
        indicatorIntervalSelect.removeAttribute('disabled');

        // Initialize Select2
        $(indicatorIntervalSelect).select2({
            placeholder: "Select interval",
            width: '80%'
        });
    }
});


// Symbol dropdown logic
document
    .getElementById("symbol-button")
    .addEventListener("click", async function () {
        const dropdown = document.getElementById("symbol-dropdown");
        const listContainer = document.getElementById("symbol-list");
        const searchInput = document.getElementById("symbol-search");

        // dropdown.classList.toggle("hidden");

        try {
            const response = await fetch(
                "http://localhost:8000/screener/api/stocks/symbols"
            );
            if (!response.ok) throw new Error("Failed to fetch symbols");

            allSymbols = await response.json();
            if (!Array.isArray(allSymbols)) {
                throw new Error("Expected an array of symbols");
            }
            console.log(allSymbols);
            dropdown.dataset.symbols = JSON.stringify(allSymbols);

            const renderList = (filteredSymbols) => {
                listContainer.innerHTML = filteredSymbols
                    .map((symbol) => {
                        const isSelected = selectedSymbols.has(symbol);
                        return `<div class="dropdown-item ${isSelected ? "selected" : ""
                            }" 
                    data-symbol="${symbol}">
                    ${symbol} ${isSelected ? "✓" : ""}
                    </div>`;
                    })
                    .join("");
            };

            renderList(allSymbols);

            // Handle symbol selection
            listContainer.addEventListener("click", (e) => {
                const symbolItem = e.target.closest(".dropdown-item");
                if (symbolItem) {
                    const symbol = symbolItem.dataset.symbol;
                    if (selectedSymbols.has(symbol)) {
                        selectedSymbols.delete(symbol);
                    } else {
                        selectedSymbols.add(symbol);
                    }
                    renderList(allSymbols);
                    filterTable();
                }
            });

            searchInput.addEventListener("input", () => {
                const searchTerm = searchInput.value.toLowerCase();
                const filtered = allSymbols.filter((symbol) =>
                    symbol.toLowerCase().includes(searchTerm)
                );
                renderList(filtered);
            });
        } catch (error) {
            console.error("Error loading symbols:", error);
            listContainer.innerHTML = `<div class="dropdown-item error">Error loading symbols</div>`;
        }
    });

// Add clear filter functionality
document
    .getElementById("clear-filter")
    .addEventListener("click", function () {
        // Clear selected symbols
        selectedSymbols.clear();

        // Update the dropdown display
        const dropdownItems = document.querySelectorAll(".dropdown-item");
        dropdownItems.forEach((item) => {
            item.classList.remove("selected");
            if (item.querySelector("span")) {
                item.querySelector("span").remove();
            }
        });

        // Show all rows
        const rows = tableBody.querySelectorAll("tr");
        rows.forEach((row) => {
            row.style.display = "";
        });

        // Optional: Close the symbol dropdown if open
        document.getElementById("symbol-dropdown").classList.add("hidden");
    });

// Update this part in your symbol dropdown code:
const renderList = (filteredSymbols) => {
    listContainer.innerHTML = filteredSymbols
        .map((symbol) => {
            const isSelected = selectedSymbols.has(symbol);
            return `<div class="dropdown-item ${isSelected ? "selected" : ""}" 
        data-symbol="${symbol}">
        ${symbol} ${isSelected ? "<span>✓</span>" : ""}
        </div>`;
        })
        .join("");
};

// Sector dropdown logic
let selectedSectors = new Set();
let allSectors = [];
document
    .getElementById("sector-button")
    .addEventListener("click", async function () {
        const dropdown = document.getElementById("sector-dropdown");
        const listContainer = document.getElementById("sector-list");
        const searchInput = document.getElementById("sector-search");

        // dropdown.classList.toggle("hidden");

        if (allSectors.length === 0) {
            try {
                const response = await fetch(
                    "http://localhost:8000/screener/api/stocks/sectors"
                );

                if (!response.ok) throw new Error("Failed to fetch sectors");

                allSectors = await response.json();
                if (!Array.isArray(allSectors)) {
                    throw new Error("Expected an array of sectors");
                }
                console.log("MY SECTORS");
                console.log(allSectors);

                const renderList = (filteredSectors) => {
                    listContainer.innerHTML = filteredSectors
                        .map((sector) => {
                            const isSelected = selectedSectors.has(sector);
                            return `<div class="dropdown-item ${isSelected ? "selected" : ""
                                }" 
              data-sector="${sector}">
              ${sector} ${isSelected ? "✓" : ""}
              </div>`;
                        })
                        .join("");
                };

                renderList(allSectors);

                // Handle sector selection
                listContainer.addEventListener("click", (e) => {
                    const sectorItem = e.target.closest(".dropdown-item");
                    if (sectorItem) {
                        const sector = sectorItem.dataset.sector;
                        if (selectedSectors.has(sector)) {
                            selectedSectors.delete(sector);
                        } else {
                            selectedSectors.add(sector);
                        }
                        renderList(allSectors);
                        console.log("Selected sectors:", selectedSectors);
                        filterTableSector(); // You'll want to modify your filterTable() to also consider sectors
                    }
                });

                searchInput.addEventListener("input", () => {
                    const searchTerm = searchInput.value.toLowerCase();
                    const filtered = allSectors.filter((sector) =>
                        sector.toLowerCase().includes(searchTerm)
                    );
                    renderList(filtered);
                });
            } catch (error) {
                console.error("Error loading sectors:", error);
                listContainer.innerHTML = `<div class="dropdown-item error">Error loading sectors</div>`;
            }
        }
    });

// Clear Sector Filters
document
    .getElementById("clear-sector-filter")
    .addEventListener("click", () => {
        selectedSectors.clear();
        filterTable();
    });

function filterTableSector() {
    const rows = tableBody.querySelectorAll("tr");
    rows.forEach((row) => {
        const symbol = row.cells[0].textContent;
        if (selectedSectors.size === 0 || selectedSectors.has(symbol)) {
            row.style.display = "";
        } else {
            row.style.display = "none";
        }
    });
}




//PROFILE JSAVASCRIPT
let selectedProfile = null;
let profilesLoaded = false;
let allProfiles = []; // Global variable to store profiles

const dropdown = document.getElementById("profiles-dropdown");
const listContainer = document.getElementById("profiles-list");
const button = document.getElementById("profiles-button");

const renderProfiles = (profilesList) => {
    allProfiles = profilesList; // Store it globally

    listContainer.innerHTML = profilesList
        .map((profile) => {
            const isSelected = selectedProfile === profile.id;
            return `
        <div class="profiles_dropdown-item ${isSelected ? "selected" : ""}" data-profile-id="${profile.id}">
          ${profile.name}
          <i class="fa-solid fa-edit edit-icon" data-profile-id="${profile.id}"></i>
          
        </div>`;
        })
        .join("");

    document.querySelectorAll(".edit-icon").forEach((icon) => {
        icon.addEventListener("click", (event) => {
            console.log("Edit icon clicked");
            const profileId = event.target.dataset.profileId;
            openProfileModal(profileId);
        });
    });
};



const fetchAndRenderProfiles = async () => {
    try {
        const response = await fetch("http://localhost:8000/screener/api/get_profiles");
        if (!response.ok) throw new Error("Failed to fetch profiles");

        const profiles = await response.json();
        if (!Array.isArray(profiles)) throw new Error("Expected an array of profiles");

        renderProfiles(profiles);

        listContainer.addEventListener("click", (e) => {
            const profileItem = e.target.closest(".profiles_dropdown-item");
            if (profileItem) {
                const profileId = parseInt(profileItem.dataset.profileId);
                selectedProfile = profileId;
                renderProfiles(profiles);
                filterStocksByProfile(profileId);
                dropdown.classList.add("hidden");
            }
        });

        profilesLoaded = true;
    } catch (err) {
        console.error("Error loading profiles:", err.message);
    }
};

button.addEventListener("click", () => {
    // dropdown.classList.toggle("hidden");

    if (!profilesLoaded) {
        fetchAndRenderProfiles();
    }
});
document.addEventListener("click", (event) => {
    const dropdownToggles = document.querySelectorAll("[data-dropdown-toggle]");
    // console.log(dropdownToggles)

    dropdownToggles.forEach((button) => {
        const dropdown = document.querySelector(button.dataset.dropdownToggle);

        // If clicked button, toggle dropdown
        if (button.contains(event.target)) {
            dropdown.classList.toggle("hidden");
            // if (!dropdown.dataset.loaded) {
            //     fetchAndRenderProfiles(); // Call your loading logic
            //     dropdown.dataset.loaded = "true"; // Prevent reload
            // }
        } 
        // If clicked outside button & dropdown, hide it
        else if (!dropdown.contains(event.target)) {
            dropdown.classList.add("hidden");
        }
    });
});


async function filterStocksByProfile(profileId) {
    try {
        const response = await fetch(`http://localhost:8000/screener/api/get_profile_stocks/${profileId}`);
        if (!response.ok) throw new Error("Failed to fetch profile stocks");

        const stocks = await response.json();
        const symbolRowMap = {};
        profileSymbolsSet = new Set(stocks);
        Object.keys(symbolRowMap).forEach(symbol => {
            const row = symbolRowMap[symbol];
            if (profileSymbolsSet.has(symbol)) {
                row.style.display = ""; // Show
            } else {
                row.style.display = "none"; // Hide
            }
        });

        console.log(`Loaded ${profileSymbolsSet.size} symbols for profile ${profileId}`);
    }catch (error) {
        console.error("Error fetching profile stocks:", error.message);
    }
}

//PROFILE ADDED BY CLIENT CODE 
document.addEventListener("DOMContentLoaded", function () {
    const addProfileButton = document.getElementById("profile-add-button-dropdown");
    const profileFormContainer = document.getElementById("profile-add-button-form");
    const stockSelect = document.getElementById("select-stocks");
    const profileNameInput = document.getElementById("profile-name");
    const addProfileForm = document.getElementById("add-profile-form");
    let selectedStocks = [];

    // Toggle form visibility
    addProfileButton.addEventListener("click", function () {
        profileFormContainer.classList.toggle("show");
    });

    // Close form
    document.getElementById("close-profile-form").addEventListener("click", function () {
        profileFormContainer.classList.remove("show");
    });

    async function fetchStockSymbols() {
        try {
            const response = await fetch("http://127.0.0.1:8000/watch/api/stocks/symbols");
            if (!response.ok) throw new Error("Failed to fetch stock symbols");

            const stockSelect = document.getElementById("select-stocks");
            if (!stockSelect) {
                console.error("Element with ID 'select-stocks' not found.");
                return;
            }

            const symbols = await response.json();
            symbols.forEach(symbol => {
                const option = document.createElement("option");
                option.value = symbol;
                option.textContent = symbol;
                option.classList.add("stock-option");
                stockSelect.appendChild(option);
            });
            // console.log("the stocks are", symbols)
        } catch (error) {
            console.error("Error loading symbols:", error);
        }
    }


    // Toggle selection of stock option with a tick
    function toggleStockSelection(stock) {
        const stockIndex = selectedStocks.indexOf(stock);

        if (stockIndex === -1) {
            // If stock is not selected, add it to selectedStocks
            selectedStocks.push(stock);
        } else {
            // If stock is already selected, remove it from selectedStocks
            selectedStocks.splice(stockIndex, 1);
        }

        updateSelectedStocksDisplay();
    }
    // Update the display of selected stocks
    function updateSelectedStocksDisplay() {
        const selectedStockList = document.getElementById("selected-stock-list");
        selectedStockList.innerHTML = ''; // Clear previous selections

        if (selectedStocks.length > 0) {
            selectedStocks.forEach(stock => {
                const stockElement = document.createElement("span");
                stockElement.textContent = stock;
                stockElement.classList.add("selected-stock");
                selectedStockList.appendChild(stockElement);
            });
        } else {
            selectedStockList.textContent = "None";
        }
    }
    function updateSelectedColumnsDisplay() {
        const selectElement = document.getElementById("selected-columns");
        const selectedColumnList = document.getElementById("selected-column-list");
        selectedColumnList.innerHTML = ''; // Clear existing list

        const selectedOptions = Array.from(selectElement.options)
            .filter(option => option.selected);

        if (selectedOptions.length > 0) {
            selectedOptions.forEach(option => {
                const columnElement = document.createElement("span");
                columnElement.textContent = option.textContent;
                columnElement.classList.add("selected-stock"); // reuse styling
                selectedColumnList.appendChild(columnElement);
            });
        } else {
            selectedColumnList.textContent = "None";
        }
    }

    // Use 'input' or 'click' instead of 'change' for better UX in <select multiple>
    document.getElementById("selected-columns").addEventListener("click", updateSelectedColumnsDisplay);

    document.getElementById("selected-columns").addEventListener("mousedown", function (e) {
        e.preventDefault();
        const option = e.target;
        if (option.tagName === 'OPTION') {
            option.selected = !option.selected;
            updateSelectedColumnsDisplay();
        }
    });

    // Stock selection click event
    document.addEventListener("DOMContentLoaded", () => {
        const stockSelect = document.getElementById("stockSelect");

        if (stockSelect) {
            stockSelect.addEventListener("click", function (event) {
                const target = event.target;

                if (target.tagName === 'OPTION') {
                    const stock = target.value;

                    if (selectedStocks.includes(stock)) {
                        target.classList.remove("selected");
                    } else {
                        target.classList.add("selected");
                    }

                    toggleStockSelection(stock);
                }
            });
        } else {
            console.error("Element with ID 'stockSelect' not found.");
        }
    });

    // document.addEventListener("DOMContentLoaded", function () {
        // Submit profile
        addProfileForm.addEventListener("submit", async function (event) {
            event.preventDefault();
            const form = button.closest('form');
            const isDefault = document.getElementById("is-default").checked;
            const selectedColumns = Array.from(document.getElementById("selected-columns").selectedOptions).map(option => option.value);
            const stockSelect = Array.from(document.querySelectorAll('.stock-select')).flatMap(select =>
                Array.from(select.selectedOptions).map(option => option.value)
              ).filter(Boolean);
            event.preventDefault();

            console.log("Selected stocks:", stockSelect);
            const profileName = profileNameInput.value;
            const data = {
                profile_name: profileName,
                stocks: stockSelect,
                is_default: isDefault,
                selected_columns: selectedColumns,
                indicators: selectedIndicators

            };
            console.log("Submitting profile data:", data);

            try {
                const response = await fetch("http://localhost:8000/screener/api/create_profile", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify(data)
                });

                const result = await response.json();
                if (response.ok) {
                    alert(result.message);
                    profileFormContainer.classList.remove("show");
                    addProfileForm.reset(); // optional: clear form after success    
                } else {
                    console.log("Server Error:", result.error);
                    alert(result.error);
                }
            } catch (error) {
                console.error("Error creating profile:", error);
                alert("Failed to create profile.");
            }
        });

        // Fetch stock symbols when the page loads
        fetchStockSymbols();
    });


// })


// Global variables
const modal = document.getElementById("profileModal");
const modalName = document.getElementById("modalProfileName");
const stockSelect = document.getElementById("edit-profile-stock-select");
const closeButton = document.querySelector(".close-button");

let selectedProfileEdit; // Track profile being edited
let allStocksCache = []; // Cache all stocks
let selectedStocks = []; // Store currently selected stocks

// Update the display of selected stocks
function updateSelectedStocksDisplay() {
    const list = document.getElementById("edit-profile-selected-stock-list");
    list.innerHTML = '';
    if (selectedStocks.length > 0) {
        selectedStocks.forEach(stock => {
            const item = document.createElement("span");
            item.textContent = stock;
            item.classList.add("selected-stock");
            list.appendChild(item);
        });
    } else {
        list.textContent = "None";
    }
}
function updateEditSelectedColumnsDisplay() {
    const selectElement = document.getElementById("edit_selected_columns");
    const selectedColumnList = document.getElementById("edit-selected-column-list");
    selectedColumnList.innerHTML = ''; // Clear old

    const selectedOptions = Array.from(selectElement.selectedOptions);

    if (selectedOptions.length > 0) {
        selectedOptions.forEach(option => {
            const columnElement = document.createElement("span");
            columnElement.textContent = option.textContent;
            columnElement.classList.add("selected-stock"); // reuse styling
            selectedColumnList.appendChild(columnElement);
        });
    } else {
        selectedColumnList.textContent = "None";
    }
}
function loadProfileForEdit(profileData) {
    // Set profile name
    modalName.value = profileData.profile_name;

    // Set selected stocks and display them
    selectedStocks = profileData.stocks || [];
    updateSelectedStocksDisplay();

    // Set selected columns
    const columnSelect = document.getElementById("edit_selected_columns");
    const selectedColumnList = document.getElementById("edit-selected-column-list");

    const selectedColumns = profileData.selected_columns || [];

    // 1. Deselect all options first
    Array.from(columnSelect.options).forEach(option => {
        option.selected = false;
    });

    // 2. Select the ones that match profileData
    selectedColumns.forEach(col => {
        const match = Array.from(columnSelect.options).find(opt => opt.value === col);
        if (match) {
            match.selected = true;
        }
    });

    // 3. Refresh the visual preview
    updateEditSelectedColumnsDisplay();
}

document.getElementById("edit_selected_columns").addEventListener("mousedown", function (e) {
    e.preventDefault();
    const option = e.target;
    if (option.tagName === 'OPTION') {
        option.selected = !option.selected;
        updateEditSelectedColumnsDisplay();
    }
});

// Fetch and populate all stock symbols
async function fetchStockSymbols() {
    try {
        const response = await fetch("http://localhost:8000/screener/api/stocks/symbols");
        if (!response.ok) throw new Error("Failed to fetch stock symbols");

        const symbols = await response.json();
        allStocksCache = symbols; // Cache it

        symbols.forEach(symbol => {
            const option = document.createElement("option");
            option.value = symbol;
            option.textContent = symbol;
            option.classList.add("stock-option");
            stockSelect.appendChild(option);
        });
    } catch (error) {
        console.error("Error loading symbols:", error);
    }
}// Open modal with selected profile data
// Open modal with selected profile data
const openProfileModal = async (profileId) => {
    const profile = allProfiles.find(p => p.id == profileId);
    if (!profile) return;

    modal.dataset.profileId = profileId;
    selectedProfileEdit = profileId;

    // Set name
    modalName.textContent = profile.name;
    document.getElementById("edit-profile-name").value = profile.name;
    document.getElementById("edit-is-default").checked = !!profile.is_default;

    document.getElementById("edit-profile-name").disabled = true;
    stockSelect.disabled = true;

    document.getElementById("saveProfileButton").style.display = "none";
    document.getElementById("editProfileButton").style.display = "inline-block";

    try {
        const res = await fetch(`http://localhost:8000/screener/api/get_profile_stocks/${profileId}`);
        selectedStocks = await res.json(); // Update global selectedStocks

        stockSelect.innerHTML = ""; // Clear old options

        const selectedGroup = document.createElement("optgroup");
        selectedGroup.label = "✓ Selected Stocks";

        selectedStocks.forEach(stock => {
            const option = document.createElement("option");
            option.value = stock;
            option.textContent = stock;
            option.selected = true;
            selectedGroup.appendChild(option);
        });

        stockSelect.appendChild(selectedGroup);
        updateSelectedStocksDisplay();
    } catch (error) {
        console.error("Error loading selected stocks:", error);
    }

    // ✅ New block to load previously selected columns & indicators
    try {
        const metaRes = await fetch(`http://localhost:8000/screener/api/get_profile_meta/${profileId}`);
        const metaData = await metaRes.json();

        // Columns
        const columnSelect = document.getElementById("edit_selected_columns");
        Array.from(columnSelect.options).forEach(option => {
            option.selected = metaData.selected_columns.includes(option.value);
        });
        updateEditSelectedColumnsDisplay();

        // Indicators
        selectedEditIndicators = metaData.indicators || [];
        renderEditIndicators();
    } catch (err) {
        console.error("Error fetching profile metadata:", err);
    }

    modal.classList.remove("hidden");
};

// Toggle selection of stock
function toggleStockSelection(stock) {
    const index = selectedStocks.indexOf(stock);
    if (index === -1) {
        selectedStocks.push(stock);
    } else {
        selectedStocks.splice(index, 1);
    }
    updateSelectedStocksDisplay();
}

// Handle click on select to toggle stock
stockSelect.addEventListener("click", function (e) {
    const option = e.target;
    if (option.tagName === 'OPTION') {
        const stock = option.value;
        if (selectedStocks.includes(stock)) {
            option.classList.remove("selected");
        } else {
            option.classList.add("selected");
        }
        toggleStockSelection(stock);
    }
});
// Enable edit mode
document.getElementById("editProfileButton").addEventListener("click", async () => {
    document.getElementById("edit-profile-name").disabled = false;
    stockSelect.disabled = false;
    document.getElementById("edit_selected_columns").disabled = false;

    document.getElementById("saveProfileButton").style.display = "inline-block";
    document.getElementById("editProfileButton").style.display = "none";

    try {
        // Fetch profile stocks
        const res = await fetch(`http://localhost:8000/screener/api/get_profile_stocks/${selectedProfileEdit}`);
        selectedStocks = await res.json();
        const selectedSet = new Set(selectedStocks);

        stockSelect.innerHTML = "";

        const selectedGroup = document.createElement("optgroup");
        selectedGroup.label = "✓ Selected Stocks";
        selectedStocks.forEach(stock => {
            const option = document.createElement("option");
            option.value = stock;
            option.textContent = stock;
            option.selected = true;
            selectedGroup.appendChild(option);
        });

        const remainingGroup = document.createElement("optgroup");
        remainingGroup.label = "All PSX Stocks";
        allStocksCache.forEach(stock => {
            if (!selectedSet.has(stock)) {
                const option = document.createElement("option");
                option.value = stock;
                option.textContent = stock;
                remainingGroup.appendChild(option);
            }
        });

        stockSelect.appendChild(selectedGroup);
        stockSelect.appendChild(remainingGroup);
        updateSelectedStocksDisplay();

        // ✅ Fetch existing selected columns (optional, based on how you're storing them)
        const colRes = await fetch(`http://localhost:8000/screener/api/get_profile_columns/${selectedProfileEdit}`);
        const existingCols = await colRes.json();
        const columnSelect = document.getElementById("edit_selected_columns");
        Array.from(columnSelect.options).forEach(option => {
            option.selected = existingCols.includes(option.value);
        });
        updateEditSelectedColumnsDisplay();

    } catch (error) {
        console.error("Error entering edit mode:", error);
    }
});

// Save profile
document.getElementById("saveProfileButton").addEventListener("click", async () => {
    const profileId = selectedProfileEdit;
    const profileName = document.getElementById("edit-profile-name").value;
    const isDefault = document.getElementById("edit-is-default").checked;

    const selectedColumnOptions = document.getElementById('edit_selected_columns').selectedOptions;
    const selectedColumns = Array.from(selectedColumnOptions).map(opt => opt.value);

    const data = {
        profile_name: profileName,
        stocks: selectedStocks,
        is_default: isDefault,
        selected_columns: selectedColumns,
        indicators: selectedEditIndicators   // ✅ Add this!
    };
    console.log("the updated data", data.selected_columns)
    console.log(data)
    try {
        const res = await fetch(`http://localhost:8000/screener/api/update_profile/${profileId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data)
        });

        const result = await res.json();

        if (res.ok) {
            alert("Profile updated successfully!");
            location.reload();
        } else {
            alert(result.error || "Error updating profile");
        }

    } catch (error) {
        console.error("Error updating profile:", error);
        alert("Failed to update profile.");
    }
});


// Delete profile
document.getElementById("deleteProfileButton").addEventListener("click", async () => {
    const confirmed = confirm("Are you sure you want to delete this profile?");
    if (!confirmed) return;

    const profileId = selectedProfileEdit;

    try {
        const res = await fetch(`http://localhost:8000/screener/api/delete_profile/${profileId}`, {
            method: "DELETE"
        });

        if (res.ok) {
            alert("Profile deleted successfully.");
            location.reload();
        } else {
            const error = await res.json();
            alert("Error deleting profile: " + (error.error || "Unknown error"));
        }

    } catch (error) {
        console.error("Failed to delete profile:", error);
        alert("An unexpected error occurred.");
    }
});

// Close modal
closeButton.addEventListener("click", () => {
    modal.classList.add("hidden");
});

// Initial fetch of stock symbols
fetchStockSymbols();


let selectedIndicators = [];

function renderSelectedIndicators() {
    const container = document.getElementById("indicator-tags");
    container.innerHTML = "";

    if (selectedIndicators.length === 0) {
        container.textContent = "None";
        return;
    }

    selectedIndicators.forEach((indicator) => {
        const span = document.createElement("span");
        span.classList.add("indicator-tag");
        span.textContent = indicator;
        container.appendChild(span);
    });
}






//indicators
document.getElementById("add-indicator").addEventListener("click", function () {
    const name = document.getElementById("indicator-name").value;
    const interval = document.getElementById("indicator-interval").value;

    // Collect all dynamic params
    const params = {};
    document.querySelectorAll("#indicator-params input").forEach(input => {
        params[input.name] = input.value;
    });

    // Ensure all fields have values
    if (!name || !interval || Object.values(params).some(v => !v)) {
        alert("Please fill in all indicator values.");
        return;
    }
    console.log(params)
    const formatted = `${name}-${Object.values(params).join("-")}-${interval}`;
    selectedIndicators.push(formatted);
    console.log(formatted)
    renderSelectedIndicators();

    // Clear params
    document.querySelectorAll("#indicator-params input").forEach(input => input.value = "");
});


let selectedEditIndicators = [];

function renderEditIndicators() {
    const container = document.getElementById("edit-indicator-tags");
    container.innerHTML = "";

    if (selectedEditIndicators.length === 0) {
        container.textContent = "None";
        return;
    }

    selectedEditIndicators.forEach((indicator) => {
        const span = document.createElement("span");
        span.classList.add("indicator-tag");
        span.textContent = indicator;
        container.appendChild(span);
    });
}

document.getElementById("edit-add-indicator").addEventListener("click", function () {
    const name = document.getElementById("edit-indicator-name").value;
    const period = document.getElementById("edit-indicator-period").value;
    const interval = document.getElementById("edit-indicator-interval").value;

    if (!name || !period || !interval) {
        alert("Please select all indicator values.");
        return;
    }

    const formatted = `${name}-${period}-${interval}`;
    selectedEditIndicators.push(formatted);
    renderEditIndicators();

    document.getElementById("edit-indicator-period").value = "";
    });
    





    ///indicators
document.addEventListener('DOMContentLoaded', function () {
  const indicatorParams = {
    SMA: { length: 14 },
    RSI: { length: 14 },
    EMA: { length: 14 },
    SUPERTREND: { signal: 3, slow: 20, fast: 10 },
    MACD: { multiplier: 2, length: 14 }
  };

  const indicatorSelect = document.getElementById("indicator-name");
  const parameterContainer = document.getElementById("indicator-params");
  const indicatorTags = document.getElementById("indicator-tags");

  function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
  }

  function createInput(param, defaultValue) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("indicator-char");

    const label = document.createElement("label");
    label.textContent = capitalize(param) + ":";
    wrapper.appendChild(label);

    const input = document.createElement("input");
    input.type = "number";
    input.name = param;
    input.value = defaultValue;
    input.min = 1;
    input.step = "any";
    wrapper.appendChild(input);

    return wrapper;
  }

  function updateParams() {
    const selected = indicatorSelect.value;
    const params = indicatorParams[selected] || {};

    parameterContainer.innerHTML = "";
    Object.entries(params).forEach(([param, defaultValue]) => {
      const inputWrapper = createInput(param, defaultValue);
      parameterContainer.appendChild(inputWrapper);
       console.log(inputWrapper)
    });
   
  }

  // Update params when the indicator dropdown changes
  indicatorSelect.addEventListener("change", updateParams);

  // Initial load
  updateParams();

  // Single click handler for Add Indicator
  document.getElementById("add-indicator").addEventListener("click", function () {
    const name = indicatorSelect.value;
    const interval = document.getElementById("indicator-interval").value;

    // Grab current input values
    const params = {};
    parameterContainer.querySelectorAll("input").forEach(input => {
      params[input.name] = parseFloat(input.value);
    });

    if (!name || !interval || Object.values(params).some(v => isNaN(v))) {
      alert("Please fill in all indicator values.");
      return;
    }

    const formatted = `${name}-${Object.values(params).join("-")}-${interval}`;
    console.log("Added:", formatted);

    const tag = document.createElement("div");
    tag.textContent = formatted;
    tag.style.padding = "5px 10px";
    tag.style.background = "#e0e0e0";
    tag.style.borderRadius = "5px";
    indicatorTags.appendChild(tag);

    // **Do NOT clear the params here**. Keep them so user can adjust or select another indicator.
    // parameterContainer.innerHTML = ""; // <-- remove this line
  });
});
