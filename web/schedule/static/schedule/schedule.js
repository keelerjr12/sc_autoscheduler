let currentTab = 0;

showTab(currentTab);

function showTab(tab) {
    let x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "block";
}

function hideTab(tab) {
    let x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "none";
}

function prevNext(increment) {
    hideTab(currentTab);
    currentTab += increment;
    showTab(currentTab);
}