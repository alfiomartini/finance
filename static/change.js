document.addEventListener('DOMContentLoaded', listeners);

function listeners(){
    let button = document.getElementById('btn-chg');
    let form = document.getElementById('change');
    let toggleForm = new HideForm();

    button.addEventListener('click', formToggle);
    form.addEventListener('submit', checkPass);

    function formToggle(){
        if (toggleForm.getHidden()){
            if (form.getAttribute('hidden') !== null)
                form.removeAttribute('hidden');
            $('#change').show();
            toggleForm.setHidden(false);
        }
        else{
            $('#change').hide();
            toggleForm.setHidden(true); 
        }
    };

    function checkPass(event){
        event.preventDefault();
        var newpass = document.getElementById('new');
        var confpass = document.getElementById('conf');
        if (newpass.value !== confpass.value){
            let modal = new Modal('');
            modal.show("New password and confirmation don't match");
            newpass.value= '';
            confpass.value = '';
            newpass.focus();
        }
        else form.submit();
        }
}
