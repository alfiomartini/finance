document.addEventListener('DOMContentLoaded', listeners)

function listeners(){
    let form = document.querySelector('form');
    let select = document.querySelector('select');

    form.addEventListener('submit', checkForm);
    select.addEventListener('change',selectSymb);

    function checkForm(event){
        event.preventDefault();
        let shares = document.querySelector('input[name="shares"]').value
        number = parseInt(shares)
        if (isNaN(number)){
            alert('You must provide a number')
        }
        else if (number < 0) {
            alert('You must provide a positive number.');
        }
        else form.submit();
    }

    function selectSymb(event){
        let selected = document.getElementById('known').value;
        document.getElementById('symbol').value = selected;
    }
}
 