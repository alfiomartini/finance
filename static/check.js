function checkUser(){
    var input = document.querySelector('input');
    var value = input.value 
    $.get('/check?username='+value, function(data){
    var avail = JSON.parse(data);
    if (avail){
        let modal = new Modal('')
        modal.show('Name is available.');
    }
    else{
        let modal = new Modal('')
        modal.show('Name is used.');
    }
    });
};