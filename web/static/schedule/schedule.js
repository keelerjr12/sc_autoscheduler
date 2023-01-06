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
    if (currentTab == 0) {
        let prevBtn = document.querySelector('#prevBtn');
        prevBtn.style.display = "none";
    }

    showTab(currentTab);
}