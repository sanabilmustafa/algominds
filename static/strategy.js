document.querySelectorAll('.strategy-tab-item').forEach((tab, index) => {
    tab.addEventListener('click', function (e) {
        e.preventDefault();

        // Toggle active class
        document.querySelectorAll('.strategy-tab-item').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');

        // Show/hide strategy sections
        const allContainer = document.querySelector('.strategies-container');
        const deployedContainer = document.querySelector('.strategy-deployed-container');

        if (index === 0) {
            allContainer.style.display = 'grid';
            deployedContainer.style.display = 'none';
        } else if (index === 1) {
            allContainer.style.display = 'none';
            deployedContainer.style.display = 'grid';
        }
    });
});

function applyDeployedState(card, strategyData) {
    console.log('Applying deployed state for:', strategyData.strategy_name);
    const deployButton = card.querySelector('.deploy-btn');
    const checkbox = card.querySelector('.strategy-status input[type="checkbox"]');
    const status = card.querySelector('.strategy-status p');

    if (strategyData.deploy_status === 'Deployed') {
        card.classList.add('deployed');

        if (deployButton) {
            deployButton.classList.add('deployed-btn');
        }

        if (checkbox) {
            checkbox.disabled = false;
            checkbox.checked = strategyData.status === 'Active';
        }

        if (status) {
            if (strategyData.status === 'Active') {
                status.textContent = 'Active';
                status.classList.remove('status-inactive');
                status.classList.add('status-active');
            } else {
                status.textContent = 'Inactive';
                status.classList.remove('status-active');
                status.classList.add('status-inactive');
            }
        }
    }
}

document.addEventListener('DOMContentLoaded', function () {
    // Activate Select2 for all selects
    const stockSelects = document.querySelectorAll('.stock-select');
    stockSelects.forEach(select => {
        $(select).select2({
            placeholder: "Select stock symbols",
            width: '80%'
        });
    });
});

