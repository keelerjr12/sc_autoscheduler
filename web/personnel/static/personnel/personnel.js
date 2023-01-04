initialize_edit_listeners();
initialize_save_listeners();

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
    let edit_delete = event.target.parentElement;
    edit_delete.style.display = 'none';

    let cell = edit_delete.parentElement;
    let save = cell.getElementsByClassName('save')[0];
    save.style.display = 'block';

    const row = cell.parentElement;
    toggle_vis(row, 'value', 'none');
    toggle_vis(row, 'options', 'block');
}

function save_clicked(event) {
    let row = event.target.parentElement.parentElement.parentElement;
    const id = row.id;

    data = {};
    data['pilot_id'] = id;

    const cells = row.getElementsByClassName('cell');
    Array.from(cells).forEach(cell => {
        const sel = cell.getElementsByTagName('select')[0];
        const select_id = sel.id;
        let select_opt = sel.options[sel.selectedIndex].text;
        
        const val = cell.getElementsByClassName('value')[0];
        val.textContent = select_opt;

        data[select_id] = select_opt;
    });

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
    console.log(data);
}