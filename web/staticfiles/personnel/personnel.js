initialize_edit_listeners();
initialize_save_listeners();

initialize_row_edit_listeners();

function initialize_row_edit_listeners() {
    let edit_elms = document.getElementsByClassName('pilot_row');

    Array.from(edit_elms).forEach(element => {
    element.addEventListener('click', row_clicked);
    });
}

function row_clicked(event) {
    const target = event.currentTarget;
    console.log(target);

    const edit_form = document.getElementById("edit_form");
    edit_form.classList.add('show');
}

function initialize_edit_listeners() {
    let edit_elms = document.getElementsByClassName('edit');

    Array.from(edit_elms).forEach(element => {
    element.addEventListener('click', edit_clicked);
    });
}

function initialize_save_listeners() {
    let save_elms = document.getElementsByClassName('save');

    Array.from(save_elms).forEach(element => {
    element.addEventListener('click', save_clicked);
    });
}

function toggle_vis(row, className, display_opt) {
    let elements = row.getElementsByClassName(className);
    Array.from(elements).forEach(el => {
        el.style.display = display_opt;
    });
}

function edit_clicked(event) {
    let edit_delete = event.currentTarget.parentElement;
    edit_delete.style.display = 'none';

    let cell = edit_delete.parentElement;
    let save = cell.getElementsByClassName('save')[0];
    save.style.display = 'block';

    const row = cell.parentElement;
    toggle_vis(row, 'value', 'none');
    toggle_vis(row, 'options', 'block');
}

function map_values(val) {
    mapped_vals = {
        'ops_supervisor': 'Operations Supervisor',
        'sof': 'SOF',
        'rsu_controller': 'RSU Controller',
        'rsu_observer': 'RSU Observer',
        'pit_ip': 'PIT IP'
    };

    return mapped_vals[val]
}

function save_clicked(event) {
    let row = event.target.parentElement.parentElement.parentElement;
    const id = row.id;

    data = {};
    data['pilot_id'] = id;

    const cells = row.getElementsByClassName('cell');
    quals = {};
    Array.from(cells).forEach(cell => {
        const sel = cell.getElementsByTagName('select')[0];
        const select_id = sel.id;
        let select_opt = sel.options[sel.selectedIndex].text;
        
        const val = cell.getElementsByClassName('value')[0];
        val.textContent = select_opt;

        quals[map_values(select_id)] = select_opt;
    });

    data['quals'] = quals;

    let save = event.target.parentElement;
    save.style.display = 'none';

    let cell = save.parentElement;
    let edit_delete = cell.getElementsByClassName('edit_delete')[0];
    edit_delete.style.display = 'block';

    toggle_vis(row, 'value', 'block');
    toggle_vis(row, 'options', 'none');

    send_data(data);
}

function send_data(data) {
    const httpRequest = new XMLHttpRequest();
    httpRequest.onreadystatechange = () => {
        if (httpRequest.readyState === XMLHttpRequest.DONE) {
            if (httpRequest.status === 200) {
                console.log("Data saved");
            }
        }
    };

    httpRequest.open('POST', '/personnel/' + data.pilot_id);
    httpRequest.setRequestHeader('Content-Type', 'application/json');

    const csrfToken = Cookies.get('csrftoken');
    httpRequest.setRequestHeader('X-CSRFToken', csrfToken);

    httpRequest.send(JSON.stringify(data));
}