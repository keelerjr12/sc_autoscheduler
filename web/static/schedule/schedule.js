let currentTab = 0;

showTab(currentTab);

function showTab(tab) {
    let x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "block";
}

function prevNext(increment) {
    alert('hey');
    currentTab += increment;
    showTab(currentTab);
}