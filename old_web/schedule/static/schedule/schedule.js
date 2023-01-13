const NUM_PAGES = 4;
let currentTab = 0;

Date.prototype.addDays = function (days) {
    let newDate = new Date(this.valueOf());
    newDate.setDate(newDate.getDate() + days);

    return newDate;
}

let dateFrom = new Date();
let dateTo = dateFrom.addDays(5);

init_tabs();
showTab(currentTab);

function init_tabs() {
    document.getElementById("dateFrom").valueAsDate = dateFrom; 
    document.getElementById("dateTo").valueAsDate = dateTo;
}


function display(component, opt) {
    component.style.display = opt;
}

function hide(component) {
    component.style.visibility = "hidden";
}

function show(component) {
    component.style.visibility = "visible";
}

function showTab(tab) {
    let x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "block";

    let y = document.getElementsByClassName("menu-list-item");
    y[currentTab].classList.add("active");
}

function hideTab(tab) {
    let x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "none";

    let y = document.getElementsByClassName("menu-list-item");
    y[currentTab].classList.remove("active");
}

function prevNext(increment) {
    hideTab(currentTab);

    if (currentTab === 1 && increment === -1)
    {
        hide(document.querySelector("#prevBtn"))
    }
    else if (currentTab === 0 && increment === 1)
    {
        show(document.querySelector("#prevBtn"));
    }
    
    if (currentTab === (NUM_PAGES - 2) && (increment === 1)) {
        display(document.querySelector("#nextBtn"), 'none')
        display(document.querySelector('#buildBtn'), 'inline-block');
    } else if (currentTab === (NUM_PAGES - 1) && (increment === -1)) {
        display(document.querySelector("#nextBtn"), 'inline-block');
        display(document.querySelector('#buildBtn'), 'none');
    }

    currentTab += increment;

    showTab(currentTab);
}