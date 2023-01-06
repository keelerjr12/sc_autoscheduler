const NUM_PAGES = 2;
let currentTab = 0;

showTab(currentTab);

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
}

function hideTab(tab) {
    let x = document.getElementsByClassName("tab");
    x[currentTab].style.display = "none";
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