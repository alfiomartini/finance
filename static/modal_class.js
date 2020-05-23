class Modal{
    constructor(message){
        this.setModal(message);
    }
    
    setModal(message){
        this._message = message;
        this._modal = `<!-- Trigger the modal with a button -->
        <button type="button" class="btn btn-primary" id="myBtn" hidden>Open Modal</button>
        <!-- The Modal -->
        <div class="modal fade" id="myModal">
            <div class="modal-dialog">
                <div class="modal-content text-dark">
                    <!-- Modal Header -->
                    <div class="modal-header">
                        <h4 class="modal-title">Error</h4>
                        <button type="button" class="close" data-dismiss="modal">×</button>
                    </div>
                    
                    <!-- Modal body -->
                    <div class="modal-body">
                    ${this._message}
                    </div>
                    
                    <!-- Modal footer -->
                    <div class="modal-footer">
                        <button type="button" class="btn btn-danger" 
                        data-dismiss="modal">Close</button>
                    </div>
                </div>
            </div>
        </div>`;
    }

    /* only when layout.html is included */
    show(message){
        let container = document.getElementById('modal-div');
        this.setModal(message);
        container.innerHTML = this.getModal();
        this.fireModal();
    }
     
    getModal(){
        return this._modal;
    }

    getMessage(){
        return this._message;
    }

    setMessage(message){
        this._message = message;
    }

    fireModal(){
        $("#myBtn").click(function(){
            $("#myModal").modal();
            });
        let event = new Event("click");
        let myBtn = document.getElementById('myBtn');
        myBtn.dispatchEvent(event);
    }

    
}

class Prompt extends Modal{
    constructor(message){
        super(''); // creates 'this' object
        this.setPrompt(message);
    }

    setPrompt(message){
        this._message = message;
        this._prompt = `<!-- Button trigger modal -->
        <button type="button" class="btn btn-primary" id="prompt-button" hidden>
          Launch demo modal
        </button>
        <!-- Modal -->
        <div class="modal fade" id="myPrompt">
          <div class="modal-dialog" role="document">
            <div class="modal-content text-dark">
              <div class="modal-header">
                <h5 class="modal-title" id="exampleModalLabel">Confirmation</h5>
                <button type="button" class="close" data-dismiss="modal" aria-label="Close">
                  <span aria-hidden="true">&times;</span>
                </button>
              </div>
              <div class="modal-body">
                ${this._message}
              </div>
              <div class="modal-footer">
                <button type="button" id="modal-yes" class="btn btn-danger" 
                onclick="";" data-dismiss="modal">
                Yes</button>
                <button type="button" id="modal-no" class="btn btn-primary" 
                onclick="" data-dismiss="modal">
                No</button>
              </div>
            </div>
          </div>
        </div>`;
    }

    getPrompt(){
        return this._prompt;
    }

    action(callback){
        callback();
    }

    firePrompt(){
        $("#prompt-button").click(function(){
            $("#myPrompt").modal();
            });
        let event = new Event("click");
        let button = document.getElementById('prompt-button');
        button.dispatchEvent(event);
    }
}