// DEPLOY button click
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('deployed-btn') || e.target.classList.contains('deploy-btn')) {
        e.preventDefault();

        const activeswitch = document.querySelector('.strategy-status input[type="checkbox"]');
        const status = document.querySelector('.strategy-status p');
        const isDeployed = e.target.classList.contains('deployed-btn');
        const button = e.target;
        const form = button.closest('form');
        const card = button.closest('.strategy');
        const checkbox = card.querySelector('.strategy-status input[type="checkbox"]');
        const stockSelect = Array.from(form.querySelectorAll('.stock-select')).flatMap(select =>
            Array.from(select.selectedOptions).map(option => option.value)
        ).filter(Boolean);
        console.log(stockSelect)
        const allocation = form.querySelector('input[name="allocation_of_balance"]').value;
        const allocationPercents = card.querySelectorAll('input[name="allocation_percent[]"]');


        const stockAllocations = [];
        for (let i = 0; i < stockSelect.length; i++) {
            const symbol = stockSelect[i];
            let percent = allocationPercents[i].value;
            console.log(percent)
            // if(percent == "" || percent == null || percent == undefined) {
            //     alert("Please fill all allocation fields before deploying.");
            //     return;
            // }

            stockAllocations.push({
                stock_symbol: symbol,
                allocation_percent: parseFloat(percent)
            });
        }
        let sum = 0;
        for(let i = 0; i < stockAllocations.length; i++) {
            sum += stockAllocations[i].allocation_percent;
        }
        if (sum !== 100) {
            alert("Total allocation percentage must equal 100%. Current total: " + sum + "%");
            return;
        }
        else{
            console.log("Total allocation percentage is valid: " + sum + "%");
            console.log(stockAllocations)
        }
    
        if (isDeployed) {
            if (confirm("Are you sure you want to undeploy this strategy?")) {
                fetch('/strategy/deploy', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        strategy_id: card.getAttribute('data-strategy-id'),
                        deploy_status: 'Undeployed',
                        status: 'Inactive',
                        strategy_name: card.querySelector('h3').textContent,
                        strategy_author: card.querySelector('.author-name').textContent,
                        description: `Type: ${card.querySelectorAll('.char .value')[0].textContent}, Asset Class: ${card.querySelectorAll('.char .value')[1].textContent}`,
                        stocks: stockSelect,
                        allocation_of_assets: allocation,
                        client_id: 1,  // dynamically insert if you have logged-in user support
                        stock_allocations: stockAllocations

                    })
                })
                    .then(response => {
                        if (!response.ok) throw new Error(`Server returned ${response.status}`);
                        return response.json();
                    })
                    .then(data => {
                        if (data.success) {
                            button.classList.remove('deployed-btn');
                            button.classList.add('deploy-btn');
                            button.textContent = 'Undeployed';

                            checkbox.checked = false;
                            checkbox.disabled = true;

                            status.classList.remove('status-active');
                            status.classList.add('status-inactive');
                            status.textContent = 'Inactive';

                            const undeployedContainer = document.getElementById('strategy-undeployed-container');
                            if (undeployedContainer) {
                                undeployedContainer.append(card);
                            }
                        } else {
                            alert('Undeploy failed: ' + data.message);
                        }
                    });
            }
        }
        else {
            if (!stockSelect.length || !allocation) {
                alert("Please fill all fields before deploying.");
                return;
            } 

            const confirmText = `
            Selected Stocks: ${stockSelect.join(', ')}\n
            Allocation: ${allocation}%\n
            Are you sure you want to deploy this strategy?
        `;

            if (confirm(confirmText)) {
                // send data to the backend via fetch
                fetch('/strategy/deploy', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-Requested-With': 'XMLHttpRequest'
                    },
                    body: JSON.stringify({
                        strategy_id: card.getAttribute('data-strategy-id'),
                        strategy_name: card.querySelector('h3').textContent,
                        strategy_author: card.querySelector('.author-name').textContent,
                        description: `Type: ${card.querySelectorAll('.char .value')[0].textContent}, Asset Class: ${card.querySelectorAll('.char .value')[1].textContent}`,
                        stocks: stockSelect,
                        allocation_of_assets: allocation,
                        status: 'Active',
                        deploy_status: 'Deployed',
                        client_id: 1, // dynamically insert if you have logged-in user support
                        stock_allocations: stockAllocations
                    })
                })
                    .then(response => {
                        if (!response.ok) {
                            throw new Error(`Server returned ${response.status}`);
                        }
                        return response.json();
                    })
                    // .then(response => response.json())
                    .then(data => {
                        if (data.success) {
                            console.log('Strategy deployed successfully:', data);

                            button.classList.remove('deploy-btn');
                            button.classList.add('deployed-btn');
                            button.textContent = 'Deployed';

                            const checkbox = card.querySelector('.strategy-status input[type="checkbox"]');
                            if (checkbox) {
                                checkbox.disabled = false;
                                checkbox.checked = true;
                            }

                            status.classList.remove('status-inactive');
                            status.classList.add('status-active');
                            status.textContent = 'Active';

                            const deployedContainer = document.getElementById('strategy-deployed-container');
                            if (deployedContainer) {
                                deployedContainer.append(card);
                            }
                            applyDeployedState(card, data)
                        } else {
                            alert('Deployment failed: ' + data.message);
                        }
                    })

            }
        }
    }
});
document.addEventListener('change', function (e) {
    if (e.target.matches('.strategy-status input[type="checkbox"]')) {
        const checkbox = e.target;
        const card = checkbox.closest('.strategy');
        const status = card.querySelector('.strategy-status p');
        const deploy_btn = card.querySelector('.deploy-btn');

        // Check if the strategy is deployed
        if (deploy_btn && deploy_btn.innerHTML.trim() === 'Undeployed') {
            alert("Please deploy the strategy before activating.");
            checkbox.checked = false;
            return;
        }

        const isActivating = checkbox.checked;
        const confirmationMessage = isActivating
            ? "Are you sure you want to activate this strategy?"
            : "Are you sure you want to deactivate this strategy?";
        const newStatus = isActivating ? 'Active' : 'Inactive';
        // const endpoint = isActivating ? '/strategy/activate' : '/strategy/deactivate';

        if (confirm(confirmationMessage)) {
            // Send request to backend
            fetch('/strategy/activation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    strategy_id: card.getAttribute('data-strategy-id'),
                    status: newStatus
                })
            })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        console.log(`Strategy ${newStatus.toLowerCase()}d successfully:`, data);
                        status.classList.toggle('status-active', isActivating);
                        status.classList.toggle('status-inactive', !isActivating);
                        status.textContent = newStatus;
                    } else {
                        alert(`${newStatus} failed: ` + data.message);
                        checkbox.checked = !isActivating; // Revert checkbox
                    }
                })
                .catch(error => {
                    console.error(`Error ${newStatus.toLowerCase()}ing strategy:`, error);
                    checkbox.checked = !isActivating; // Revert checkbox
                });
        } else {
            checkbox.checked = !isActivating; // Revert checkbox if user cancels
        }
    }
});



// document.addEventListener('DOMContentLoaded', () => {
//     const strategyContainers = document.querySelectorAll('.strategy');

//     strategyContainers.forEach(container => {
//         const strategyId = container.dataset.strategyId;
//         const stockSelect = container.querySelector('.stock-select-' + strategyId);
//         // const stockSelect = container.querySelector('#stock-select-' + strategyId);
//         const allocationsContainer = container.querySelector('#stock-allocations-' + strategyId);

//         // Extract backend allocations from a hidden input or JSON script tag
//         const rawAllocations = container.querySelector('.backend-allocations');
//         const allocations = rawAllocations ? JSON.parse(rawAllocations.textContent) : {};

//         const updateAllocations = () => {
//             const selectedStocks = Array.from(stockSelect.selectedOptions).map(opt => opt.value);
//             allocationsContainer.innerHTML = '';
       
//             selectedStocks.forEach(symbol => {
//                 const defaultPercent = (100 / selectedStocks.length).toFixed(2);
//                 const percent = allocations[symbol] || defaultPercent;
//                 const row = document.createElement('div');
//                 row.classList.add('stock-row');
//                 // row.innerHTML = `
//                 //     <label>${symbol}</label>
//                 //     <input class="stock-name" type="hidden" name="stock_symbol[]" value="${symbol}" />
//                 //     <input class="stock-allocation" name="allocation_percent[]" type="number" min="1" max="100" value="${percent}" placeholder="Allocation %"  />
//                 // `;
//                 allocationsContainer.appendChild(row);
//             });
//         };

//         // Initial population
//         updateAllocations();

//         // On selection change
//         stockSelect.addEventListener('change', updateAllocations);
//     });
// });


