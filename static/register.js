document.addEventListener('DOMContentLoaded', listeners)

function listeners(){

    let input = document.querySelector('input[name="username"]');
    let form = document.querySelector('form');

    input.addEventListener('change', checkUser);
    form.addEventListener('submit', checkPass);

    function checkUser(){
        var value = input.value;
        $.get('/check?username='+value, function(data){
            var avail = JSON.parse(data);
            if (!avail) {
                let modal = new Modal('');
                modal.show('Name already in use.');
                input.value= '';
                input.focus();
            }   
        });
    }

    function checkPass(event){
        event.preventDefault();
        let pass = document.getElementById('pass');
        let conf = document.getElementById('conf');
        if (pass.value !== conf.value){
            let modal = new Modal('');
            modal.show("New password and confirmation don't match");
            pass.value= '';
            conf.value = '';
            pass.focus();
        }
        else form.submit();
    }
}