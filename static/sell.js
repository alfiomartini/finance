document.addEventListener('DOMContentLoaded', listeners)

function listeners(){
    let form = document.querySelector('form');
    let select = document.querySelector('select');
    let known = document.querySelector('input[name="symbol"]').dataset.symbol;
    
    if (known !== 'unknown'){
        document.getElementById('symbol').value = known;
    }

    form.addEventListener('submit', message);
    select.addEventListener('change',selectSymb);

    function message(){
        let spinner = document.getElementById('spinner');
        form.style.display = 'none';
        spinner.innerHTML = `<div class=btn-spinner>
                               <button class="btn btn-primary">
                                 <span class="spinner-border spinner-border-sm"></span>
                                Wait a moment...
                              </button> </div>`
    }

    // function checkForm(event){
    //     event.preventDefault();
    //     let shares = document.querySelector('input[name="shares"]').value
    //     number = parseInt(shares)
    //     if (isNaN(number)){
    //         let modal = new Modal();
    //         modal.show('You must provide a number');
    //     }
    //     else if (number <= 0) {
    //         let modal = new Modal('');
    //         modal.show('You must provide a positive number.');
    //     }
    //     else form.submit();
    // }

    function selectSymb(event){
        let selected = document.getElementById('known').value;
        document.getElementById('symbol').value = selected;
    }
}
 