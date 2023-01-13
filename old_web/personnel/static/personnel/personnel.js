add_listeners('.edit-btn', edit_clicked);
add_listeners('.save-btn', save_clicked);

function add_listeners(element, fn) {
    document.querySelectorAll(element).forEach(el => el.addEventListener('click', fn));
}

function get_row(target) {
    const row = target.parentElement.parentElement.parentElement;
    return row;
}

function edit_clicked(event) {
    const row = get_row(event.currentTarget);

    row.querySelector('.edit_delete').classList.toggle('d-none');
    row.querySelector('.save').classList.toggle('d-none');

    row.querySelectorAll('.value').forEach(val => val.classList.toggle('d-none'));
    row.querySelectorAll('.options').forEach(val => val.classList.toggle('d-none'));
}

function save_clicked(event) {
    const row = get_row(event.currentTarget)

    row.querySelectorAll('select').forEach(sel => sel.classList.toggle('d-none'));
    row.querySelectorAll('.value').forEach(val => val.classList.toggle('d-none'));

    row.querySelector('.save').classList.toggle('d-none');
    row.querySelector('.edit_delete').classList.toggle('d-none');

    row.querySelectorAll('.cell').forEach(cell => {
        const value = cell.querySelector('.value');
        const select = cell.querySelector('select');

        value.textContent = select.options[select.selectedIndex].text;
    });

    const person_id = row.id;
    const assigned_org = row.querySelector('.org .value').textContent;
    
    let qual_names = [];
    document.querySelectorAll('.qual_header').forEach(qual => qual_names.push(qual.textContent));

    let quals = {};
    row.querySelectorAll('.qual .value').forEach((qual, index) => quals[qual_names[index]] = qual.textContent);

    data = {
        "person_id": person_id,
        "org": assigned_org,
        "quals": quals
    };

    send_data(data);
}

function send_data(data) {
    console.log(data);
    const httpRequest = new XMLHttpRequest();
    httpRequest.onreadystatechange = () => {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                console.log("Data saved");
            }
        }
    };

    httpRequest.open('POST', '/personnel/' + data.person_id);
    httpRequest.setRequestHeader('Content-Type', 'application/json');

    const csrfToken = Cookies.get('csrftoken');
    httpRequest.setRequestHeader('X-CSRFToken', csrfToken);

    httpRequest.send(JSON.stringify(data));
}