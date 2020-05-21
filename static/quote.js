document.addEventListener('DOMContentLoaded', listeners)

function listeners(){
    let form = document.querySelector('form');

    form.addEventListener('submit', checkForm);

    function checkForm(event){
        event.preventDefault();
        let input = document.querySelector('input');
        let val = input.value;
        let patt = /[a-z]+/i;
        if (patt.test(val))
            form.submit();
        else {
            alert('Only alphabetical characters allowed.');
        }
    }
}