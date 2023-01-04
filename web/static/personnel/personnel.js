let elms = document.getElementsByClassName('cell');

Array.from(elms).forEach(element => {
   console.log(element);
   element.addEventListener('click', () => {console.log('clicked')});
});