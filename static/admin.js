// =============================
// ADMIN PANEL SCRIPT
// =============================

document.addEventListener("DOMContentLoaded", function () {

    console.log("Admin panel loaded");


    // =============================
    // SIDEBAR ACTIVE MENU
    // =============================

    const links = document.querySelectorAll(".sidebar li");

    links.forEach(link => {
        link.addEventListener("click", () => {

            links.forEach(l => l.classList.remove("active"));

            link.classList.add("active");

        });
    });



    // =============================
    // SEARCH FILTER (USERS PAGE)
    // =============================

    const userSearch = document.querySelector("#userSearch");

    if(userSearch){

        userSearch.addEventListener("keyup", function(){

            const value = this.value.toLowerCase();

            const rows = document.querySelectorAll("#usersTable tr");

            rows.forEach(row => {

                const text = row.innerText.toLowerCase();

                row.style.display = text.includes(value) ? "" : "none";

            });

        });

    }



    // =============================
    // SEARCH FILTER (ORDERS)
    // =============================

    const orderSearch = document.querySelector("#orderSearch");

    if(orderSearch){

        orderSearch.addEventListener("keyup", function(){

            const value = this.value.toLowerCase();

            const rows = document.querySelectorAll("#ordersTable tr");

            rows.forEach(row => {

                const text = row.innerText.toLowerCase();

                row.style.display = text.includes(value) ? "" : "none";

            });

        });

    }



    // =============================
    // MENU ITEM DELETE BUTTON
    // =============================

    const deleteButtons = document.querySelectorAll(".delete-item");

    deleteButtons.forEach(btn => {

        btn.addEventListener("click", function(){

            const card = btn.closest(".menu-card");

            if(confirm("Delete this menu item?")){

                card.remove();

            }

        });

    });



    // =============================
    // MENU ITEM EDIT BUTTON
    // =============================

    const editButtons = document.querySelectorAll(".edit-item");

    editButtons.forEach(btn => {

        btn.addEventListener("click", function(){

            const card = btn.closest(".menu-card");

            const title = card.querySelector("h3");

            const newName = prompt("Edit item name", title.innerText);

            if(newName){

                title.innerText = newName;

            }

        });

    });



    // =============================
    // ORDER STATUS CHANGE
    // =============================

    const statusSelect = document.querySelectorAll(".status-select");

    statusSelect.forEach(select => {

        select.addEventListener("change", function(){

            const status = select.value;

            const badge = select.parentElement.querySelector(".status-badge");

            badge.innerText = status;

            badge.className = "status-badge " + status.toLowerCase();

        });

    });



    // =============================
    // SETTINGS MEAL MODE
    // =============================

    const mealButtons = document.querySelectorAll(".meal-mode");

    mealButtons.forEach(btn => {

        btn.addEventListener("click", function(){

            mealButtons.forEach(b => b.classList.remove("active"));

            btn.classList.add("active");

        });

    });



    // =============================
    // DASHBOARD CHARTS
    // =============================

    if(document.getElementById("revenueChart")){

        new Chart(

            document.getElementById("revenueChart"),

            {
                type: "line",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Revenue",
                            data: [],
                            borderColor: "#10b981",
                            tension: 0.4
                        }
                    ]
                },
                options: {
                    responsive: true
                }
            }

        );

    }



    if(document.getElementById("categoryChart")){

        new Chart(

            document.getElementById("categoryChart"),

            {
                type: "bar",
                data: {
                    labels: [],
                    datasets: [
                        {
                            label: "Categories",
                            data: [],
                            backgroundColor: "#10b981"
                        }
                    ]
                },
                options: {
                    responsive: true
                }
            }

        );

    }



    if(document.getElementById("orderChart")){

        new Chart(

            document.getElementById("orderChart"),

            {
                type: "doughnut",
                data: {
                    labels: [],
                    datasets: [
                        {
                            data: [],
                            backgroundColor: [
                                "#f59e0b",
                                "#3b82f6",
                                "#10b981"
                            ]
                        }
                    ]
                }
            }

        );

    }


});